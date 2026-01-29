import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError

from backend.common.rbac import require_roles
from backend.common.exceptions import AppException
from backend.appointments.schemas import AppointmentCreateSchema
from backend.appointments.service import (
    book_appointment,
    get_member_appointments,
    get_doctor_appointments,
    get_all_appointments,
    cancel_appointment,
    get_appointment_by_id
)

logger = logging.getLogger(__name__)

appointments_bp = Blueprint("appointments", __name__, url_prefix="/appointments")


@appointments_bp.route("", methods=["POST"])
@require_roles("MEMBER")
def book_appointment_api():
    """Book an appointment. Only MEMBER can book."""
    logger.info("Received request to book appointment")

    member_id = get_jwt_identity()

    schema = AppointmentCreateSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        logger.warning(f"Validation error: {err.messages}")
        raise AppException(str(err.messages))

    appointment = book_appointment(
        availability_id=data["availability_id"],
        member_id=member_id
    )

    logger.info(f"Appointment booked: {appointment.id}")
    return {
        "id": appointment.id,
        "doctor_id": appointment.doctor_id,
        "date": str(appointment.date),
        "start_time": str(appointment.start_time),
        "end_time": str(appointment.end_time),
        "status": appointment.status,
        "message": "Appointment booked successfully"
    }, 201


@appointments_bp.route("", methods=["GET"])
@jwt_required()
def get_appointments_api():
    """
    Get appointments based on role:
    - ADMIN: See all appointments
    - DOCTOR: See own appointments (where they are the doctor)
    - MEMBER: See own appointments
    """
    logger.info("Received request to get appointments")

    claims = get_jwt()
    current_user_id = get_jwt_identity()
    current_user_role = claims.get("role")

    if current_user_role == "ADMIN":
        appointments = get_all_appointments()
    elif current_user_role == "DOCTOR":
        # For doctor, we need to find their doctor_id
        # For now, return empty as doctors are separate from users
        appointments = []
    else:  # MEMBER
        appointments = get_member_appointments(current_user_id)

    return [
        {
            "id": apt.id,
            "member_id": apt.member_id,
            "member_email": apt.member.email if apt.member else None,
            "doctor_id": apt.doctor_id,
            "doctor_name": apt.doctor.name if apt.doctor else None,
            "date": str(apt.date),
            "start_time": str(apt.start_time),
            "end_time": str(apt.end_time),
            "status": apt.status
        }
        for apt in appointments
    ]


@appointments_bp.route("/<int:appointment_id>", methods=["GET"])
@jwt_required()
def get_appointment_detail_api(appointment_id):
    """Get a single appointment detail."""
    logger.info(f"Received request to get appointment {appointment_id}")

    claims = get_jwt()
    current_user_id = get_jwt_identity()
    current_user_role = claims.get("role")

    appointment = get_appointment_by_id(appointment_id)
    if not appointment:
        raise AppException("Appointment not found")

    # Check authorization
    if current_user_role == "MEMBER" and appointment.member_id != current_user_id:
        raise AppException("You can only view your own appointments")

    return {
        "id": appointment.id,
        "member_id": appointment.member_id,
        "member_email": appointment.member.email if appointment.member else None,
        "doctor_id": appointment.doctor_id,
        "doctor_name": appointment.doctor.name if appointment.doctor else None,
        "date": str(appointment.date),
        "start_time": str(appointment.start_time),
        "end_time": str(appointment.end_time),
        "status": appointment.status
    }


@appointments_bp.route("/<int:appointment_id>/cancel", methods=["PATCH"])
@jwt_required()
def cancel_appointment_api(appointment_id):
    """Cancel an appointment."""
    logger.info(f"Received request to cancel appointment {appointment_id}")

    claims = get_jwt()
    current_user_id = get_jwt_identity()
    current_user_role = claims.get("role")

    appointment = cancel_appointment(
        appointment_id=appointment_id,
        current_user_id=current_user_id,
        current_user_role=current_user_role
    )

    return {
        "id": appointment.id,
        "status": appointment.status,
        "message": "Appointment cancelled successfully"
    }
