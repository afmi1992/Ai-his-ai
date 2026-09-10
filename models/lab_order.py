from datetime import datetime
from extensions import db


class LabOrder(db.Model):
    __tablename__ = "lab_orders"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=True)
    lab_test_id = db.Column(db.Integer, db.ForeignKey("lab_tests.id"), nullable=False)

    status = db.Column(db.String(50), default="Ordered")

    priority = db.Column(db.String(50), default="Routine")
    clinical_notes = db.Column(db.Text, nullable=True)

    ordered_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_deleted = db.Column(db.Boolean, default=False)

    patient = db.relationship("Patient", backref="lab_orders")
    doctor = db.relationship("Doctor", backref="lab_orders")
    lab_test = db.relationship("LabTest", backref="lab_orders")

    def __repr__(self):
        return f"<LabOrder {self.id} - {self.status}>"