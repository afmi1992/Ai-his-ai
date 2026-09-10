from extensions import db
from datetime import datetime

class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)

    mrn = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    full_name = db.Column(
        db.String(200),
        nullable=False
    )

    date_of_birth = db.Column(
        db.Date
    )

    gender = db.Column(
        db.String(20)
    )

    phone = db.Column(
        db.String(50)
    )

    address = db.Column(
        db.Text
    )

    blood_group = db.Column(
        db.String(10)
    )

    insurance_provider = db.Column(
        db.String(200)
    )

    status = db.Column(
        db.String(50),
        default="Active"
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

    # NEW: Direct relationship to AI Lab Analysis records
    ai_lab_records = db.relationship(
        "AILabRecord", 
        backref="patient", 
        lazy=True, 
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Patient {self.full_name}>"


# NEW: Model for the quick AI paste-and-analyze presentation workflow
class AILabRecord(db.Model):
    __tablename__ = "ai_lab_records"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    
    raw_text = db.Column(db.Text, nullable=False)
    ai_analysis = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AILabRecord {self.id} for Patient {self.patient_id}>"