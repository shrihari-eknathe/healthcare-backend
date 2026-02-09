import logging
from backend.doctors.models import Doctor
from backend.doctors.repository import doctor_repository
from backend.departments.repository import department_repository
from backend.auth.repository import user_repository
from backend.common.exceptions import AppException
from backend.common.enums import UserRole
from backend.common.db import db

logger = logging.getLogger(__name__)


def create_doctor(name: str, email: str, user_id: int = None) -> Doctor:
    """Create a new doctor profile."""
    logger.info(f"Creating new doctor: {name}")
    
    if user_id:
        user = user_repository.find_by_id(user_id)
        if not user:
            raise AppException("User not found")
        if user.role != UserRole.DOCTOR.value:
            raise AppException("User must have DOCTOR role to be linked")
        
        existing_doctor = doctor_repository.find_by_user_id(user_id)
        if existing_doctor:
            raise AppException("User is already linked to a doctor profile")
    
    doctor = doctor_repository.create(name, email, user_id)
    db.session.commit()
    
    logger.info(f"Doctor created with id: {doctor.id}")
    return doctor


def list_doctors() -> list[Doctor]:
    """List all doctors."""
    logger.info("Listing all doctors")
    return doctor_repository.get_all()


def get_doctor_by_id(doctor_id: int) -> Doctor | None:
    """Get a doctor by ID."""
    return doctor_repository.find_by_id(doctor_id)


def get_doctor_by_user_id(user_id: int) -> Doctor | None:
    """Get a doctor by their linked user ID."""
    return doctor_repository.find_by_user_id(user_id)


def assign_doctor_to_department(doctor_id: int, department_id: int) -> Doctor:
    """Assign a doctor to a department."""
    logger.info(f"Assigning doctor {doctor_id} to department {department_id}")
    
    doctor = doctor_repository.find_by_id(doctor_id)
    department = department_repository.find_by_id(department_id)

    if not doctor:
        raise AppException("Doctor not found")
    if not department:
        raise AppException("Department not found")

    doctor.department_id = department.id
    db.session.commit()
    
    logger.info(f"Doctor {doctor_id} assigned to department {department_id}")
    return doctor


def link_doctor_to_user(doctor_id: int, user_id: int) -> Doctor:
    """Link a doctor profile to a user account."""
    logger.info(f"Linking doctor {doctor_id} to user {user_id}")
    
    doctor = doctor_repository.find_by_id(doctor_id)
    if not doctor:
        raise AppException("Doctor not found")
    
    if doctor.user_id:
        raise AppException("Doctor is already linked to a user account")
    
    user = user_repository.find_by_id(user_id)
    if not user:
        raise AppException("User not found")
    
    if user.role != UserRole.DOCTOR.value:
        raise AppException("User must have DOCTOR role")
    
    existing_doctor = doctor_repository.find_by_user_id(user_id)
    if existing_doctor:
        raise AppException("User is already linked to another doctor profile")
    
    doctor = doctor_repository.link_user(doctor, user_id)
    db.session.commit()
    
    logger.info(f"Doctor {doctor_id} linked to user {user_id}")
    return doctor
