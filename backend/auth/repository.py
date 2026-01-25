import logging
from backend.auth.models import User
from backend.common.db import db

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for User database operations."""

    def create(self, email: str, password: str, role: str) -> User:
        """Create a new user in the database."""
        logger.debug(f"Creating user with email: {email}")
        user = User(email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        logger.info(f"User created with id: {user.id}")
        return user

    def find_by_email(self, email: str) -> User | None:
        """Find a user by email address."""
        logger.debug(f"Finding user by email: {email}")
        return User.query.filter_by(email=email).first()

    def find_by_id(self, user_id: int) -> User | None:
        """Find a user by ID."""
        logger.debug(f"Finding user by id: {user_id}")
        return db.session.get(User, user_id)

    def get_all(self) -> list[User]:
        """Get all users."""
        logger.debug("Fetching all users")
        return User.query.all()


# Singleton instance for easy import
user_repository = UserRepository()
