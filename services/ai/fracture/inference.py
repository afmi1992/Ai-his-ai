from pathlib import Path

from ultralytics import YOLO


# ---------------------------------------------------------
# Fracture AI Configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "model" / "best.pt"

CONFIDENCE_THRESHOLD = 0.25

IMAGE_SIZE = 640


# ---------------------------------------------------------
# Model Loader
# ---------------------------------------------------------

_fracture_model = None


def get_fracture_model():
    """
    Load the Fracture YOLO model once and reuse it.

    Lazy loading prevents the model from loading during
    Flask startup unless the Fracture AI service is used.
    """

    global _fracture_model

    if _fracture_model is None:

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Fracture AI model was not found at: {MODEL_PATH}"
            )

        _fracture_model = YOLO(
            str(MODEL_PATH)
        )

    return _fracture_model


# ---------------------------------------------------------
# Fracture AI Prediction
# ---------------------------------------------------------

def predict_fracture(image_path):
    """
    Run YOLO fracture detection.

    Returns:
        detections
        metadata
        raw_result
    """

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Fracture image was not found: {image_path}"
        )

    model = get_fracture_model()

    results = model.predict(
        source=str(image_path),
        conf=CONFIDENCE_THRESHOLD,
        imgsz=IMAGE_SIZE,
        verbose=False
    )

    result = results[0]

    detections = []

    # -----------------------------------------------------
    # Extract YOLO detections
    # -----------------------------------------------------

    if result.boxes is not None:

        for box in result.boxes:

            class_id = int(
                box.cls[0].item()
            )

            confidence = float(
                box.conf[0].item()
            )

            coordinates = (
                box.xyxy[0]
                .cpu()
                .tolist()
            )

            class_name = model.names[
                class_id
            ]

            detection = {
                "class_id": class_id,
                "class_name": class_name,
                "confidence": confidence,
                "bounding_box": {
                    "x1": float(coordinates[0]),
                    "y1": float(coordinates[1]),
                    "x2": float(coordinates[2]),
                    "y2": float(coordinates[3])
                }
            }

            detections.append(
                detection
            )

    # -----------------------------------------------------
    # Clinical Summary
    # -----------------------------------------------------

    fracture_detections = [
        detection
        for detection in detections
        if detection["class_name"].lower()
        == "fractured"
    ]

    fracture_detected = (
        len(fracture_detections) > 0
    )

    highest_confidence = 0.0

    if detections:

        highest_confidence = max(
            detection["confidence"]
            for detection in detections
        )

    fracture_confidence = 0.0

    if fracture_detections:

        fracture_confidence = max(
            detection["confidence"]
            for detection
            in fracture_detections
        )

    # -----------------------------------------------------
    # Metadata
    # -----------------------------------------------------

    metadata = {
        "model_name":
            "Fracture Detection YOLO",

        "model_version":
            "best.pt",

        "model_type":
            "object_detection",

        "confidence_threshold":
            CONFIDENCE_THRESHOLD,

        "image_size":
            IMAGE_SIZE,

        "classes":
            model.names,

        "total_detections":
            len(detections),

        "fracture_detected":
            fracture_detected,

        "fracture_count":
            len(fracture_detections),

        "highest_confidence":
            highest_confidence,

        "fracture_confidence":
            fracture_confidence
    }

    return {
        "detections": detections,
        "metadata": metadata,
        "raw_result": result
    }