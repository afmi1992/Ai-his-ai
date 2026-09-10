from datetime import datetime
from extensions import db


class LabResult(db.Model):
    __tablename__ = "lab_results"

    id = db.Column(db.Integer, primary_key=True)

    lab_order_id = db.Column(db.Integer, db.ForeignKey("lab_orders.id"), nullable=False)

    # Standard discrete lab values
    result_value = db.Column(db.String(100), nullable=False)
    result_unit = db.Column(db.String(50), nullable=True)
    reference_range = db.Column(db.String(100), nullable=True)

    flag = db.Column(db.String(50), default="Normal")
    interpretation = db.Column(db.Text, nullable=True)
    
    # NEW: AI Clinical Decision Support Fields
    raw_text = db.Column(db.Text, nullable=True)      # Stores the pasted CBC/Chemistry text
    ai_analysis = db.Column(db.Text, nullable=True)   # Stores the Gemini alerts/recommendations

    validated_by = db.Column(db.String(150), nullable=True)
    validated_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_deleted = db.Column(db.Boolean, default=False)

    lab_order = db.relationship("LabOrder", backref="results")

    def __repr__(self):
        return f"<LabResult {self.id} - {self.flag}>"