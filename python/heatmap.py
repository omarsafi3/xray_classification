import os
import re
import tensorflow as tf
from tensorflow.keras import backend as K
from tensorflow.keras.layers import GlobalAveragePooling2D, Reshape, Dense, multiply
from tf_keras_vis.gradcam import Gradcam
from tf_keras_vis.utils.model_modifiers import ReplaceToLinear
from tf_keras_vis.utils.scores import CategoricalScore
import numpy as np
from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt
from tf_keras_vis.utils.scores import CategoricalScore, Score
import io
from PIL import Image
import requests
import argparse
import json
import base64
# Your custom blocks / metrics here (SEBlock, sensitivity, specificity) ...
class DummyScore(Score):
    def __call__(self, outputs):
        return tf.zeros((outputs.shape[0],))
def SEBlock(se_ratio=16, activation="relu", data_format='channels_last', kernel_initializer="he_normal"):
    def block(input_tensor):
        channel_axis = -1 if data_format == 'channels_last' else 1
        input_channels = K.int_shape(input_tensor)[channel_axis]
        reduced_channels = max(1, input_channels // se_ratio)
        x = GlobalAveragePooling2D(data_format=data_format)(input_tensor)
        x = Reshape((1, 1, input_channels))(x) if data_format == 'channels_last' else Reshape((input_channels, 1, 1))(x)
        x = Dense(reduced_channels, activation=activation, kernel_initializer=kernel_initializer)(x)
        x = Dense(input_channels, activation='sigmoid', kernel_initializer=kernel_initializer)(x)
        x = multiply([input_tensor, x])
        return x
    return block

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

# --------- Load Best Model Function ---------
def load_best_model_from_dir(save_dir, custom_objects):
    if not os.path.exists(save_dir):
        raise FileNotFoundError(f"Save directory '{save_dir}' not found")

    model_files = [f for f in os.listdir(save_dir) if f.endswith(".keras")]
    if not model_files:
        raise FileNotFoundError("No saved `.keras` models found in the directory.")

    def extract_val_loss(filename):
        match = re.search(r"loss_([\d\.]+)", filename)
        if match:
            val_loss_str = match.group(1).rstrip('.')  # <-- strip trailing dot
            return float(val_loss_str)
        return float('inf')

    best_model_file = min(model_files, key=extract_val_loss)
    best_model_path = os.path.join(save_dir, best_model_file)
    print(f"Loading best model: {best_model_file} with val_loss = {extract_val_loss(best_model_file)}")
    return tf.keras.models.load_model(best_model_path, custom_objects=custom_objects)

# --------- Main Execution ---------

save_dir = r"C:\Users\LOQ\Documents\GitHub\xray_classification\python\saved_models"  # update to your path

# Load best model automatically
model = load_best_model_from_dir(save_dir, custom_objects={
    'SEBlock': SEBlock,
    'sensitivity': sensitivity,
    'specificity': specificity
})

# Image preprocessing
parser = argparse.ArgumentParser()
parser.add_argument("--img_path", required=True)
args = parser.parse_args()
img_path = args.img_path
img = image.load_img(img_path, target_size=(224, 224))
img_array = np.expand_dims(image.img_to_array(img) / 255.0, axis=0)

# Prediction and GradCAM setup
preds = model.predict(img_array)
top_class = np.argmax(preds[0])
score = CategoricalScore([top_class])


last_conv_layer_name = None
for layer in reversed(model.layers):
    if isinstance(layer, tf.keras.layers.Conv2D):
        last_conv_layer_name = layer.name
        break

if last_conv_layer_name is None:
    raise ValueError("No Conv2D layer found in the model.")

print("Last Conv2D layer in the model:", last_conv_layer_name)

last_conv_layer = model.get_layer(last_conv_layer_name)

grad_model = tf.keras.Model(inputs=model.input, outputs=[last_conv_layer.output, model.output])

gradcam = Gradcam(grad_model, model_modifier=ReplaceToLinear(), clone=False)
dummy_score = DummyScore()
heatmap = gradcam([dummy_score, score], img_array)[0]


# Class names in order used by the CNN
class_names = ["Covid", "Normal", "Pneumonia-Bacterial", "Pneumonia-Viral"]
top_class_name = class_names[top_class]

print("Top predicted class:", top_class_name)

# Create a combined RGB image (original + heatmap overlay)
fig, ax = plt.subplots()
ax.imshow(img)
ax.imshow(heatmap, cmap='jet', alpha=0.5)
ax.axis('off')

# Save the figure to a bytes buffer
buf = io.BytesIO()
plt.savefig(buf, format='PNG', bbox_inches='tight', pad_inches=0)
buf.seek(0)
image_bytes = buf.getvalue()
buf.close()
import sys
# Send heatmap + prediction to backend
image_base64 = base64.b64encode(image_bytes).decode('utf-8')
print(f"Last Conv2D layer in the model: {last_conv_layer_name}", file=sys.stderr)
print(f"Top predicted class: {top_class_name}", file=sys.stderr)
output = {
    "prediction": top_class_name,
    "heatmap_base64": image_base64
}

print(json.dumps(output))