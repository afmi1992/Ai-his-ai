from datetime import datetime
from extensions import db


class Medication(db.Model):
    __tablename__ = "medications"

    id = db.Column(db.Integer, primary_key=True)

    medication_code = db.Column(db.String(50), unique=True, nullable=False)
    medication_name = db.Column(db.String(150), nullable=False)

    dosage_form = db.Column(db.String(100), nullable=True)
    strength = db.Column(db.String(100), nullable=True)

    category = db.Column(db.String(100), nullable=True)

    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Medication {self.medication_code} - {self.medication_name}>"