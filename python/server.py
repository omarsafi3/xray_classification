import os
import flwr as fl
import numpy as np
import logging
import tensorflow as tf
from keras.applications import ResNet50V2
from keras import layers, Model, Input
from keras.layers import GlobalAveragePooling2D, Reshape, Dense, multiply, BatchNormalization, Dropout, Conv2D, Add
from keras.regularizers import l2
from flwr.common import parameters_to_ndarrays
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
from keras.models import model_from_json
from IPython.display import clear_output
import requests

# Enable logging
logging.basicConfig(level=logging.INFO)

# Enable GPU memory growth if available
gpus = tf.config.list_physical_devices('GPU')
def load_central_test_data(test_dir, batch_size=32):
    test_dataset = tf.keras.preprocessing.image_dataset_from_directory(
        test_dir,
        labels='inferred',
        label_mode='categorical',  # Matches client label format
        image_size=(224, 224),
        batch_size=batch_size,
        shuffle=False  # Important: do not shuffle test data
    )

    # Normalize to [0, 1] range just like in the client
    test_dataset = test_dataset.map(lambda x, y: (x / 255.0, y))
    return test_dataset

if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        logging.warning(f"Failed to set memory growth: {e}")


def safe_div(numerator, denominator):
    return tf.math.divide_no_nan(numerator, denominator)

def sensitivity(y_true, y_pred):
    y_pred = tf.round(y_pred)
    true_positives = tf.reduce_sum(y_true * y_pred)
    possible_positives = tf.reduce_sum(y_true)
    return safe_div(true_positives, possible_positives)

def specificity(y_true, y_pred):
    y_pred = tf.round(y_pred)
    true_negatives = tf.reduce_sum((1 - y_true) * (1 - y_pred))
    possible_negatives = tf.reduce_sum(1 - y_true)
    return safe_div(true_negatives, possible_negatives)

