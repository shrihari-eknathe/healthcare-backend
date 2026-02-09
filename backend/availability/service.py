import logging
from datetime import date, time
from backend.availability.models import Availability
from backend.availability.repository import availability_repository
from backend.doctors.repository import doctor_repository
from backend.common.exceptions import AppException, ForbiddenError
from backend.common.db import db

logger = logging.getLogger(__name__)


def create_availability(doctor_id: int, date: date, start_time: time, end_time: time, 
                        current_user_id: int, current_user_role: str) -> Availability:
    """Create a new availability slot."""
    logger.info(f"Creating availability for doctor {doctor_id}")

    doctor = doctor_repository.find_by_id(doctor_id)
    if not doctor:
        raise AppException("Doctor not found")

    # Doctor can only manage their own availability
    if current_user_role == "DOCTOR":
        if doctor.user_id != current_user_id:
            logger.warning(f"Doctor {current_user_id} tried to modify doctor {doctor_id}'s availability")
            raise ForbiddenError("You can only manage your own availability")

    if start_time >= end_time:
        raise AppException("Start time must be before end time")

    if availability_repository.check_overlap(doctor_id, date, start_time, end_time):
        raise AppException("This time slot overlaps with an existing availability")

    availability = availability_repository.create(doctor_id, date, start_time, end_time)
    db.session.commit()
    
    logger.info(f"Availability created with id: {availability.id}")
    return availability


def get_doctor_availability(doctor_id: int) -> list[Availability]:
    """Get all availability slots for a doctor."""
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
    """Delete an availability slot."""
    logger.info(f"Deleting availability {availability_id}")

    availability = availability_repository.find_by_id(availability_id)
    if not availability:
        raise AppException("Availability slot not found")

    if availability.is_booked:
        raise AppException("Cannot delete a booked slot")

    # Doctor can only delete their own availability
    if current_user_role == "DOCTOR":
        doctor = doctor_repository.find_by_id(availability.doctor_id)
        if not doctor or doctor.user_id != current_user_id:
            logger.warning(f"Doctor {current_user_id} tried to delete another doctor's availability")
            raise ForbiddenError("You can only delete your own availability")

    availability_repository.delete(availability)
    db.session.commit()
    
    logger.info(f"Availability {availability_id} deleted")


def list_all_availability() -> list[Availability]:
    """List all availability slots (admin only)."""
    logger.info("Listing all availability slots")
    return availability_repository.get_all()


def get_my_availability(user_id: int) -> list[Availability]:
    """Get availability for the logged-in doctor."""
    doctor = doctor_repository.find_by_user_id(user_id)
    if not doctor:
        raise AppException("No doctor profile linked to your account")
    
    return availability_repository.find_by_doctor_id(doctor.id)
