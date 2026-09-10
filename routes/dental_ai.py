from pathlib import Path
from uuid import uuid4

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

from services.ai.dental.inference import (
    predict_dental_segmentation
)


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


def register_dental_ai_routes(app):

    # =====================================================
    # Dental AI Workspace
    # =====================================================

    @app.route(
        "/ai/dental",
        methods=["GET", "POST"]
    )
    @login_required
    def dental_ai():

        result = None

        if request.method == "POST":

            # -------------------------------------------------
            # Validate uploaded file
            # -------------------------------------------------

            if "image" not in request.files:

                flash(
                    "Please select a dental image.",
                    "warning"
                )

                return redirect(
                    url_for("dental_ai")
                )

            file = request.files["image"]

            if not file.filename:

                flash(
                    "Please select a dental image.",
                    "warning"
                )

                return redirect(
                    url_for("dental_ai")
                )

            if not allowed_file(file.filename):

                flash(
                    "Supported formats: PNG, JPG and JPEG.",
                    "danger"
                )

                return redirect(
                    url_for("dental_ai")
                )

            # =================================================
            # AI Working Directory
            # =================================================

            ai_directory = (
                Path(current_app.instance_path)
                / "ai"
                / "dental"
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

            # =================================================
            # Unique Analysis ID
            # =================================================

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

                # =================================================
                # Run Dental U-Net
                # =================================================

                prediction = (
                    predict_dental_segmentation(
                        input_path
                    )
                )

                binary_mask = prediction[
                    "binary_mask"
                ]

                metadata = prediction[
                    "metadata"
                ]

                # =================================================
                # Create Segmentation Mask
                # =================================================

                mask_image_array = (
                    binary_mask * 255
                ).astype(np.uint8)

                mask_filename = (
                    f"{analysis_id}_mask.png"
                )

                mask_path = (
                    result_directory
                    / mask_filename
                )

                Image.fromarray(
                    mask_image_array,
                    mode="L"
                ).save(mask_path)

                # =================================================
                # Create Display Version of Original Image
                # =================================================

                original_image = (
                    Image.open(input_path)
                    .convert("RGB")
                )

                original_display = (
                    original_image.resize(
                        (256, 256)
                    )
                )

                original_filename = (
                    f"{analysis_id}_original.png"
                )

                original_display_path = (
                    result_directory
                    / original_filename
                )

                original_display.save(
                    original_display_path
                )

                # =================================================
                # Create AI Overlay
                # =================================================

                original_array = np.array(
                    original_display,
                    dtype=np.uint8
                )

                mask_boolean = (
                    binary_mask > 0
                )

                overlay_array = (
                    original_array.copy()
                )

                # Highlight segmented region
                # Red overlay
                red_layer = np.zeros_like(
                    overlay_array
                )

                red_layer[:, :, 0] = 255

                alpha = 0.45

                overlay_array[
                    mask_boolean
                ] = (
                    (
                        1 - alpha
                    )
                    * overlay_array[
                        mask_boolean
                    ]
                    +
                    alpha
                    * red_layer[
                        mask_boolean
                    ]
                ).astype(np.uint8)

                overlay_filename = (
                    f"{analysis_id}_overlay.png"
                )

                overlay_path = (
                    result_directory
                    / overlay_filename
                )

                Image.fromarray(
                    overlay_array
                ).save(
                    overlay_path
                )

                # =================================================
                # Prepare Result for UI
                # =================================================

                result = {

                    "analysis_id":
                        analysis_id,

                    "uploaded_filename":
                        file.filename,

                    "stored_filename":
                        input_filename,

                    "original_filename":
                        original_filename,

                    "mask_filename":
                        mask_filename,

                    "overlay_filename":
                        overlay_filename,

                    "metadata":
                        metadata
                }

                flash(
                    "Dental AI analysis completed successfully.",
                    "success"
                )

            except Exception as error:

                current_app.logger.exception(
                    "Dental AI inference failed"
                )

                flash(
                    f"Dental AI analysis failed: {error}",
                    "danger"
                )

        return render_template(
            "dental_ai.html",
            result=result
        )

    # =====================================================
    # Serve Dental AI Result Images
    # =====================================================

    @app.route(
        "/ai/dental/results/<filename>"
    )
    @login_required
    def dental_ai_result(filename):

        result_directory = (
            Path(current_app.instance_path)
            / "ai"
            / "dental"
            / "results"
        )

        return send_from_directory(
            result_directory,
            filename
        )