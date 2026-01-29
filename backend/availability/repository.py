import logging
from datetime import date, time
from backend.availability.models import Availability
from backend.common.db import db

logger = logging.getLogger(__name__)


class AvailabilityRepository:
    """Repository for Availability database operations."""

    def create(self, doctor_id: int, date: date, start_time: time, end_time: time) -> Availability:
        """Create a new availability slot."""
        logger.debug(f"Creating availability for doctor {doctor_id} on {date}")
        availability = Availability(
            doctor_id=doctor_id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            is_booked=False
        )
        db.session.add(availability)
        db.session.commit()
        logger.info(f"Availability created with id: {availability.id}")
        return availability

    def find_by_id(self, availability_id: int) -> Availability | None:
        """Find availability by ID."""
        logger.debug(f"Finding availability by id: {availability_id}")
        return db.session.get(Availability, availability_id)

    def find_by_doctor_id(self, doctor_id: int) -> list[Availability]:
        """Find all availability slots for a doctor."""
        logger.debug(f"Finding availability for doctor: {doctor_id}")
        return Availability.query.filter_by(doctor_id=doctor_id).all()

    def find_available_by_doctor_id(self, doctor_id: int) -> list[Availability]:
        """Find available (not booked) slots for a doctor."""
        logger.debug(f"Finding available slots for doctor: {doctor_id}")
        return Availability.query.filter_by(
            doctor_id=doctor_id,
            is_booked=False
        ).all()

    def get_all(self) -> list[Availability]:
        """Get all availability slots."""
        logger.debug("Fetching all availability slots")
        return Availability.query.all()

    def update(self, availability: Availability) -> Availability:
        """Update availability slot."""
        logger.debug(f"Updating availability id: {availability.id}")
        db.session.commit()
        logger.info(f"Availability updated: {availability.id}")
        return availability

    def delete(self, availability: Availability) -> None:
        """Delete availability slot."""
        logger.debug(f"Deleting availability id: {availability.id}")
        db.session.delete(availability)
        db.session.commit()
        logger.info(f"Availability deleted: {availability.id}")

    def check_overlap(self, doctor_id: int, date: date, start_time: time, end_time: time) -> bool:
        """Check if there's an overlapping slot."""
        logger.debug(f"Checking for overlapping slots for doctor {doctor_id}")
        existing = Availability.query.filter(
            Availability.doctor_id == doctor_id,
            Availability.date == date,
            Availability.start_time < end_time,
            Availability.end_time > start_time
        ).first()
        return existing is not None


# Singleton instance
availability_repository = AvailabilityRepository()
