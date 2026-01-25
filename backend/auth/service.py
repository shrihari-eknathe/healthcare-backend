import logging
from backend.auth.models import User
from backend.auth.repository import user_repository
from backend.common.security import hash_password, verify_password
from backend.common.exceptions import UnauthorizedError, AppException

logger = logging.getLogger(__name__)


def register_user(email: str, password: str, role: str) -> User:
    """Register a new user."""
    logger.info(f"Registering user: {email}")
    
    # Check if user already exists
    existing_user = user_repository.find_by_email(email)
    if existing_user:
        logger.warning(f"Email already registered: {email}")
        raise AppException("Email already registered")

    # Hash password and create user
    hashed_password = hash_password(password)
    user = user_repository.create(email, hashed_password, role)
    
    logger.info(f"User created with id: {user.id}")
    return user


def authenticate_user(email: str, password: str) -> User:
    """Authenticate a user by email and password."""
    logger.info(f"Authenticating user: {email}")
    
    user = user_repository.find_by_email(email)
    if not user or not verify_password(password, user.password):
        logger.warning(f"Invalid credentials for: {email}")
        raise UnauthorizedError("Invalid credentials")
    
    logger.info(f"User authenticated: {email}")
    return user
