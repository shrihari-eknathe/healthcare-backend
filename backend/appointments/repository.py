import logging
from datetime import date, time
from backend.appointments.models import Appointment
from backend.common.db import db

logger = logging.getLogger(__name__)


class AppointmentRepository:
    """Repository for Appointment database operations."""

    def create(self, member_id: int, doctor_id: int, availability_id: int,
               date: date, start_time: time, end_time: time) -> Appointment:
        """Create a new appointment."""
        logger.debug(f"Creating appointment for member {member_id} with doctor {doctor_id}")
        appointment = Appointment(
            member_id=member_id,
            doctor_id=doctor_id,
            availability_id=availability_id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            status="SCHEDULED"
        )
        db.session.add(appointment)
        db.session.commit()
        logger.info(f"Appointment created with id: {appointment.id}")
        return appointment

    def find_by_id(self, appointment_id: int) -> Appointment | None:
        """Find appointment by ID."""
        logger.debug(f"Finding appointment by id: {appointment_id}")
        return db.session.get(Appointment, appointment_id)

    def find_by_member_id(self, member_id: int) -> list[Appointment]:
        """Find all appointments for a member."""
        logger.debug(f"Finding appointments for member: {member_id}")
        return Appointment.query.filter_by(member_id=member_id).all()

    def find_by_doctor_id(self, doctor_id: int) -> list[Appointment]:
        """Find all appointments for a doctor."""
        logger.debug(f"Finding appointments for doctor: {doctor_id}")
        return Appointment.query.filter_by(doctor_id=doctor_id).all()

    def get_all(self) -> list[Appointment]:
        """Get all appointments."""
        logger.debug("Fetching all appointments")
        return Appointment.query.all()

    def update(self, appointment: Appointment) -> Appointment:
        """Update appointment."""
        logger.debug(f"Updating appointment id: {appointment.id}")
        db.session.commit()
        logger.info(f"Appointment updated: {appointment.id}")
        return appointment

    def find_by_availability_id(self, availability_id: int) -> Appointment | None:
        """Find appointment by availability slot."""
        logger.debug(f"Finding appointment for availability: {availability_id}")
        return Appointment.query.filter_by(availability_id=availability_id).first()


# Singleton instance
appointment_repository = AppointmentRepository()
