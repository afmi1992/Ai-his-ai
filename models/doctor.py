from datetime import datetime
from extensions import db


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)

    employee_id = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    full_name = db.Column(
        db.String(200),
        nullable=False
    )

    specialty = db.Column(
        db.String(150),
        nullable=False
    )

    department = db.Column(
        db.String(150),
        nullable=True
    )

    phone = db.Column(
        db.String(50),
        nullable=True
    )

    email = db.Column(
        db.String(150),
        nullable=True
    )

    license_number = db.Column(
        db.String(100),
        nullable=True
    )

    telemedicine_enabled = db.Column(
        db.Boolean,
        default=False
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

    def __repr__(self):
        return f"<Doctor {self.full_name}>"