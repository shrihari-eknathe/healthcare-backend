"""Model Registry - Import all models for SQLAlchemy."""

from backend.auth.models import User
from backend.departments.models import Department
from backend.doctors.models import Doctor
from backend.availability.models import Availability
from backend.appointments.models import Appointment
from backend.reimbursements.models import Reimbursement

ALL_MODELS = [
    User,
    Department,
    Doctor,
    Availability,
    Appointment,
    Reimbursement,
]
