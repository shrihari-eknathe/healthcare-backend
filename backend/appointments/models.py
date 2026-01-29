from backend.common.db import db
from datetime import datetime


class Appointment(db.Model):
    """Appointment bookings."""
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.id"),
        nullable=False
    )
    availability_id = db.Column(
        db.Integer,
        db.ForeignKey("availability.id"),
        nullable=False
    )
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default="SCHEDULED")  # SCHEDULED, COMPLETED, CANCELLED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    member = db.relationship("User", backref="appointments")
    doctor = db.relationship("Doctor", backref="appointments")
    availability = db.relationship("Availability", backref="appointment")

    def __repr__(self):
        return f"<Appointment {self.id} - {self.date} {self.start_time}>"
