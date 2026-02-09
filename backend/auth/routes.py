import logging
from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    get_jwt_identity,
    jwt_required
)
from marshmallow import ValidationError

from backend.auth.service import register_user, authenticate_user, update_user_role, get_user_by_id
from backend.auth.schemas import RegisterSchema, LoginSchema, RoleAssignmentSchema
from backend.common.exceptions import AppException
from backend.common.rbac import require_roles
from backend.common.enums import UserRole

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user (always as MEMBER)."""
    logger.info("Received registration request")
    
    schema = RegisterSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        logger.warning(f"Validation error: {err.messages}")
        raise AppException(str(err.messages))

    user = register_user(
        data["email"],
        data["password"],
        role=UserRole.MEMBER.value
    )
    
    logger.info(f"User registered with id: {user.id}")
    return {"message": "User registered", "user_id": user.id}, 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login and get access + refresh tokens."""
    logger.info("Received login request")
    
    schema = LoginSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        logger.warning(f"Validation error: {err.messages}")
        raise AppException(str(err.messages))

    user = authenticate_user(data["email"], data["password"])

    access_token = create_access_token(
        identity=user.id,
        additional_claims={"role": user.role}
    )
    refresh_token = create_refresh_token(
        identity=user.id,
        additional_claims={"role": user.role}
    )
    
    logger.info(f"User logged in with id: {user.id}")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Get new access token using refresh token."""
    logger.info("Received token refresh request")
    
    current_user_id = get_jwt_identity()
    user = get_user_by_id(current_user_id)
    
    if not user:
        raise AppException("User not found")
    
    access_token = create_access_token(
        identity=user.id,
        additional_claims={"role": user.role}
    )
    
    logger.info(f"Token refreshed for user id: {user.id}")
    return {"access_token": access_token}


@auth_bp.route("/users/<int:user_id>/role", methods=["PATCH"])
@require_roles("ADMIN")
def assign_role(user_id):
    """Assign role to user (admin only)."""
    logger.info(f"Received role assignment request for user {user_id}")
    
    schema = RoleAssignmentSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        logger.warning(f"Validation error: {err.messages}")
        raise AppException(str(err.messages))
    
    admin_id = get_jwt_identity()
    
    if user_id == admin_id and data["role"] != UserRole.ADMIN.value:
        raise AppException("You cannot change your own role")
    
    user = update_user_role(user_id, data["role"])
    
    logger.info(f"Role updated for user {user_id} to {data['role']}")
    return {
        "message": "Role updated successfully",
        "user_id": user.id,
        "role": user.role
    }


@auth_bp.route("/me", methods=["GET"])
@require_roles("ADMIN", "DOCTOR", "MEMBER")
def get_current_user():
    """Get current logged in user info."""
    user_id = get_jwt_identity()
    user = get_user_by_id(user_id)
    
    if not user:
        raise AppException("User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role
    }
