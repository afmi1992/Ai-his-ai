from datetime import datetime
from extensions import db


class LabTest(db.Model):
    __tablename__ = "lab_tests"

    id = db.Column(db.Integer, primary_key=True)

    test_code = db.Column(db.String(50), unique=True, nullable=False)
    test_name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=True)

    sample_type = db.Column(db.String(100), nullable=True)
    unit = db.Column(db.String(50), nullable=True)
    reference_range = db.Column(db.String(100), nullable=True)

    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<LabTest {self.test_code} - {self.test_name}>"