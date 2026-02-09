from datetime import datetime
from backend.common.db import db


class Reimbursement(db.Model):
    __tablename__ = "reimbursements"

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False)
    
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    receipt_url = db.Column(db.String(500), nullable=False)  # Proof of payment
    
    status = db.Column(db.String(20), default="PENDING")  # PENDING, APPROVED, REJECTED
    admin_notes = db.Column(db.String(500), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    member = db.relationship("User", backref="reimbursements")
    appointment = db.relationship("Appointment", backref="reimbursement")
