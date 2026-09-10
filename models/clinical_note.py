from datetime import datetime
from extensions import db


class ClinicalNote(db.Model):
    __tablename__ = "clinical_notes"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        nullable=False
    )

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.id"),
        nullable=True
    )

    note_type = db.Column(
        db.String(50),
        default="Progress Note"
    )

    chief_complaint = db.Column(
        db.Text,
        nullable=True
    )

    history_of_present_illness = db.Column(
        db.Text,
        nullable=True
    )

    assessment = db.Column(
        db.Text,
        nullable=True
    )

    plan = db.Column(
        db.Text,
        nullable=True
    )

    diagnosis_text = db.Column(
        db.String(255),
        nullable=True
    )

    ai_summary = db.Column(
        db.Text,
        nullable=True
    )

    ai_risk_score = db.Column(
        db.Float,
        nullable=True
    )

    ai_recommendation = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    is_deleted = db.Column(
        db.Boolean,
        default=False
    )

    patient = db.relationship(
        "Patient",
        backref="clinical_notes"
    )

    doctor = db.relationship(
        "Doctor",
        backref="clinical_notes"
    )

    def __repr__(self):
        return f"<ClinicalNote {self.id} - Patient {self.patient_id}>"