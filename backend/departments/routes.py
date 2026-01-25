import logging
from flask import Blueprint, request
from marshmallow import ValidationError

from backend.common.rbac import require_roles
from backend.common.exceptions import AppException
from backend.departments.schemas import DepartmentCreateSchema
from backend.departments.service import create_department, list_departments

logger = logging.getLogger(__name__)

departments_bp = Blueprint("departments", __name__, url_prefix="/departments")


@departments_bp.route("", methods=["POST"])
@require_roles("ADMIN")
def create_department_api():
    """Create a new department."""
    logger.info("Received request to create department")
    
    schema = DepartmentCreateSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        logger.warning(f"Validation error: {err.messages}")
        raise AppException(str(err.messages))

    dept = create_department(data["name"])
    logger.info(f"Department created successfully: {dept.id}")
    
    return {
        "id": dept.id,
        "name": dept.name
    }, 201


@departments_bp.route("", methods=["GET"])
@require_roles("ADMIN")
def list_departments_api():
    """List all departments."""
    logger.info("Received request to list departments")
    
    departments = list_departments()
    
    return [
        {"id": d.id, "name": d.name}
        for d in departments
    ]
