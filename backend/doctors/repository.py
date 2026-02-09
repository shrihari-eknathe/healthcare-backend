import logging
from backend.doctors.models import Doctor
from backend.common.db import db

logger = logging.getLogger(__name__)


class DoctorRepository:
    """Repository for Doctor database operations."""

    def create(self, name: str, email: str, user_id: int = None) -> Doctor:
        """Create a new doctor."""
        logger.debug(f"Creating doctor: {name}")
        doctor = Doctor(name=name, email=email, user_id=user_id)
        db.session.add(doctor)
        return doctor

    def find_by_id(self, doctor_id: int) -> Doctor | None:
        """Find a doctor by ID."""
        return db.session.get(Doctor, doctor_id)

    def find_by_email(self, email: str) -> Doctor | None:
        """Find a doctor by email."""
        return Doctor.query.filter_by(email=email).first()

    def find_by_user_id(self, user_id: int) -> Doctor | None:
        """Find a doctor by their linked user ID."""
        return Doctor.query.filter_by(user_id=user_id).first()

    def get_all(self) -> list[Doctor]:
        """Get all doctors."""
        return Doctor.query.all()

    def link_user(self, doctor: Doctor, user_id: int) -> Doctor:
        """Link a doctor to a user account."""
        doctor.user_id = user_id
        return doctor


doctor_repository = DoctorRepository()
