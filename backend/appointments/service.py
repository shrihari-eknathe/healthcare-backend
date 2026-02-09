import logging
from backend.appointments.models import Appointment
from backend.appointments.repository import appointment_repository
from backend.availability.repository import availability_repository
from backend.doctors.repository import doctor_repository
from backend.common.exceptions import AppException, ForbiddenError
from backend.common.db import db

logger = logging.getLogger(__name__)


def book_appointment(availability_id: int, member_id: int) -> Appointment:
    """Book an appointment with row lock to prevent double booking."""
    logger.info(f"Booking appointment for member {member_id} with availability {availability_id}")

    try:
        # Lock the row to prevent race conditions
        availability = availability_repository.find_by_id_with_lock(availability_id)
        
        if not availability:
            raise AppException("Availability slot not found")

        if availability.is_booked:
            raise AppException("This time slot is already booked")

        appointment = appointment_repository.create(
            member_id=member_id,
            doctor_id=availability.doctor_id,
            availability_id=availability.id,
            date=availability.date,
            start_time=availability.start_time,
            end_time=availability.end_time
        )

        availability.is_booked = True
        db.session.commit()

        logger.info(f"Appointment booked: {appointment.id}")
        return appointment
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to book appointment: {str(e)}")
        raise


def get_member_appointments(member_id: int) -> list[Appointment]:
    """Get all appointments for a member."""
    logger.info(f"Getting appointments for member {member_id}")
    return appointment_repository.find_by_member_id(member_id)


def get_doctor_appointments(doctor_id: int) -> list[Appointment]:
    """Get all appointments for a doctor."""
    logger.info(f"Getting appointments for doctor {doctor_id}")
    return appointment_repository.find_by_doctor_id(doctor_id)


def get_all_appointments() -> list[Appointment]:
    """Get all appointments (admin only)."""
    logger.info("Getting all appointments")
    return appointment_repository.get_all()


def cancel_appointment(appointment_id: int, current_user_id: int, current_user_role: str) -> Appointment:
    """Cancel an appointment."""
    logger.info(f"Cancelling appointment {appointment_id}")

    appointment = appointment_repository.find_by_id(appointment_id)
    if not appointment:
        raise AppException("Appointment not found")

    if appointment.status == "CANCELLED":
        raise AppException("Appointment is already cancelled")

    # Check authorization
    if current_user_role == "MEMBER" and appointment.member_id != current_user_id:
        raise ForbiddenError("You can only cancel your own appointments")
    
    if current_user_role == "DOCTOR":
        doctor = doctor_repository.find_by_user_id(current_user_id)
        if not doctor or appointment.doctor_id != doctor.id:
            raise ForbiddenError("You can only cancel your own appointments")

    appointment.status = "CANCELLED"

    availability = availability_repository.find_by_id(appointment.availability_id)
    if availability:
        availability.is_booked = False

    db.session.commit()

    logger.info(f"Appointment {appointment_id} cancelled")
    return appointment


def get_appointment_by_id(appointment_id: int) -> Appointment | None:
    """Get a single appointment by ID."""
    return appointment_repository.find_by_id(appointment_id)
