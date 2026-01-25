import logging
from backend.departments.models import Department
from backend.common.db import db

logger = logging.getLogger(__name__)


class DepartmentRepository:
    """Repository for Department database operations."""

    def create(self, name: str) -> Department:
        """Create a new department."""
        logger.debug(f"Creating department with name: {name}")
        department = Department(name=name)
        db.session.add(department)
        db.session.commit()
        logger.info(f"Department created with id: {department.id}")
        return department

    def find_by_id(self, department_id: int) -> Department | None:
        """Find a department by ID."""
        logger.debug(f"Finding department by id: {department_id}")
        return db.session.get(Department, department_id)

    def find_by_name(self, name: str) -> Department | None:
        """Find a department by name."""
        logger.debug(f"Finding department by name: {name}")
        return Department.query.filter_by(name=name).first()

    def get_all(self) -> list[Department]:
        """Get all departments."""
        logger.debug("Fetching all departments")
        return Department.query.all()


# Singleton instance
department_repository = DepartmentRepository()
