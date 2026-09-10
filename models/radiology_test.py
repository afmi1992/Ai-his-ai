from datetime import datetime
from extensions import db


class RadiologyTest(db.Model):
    __tablename__ = "radiology_tests"

    id = db.Column(db.Integer, primary_key=True)

    test_code = db.Column(db.String(50), unique=True, nullable=False)
    test_name = db.Column(db.String(150), nullable=False)
    modality = db.Column(db.String(100), nullable=False)

    body_part = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)

    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RadiologyTest {self.test_code} - {self.test_name}>"