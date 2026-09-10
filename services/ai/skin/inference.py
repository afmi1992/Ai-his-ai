from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms


# ---------------------------------------------------------
# Skin AI Configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    BASE_DIR
    / "model"
    / "efficientnet_b0_ham10000_binary.pth"
)

IMAGE_SIZE = 224

CLASS_NAMES = {
    0: "Nevus",
    1: "Melanoma"
}

MELANOMA_CLASS_INDEX = 1


# ---------------------------------------------------------
# Device Configuration
# ---------------------------------------------------------

DEVICE = torch.device(
    "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)


# ---------------------------------------------------------
# Model Loader
# ---------------------------------------------------------

_skin_model = None


def get_skin_model():
    """
    Load the EfficientNet-B0 skin lesion classifier once
    and reuse it for subsequent predictions.
    """

    global _skin_model

    if _skin_model is not None:
        return _skin_model

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Skin AI model was not found at: {MODEL_PATH}"
        )

    # -----------------------------------------------------
    # Reconstruct EfficientNet-B0 architecture
    # -----------------------------------------------------

    model = models.efficientnet_b0(
        weights=None
    )

    model.classifier[1] = nn.Linear(
        model.classifier[1].in_features,
        2
    )

    # -----------------------------------------------------
    # Load checkpoint
    # -----------------------------------------------------

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
        weights_only=False
    )

    # Support different checkpoint formats
    if isinstance(checkpoint, dict):

        if "model_state_dict" in checkpoint:
            state_dict = checkpoint[
                "model_state_dict"
            ]

        elif "state_dict" in checkpoint:
            state_dict = checkpoint[
                "state_dict"
            ]

        else:
            state_dict = checkpoint

    else:
        raise ValueError(
            "Unsupported Skin AI checkpoint format."
        )

    model.load_state_dict(
        state_dict,
        strict=True
    )

    model.to(DEVICE)

    model.eval()

    _skin_model = model

    return _skin_model


# ---------------------------------------------------------
# Image Preprocessing
# ---------------------------------------------------------

_skin_transform = transforms.Compose(
    [
        transforms.Resize(
            (IMAGE_SIZE, IMAGE_SIZE)
        ),

        transforms.ToTensor(),

        transforms.Normalize(
            mean=[
                0.485,
                0.456,
                0.406
            ],
            std=[
                0.229,
                0.224,
                0.225
            ]
        )
    ]
)


def preprocess_skin_image(image_path):
    """
    Prepare skin lesion image for EfficientNet-B0.

    Expected tensor shape:
        (1, 3, 224, 224)
    """

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Skin image was not found: {image_path}"
        )

    image = Image.open(
        image_path
    ).convert("RGB")

    tensor = _skin_transform(
        image
    )

    tensor = tensor.unsqueeze(0)

    return tensor.to(DEVICE)


# ---------------------------------------------------------
# Skin AI Prediction
# ---------------------------------------------------------

def predict_skin_lesion(image_path):
    """
    Run EfficientNet-B0 inference for binary
    melanoma-versus-nevus classification.
    """

    model = get_skin_model()

    input_tensor = preprocess_skin_image(
        image_path
    )

    with torch.inference_mode():

        logits = model(
            input_tensor
        )

        probabilities = torch.softmax(
            logits,
            dim=1
        )

    probabilities = (
        probabilities
        .detach()
        .cpu()
        .numpy()[0]
    )

    nevus_probability = float(
        probabilities[0]
    )

    melanoma_probability = float(
        probabilities[MELANOMA_CLASS_INDEX]
    )

    predicted_index = int(
        probabilities.argmax()
    )

    predicted_class = CLASS_NAMES[
        predicted_index
    ]

    confidence = float(
        probabilities[
            predicted_index
        ]
    )

    # -----------------------------------------------------
    # Clinical-support interpretation
    # -----------------------------------------------------

    if predicted_index == MELANOMA_CLASS_INDEX:

        interpretation = (
            "The AI model assigned the higher probability "
            "to the melanoma class."
        )

    else:

        interpretation = (
            "The AI model assigned the higher probability "
            "to the nevus class."
        )

    # -----------------------------------------------------
    # Structured AI Result
    # -----------------------------------------------------

    return {

        "prediction": {
            "class_index":
                predicted_index,

            "class_name":
                predicted_class,

            "confidence":
                confidence,

            "nevus_probability":
                nevus_probability,

            "melanoma_probability":
                melanoma_probability
        },

        "metadata": {
            "model_name":
                "EfficientNet-B0",

            "model_version":
                "HAM10000 Binary",

            "model_type":
                "image_classification",

            "task":
                "Melanoma vs Nevus Classification",

            "input_shape":
                [224, 224, 3],

            "classes":
                [
                    "Nevus",
                    "Melanoma"
                ],

            "device":
                str(DEVICE)
        },

        "interpretation":
            interpretation
    }