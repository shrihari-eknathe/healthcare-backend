import logging
from backend.auth.models import User
from backend.common.db import db

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for User database operations."""

    def create(self, email: str, password: str, role: str) -> User:
        """Create a new user."""
        logger.debug("Creating new user")
        user = User(email=email, password=password, role=role)
        db.session.add(user)
        return user

    def find_by_email(self, email: str) -> User | None:
        """Find user by email."""
        return User.query.filter_by(email=email).first()

    def find_by_id(self, user_id: int) -> User | None:
        """Find user by ID."""
        return db.session.get(User, user_id)

    def get_all(self) -> list[User]:
        """Get all users."""
        return User.query.all()

    def update_role(self, user: User, new_role: str) -> User:
        """Update user role."""
        user.role = new_role
        return user


user_repository = UserRepository()
