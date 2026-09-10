from datetime import datetime
from extensions import db


class Dispensing(db.Model):
    __tablename__ = "dispensings"

    id = db.Column(db.Integer, primary_key=True)

    prescription_id = db.Column(
        db.Integer,
        db.ForeignKey("prescriptions.id"),
        nullable=False
    )

    quantity_dispensed = db.Column(db.Integer, nullable=False)
    dispensed_by = db.Column(db.String(150), nullable=True)

    dispensing_notes = db.Column(db.Text, nullable=True)

    dispensed_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_deleted = db.Column(db.Boolean, default=False)

    prescription = db.relationship("Prescription", backref="dispensings")

    def __repr__(self):
        return f"<Dispensing {self.id}>"