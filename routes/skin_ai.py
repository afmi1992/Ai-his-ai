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

from services.ai.skin.inference import (
    predict_skin_lesion
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg"
}


def allowed_file(filename):

    return (
        "."
        in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ---------------------------------------------------------
# Skin AI Routes
# ---------------------------------------------------------

def register_skin_ai_routes(app):

    # -----------------------------------------------------
    # Skin AI Workspace
    # -----------------------------------------------------

    @app.route(
        "/ai/skin",
        methods=["GET", "POST"]
    )
    @login_required
    def skin_ai():

        result = None

        if request.method == "POST":

            # -------------------------------------------------
            # Validate Uploaded Image
            # -------------------------------------------------

            if "image" not in request.files:

                flash(
                    "Please select a skin lesion image.",
                    "warning"
                )

                return redirect(
                    url_for("skin_ai")
                )

            file = request.files["image"]

            if not file.filename:

                flash(
                    "Please select a skin lesion image.",
                    "warning"
                )

                return redirect(
                    url_for("skin_ai")
                )

            if not allowed_file(file.filename):

                flash(
                    "Supported formats: PNG, JPG and JPEG.",
                    "danger"
                )

                return redirect(
                    url_for("skin_ai")
                )

            # -------------------------------------------------
            # AI Working Directory
            # -------------------------------------------------

            ai_directory = (
                Path(current_app.instance_path)
                / "ai"
                / "skin"
            )

            input_directory = (
                ai_directory
                / "input"
            )

            input_directory.mkdir(
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

            file.save(
                input_path
            )

            # -------------------------------------------------
            # Run EfficientNet-B0 Skin AI
            # -------------------------------------------------

            try:

                prediction_result = (
                    predict_skin_lesion(
                        input_path
                    )
                )

                prediction = (
                    prediction_result[
                        "prediction"
                    ]
                )

                metadata = (
                    prediction_result[
                        "metadata"
                    ]
                )

                # -------------------------------------------------
                # Prepare Metadata for UI
                # -------------------------------------------------

                metadata_for_ui = {

                    "model_name":
                        metadata.get(
                            "model_name",
                            "EfficientNet-B0"
                        ),

                    "architecture":
                        "EfficientNet-B0",

                    "model_version":
                        metadata.get(
                            "model_version",
                            "HAM10000 Binary"
                        ),

                    "model_type":
                        metadata.get(
                            "model_type",
                            "image_classification"
                        ),

                    "task":
                        metadata.get(
                            "task",
                            "Melanoma vs Nevus Classification"
                        ),

                    "device":
                        metadata.get(
                            "device",
                            "Unknown"
                        )
                }

                # -------------------------------------------------
                # Standard Result Object for Skin AI Workspace
                # -------------------------------------------------

                result = {

                    "analysis_id":
                        analysis_id,

                    "original_filename":
                        file.filename,

                    "stored_filename":
                        input_filename,

                    "predicted_class":
                        prediction[
                            "class_name"
                        ],

                    "class_index":
                        prediction[
                            "class_index"
                        ],

                    "confidence":
                        prediction[
                            "confidence"
                        ],

                    "nevus_probability":
                        prediction[
                            "nevus_probability"
                        ],

                    "melanoma_probability":
                        prediction[
                            "melanoma_probability"
                        ],

                    "interpretation":
                        prediction_result[
                            "interpretation"
                        ],

                    "metadata":
                        metadata_for_ui,

                    "image_url":
                        url_for(
                            "skin_ai_input_image",
                            filename=input_filename
                        )
                }

                flash(
                    "Skin AI analysis completed successfully.",
                    "success"
                )

            except Exception as error:

                current_app.logger.exception(
                    "Skin AI inference failed"
                )

                flash(
                    f"Skin AI analysis failed: {error}",
                    "danger"
                )

        # -----------------------------------------------------
        # Render Skin AI Workspace
        # -----------------------------------------------------

        return render_template(
            "skin_ai.html",
            result=result
        )


    # -----------------------------------------------------
    # Securely Serve Uploaded Skin Images
    # -----------------------------------------------------

    @app.route(
        "/ai/skin/input/<filename>"
    )
    @login_required
    def skin_ai_input_image(filename):

        input_directory = (
            Path(current_app.instance_path)
            / "ai"
            / "skin"
            / "input"
        )

        return send_from_directory(
            input_directory,
            filename
        )