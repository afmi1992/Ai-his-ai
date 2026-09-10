from datetime import datetime
from extensions import db


class RadiologyOrder(db.Model):
    __tablename__ = "radiology_orders"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=True)
    radiology_test_id = db.Column(db.Integer, db.ForeignKey("radiology_tests.id"), nullable=False)

    status = db.Column(db.String(50), default="Ordered")
    priority = db.Column(db.String(50), default="Routine")

    clinical_indication = db.Column(db.Text, nullable=True)

    ordered_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_deleted = db.Column(db.Boolean, default=False)

    patient = db.relationship("Patient", backref="radiology_orders")
    doctor = db.relationship("Doctor", backref="radiology_orders")
    radiology_test = db.relationship("RadiologyTest", backref="radiology_orders")

    def __repr__(self):
        return f"<RadiologyOrder {self.id} - {self.status}>"