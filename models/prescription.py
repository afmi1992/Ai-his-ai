from datetime import datetime
from extensions import db


class Prescription(db.Model):
    __tablename__ = "prescriptions"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=True)
    medication_id = db.Column(db.Integer, db.ForeignKey("medications.id"), nullable=False)

    dose = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(100), nullable=False)

    instructions = db.Column(db.Text, nullable=True)

    status = db.Column(db.String(50), default="Prescribed")

    prescribed_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_deleted = db.Column(db.Boolean, default=False)

    patient = db.relationship("Patient", backref="prescriptions")
    doctor = db.relationship("Doctor", backref="prescriptions")
    medication = db.relationship("Medication", backref="prescriptions")

    def __repr__(self):
        return f"<Prescription {self.id} - {self.status}>"