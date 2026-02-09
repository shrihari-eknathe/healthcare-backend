import logging
from backend.departments.models import Department
from backend.departments.repository import department_repository
from backend.common.db import db

logger = logging.getLogger(__name__)


def create_department(name: str) -> Department:
    """Create a new department."""
    logger.info(f"Creating new department: {name}")
    department = department_repository.create(name)
    db.session.commit()
    
    logger.info(f"Department created with id: {department.id}")
    return department


def list_departments() -> list[Department]:
    """List all departments."""
    logger.info("Listing all departments")
    return department_repository.get_all()


def get_department_by_id(department_id: int) -> Department | None:
    """Get a department by ID."""
    return department_repository.find_by_id(department_id)
