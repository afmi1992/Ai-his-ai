from datetime import datetime
from extensions import db


class RadiologyReport(db.Model):
    __tablename__ = "radiology_reports"

    id = db.Column(db.Integer, primary_key=True)

    radiology_order_id = db.Column(
        db.Integer,
        db.ForeignKey("radiology_orders.id"),
        nullable=False
    )

    findings = db.Column(db.Text, nullable=False)
    impression = db.Column(db.Text, nullable=False)

    report_status = db.Column(db.String(50), default="Final")

    reported_by = db.Column(db.String(150), nullable=True)
    reported_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_deleted = db.Column(db.Boolean, default=False)

    radiology_order = db.relationship(
        "RadiologyOrder",
        backref="reports"
    )

    def __repr__(self):
        return f"<RadiologyReport {self.id} - {self.report_status}>"