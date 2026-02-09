from backend.common.db import db


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Link to User account - allows doctor to login and manage their data
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        unique=True
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=True
    )

    # Relationships
    user = db.relationship("User", backref="doctor_profile")
    department = db.relationship("Department", backref="doctors")

    def is_owned_by(self, user_id: int) -> bool:
        """Check if this doctor profile belongs to the given user."""
        return self.user_id == user_id
