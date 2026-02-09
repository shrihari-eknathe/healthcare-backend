import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError

from backend.common.rbac import require_roles
from backend.common.exceptions import AppException
from backend.availability.schemas import AvailabilityCreateSchema
from backend.availability.service import (
    create_availability,
    get_available_slots,
    delete_availability,
    list_all_availability,
    get_my_availability
)

logger = logging.getLogger(__name__)

availability_bp = Blueprint("availability", __name__, url_prefix="/availability")


@availability_bp.route("", methods=["POST"])
@require_roles("DOCTOR", "ADMIN")
def create_availability_api():
    """Create a new availability slot."""
    logger.info("Received request to create availability")

    claims = get_jwt()
    current_user_id = get_jwt_identity()
    current_user_role = claims.get("role")

    schema = AvailabilityCreateSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        logger.warning(f"Validation error: {err.messages}")
        raise AppException(str(err.messages))

    availability = create_availability(
        doctor_id=data["doctor_id"],
        date=data["date"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        current_user_id=current_user_id,
        current_user_role=current_user_role
    )

    logger.info(f"Availability created: {availability.id}")
    return {
        "id": availability.id,
        "doctor_id": availability.doctor_id,
        "date": str(availability.date),
        "start_time": str(availability.start_time),
        "end_time": str(availability.end_time),
        "is_booked": availability.is_booked
    }, 201


@availability_bp.route("/my", methods=["GET"])
@require_roles("DOCTOR")
def get_my_availability_api():
    """Get the logged-in doctor's availability slots."""
    logger.info("Received request to get own availability")
    
    current_user_id = get_jwt_identity()
    slots = get_my_availability(current_user_id)
    
    return [
        {
            "id": slot.id,
            "doctor_id": slot.doctor_id,
            "date": str(slot.date),
            "start_time": str(slot.start_time),
            "end_time": str(slot.end_time),
            "is_booked": slot.is_booked
        }
        for slot in slots
    ]


@availability_bp.route("/doctor/<int:doctor_id>", methods=["GET"])
@jwt_required()
def get_doctor_availability_api(doctor_id):
    """Get available slots for a specific doctor."""
    logger.info(f"Received request to get availability for doctor {doctor_id}")

    slots = get_available_slots(doctor_id)

    return [
        {
            "id": slot.id,
            "doctor_id": slot.doctor_id,
            "date": str(slot.date),
            "start_time": str(slot.start_time),
            "end_time": str(slot.end_time),
            "is_booked": slot.is_booked
        }
        for slot in slots
    ]


@availability_bp.route("", methods=["GET"])
@require_roles("ADMIN")
def list_all_availability_api():
    """List all availability slots (admin only)."""
    logger.info("Received request to list all availability")

    slots = list_all_availability()

    return [
        {
            "id": slot.id,
            "doctor_id": slot.doctor_id,
            "doctor_name": slot.doctor.name if slot.doctor else None,
            "date": str(slot.date),
            "start_time": str(slot.start_time),
            "end_time": str(slot.end_time),
            "is_booked": slot.is_booked
        }
        for slot in slots
    ]


@availability_bp.route("/<int:availability_id>", methods=["DELETE"])
@require_roles("DOCTOR", "ADMIN")
def delete_availability_api(availability_id):
    """Delete an availability slot."""
    logger.info(f"Received request to delete availability {availability_id}")

    claims = get_jwt()
    current_user_id = get_jwt_identity()
    current_user_role = claims.get("role")

    delete_availability(availability_id, current_user_id, current_user_role)

    return {"message": "Availability deleted successfully"}
