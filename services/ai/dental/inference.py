try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    tf = None
    TENSORFLOW_AVAILABLE = False
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image


# ---------------------------------------------------------
# Dental AI Configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "model" / "dental_ai_v2.keras"

IMAGE_SIZE = (256, 256)

SEGMENTATION_THRESHOLD = 0.5


# ---------------------------------------------------------
# Model Loader
# ---------------------------------------------------------

_dental_model = None


def get_dental_model():
    """
    Load the Dental U-Net model once and reuse it.

    Lazy loading prevents TensorFlow from loading during
    the initial Flask application startup unless the
    Dental AI service is actually used.
    """

    global _dental_model

    if _dental_model is None:

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Dental AI model was not found at: {MODEL_PATH}"
            )

        _dental_model = tf.keras.models.load_model(
            MODEL_PATH,
            compile=False
        )

    return _dental_model


# ---------------------------------------------------------
# Image Preprocessing
# ---------------------------------------------------------

def preprocess_dental_image(image_path):
    """
    Prepare a dental image for the U-Net model.

    Expected model input:
        (batch, 256, 256, 1)
    """

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Dental image was not found: {image_path}"
        )

    image = Image.open(image_path)

    # Model expects one channel
    image = image.convert("L")

    # Resize to model input dimensions
    image = image.resize(IMAGE_SIZE)

    image_array = np.asarray(
        image,
        dtype=np.float32
    )

    # Normalize image pixels
    image_array = image_array / 255.0

    # Add channel dimension
    image_array = np.expand_dims(
        image_array,
        axis=-1
    )

    # Add batch dimension
    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    return image_array


# ---------------------------------------------------------
# Dental AI Prediction
# ---------------------------------------------------------

def predict_dental_segmentation(image_path):
    """
    Run dental segmentation inference.

    Returns:
        probability_mask
        binary_mask
        metadata
    """

    model = get_dental_model()

    input_image = preprocess_dental_image(
        image_path
    )

    prediction = model.predict(
        input_image,
        verbose=0
    )

    probability_mask = prediction[0, :, :, 0]

    binary_mask = (
        probability_mask >= SEGMENTATION_THRESHOLD
    ).astype(np.uint8)

    metadata = {
        "model_name": "Dental U-Net",
        "model_version": "dental_ai_v2",
        "model_type": "image_segmentation",
        "input_shape": [256, 256, 1],
        "output_shape": [256, 256, 1],
        "threshold": SEGMENTATION_THRESHOLD,
        "positive_pixel_ratio": float(
            np.mean(binary_mask)
        )
    }

    return {
        "probability_mask": probability_mask,
        "binary_mask": binary_mask,
        "metadata": metadata
    }