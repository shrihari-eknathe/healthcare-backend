import logging
from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError

from backend.auth.service import register_user, authenticate_user
from backend.auth.schemas import RegisterSchema, LoginSchema
from backend.common.exceptions import AppException

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user."""
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
        data["role"]
    )
    
    logger.info(f"User registered successfully: {user.email}")
    return {"message": "User registered"}, 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login and get access token."""
    logger.info("Received login request")
    
    schema = LoginSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        logger.warning(f"Validation error: {err.messages}")
        raise AppException(str(err.messages))

    user = authenticate_user(data["email"], data["password"])

    token = create_access_token(
        identity=user.id,
        additional_claims={"role": user.role}
    )
    
    logger.info(f"User logged in successfully: {user.email}")
    return {"access_token": token}
