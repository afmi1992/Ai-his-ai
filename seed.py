from app import create_app
from extensions import db
from models.user import User, Role, Permission
from models.patient import Patient

app = create_app()

roles_data = [
    "super_admin",
    "admin",
    "doctor",
    "patient",
    "laboratory",
    "radiology",
    "pharmacist",
    "nurse",
    "receptionist",
    "dentist",
    "physical_therapist"
]

permissions_data = [
    "manage_users",
    "manage_roles",
    "view_dashboard",
    "manage_patients",
    "manage_emr",
    "manage_appointments",
    "manage_lab_orders",
    "manage_radiology_orders",
    "manage_prescriptions",
    "manage_inventory",
    "view_reports",
    "manage_system_settings"
]


def seed_core_data():
    for permission_name in permissions_data:
        if not Permission.query.filter_by(name=permission_name).first():
            db.session.add(Permission(name=permission_name))

    db.session.commit()

    all_permissions = Permission.query.all()

    for role_name in roles_data:
        role = Role.query.filter_by(name=role_name).first()

        if not role:
            role = Role(name=role_name)
            db.session.add(role)

        if role_name == "super_admin":
            role.permissions = all_permissions
        else:
            role.permissions = [
                p for p in all_permissions
                if p.name in ["view_dashboard"]
            ]

    db.session.commit()

    super_admin_role = Role.query.filter_by(name="super_admin").first()
    admin = User.query.filter_by(email="admin@ihis.com").first()

    if not admin:
        admin = User(
            full_name="System Super Admin",
            email="admin@ihis.com",
            role=super_admin_role,
            is_active_user=True
        )
        admin.set_password("Admin@12345")
        db.session.add(admin)
    else:
        admin.role = super_admin_role
        admin.is_active_user = True

    db.session.commit()


def seed_patients():
    if Patient.query.first():
        return

    patients = [
        Patient(
            mrn="MRN001",
            full_name="Ahmed Ali",
            gender="Male",
            phone="01000000001",
            blood_group="A+"
        ),
        Patient(
            mrn="MRN002",
            full_name="Sara Mohamed",
            gender="Female",
            phone="01000000002",
            blood_group="O+"
        ),
        Patient(
            mrn="MRN003",
            full_name="Omar Hassan",
            gender="Male",
            phone="01000000003",
            blood_group="B+"
        )
    ]

    db.session.add_all(patients)
    db.session.commit()


def seed_lab_tests():
    from models.lab_test import LabTest

    lab_tests = [
        LabTest(
            test_code="CBC",
            test_name="Complete Blood Count",
            category="Hematology",
            sample_type="Blood",
            unit="",
            reference_range=""
        ),
        LabTest(
            test_code="HBA1C",
            test_name="Hemoglobin A1c",
            category="Diabetes",
            sample_type="Blood",
            unit="%",
            reference_range="4.0 - 5.6"
        ),
        LabTest(
            test_code="CREAT",
            test_name="Creatinine",
            category="Kidney Function",
            sample_type="Blood",
            unit="mg/dL",
            reference_range="0.7 - 1.3"
        ),
        LabTest(
            test_code="ALT",
            test_name="Alanine Aminotransferase",
            category="Liver Function",
            sample_type="Blood",
            unit="U/L",
            reference_range="7 - 56"
        ),
    ]

    for test in lab_tests:
        if not LabTest.query.filter_by(test_code=test.test_code).first():
            db.session.add(test)

    db.session.commit()


def seed_radiology_tests():
    from models.radiology_test import RadiologyTest

    radiology_tests = [
        RadiologyTest(
            test_code="XR-CHEST",
            test_name="Chest X-Ray",
            modality="X-Ray",
            body_part="Chest",
            description="Standard chest radiography"
        ),
        RadiologyTest(
            test_code="CT-BRAIN",
            test_name="CT Brain",
            modality="CT",
            body_part="Brain",
            description="Computed tomography of the brain"
        ),
        RadiologyTest(
            test_code="MRI-SPINE",
            test_name="MRI Spine",
            modality="MRI",
            body_part="Spine",
            description="Magnetic resonance imaging of the spine"
        ),
        RadiologyTest(
            test_code="US-ABDOMEN",
            test_name="Abdominal Ultrasound",
            modality="Ultrasound",
            body_part="Abdomen",
            description="Ultrasound examination of the abdomen"
        ),
    ]

    for test in radiology_tests:
        if not RadiologyTest.query.filter_by(test_code=test.test_code).first():
            db.session.add(test)

    db.session.commit()


def seed_medications():
    from models.medication import Medication

    medications = [
        Medication(
            medication_code="PARA-500",
            medication_name="Paracetamol",
            dosage_form="Tablet",
            strength="500 mg",
            category="Analgesic"
        ),
        Medication(
            medication_code="AMOX-500",
            medication_name="Amoxicillin",
            dosage_form="Capsule",
            strength="500 mg",
            category="Antibiotic"
        ),
        Medication(
            medication_code="MET-500",
            medication_name="Metformin",
            dosage_form="Tablet",
            strength="500 mg",
            category="Antidiabetic"
        ),
        Medication(
            medication_code="ATOR-20",
            medication_name="Atorvastatin",
            dosage_form="Tablet",
            strength="20 mg",
            category="Lipid Lowering"
        ),
    ]

    for medication in medications:
        if not Medication.query.filter_by(
            medication_code=medication.medication_code
        ).first():
            db.session.add(medication)

    db.session.commit()


with app.app_context():
    seed_core_data()
    seed_patients()
    seed_lab_tests()
    seed_radiology_tests()
    seed_medications()

    print("Seed data created successfully.")