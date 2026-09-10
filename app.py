from flask import Flask, redirect, url_for
from extensions import db, login_manager, migrate


def create_app():

    app = Flask(__name__)
    app.config.from_object("config.Config")

    # -----------------------------------------------------
    # Initialize Flask Extensions
    # -----------------------------------------------------

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "login"

    migrate.init_app(app, db)

    # -----------------------------------------------------
    # Application Context
    # -----------------------------------------------------

    with app.app_context():

        # -------------------------------------------------
        # Import Application Routes
        # -------------------------------------------------

        from routes.users import register_user_routes
        from routes.dental import register_dental_routes
        from routes.patients import register_patient_routes
        from routes.appointments import register_appointment_routes
        from routes.doctors import register_doctor_routes
        from routes.laboratory import register_laboratory_routes
        from routes.radiology import register_radiology_routes
        from routes.pharmacy import register_pharmacy_routes
        from routes.emr import register_emr_routes
        from routes.problems import register_problem_routes

        # -------------------------------------------------
        # Import Clinical AI Routes
        # -------------------------------------------------

        from routes.dental_ai import register_dental_ai_routes
        from routes.caries_ai import register_caries_ai_routes  # Dedicated Age-Adaptive Caries AI
        from routes.fracture_ai import register_fracture_ai_routes
        from routes.skin_ai import register_skin_ai_routes
        from routes.clinical_ai import register_clinical_ai_routes
        from routes.lab_ai import register_lab_ai_routes  # <--- NEW: Lab AI Routes

        # -------------------------------------------------
        # Import Database Models
        # -------------------------------------------------

        import models
        from models.user import User, Role
        from models.medication import Medication
        from models.lab_test import LabTest  # <--- Imported LabTest for seeding

        # -------------------------------------------------
        # Auto-Seed Database, Roles & Default Admin
        # -------------------------------------------------

        def auto_seed_system():
            try:
                db.create_all()

                # 1. Ensure the 'Admin' role exists
                admin_role = Role.query.filter_by(name="Admin").first()
                if not admin_role:
                    admin_role = Role(name="Admin", description="Full system administrator")
                    db.session.add(admin_role)
                    db.session.commit()

                # 2. Ensure default admin user exists
                admin_user = User.query.filter_by(email="admin@hospital.com").first()
                if not admin_user:
                    admin_user = User(
                        full_name="System Administrator",
                        email="admin@hospital.com",
                        role_id=admin_role.id,
                        is_active_user=True
                    )
                    admin_user.set_password("admin123")
                    db.session.add(admin_user)
                    db.session.commit()
                    print("[iHIS Setup] Default admin created: admin@hospital.com / admin123")

            except Exception as e:
                db.session.rollback()
                print(f"[iHIS Setup Error] Admin initialization failed: {e}")

        auto_seed_system()

        # -------------------------------------------------
        # Auto-Seed Laboratory Tests
        # -------------------------------------------------

        def auto_seed_lab_tests():
            common_tests = [
                {"test_code": "CBC01", "test_name": "Complete Blood Count (CBC)", "category": "Hematology", "sample_type": "Whole Blood", "unit": "Various", "reference_range": "Standard"},
                {"test_code": "CREAT01", "test_name": "Serum Creatinine", "category": "Chemistry", "sample_type": "Serum", "unit": "mg/dL", "reference_range": "0.7 - 1.3"},
                {"test_code": "BUN01", "test_name": "Blood Urea Nitrogen (BUN)", "category": "Chemistry", "sample_type": "Serum", "unit": "mg/dL", "reference_range": "7 - 20"},
                {"test_code": "VITD01", "test_name": "25-Hydroxy Vitamin D", "category": "Chemistry", "sample_type": "Serum", "unit": "ng/mL", "reference_range": "30 - 100"},
                {"test_code": "FBG01", "test_name": "Fasting Blood Glucose", "category": "Chemistry", "sample_type": "Serum", "unit": "mg/dL", "reference_range": "70 - 99"},
                {"test_code": "ALT01", "test_name": "Alanine Aminotransferase (ALT)", "category": "Chemistry", "sample_type": "Serum", "unit": "U/L", "reference_range": "7 - 55"},
                {"test_code": "AST01", "test_name": "Aspartate Aminotransferase (AST)", "category": "Chemistry", "sample_type": "Serum", "unit": "U/L", "reference_range": "8 - 48"}
            ]
            try:
                for item in common_tests:
                    exists = LabTest.query.filter_by(test_code=item["test_code"]).first()
                    if not exists:
                        db.session.add(LabTest(**item))
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"[iHIS Setup Error] Lab tests initialization failed: {e}")

        auto_seed_lab_tests()

        # -------------------------------------------------
        # Auto-Seed Egyptian Drug Index
        # -------------------------------------------------

        def auto_seed_egyptian_drugs():
            egyptian_drugs = [
                {"trade": "Cataflam", "generic": "Diclofenac Potassium", "strength": "50 mg", "form": "Tablet"},
                {"trade": "Voltaren", "generic": "Diclofenac Sodium", "strength": "75 mg/3ml", "form": "Ampoule"},
                {"trade": "Brufen", "generic": "Ibuprofen", "strength": "400 mg", "form": "Tablet"},
                {"trade": "Brufen", "generic": "Ibuprofen", "strength": "600 mg", "form": "Tablet"},
                {"trade": "Panadol Extra", "generic": "Paracetamol / Caffeine", "strength": "500 mg / 65 mg", "form": "Tablet"},
                {"trade": "Panadol Advance", "generic": "Paracetamol", "strength": "500 mg", "form": "Tablet"},
                {"trade": "Paramol", "generic": "Paracetamol", "strength": "500 mg", "form": "Tablet"},
                {"trade": "Ketofan", "generic": "Ketoprofen", "strength": "50 mg", "form": "Capsule"},
                {"trade": "Antinal", "generic": "Nifuroxazide", "strength": "200 mg", "form": "Capsule"},
                {"trade": "Augmentin", "generic": "Amoxicillin / Clavulanic Acid", "strength": "1 g", "form": "Tablet"},
                {"trade": "Augmentin", "generic": "Amoxicillin / Clavulanic Acid", "strength": "625 mg", "form": "Tablet"},
                {"trade": "Hibiotic", "generic": "Amoxicillin / Clavulanic Acid", "strength": "1 g", "form": "Tablet"},
                {"trade": "Curam", "generic": "Amoxicillin / Clavulanic Acid", "strength": "1 g", "form": "Tablet"},
                {"trade": "Amoxil", "generic": "Amoxicillin", "strength": "500 mg", "form": "Capsule"},
                {"trade": "Zithrokan", "generic": "Azithromycin", "strength": "500 mg", "form": "Capsule"},
                {"trade": "Ciprobay", "generic": "Ciprofloxacin", "strength": "500 mg", "form": "Tablet"},
                {"trade": "Tavanic", "generic": "Levofloxacin", "strength": "500 mg", "form": "Tablet"},
                {"trade": "Claforan", "generic": "Cefotaxime", "strength": "1 g", "form": "Vial"},
                {"trade": "Ceftriaxone", "generic": "Ceftriaxone", "strength": "1 g", "form": "Vial"},
                {"trade": "Flagyl", "generic": "Metronidazole", "strength": "500 mg", "form": "Tablet"},
                {"trade": "Bactrim", "generic": "Sulfamethoxazole / Trimethoprim", "strength": "400/80 mg", "form": "Tablet"},
                {"trade": "Sutrim", "generic": "Sulfamethoxazole / Trimethoprim", "strength": "800/160 mg", "form": "Tablet"},
                {"trade": "Concor", "generic": "Bisoprolol", "strength": "5 mg", "form": "Tablet"},
                {"trade": "Concor", "generic": "Bisoprolol", "strength": "2.5 mg", "form": "Tablet"},
                {"trade": "Capoten", "generic": "Captopril", "strength": "25 mg", "form": "Tablet"},
                {"trade": "Norvasc", "generic": "Amlodipine", "strength": "5 mg", "form": "Tablet"},
                {"trade": "Exforge", "generic": "Amlodipine / Valsartan", "strength": "5/160 mg", "form": "Tablet"},
                {"trade": "Natrilix SR", "generic": "Indapamide", "strength": "1.5 mg", "form": "Tablet"},
                {"trade": "Aldactone", "generic": "Spironolactone", "strength": "25 mg", "form": "Tablet"},
                {"trade": "Lasix", "generic": "Furosemide", "strength": "40 mg", "form": "Tablet"},
                {"trade": "Ator", "generic": "Atorvastatin", "strength": "20 mg", "form": "Tablet"},
                {"trade": "Lipitor", "generic": "Atorvastatin", "strength": "40 mg", "form": "Tablet"},
                {"trade": "Crestor", "generic": "Rosuvastatin", "strength": "10 mg", "form": "Tablet"},
                {"trade": "Plavix", "generic": "Clopidogrel", "strength": "75 mg", "form": "Tablet"},
                {"trade": "Aspocid", "generic": "Acetylsalicylic Acid", "strength": "75 mg", "form": "Chewable Tablet"},
                {"trade": "Cidophage", "generic": "Metformin", "strength": "500 mg", "form": "Tablet"},
                {"trade": "Cidophage Retard", "generic": "Metformin", "strength": "850 mg", "form": "Tablet"},
                {"trade": "Glucophage", "generic": "Metformin", "strength": "1000 mg", "form": "Tablet"},
                {"trade": "Amaryl", "generic": "Glimepiride", "strength": "2 mg", "form": "Tablet"},
                {"trade": "Amaryl", "generic": "Glimepiride", "strength": "3 mg", "form": "Tablet"},
                {"trade": "Galvus Met", "generic": "Vildagliptin / Metformin", "strength": "50/1000 mg", "form": "Tablet"},
                {"trade": "Jardiance", "generic": "Empagliflozin", "strength": "10 mg", "form": "Tablet"},
                {"trade": "Eltroxin", "generic": "Levothyroxine", "strength": "50 mcg", "form": "Tablet"},
                {"trade": "Controloc", "generic": "Pantoprazole", "strength": "40 mg", "form": "Tablet"},
                {"trade": "Nexium", "generic": "Esomeprazole", "strength": "40 mg", "form": "Tablet"},
                {"trade": "Gastrazole", "generic": "Omeprazole", "strength": "20 mg", "form": "Capsule"},
                {"trade": "Motilium", "generic": "Domperidone", "strength": "10 mg", "form": "Tablet"},
                {"trade": "Spasmo-Digestin", "generic": "Digestive Enzymes / Antispasmodic", "strength": "Standard", "form": "Tablet"},
                {"trade": "Duspatalin Retard", "generic": "Mebeverine", "strength": "200 mg", "form": "Capsule"},
                {"trade": "Zyrtec", "generic": "Cetirizine", "strength": "10 mg", "form": "Tablet"},
                {"trade": "Claritine", "generic": "Loratadine", "strength": "10 mg", "form": "Tablet"},
                {"trade": "Telfast", "generic": "Fexofenadine", "strength": "180 mg", "form": "Tablet"},
                {"trade": "Ventolin", "generic": "Salbutamol", "strength": "100 mcg", "form": "Inhaler"}
            ]

            try:
                for item in egyptian_drugs:
                    display_name = f"{item['trade']} ({item['generic']})"
                    exists = Medication.query.filter(
                        (Medication.medication_name == display_name) | 
                        (Medication.medication_name.like(f"{item['trade']}%"))
                    ).first()

                    if not exists:
                        db.session.add(Medication(
                            medication_name=display_name,
                            strength=f"{item['strength']} - {item['form']}",
                            is_active=True,
                            is_deleted=False
                        ))
                db.session.commit()
            except Exception as e:
                db.session.rollback()

        auto_seed_egyptian_drugs()

        # -------------------------------------------------
        # Authentication Routes
        # -------------------------------------------------

        from auth.routes import register_auth_routes

        # -------------------------------------------------
        # Register Authentication
        # -------------------------------------------------

        register_auth_routes(app)

        # -------------------------------------------------
        # Register Core iHIS Routes
        # -------------------------------------------------

        register_user_routes(app)
        register_patient_routes(app)
        register_appointment_routes(app)
        register_doctor_routes(app)

        register_laboratory_routes(app)
        register_radiology_routes(app)
        register_pharmacy_routes(app)
        register_dental_routes(app)

        register_emr_routes(app)
        register_problem_routes(app)

        # -------------------------------------------------
        # Register Clinical AI Services
        # -------------------------------------------------

        register_dental_ai_routes(app)
        register_caries_ai_routes(app)  # <--- Added dedicated Caries AI
        register_fracture_ai_routes(app)
        register_skin_ai_routes(app)
        register_lab_ai_routes(app)     # <--- NEW: Lab AI Registration

        # -------------------------------------------------
        # Register Clinical AI Command Center
        # -------------------------------------------------

        register_clinical_ai_routes(app)

        # -------------------------------------------------
        # Flask-Login User Loader
        # -------------------------------------------------

        @login_manager.user_loader
        def load_user(user_id):
            return db.session.get(
                User,
                int(user_id)
            )

    # -----------------------------------------------------
    # Home Route
    # -----------------------------------------------------

    @app.route("/")
    def home():
        return redirect(url_for("login"))

    return app


# ---------------------------------------------------------
# Create Application
# ---------------------------------------------------------

app = create_app()


# ---------------------------------------------------------
# Development Server
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)