from datetime import datetime
from extensions import db


class Appointment(db.Model):
    __tablename__ = "appointments"

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

    appointment_date = db.Column(
        db.Date,
        nullable=False
    )

    appointment_time = db.Column(
        db.Time,
        nullable=False
    )

    appointment_type = db.Column(
        db.String(50),
        default="In-Person"
    )

    status = db.Column(
        db.String(50),
        default="Scheduled"
    )

    reason = db.Column(
        db.String(255),
        nullable=True
    )

    notes = db.Column(
        db.Text,
        nullable=True
    )

    telemedicine_link = db.Column(
        db.String(255),
        nullable=True
    )

    is_telemedicine = db.Column(
        db.Boolean,
        default=False
    )

    is_deleted = db.Column(
        db.Boolean,
        default=False
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
        backref="appointments"
    )

    doctor = db.relationship(
        "Doctor",
        backref="appointments"
    )

    def __repr__(self):
        return f"<Appointment {self.id} - {self.status}>"