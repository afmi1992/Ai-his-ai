from datetime import datetime

from extensions import db


class Problem(db.Model):

    __tablename__ = "problems"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        nullable=False
    )

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.id"),
        nullable=False
    )

    diagnosis_name = db.Column(
        db.String(200),
        nullable=False
    )

    icd10_code = db.Column(
        db.String(20)
    )

    problem_type = db.Column(
        db.String(50),
        default="Diagnosis"
    )

    clinical_status = db.Column(
        db.String(50),
        default="Active"
    )

    severity = db.Column(
        db.String(50)
    )

    onset_date = db.Column(
        db.Date
    )

    resolved_date = db.Column(
        db.Date
    )

    notes = db.Column(
        db.Text
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
        backref="problems"
    )

    doctor = db.relationship(
        "Doctor",
        backref="problems"
    )