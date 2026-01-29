from backend.common.db import db


class Availability(db.Model):
    """Doctor availability slots."""
    __tablename__ = "availability"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.id"),
        nullable=False
    )
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_booked = db.Column(db.Boolean, default=False)

    # Relationship
    doctor = db.relationship("Doctor", backref="availability_slots")

    def __repr__(self):
        return f"<Availability {self.date} {self.start_time}-{self.end_time}>"