def SEBlock(input_tensor, se_ratio=16, activation='relu', kernel_initializer='he_normal'):
    input_channels = input_tensor.shape[-1]
    reduced_channels = max(1, input_channels // se_ratio)
    x = GlobalAveragePooling2D()(input_tensor)
    x = Reshape((1, 1, input_channels))(x)
    x = Conv2D(reduced_channels, 1, activation=activation, kernel_initializer=kernel_initializer)(x)
    x = Conv2D(input_channels, 1, activation='sigmoid', kernel_initializer=kernel_initializer)(x)
    return multiply([input_tensor, x])

def build_improved_se_resnet(num_classes=4):
    base = ResNet50V2(include_top=False, weights="imagenet", input_shape=(224, 224, 3))
    for layer in base.layers[:100]:
        layer.trainable = False
    inputs = base.input
    x3 = SEBlock(base.get_layer("conv4_block6_out").output)
    x4 = SEBlock(base.get_layer("conv5_block3_out").output)
    x4 = Conv2D(1024, 1, padding='same')(x4)
    x = Add()([x3, x4])
    x = GlobalAveragePooling2D()(x)
    x = BatchNormalization()(x)
    x = Dropout(0.5)(x)
    x = Dense(512, activation='relu', kernel_regularizer=l2(0.01))(x)
    outputs = Dense(num_classes, activation='softmax')(x)
    return Model(inputs=inputs, outputs=outputs)


class SaveBestModelStrategy(fl.server.strategy.FedAvg):
    def __init__(self, model_builder, save_dir="saved_models", **kwargs):
        self.test_data = kwargs.pop("test_data", None)  # pop first
        super().__init__(**kwargs)                      # then call parent constructor
	# Call this once
        test_data_path = os.environ.get("TEST_DATA_PATH", "test")
        self.test_data = load_central_test_data(test_data_path)

        self.best_val_loss = get_best_val_loss(save_dir)
        self.model_builder = model_builder
        self.save_dir = save_dir
        self.last_parameters = None
        self.rounds = []           
        self.acc_per_round = []  
    def _plot_accuracy(self):
        plt.clf()  # Clear current figure
        plt.plot(self.rounds, self.acc_per_round, marker='o', color='blue')
        plt.title("Accuracy vs. Round (on Server Test Data)")
        plt.xlabel("Federated Round")
        plt.ylabel("Test Accuracy")
        plt.grid(True)
        plt.tight_layout()
   	 # Save figure to a file that updates every round
        plt.savefig("accuracy_progress.png")
        plt.close()




       
    def _evaluate_on_central_data(self, aggregated_parameters, round_number):
        model = self.model_builder()
        model.set_weights(fl.common.parameters_to_ndarrays(aggregated_parameters))
        test_dataset = self.test_data
	
        model.compile(
	    optimizer=tf.keras.optimizers.Adam(1e-4),
	    loss=tf.keras.losses.CategoricalCrossentropy(),
	    metrics=["accuracy", sensitivity, specificity]
	)

        loss, acc, sensitivity_val, specificity_val = model.evaluate(test_dataset, verbose=0)


        self.acc_per_round.append(acc)
        self.rounds.append(round_number)

        self._plot_accuracy()
        self._send_global_metrics({
        "round": round_number,
        "testLoss": round(float(loss), 4),
        "testAccuracy": round(float(acc), 4),
        "sensitivity": round(float(sensitivity_val), 4),
        "specificity": round(float(specificity_val), 4)
    })


        plt.clf()
        plt.plot(self.rounds, self.acc_per_round, label="Server Test Accuracy", marker='o')
        plt.xlabel("Round")
        plt.ylabel("Accuracy")
        plt.title("Central Test Accuracy Over Rounds")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.pause(0.01)
        self._plot_accuracy()

    def _send_global_metrics(self, metrics):
        try:
            backend_url = os.environ.get("BACKEND_URL", "http://localhost:8080")
            response = requests.post(f"{backend_url}/api/v1/model/metrics/save", json=metrics)
            logging.info(f"[Dashboard] Sent global metrics: {metrics}, Response: {response.status_code}, {response.text}")
        except Exception as e:
            logging.warning(f"[Dashboard] Failed to send metrics: {e}")


    def aggregate_fit(self, server_round, results, failures):
        """Aggregate fit results and metrics."""
        if not results:
            logging.warning(f"[Aggregate_Fit] No results received at round {server_round}")
            return None, {}
        try:
            # Extract parameters and metrics from results
            parameters = [fit_res.parameters for _, fit_res in results]
            num_examples = [fit_res.num_examples for _, fit_res in results]
            fit_metrics = [fit_res.metrics for _, fit_res in results]
            logging.info(fit_metrics)
            # Aggregate parameters using weighted average
            aggregated_parameters = fl.common.parameters_to_ndarrays(parameters[0]) # [Layer X Weight, Layer X Bias, ...]
            total_examples = sum(num_examples) # Total Number of examples 
            for i, param in enumerate(aggregated_parameters): # Loop over each Layer
                weighted_sum = sum(
                    fl.common.parameters_to_ndarrays(res.parameters)[i] * 1/ (fit_metrics[j]["val_loss"] + 1e-9)# Calculate Weighted Sum of Layer i
                    for j, (_, res) in enumerate(results) # Loop on each client
                )
                weight_sum = sum(
    			1 / (fit_metrics[j]["val_loss"] + 1e-9)
    			for j in range(len(results))
			)
		
                aggregated_parameters[i] = weighted_sum/ weight_sum
                
            # Aggregate fit metrics
            aggregated_metrics = {}
            for metrics in fit_metrics:
                for metric_name, metric_value in metrics.items():
                    if metric_name not in aggregated_metrics:
                        aggregated_metrics[metric_name] = []
                    aggregated_metrics[metric_name].append((metric_value, total_examples))
            metrics = {}
            for metric_name, values in aggregated_metrics.items():
                total_weighted = sum(value * weight for value, weight in values)
                total_examples = sum(weight for _, weight in values)
                metrics[metric_name] = total_weighted / total_examples if total_examples > 0 else 0.0
            logging.info(f"[Aggregate_Fit] Round {server_round} - Metrics: {metrics}")

            # Store parameters for evaluation
            self.last_parameters = fl.common.ndarrays_to_parameters(aggregated_parameters)
            self._evaluate_on_central_data(self.last_parameters, server_round)

            return self.last_parameters, metrics
        except Exception as e:
            logging.error(f"[Aggregate_Fit] Error in aggregate_fit: {e}")
            raise

    def aggregate_evaluate(self, server_round, results, failures):
        """Aggregate evaluation results."""
        if not results:
            logging.warning(f"[Aggregate_Evaluate] No results received at round {server_round}")
            return None, {}
        try:
            total_loss = sum(result[1].loss * result[1].num_examples for result in results)
            total_examples = sum(result[1].num_examples for result in results)
            aggregated_loss = total_loss / total_examples if total_examples > 0 else float('inf')
            aggregated_metrics = {}
            for metric_name in results[0][1].metrics.keys():
                metric_sum = sum(result[1].metrics[metric_name] * result[1].num_examples for result in results)
                aggregated_metrics[metric_name] = metric_sum / total_examples if total_examples > 0 else 0.0
            logging.info(f"[Aggregate_Evaluate] Round {server_round} - Loss: {aggregated_loss:.4f}, Metrics: {aggregated_metrics}")

            # Force evaluation using aggregated results
            self._force_evaluate(server_round, aggregated_loss, aggregated_metrics)

            return aggregated_loss, aggregated_metrics
        except Exception as e:
            logging.error(f"[Aggregate_Evaluate] Error in aggregate_evaluate: {e}")
            raise

    def _force_evaluate(self, server_round, val_loss, metrics):
        """Force evaluation logic to save model if val_loss improves."""
        logging.info(f"[Evaluate_Round] Starting round {server_round}")
        try:
            if val_loss is not None and val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                logging.info(f"[Evaluate_Round] New best val_loss: {val_loss:.4f} at round {server_round}")
                try:
                    if self.last_parameters is not None:
                        self.save_model(self.last_parameters, server_round, val_loss)
                    else:
                        logging.warning(f"[Evaluate_Round] No parameters available to save at round {server_round}")
                except Exception as e:
                    logging.error(f"[Evaluate_Round] Failed to save model: {e}")
            else:
                logging.info(f"[Evaluate_Round] No improvement: val_loss {val_loss:.4f} (best: {self.best_val_loss:.4f})")
        except Exception as e:
            logging.error(f"[Evaluate_Round] Error in force_evaluate: {e}")

    def save_model(self, parameters, server_round, val_loss):
        try:
            # Convert Flower Parameters to NumPy arrays
            weights = parameters_to_ndarrays(parameters)

            # Rebuild the Keras model using your model builder
            model = self.model_builder()
            model.set_weights(weights)  # Set the weights received from server

            # Create save directory if it doesn't exist
            os.makedirs(self.save_dir, exist_ok=True)
            model_path = os.path.join(self.save_dir, f"model_round_{server_round}_loss_{val_loss:.4f}.keras")

            model.save(model_path)
            logging.info(f"[SAVE_MODEL] Saved model to {model_path}")
        except Exception as e:
            logging.error(f"[Evaluate_Round] Failed to save model: {e}")




    @staticmethod
    def parameters_to_weights(parameters):
        return [np.array(t, dtype=np.float32) for t in parameters.tensors]

def load_latest_model_weights(model, save_dir):
    import re

    if not os.path.exists(save_dir):
        return model  # Nothing to load

    # List saved models and sort by round or val_loss
    model_files = [f for f in os.listdir(save_dir) if f.endswith(".keras")]
    if not model_files:
        return model  # No saved model

    
    def extract_info(fname):
        match = re.search(r"model_round_(\d+)_loss_([\d.]+)", fname)
        if match:
            round_num = int(match.group(1))
            val_loss_str = match.group(2).rstrip('.')  
            val_loss = float(val_loss_str)
            return round_num, val_loss
        return -1, float("inf")


    # Get latest or best model
    best_model_file = max(model_files, key=lambda f: extract_info(f)[0])  
    model_path = os.path.join(save_dir, best_model_file)

    print(f"[LOAD_MODEL] Loading model from: {model_path}")
    model.load_weights(model_path)
    return model


def get_best_val_loss(save_dir):
    import re
    if not os.path.exists(save_dir):
        return float("inf")
    model_files = [f for f in os.listdir(save_dir) if f.endswith(".keras")]
    if not model_files:
        return float("inf")
    losses = []
    for f in model_files:
        match = re.search(r"loss_([\d.]+)", f)
        if match:
            losses.append(float(match.group(1).rstrip('.')))

    return min(losses) if losses else float("inf")

def model_builder():
    model = build_improved_se_resnet(num_classes=4)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss="categorical_crossentropy",
        metrics=["accuracy", sensitivity, specificity]
    )
    model = load_latest_model_weights(model, save_dir="saved_models")
    return model



if __name__ == "__main__":
    _ = model_builder()


    test_data_path = os.environ.get("TEST_DATA_PATH", "test")
    strategy = SaveBestModelStrategy(
        model_builder=model_builder,
        test_data = load_central_test_data(test_data_path),  #
        fraction_fit=1.0,
        fraction_evaluate=1.0,
        min_fit_clients=1,
        min_evaluate_clients=1,
        min_available_clients=1,
        evaluate_metrics_aggregation_fn=SaveBestModelStrategy.aggregate_evaluate
    )
    plt.ion()  # Turn on interactive mode

    fl.server.start_server(
        server_address="localhost:8081",
        config=fl.server.ServerConfig(num_rounds=100),
        strategy=strategy
    )
