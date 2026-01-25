import logging
from backend.departments.models import Department
from backend.departments.repository import department_repository

logger = logging.getLogger(__name__)


def create_department(name: str) -> Department:
    """Create a new department."""
    logger.info(f"Creating new department: {name}")
    return department_repository.create(name)


def list_departments() -> list[Department]:
    """List all departments."""
    logger.info("Listing all departments")
    return department_repository.get_all()


def get_department_by_id(department_id: int) -> Department | None:
    """Get a department by ID."""
    logger.info(f"Getting department by id: {department_id}")
    return department_repository.find_by_id(department_id)
