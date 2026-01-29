import logging
from backend.appointments.models import Appointment
from backend.appointments.repository import appointment_repository
from backend.availability.repository import availability_repository
from backend.doctors.repository import doctor_repository
from backend.common.exceptions import AppException, ForbiddenError

logger = logging.getLogger(__name__)


def book_appointment(availability_id: int, member_id: int) -> Appointment:
    """
    Book an appointment.
    Only MEMBER can book appointments.
    Prevents double booking.
    """
    logger.info(f"Booking appointment for member {member_id} with availability {availability_id}")

    # Get the availability slot
    availability = availability_repository.find_by_id(availability_id)
    if not availability:
        raise AppException("Availability slot not found")

    # Check if already booked (prevent double booking)
    if availability.is_booked:
        raise AppException("This time slot is already booked")

    # Create the appointment
    appointment = appointment_repository.create(
        member_id=member_id,
        doctor_id=availability.doctor_id,
        availability_id=availability.id,
        date=availability.date,
        start_time=availability.start_time,
        end_time=availability.end_time
    )

    # Mark the availability slot as booked
    availability.is_booked = True
    availability_repository.update(availability)

    logger.info(f"Appointment booked: {appointment.id}")
    return appointment


def get_member_appointments(member_id: int) -> list[Appointment]:
    """Get all appointments for a member."""
    logger.info(f"Getting appointments for member {member_id}")
    return appointment_repository.find_by_member_id(member_id)


def get_doctor_appointments(doctor_id: int) -> list[Appointment]:
    """Get all appointments for a doctor."""
    logger.info(f"Getting appointments for doctor {doctor_id}")
    return appointment_repository.find_by_doctor_id(doctor_id)


def get_all_appointments() -> list[Appointment]:
    """Get all appointments (for admin)."""
    logger.info("Getting all appointments")
    return appointment_repository.get_all()


def cancel_appointment(appointment_id: int, current_user_id: int, current_user_role: str) -> Appointment:
    """
    Cancel an appointment.
    - MEMBER can cancel their own appointment
    - DOCTOR can cancel their own appointment
    - ADMIN can cancel any appointment
    """
    logger.info(f"Cancelling appointment {appointment_id}")

    appointment = appointment_repository.find_by_id(appointment_id)
    if not appointment:
        raise AppException("Appointment not found")

    if appointment.status == "CANCELLED":
        raise AppException("Appointment is already cancelled")

    # Check authorization
    if current_user_role == "MEMBER" and appointment.member_id != current_user_id:
        raise ForbiddenError("You can only cancel your own appointments")

    # Update appointment status
    appointment.status = "CANCELLED"
    appointment_repository.update(appointment)

    # Free up the availability slot
    availability = availability_repository.find_by_id(appointment.availability_id)
    if availability:
        availability.is_booked = False
        availability_repository.update(availability)

    logger.info(f"Appointment {appointment_id} cancelled")
    return appointment


def get_appointment_by_id(appointment_id: int) -> Appointment | None:
    """Get a single appointment by ID."""
    return appointment_repository.find_by_id(appointment_id)
