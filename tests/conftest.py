"""
Pytest configuration and fixtures.
"""
import os
import pytest
from flask_jwt_extended import create_access_token

# Set test environment BEFORE importing app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key"

from backend.main import create_app
from backend.common.db import db
from backend.auth.models import User
from backend.doctors.models import Doctor
from backend.common.security import hash_password


@pytest.fixture
def app():
    """Create test application with in-memory SQLite database."""
    app = create_app()
    
    # Ensure test config
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture
def admin_user(app):
    """Create an admin user in the test database."""
    with app.app_context():
        user = User(
            email="admin@test.com",
            password=hash_password("password123"),
            role="ADMIN"
        )
        db.session.add(user)
        db.session.commit()
        
        return {"id": user.id, "email": user.email, "role": user.role}


@pytest.fixture
def member_user(app):
    """Create a member user in the test database."""
    with app.app_context():
        user = User(
            email="member@test.com",
            password=hash_password("password123"),
            role="MEMBER"
        )
        db.session.add(user)
        db.session.commit()
        
        return {"id": user.id, "email": user.email, "role": user.role}


@pytest.fixture
def doctor_user(app):
    """Create a doctor user in the test database."""
    with app.app_context():
        user = User(
            email="doctor@test.com",
            password=hash_password("password123"),
            role="DOCTOR"
        )
        db.session.add(user)
        db.session.commit()
        
        return {"id": user.id, "email": user.email, "role": user.role}


@pytest.fixture
def doctor_with_profile(app, doctor_user):
    """Create a doctor user with linked doctor profile."""
    with app.app_context():
        doctor = Doctor(
            name="Dr. Test Doctor",
            email="drtest@hospital.com",
            user_id=doctor_user["id"]
        )
        db.session.add(doctor)
        db.session.commit()
        
        return {
            "user_id": doctor_user["id"],
            "doctor_id": doctor.id,
            "name": doctor.name,
            "email": doctor.email
        }


@pytest.fixture
def admin_token(app, admin_user):
    """Generate JWT token for admin user."""
    with app.app_context():
        token = create_access_token(
            identity=admin_user["id"],
            additional_claims={"role": admin_user["role"]}
        )
        return token


@pytest.fixture
def member_token(app, member_user):
    """Generate JWT token for member user."""
    with app.app_context():
        token = create_access_token(
            identity=member_user["id"],
            additional_claims={"role": member_user["role"]}
        )
        return token


@pytest.fixture
def doctor_token(app, doctor_user):
    """Generate JWT token for doctor user."""
    with app.app_context():
        token = create_access_token(
            identity=doctor_user["id"],
            additional_claims={"role": doctor_user["role"]}
        )
        return token


@pytest.fixture
def auth_headers(admin_token):
    """Return headers with admin JWT token."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def member_headers(member_token):
    """Return headers with member JWT token."""
    return {"Authorization": f"Bearer {member_token}"}


@pytest.fixture
def doctor_headers(doctor_token):
    """Return headers with doctor JWT token."""
    return {"Authorization": f"Bearer {doctor_token}"}
