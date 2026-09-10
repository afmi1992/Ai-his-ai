from pathlib import Path
from uuid import uuid4

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

from services.ai.fracture.inference import predict_fracture


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


def register_fracture_ai_routes(app):

    # -----------------------------------------------------
    # Fracture AI Workspace
    # -----------------------------------------------------

    @app.route(
        "/ai/fracture",
        methods=["GET", "POST"]
    )
    @login_required
    def fracture_ai():

        result = None

        if request.method == "POST":

            if "image" not in request.files:
                flash(
                    "Please select an X-ray image.",
                    "warning"
                )
                return redirect(
                    url_for("fracture_ai")
                )

            file = request.files["image"]

            if not file.filename:
                flash(
                    "Please select an X-ray image.",
                    "warning"
                )
                return redirect(
                    url_for("fracture_ai")
                )

            if not allowed_file(file.filename):
                flash(
                    "Supported formats: PNG, JPG and JPEG.",
                    "danger"
                )
                return redirect(
                    url_for("fracture_ai")
                )

            # -------------------------------------------------
            # AI Working Directories
            # -------------------------------------------------

            ai_directory = (
                Path(current_app.instance_path)
                / "ai"
                / "fracture"
            )

            input_directory = (
                ai_directory / "input"
            )

            result_directory = (
                ai_directory / "results"
            )

            input_directory.mkdir(
                parents=True,
                exist_ok=True
            )

            result_directory.mkdir(
                parents=True,
                exist_ok=True
            )

            # -------------------------------------------------
            # Unique Analysis ID
            # -------------------------------------------------

            analysis_id = uuid4().hex

            extension = (
                file.filename
                .rsplit(".", 1)[1]
                .lower()
            )

            input_filename = (
                f"{analysis_id}.{extension}"
            )

            input_path = (
                input_directory
                / input_filename
            )

            file.save(input_path)

            try:

                # ---------------------------------------------
                # Run YOLO Fracture AI
                # ---------------------------------------------

                prediction = predict_fracture(
                    input_path
                )

                metadata = prediction[
                    "metadata"
                ]

                detections = prediction[
                    "detections"
                ]

                raw_result = prediction[
                    "raw_result"
                ]

                # ---------------------------------------------
                # Generate Annotated X-Ray
                # ---------------------------------------------

                annotated_image = (
                    raw_result.plot()
                )

                annotated_filename = (
                    f"{analysis_id}_annotated.jpg"
                )

                annotated_path = (
                    result_directory
                    / annotated_filename
                )

                # YOLO plot() returns BGR numpy array.
                # Convert to RGB before saving with PIL.

                from PIL import Image

                annotated_rgb = (
                    annotated_image[:, :, ::-1]
                )

                Image.fromarray(
                    annotated_rgb
                ).save(
                    annotated_path,
                    quality=95
                )

                # ---------------------------------------------
                # Result Object
                # ---------------------------------------------

                result = {
                    "analysis_id":
                        analysis_id,

                    "original_filename":
                        file.filename,

                    "stored_filename":
                        input_filename,

                    "annotated_filename":
                        annotated_filename,

                    "metadata":
                        metadata,

                    "detections":
                        detections
                }

                flash(
                    "Fracture AI analysis completed successfully.",
                    "success"
                )

            except Exception as error:

                current_app.logger.exception(
                    "Fracture AI inference failed"
                )

                flash(
                    f"Fracture AI analysis failed: {error}",
                    "danger"
                )

        return render_template(
            "fracture_ai.html",
            result=result
        )


    # -----------------------------------------------------
    # Serve Generated AI Result Images
    # -----------------------------------------------------

    @app.route(
        "/ai/fracture/results/<filename>"
    )
    @login_required
    def fracture_ai_result_image(filename):

        result_directory = (
            Path(current_app.instance_path)
            / "ai"
            / "fracture"
            / "results"
        )

        return send_from_directory(
            result_directory,
            filename
        )