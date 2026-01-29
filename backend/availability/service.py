import logging
from datetime import date, time
from backend.availability.models import Availability
from backend.availability.repository import availability_repository
from backend.doctors.repository import doctor_repository
from backend.common.exceptions import AppException, ForbiddenError

logger = logging.getLogger(__name__)


def create_availability(doctor_id: int, date: date, start_time: time, end_time: time, current_user_id: int, current_user_role: str) -> Availability:
    """
    Create a new availability slot.
    Only the doctor themselves can add their availability.
    """
    logger.info(f"Creating availability for doctor {doctor_id}")

    # Verify doctor exists
    doctor = doctor_repository.find_by_id(doctor_id)
    if not doctor:
        raise AppException("Doctor not found")

    # Validate time range
    if start_time >= end_time:
        raise AppException("Start time must be before end time")

    # Check for overlapping slots
    if availability_repository.check_overlap(doctor_id, date, start_time, end_time):
        raise AppException("This time slot overlaps with an existing availability")

    return availability_repository.create(doctor_id, date, start_time, end_time)


def get_doctor_availability(doctor_id: int) -> list[Availability]:
    """Get all availability slots for a specific doctor."""
    logger.info(f"Getting availability for doctor {doctor_id}")
    
    doctor = doctor_repository.find_by_id(doctor_id)
    if not doctor:
        raise AppException("Doctor not found")
    
    return availability_repository.find_by_doctor_id(doctor_id)


def get_available_slots(doctor_id: int) -> list[Availability]:
    """Get available (not booked) slots for a doctor."""
    logger.info(f"Getting available slots for doctor {doctor_id}")
    
    doctor = doctor_repository.find_by_id(doctor_id)
    if not doctor:
        raise AppException("Doctor not found")
    
    return availability_repository.find_available_by_doctor_id(doctor_id)


def delete_availability(availability_id: int, current_user_id: int, current_user_role: str) -> None:
    """
    Delete an availability slot.
    Only the doctor who owns it or admin can delete.
    """
    logger.info(f"Deleting availability {availability_id}")

    availability = availability_repository.find_by_id(availability_id)
    if not availability:
        raise AppException("Availability slot not found")

    if availability.is_booked:
        raise AppException("Cannot delete a booked slot")

    availability_repository.delete(availability)
    logger.info(f"Availability {availability_id} deleted")


def list_all_availability() -> list[Availability]:
    """List all availability slots (for admin)."""
    logger.info("Listing all availability slots")
    return availability_repository.get_all()
