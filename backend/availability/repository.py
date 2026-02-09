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
        return availability

    def find_by_id(self, availability_id: int) -> Availability | None:
        """Find availability by ID."""
        return db.session.get(Availability, availability_id)

    def find_by_id_with_lock(self, availability_id: int) -> Availability | None:
        """Find availability by ID with row lock (prevents double booking)."""
        return Availability.query.with_for_update().filter_by(id=availability_id).first()

    def find_by_doctor_id(self, doctor_id: int) -> list[Availability]:
        """Find all availability slots for a doctor."""
        return Availability.query.filter_by(doctor_id=doctor_id).all()

    def find_available_by_doctor_id(self, doctor_id: int) -> list[Availability]:
        """Find available (not booked) slots for a doctor."""
        return Availability.query.filter_by(doctor_id=doctor_id, is_booked=False).all()

    def get_all(self) -> list[Availability]:
        """Get all availability slots."""
        return Availability.query.all()

    def delete(self, availability: Availability) -> None:
        """Delete availability slot."""
        db.session.delete(availability)

    def check_overlap(self, doctor_id: int, date: date, start_time: time, end_time: time) -> bool:
        """Check if there's an overlapping slot."""
        existing = Availability.query.filter(
            Availability.doctor_id == doctor_id,
            Availability.date == date,
            Availability.start_time < end_time,
            Availability.end_time > start_time
        ).first()
        return existing is not None


availability_repository = AvailabilityRepository()
