import logging
from flask import Blueprint, request
from marshmallow import ValidationError

from backend.common.rbac import require_roles
from backend.common.exceptions import AppException
from backend.doctors.schemas import DoctorCreateSchema, DoctorAssignSchema
from backend.doctors.service import (
    create_doctor,
    list_doctors,
    assign_doctor_to_department
)

logger = logging.getLogger(__name__)

doctors_bp = Blueprint("doctors", __name__, url_prefix="/doctors")


@doctors_bp.route("", methods=["POST"])
@require_roles("ADMIN")
def create_doctor_api():
    """Create a new doctor."""
    logger.info("Received request to create doctor")
    
    schema = DoctorCreateSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        logger.warning(f"Validation error: {err.messages}")
        raise AppException(str(err.messages))

    doctor = create_doctor(data["name"], data["email"])
    logger.info(f"Doctor created successfully: {doctor.id}")
    
    return {
        "id": doctor.id,
        "name": doctor.name,
        "email": doctor.email
    }, 201


@doctors_bp.route("", methods=["GET"])
@require_roles("ADMIN")
def list_doctors_api():
    """List all doctors."""
    logger.info("Received request to list doctors")
    
    doctors = list_doctors()
    
    return [
        {
            "id": d.id,
            "name": d.name,
            "email": d.email,
            "department": d.department.name if d.department else None
        }
        for d in doctors
    ]


@doctors_bp.route("/assign", methods=["POST"])
@require_roles("ADMIN")
def assign_doctor_api():
    """Assign a doctor to a department."""
    logger.info("Received request to assign doctor to department")
    
    schema = DoctorAssignSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        logger.warning(f"Validation error: {err.messages}")
        raise AppException(str(err.messages))

    assign_doctor_to_department(
        data["doctor_id"],
        data["department_id"]
    )
    
    logger.info("Doctor assigned successfully")
    return {"message": "Doctor assigned successfully"}
