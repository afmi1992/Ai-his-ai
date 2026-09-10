from datetime import datetime

from extensions import db


class DentalVisit(db.Model):
    __tablename__ = "dental_visits"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        nullable=False
    )

    # Date of the documented dental visit
    visit_date = db.Column(
        db.Date,
        nullable=False
    )

    # Patient's main complaint
    chief_complaint = db.Column(
        db.Text,
        nullable=True
    )

    # Dental procedure performed during the visit
    procedure = db.Column(
        db.Text,
        nullable=True
    )

    # Procedure that may be needed in the future
    future_procedure_required = db.Column(
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
        backref="dental_visits"
    )

    def __repr__(self):
        return (
            f"<DentalVisit "
            f"Patient={self.patient_id} "
            f"Date={self.visit_date}>"
        )
    