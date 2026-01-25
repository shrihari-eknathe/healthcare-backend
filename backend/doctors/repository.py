import logging
from backend.doctors.models import Doctor
from backend.common.db import db

logger = logging.getLogger(__name__)


class DoctorRepository:
    """Repository for Doctor database operations."""

    def create(self, name: str, email: str) -> Doctor:
        """Create a new doctor."""
        logger.debug(f"Creating doctor with name: {name}, email: {email}")
        doctor = Doctor(name=name, email=email)
        db.session.add(doctor)
        db.session.commit()
        logger.info(f"Doctor created with id: {doctor.id}")
        return doctor

    def find_by_id(self, doctor_id: int) -> Doctor | None:
        """Find a doctor by ID."""
        logger.debug(f"Finding doctor by id: {doctor_id}")
        return db.session.get(Doctor, doctor_id)

    def find_by_email(self, email: str) -> Doctor | None:
        """Find a doctor by email."""
        logger.debug(f"Finding doctor by email: {email}")
        return Doctor.query.filter_by(email=email).first()

    def get_all(self) -> list[Doctor]:
        """Get all doctors."""
        logger.debug("Fetching all doctors")
        return Doctor.query.all()

    def update(self, doctor: Doctor) -> Doctor:
        """Update a doctor (commit changes)."""
        logger.debug(f"Updating doctor id: {doctor.id}")
        db.session.commit()
        logger.info(f"Doctor updated: {doctor.id}")
        return doctor


# Singleton instance
doctor_repository = DoctorRepository()
