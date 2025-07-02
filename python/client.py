import os
import flwr as fl
import tensorflow as tf
from keras.applications import ResNet50V2
from keras import layers, Model, Input
from keras.layers import GlobalAveragePooling2D, Reshape, Dense, multiply, BatchNormalization, Dropout, Conv2D, Add
from keras.regularizers import l2
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)

# Enable GPU memory growth
gpus = tf.config.experimental.list_physical_devices('GPU')
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

class FlowerClient(fl.client.NumPyClient):
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.model = build_improved_se_resnet(num_classes=4)
        self.load_data()
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)
        self.loss_fn = tf.keras.losses.CategoricalCrossentropy()
        self.es = EarlyStopping(monitor="val_loss", patience=10, verbose=1, mode="min", restore_best_weights=True)
        self.lrr = ReduceLROnPlateau(monitor="val_loss", patience=3, factor=0.1, min_lr=1e-6, verbose=1)

    def load_data(self):
        try:
            self.train_dataset = tf.keras.preprocessing.image_dataset_from_directory(
                self.dataset_path,
                validation_split=0.1,
                subset="training",
                seed=42,
                labels="inferred",
                label_mode="categorical",
                image_size=(224, 224),
                batch_size=32,
                shuffle=True
            ).map(lambda x, y: (x / 255.0, y))

            self.val_dataset = tf.keras.preprocessing.image_dataset_from_directory(
                self.dataset_path,
                validation_split=0.1,
                subset="validation",
                seed=42,
                labels="inferred",
                label_mode="categorical",
                image_size=(224, 224),
                batch_size=32,
                shuffle=True
            ).map(lambda x, y: (x / 255.0, y))

            self.train_samples = sum(batch[0].shape[0] for batch in self.train_dataset)
            self.val_samples = sum(batch[0].shape[0] for batch in self.val_dataset)

            logging.info(f"Loaded {self.train_samples} training samples and {self.val_samples} validation samples")

            if self.train_samples == 0 or self.val_samples == 0:
                raise ValueError("Empty dataset detected")

        except Exception as e:
            logging.error(f"Failed to load data: {e}")
            raise

    def get_parameters(self, config):
        return self.model.get_weights()

    def train_step(self, parameters):
        self.model.set_weights(parameters)
        self.model.compile(optimizer=self.optimizer, loss=self.loss_fn, metrics=['accuracy', sensitivity, specificity])
        history = self.model.fit(self.train_dataset, epochs=3, verbose=1, callbacks=[self.es, self.lrr], validation_data=self.val_dataset)
        return self.model.get_weights(), self.train_samples, history

    def evaluate(self, parameters, config):
        self.model.set_weights(parameters)
        self.model.compile(optimizer=self.optimizer, loss=self.loss_fn, metrics=['accuracy', sensitivity, specificity])
        try:
            results = self.model.evaluate(self.val_dataset, verbose=1)
            loss, accuracy, sens, spec = results
            return loss, self.val_samples, {"accuracy": accuracy, "sensitivity": sens, "specificity": spec}
        except Exception as e:
            logging.error(f"Evaluate failed: {e}")
            raise

    def fit(self, parameters, config):
        try:
            weights, num_examples, history = self.train_step(parameters)
            metrics = {
                "loss": float(history.history["loss"][-1]),
                "val_loss": float(history.history["val_loss"][-1]),
                "accuracy": float(history.history["accuracy"][-1]),
                "val_accuracy": float(history.history["val_accuracy"][-1]),
                "sensitivity": float(history.history["sensitivity"][-1]),
                "specificity": float(history.history["specificity"][-1]),
            }
            return weights, num_examples, metrics
        except Exception as e:
            logging.error(f"Fit failed: {e}")
            raise

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_path", type=str, required=True, help="Path to dataset folder")
    args = parser.parse_args()

    fl.client.start_numpy_client(
        server_address="host.docker.internal:8081",
        client=FlowerClient(dataset_path=args.dataset_path)
    )
