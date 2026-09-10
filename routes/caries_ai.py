import os
from pathlib import Path
from uuid import uuid4
import cv2
import numpy as np
from PIL import Image

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    send_from_directory
)
from flask_login import login_required

from services.ai.caries_age.caries_service import run_age_adaptive_caries


ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg"
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def register_caries_ai_routes(app):

    # =====================================================
    # Age-Adaptive Caries AI Workspace
    # =====================================================

    @app.route(
        "/ai/caries",
        methods=["GET", "POST"]
    )
    @login_required
    def caries_ai_dashboard():

        result = None

        if request.method == "POST":

            # -------------------------------------------------
            # Validate Uploaded File
            # -------------------------------------------------

            if "image" not in request.files:
                flash("Please select a dental X-ray image.", "warning")
                return redirect(url_for("caries_ai_dashboard"))

            file = request.files["image"]

            if not file.filename:
                flash("Please select a dental X-ray image.", "warning")
                return redirect(url_for("caries_ai_dashboard"))

            if not allowed_file(file.filename):
                flash("Supported formats: PNG, JPG and JPEG.", "danger")
                return redirect(url_for("caries_ai_dashboard"))

            # -------------------------------------------------
            # Mandatory Patient Age Validation
            # -------------------------------------------------

            patient_age = request.form.get("patient_age", "").strip()
            if not patient_age:
                flash("Patient age is mandatory to route between pediatric and adult models.", "warning")
                return redirect(url_for("caries_ai_dashboard"))

            try:
                age_val = int(patient_age)
                if age_val <= 0 or age_val > 120:
                    raise ValueError("Age out of range")
            except ValueError:
                flash("Please enter a valid patient age between 1 and 120.", "warning")
                return redirect(url_for("caries_ai_dashboard"))

            # =================================================
            # AI Working Directory
            # =================================================

            ai_directory = (
                Path(current_app.instance_path)
                / "ai"
                / "caries"
            )

            input_directory = ai_directory / "input"
            result_directory = ai_directory / "results"

            input_directory.mkdir(parents=True, exist_ok=True)
            result_directory.mkdir(parents=True, exist_ok=True)

            # =================================================
            # Unique Analysis ID
            # =================================================

            analysis_id = uuid4().hex

            extension = (
                file.filename
                .rsplit(".", 1)[1]
                .lower()
            )

            input_filename = f"{analysis_id}.{extension}"
            input_path = input_directory / input_filename

            file.save(str(input_path))

            try:
                # =================================================
                # Run Age-Adaptive YOLO Inference
                # =================================================

                yolo_results, used_category = run_age_adaptive_caries(
                    str(input_path),
                    age=age_val
                )

                # =================================================
                # Parse Detections & Render Output Image
                # =================================================

                detections = []
                annotated_filename = f"{analysis_id}_caries_detection.jpg"
                annotated_path = result_directory / annotated_filename

                if yolo_results and len(yolo_results) > 0:
                    first_res = yolo_results[0]
                    
                    # Draw YOLO bounding boxes onto image
                    annotated_bgr = first_res.plot()
                    cv2.imwrite(str(annotated_path), annotated_bgr)

                    # Extract box coordinates and detection labels
                    names = getattr(first_res, "names", {})
                    boxes = getattr(first_res, "boxes", None)

                    if boxes is not None:
                        for box in boxes:
                            cls_id = int(box.cls[0].item())
                            conf = float(box.conf[0].item())
                            label = names.get(cls_id, f"Class {cls_id}")
                            detections.append({
                                "label": label,
                                "confidence": round(conf * 100, 1),
                                "box": [round(coord, 1) for coord in box.xyxy[0].tolist()]
                            })
                else:
                    Image.open(str(input_path)).save(str(annotated_path))

                # =================================================
                # Prepare Result for UI
                # =================================================

                result = {
                    "analysis_id": analysis_id,
                    "uploaded_filename": file.filename,
                    "stored_filename": input_filename,
                    "annotated_filename": annotated_filename,
                    "patient_age": patient_age,
                    "model_used": used_category.capitalize(),
                    "detections_count": len(detections),
                    "detections": detections
                }

                flash(
                    f"Caries analysis completed ({used_category.capitalize()} model).",
                    "success"
                )

            except Exception as error:
                current_app.logger.exception("Age-Adaptive Caries AI failed")
                flash(f"Caries analysis failed: {error}", "danger")

        return render_template(
            "caries_ai.html",
            result=result
        )

    # =====================================================
    # Serve Caries AI Result Images
    # =====================================================

    @app.route(
        "/ai/caries/results/<filename>"
    )
    @login_required
    def caries_ai_result(filename):

        result_directory = (
            Path(current_app.instance_path)
            / "ai"
            / "caries"
            / "results"
        )

        return send_from_directory(
            result_directory,
            filename
        )