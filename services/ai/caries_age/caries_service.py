import os
from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ADULT_MODEL_PATH = os.path.join(BASE_DIR, "adult_caries_best.pt")
CHILD_MODEL_PATH = os.path.join(BASE_DIR, "children_caries_best.pt")
DEFAULT_MODEL_PATH = os.path.join(BASE_DIR, "best.pt")

# Lazy-load models on demand
models_dict = {}

def get_caries_model(category):
    if category not in models_dict:
        if category == "child":
            models_dict[category] = YOLO(CHILD_MODEL_PATH)
        elif category == "adult":
            models_dict[category] = YOLO(ADULT_MODEL_PATH)
        else:
            models_dict[category] = YOLO(DEFAULT_MODEL_PATH)
    return models_dict[category]

def run_age_adaptive_caries(image_path, age=None):
    if age is not None:
        try:
            category = "child" if int(age) < 12 else "adult"
        except (ValueError, TypeError):
            category = "general"
    else:
        category = "general"

    model = get_caries_model(category)
    results = model.predict(source=image_path, conf=0.25, save=False)
    return results, category