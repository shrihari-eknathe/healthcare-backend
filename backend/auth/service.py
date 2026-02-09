import logging
from backend.auth.models import User
from backend.auth.repository import user_repository
from backend.common.security import hash_password, verify_password
from backend.common.exceptions import UnauthorizedError, AppException
from backend.common.db import db

logger = logging.getLogger(__name__)


def register_user(email: str, password: str, role: str) -> User:
    """Register a new user."""
    logger.info("Registering new user")
    
    existing_user = user_repository.find_by_email(email)
    if existing_user:
        logger.warning("Email already registered")
        raise AppException("Email already registered")

    hashed_password = hash_password(password)
    user = user_repository.create(email, hashed_password, role)
    db.session.commit()
    
    logger.info(f"User created with id: {user.id}")
    return user


def authenticate_user(email: str, password: str) -> User:
    """Authenticate user by email and password."""
    logger.info("Authenticating user")
    
    user = user_repository.find_by_email(email)
    if not user or not verify_password(password, user.password):
        logger.warning("Invalid credentials attempt")
        raise UnauthorizedError("Invalid credentials")
    
    logger.info(f"User authenticated with id: {user.id}")
    return user


def update_user_role(user_id: int, new_role: str) -> User:
    """Update a user's role (admin only)."""
    logger.info(f"Updating role for user {user_id} to {new_role}")
    
    user = user_repository.find_by_id(user_id)
    if not user:
        raise AppException("User not found")
    
    user = user_repository.update_role(user, new_role)
    db.session.commit()
    
    logger.info(f"Role updated for user {user_id}")
    return user


def get_user_by_id(user_id: int) -> User | None:
    """Get a user by ID."""
    return user_repository.find_by_id(user_id)
