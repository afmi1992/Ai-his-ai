from flask import (
    render_template
)

from flask_login import (
    login_required
)

from services.ai.registry import (
    get_ai_models,
    get_ai_model_count,
    get_ready_ai_model_count
)


# ---------------------------------------------------------
# Clinical AI Command Center Routes
# ---------------------------------------------------------

def register_clinical_ai_routes(app):

    # -----------------------------------------------------
    # Clinical AI Command Center
    # -----------------------------------------------------

    @app.route("/ai")
    @app.route("/ai/command-center")
    @login_required
    def clinical_ai_command_center():

        # -------------------------------------------------
        # Load AI Model Registry
        # -------------------------------------------------

        models = get_ai_models()

        total_models = (
            get_ai_model_count()
        )

        ready_models = (
            get_ready_ai_model_count()
        )

        # -------------------------------------------------
        # Command Center Statistics
        # -------------------------------------------------

        ai_statistics = {

            "total_models":
                total_models,

            "ready_models":
                ready_models,

            "specialties":
                len(
                    {
                        model[
                            "specialty"
                        ]
                        for model
                        in models.values()
                    }
                ),

            "ai_tasks":
                len(
                    {
                        model[
                            "task_type"
                        ]
                        for model
                        in models.values()
                    }
                )
        }

        # -------------------------------------------------
        # Render Clinical AI Command Center
        # -------------------------------------------------

        return render_template(
            "clinical_ai.html",
            ai_models=models,
            ai_statistics=ai_statistics
        )