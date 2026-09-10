from datetime import datetime
from extensions import db


class DentalRecord(db.Model):
    __tablename__ = "dental_records"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        nullable=False
    )

    # FDI tooth number
    tooth_number = db.Column(
        db.String(5),
        nullable=False
    )

    # Permanent or Primary
    dentition = db.Column(
        db.String(20),
        nullable=False,
        default="Permanent"
    )

    # Diagnosis code:
    # O = Healthy / Sound
    # M = Missing due to caries
    # E = Missing due to eruption
    # D = Decayed
    # F = Filled
    # C = Crown
    # I = Implant
    diagnosis_code = db.Column(
        db.String(5),
        nullable=True
    )

    notes = db.Column(
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

    patient = db.relationship(
        "Patient",
        backref="dental_records"
    )

    def __repr__(self):
        return (
            f"<DentalRecord "
            f"Patient={self.patient_id} "
            f"Tooth={self.tooth_number} "
            f"Diagnosis={self.diagnosis_code}>"
        )
