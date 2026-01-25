import logging
from backend.doctors.models import Doctor
from backend.doctors.repository import doctor_repository
from backend.departments.repository import department_repository
from backend.common.exceptions import AppException

logger = logging.getLogger(__name__)


def create_doctor(name: str, email: str) -> Doctor:
    """Create a new doctor."""
    logger.info(f"Creating new doctor: {name}")
    return doctor_repository.create(name, email)


def list_doctors() -> list[Doctor]:
    """List all doctors."""
    logger.info("Listing all doctors")
    return doctor_repository.get_all()


def get_doctor_by_id(doctor_id: int) -> Doctor | None:
    """Get a doctor by ID."""
    logger.info(f"Getting doctor by id: {doctor_id}")
    return doctor_repository.find_by_id(doctor_id)


def assign_doctor_to_department(doctor_id: int, department_id: int) -> Doctor:
    """Assign a doctor to a department."""
    logger.info(f"Assigning doctor {doctor_id} to department {department_id}")
    
    doctor = doctor_repository.find_by_id(doctor_id)
    department = department_repository.find_by_id(department_id)

    if not doctor:
        logger.warning(f"Doctor not found: {doctor_id}")
        raise AppException("Doctor not found")

    if not department:
        logger.warning(f"Department not found: {department_id}")
        raise AppException("Department not found")

    doctor.department_id = department.id
    doctor_repository.update(doctor)
    
    logger.info(f"Doctor {doctor_id} assigned to department {department_id}")
    return doctor
