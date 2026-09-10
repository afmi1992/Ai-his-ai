# ---------------------------------------------------------
# iHIS Clinical AI Model Registry
# ---------------------------------------------------------
#
# Central registry for AI services integrated into iHIS.
#
# This registry provides a unified description of each
# deployed AI model and will later support:
#
# - Clinical AI Command Center
# - Patient-linked AI analyses
# - Model version tracking
# - Human review workflows
# - Audit trails
# - Future AI model expansion
#
# ---------------------------------------------------------


AI_MODEL_REGISTRY = {

    # -----------------------------------------------------
    # Dental AI
    # -----------------------------------------------------

    "dental": {

        "id": "dental",

        "name": "Dental AI",

        "specialty": "Dentistry",

        "task": "Dental Image Segmentation",

        "task_type": "Segmentation",

        "architecture": "U-Net",

        "framework": "TensorFlow / Keras",

        "model_version": "dental_ai_v2",

        "status": "Ready",

        "route": "dental_ai",

        "description":
            "AI-assisted dental image segmentation "
            "for clinical decision-support workflows.",

        "clinical_role":
            "Decision Support"
    },


    # -----------------------------------------------------
    # Age-Adaptive Dental Caries AI (New Multi-Model)
    # -----------------------------------------------------

    "caries_ai": {

        "id": "caries_ai",

        "name": "Age-Adaptive Caries AI",

        "specialty": "Dentistry / Pedodontics",

        "task": "Pediatric & Adult Caries Detection",

        "task_type": "Object Detection",

        "architecture": "YOLO Multi-Model Ensemble",

        "framework": "Ultralytics / PyTorch",

        "model_version": "v1.0 (Dual-Engine)",

        "status": "Ready",

        "route": "caries_ai_dashboard",

        "description":
            "Dual-engine dental caries detection dynamically switching "
            "between pediatric and adult YOLO models based on patient age.",

        "clinical_role":
            "Decision Support"
    },


    # -----------------------------------------------------
    # Fracture AI
    # -----------------------------------------------------

    "fracture": {

        "id": "fracture",

        "name": "Fracture AI",

        "specialty": "Radiology / Orthopedics",

        "task": "X-Ray Object Detection",

        "task_type": "Object Detection",

        "architecture": "YOLO",

        "framework": "Ultralytics / PyTorch",

        "model_version": "best.pt",

        "status": "Ready",

        "route": "fracture_ai",

        "description":
            "AI-assisted X-ray object detection "
            "for musculoskeletal imaging workflows.",

        "clinical_role":
            "Decision Support"
    },


    # -----------------------------------------------------
    # Skin AI
    # -----------------------------------------------------

    "skin": {

        "id": "skin",

        "name": "Skin AI",

        "specialty": "Dermatology",

        "task": "Melanoma vs Nevus Classification",

        "task_type": "Classification",

        "architecture": "EfficientNet-B0",

        "framework": "PyTorch / Torchvision",

        "model_version": "HAM10000 Binary",

        "status": "Ready",

        "route": "skin_ai",

        "description": (
            "AI-assisted dermoscopic skin lesion "
            "classification for melanoma versus "
            "nevus decision-support workflows."
        ),

        "clinical_role": "Decision Support"
    },


    # -----------------------------------------------------
    # Pharmacy Clinical Decision Support (CDS) AI
    # -----------------------------------------------------

    "pharmacy": {

        "id": "pharmacy",

        "name": "Pharmacy CDS AI",

        "specialty": "Pharmacotherapy & Drug Safety",

        "task": "Drug-Disease & Allergy Safety Interception",

        "task_type": "Generative Clinical CDS",

        "architecture": "Gemini 1.5-Flash",

        "framework": "Google GenAI / openFDA",

        "model_version": "v1.0-Flash",

        "status": "Ready",

        "route": "pharmacy_dashboard",

        "description": (
            "AI-assisted clinical decision support that intercepts "
            "severe drug-disease contraindications, allergy conflicts, "
            "and enforces physician override rationale auditing."
        ),

        "clinical_role": "Safety Decision Support"
    }
}


# ---------------------------------------------------------
# Registry Helpers
# ---------------------------------------------------------

def get_ai_models():
    """
    Return all registered Clinical AI models.
    """

    return AI_MODEL_REGISTRY


def get_ai_model(model_id):
    """
    Return one registered AI model by its ID.
    """

    return AI_MODEL_REGISTRY.get(
        model_id
    )


def get_ready_ai_models():
    """
    Return only AI models currently marked as Ready.
    """

    return {
        model_id: model
        for model_id, model
        in AI_MODEL_REGISTRY.items()
        if model.get("status") == "Ready"
    }


def get_ai_model_count():
    """
    Return the total number of registered AI models.
    """

    return len(
        AI_MODEL_REGISTRY
    )


def get_ready_ai_model_count():
    """
    Return the number of AI models currently Ready.
    """

    return len(
        get_ready_ai_models()
    )