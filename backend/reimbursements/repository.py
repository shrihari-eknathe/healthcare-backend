import logging
from backend.reimbursements.models import Reimbursement
from backend.common.db import db

logger = logging.getLogger(__name__)


class ReimbursementRepository:
    """Repository for Reimbursement database operations."""

    def create(self, member_id: int, appointment_id: int, amount: float, 
               receipt_url: str, description: str = None, status: str = "PENDING") -> Reimbursement:
        """Create a new reimbursement claim."""
        logger.debug(f"Creating reimbursement for member {member_id}")
        reimbursement = Reimbursement(
            member_id=member_id,
            appointment_id=appointment_id,
            amount=amount,
            receipt_url=receipt_url,
            description=description,
            status=status
        )
        db.session.add(reimbursement)
        return reimbursement

    def find_by_id(self, reimbursement_id: int) -> Reimbursement | None:
        """Find reimbursement by ID."""
        return db.session.get(Reimbursement, reimbursement_id)

    def find_by_member_id(self, member_id: int) -> list[Reimbursement]:
        """Find all reimbursements for a member."""
        return Reimbursement.query.filter_by(member_id=member_id).all()

    def find_by_appointment_id(self, appointment_id: int) -> Reimbursement | None:
        """Find reimbursement by appointment ID."""
        return Reimbursement.query.filter_by(appointment_id=appointment_id).first()

    def get_all(self) -> list[Reimbursement]:
        """Get all reimbursements."""
        return Reimbursement.query.all()

    def get_pending(self) -> list[Reimbursement]:
        """Get all pending reimbursements."""
        return Reimbursement.query.filter_by(status="PENDING").all()


reimbursement_repository = ReimbursementRepository()
