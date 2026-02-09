import logging
from backend.reimbursements.models import Reimbursement
from backend.reimbursements.repository import reimbursement_repository
from backend.appointments.repository import appointment_repository
from backend.common.exceptions import AppException, ForbiddenError
from backend.common.feature_flags import is_feature_enabled
from backend.common.db import db

logger = logging.getLogger(__name__)

AUTO_APPROVE_THRESHOLD = 100.0


def submit_claim(member_id: int, appointment_id: int, amount: float, 
                 receipt_url: str, description: str = None) -> Reimbursement:
    """Submit a reimbursement claim."""
    logger.info(f"Submitting claim for member {member_id}, appointment {appointment_id}")

    # Validate appointment
    appointment = appointment_repository.find_by_id(appointment_id)
    if not appointment:
        raise AppException("Appointment not found")
    
    if appointment.member_id != member_id:
        raise ForbiddenError("You can only claim reimbursement for your own appointments")

    if appointment.status != "COMPLETED":
        raise AppException("Can only claim reimbursement for completed appointments")

    # Check for existing claim
    existing = reimbursement_repository.find_by_appointment_id(appointment_id)
    if existing:
        raise AppException("Reimbursement already submitted for this appointment")

    # Auto-approve small claims if feature enabled
    status = "PENDING"
    if is_feature_enabled("auto_approve_small_claims") and amount <= AUTO_APPROVE_THRESHOLD:
        status = "APPROVED"
        logger.info(f"Auto-approving claim under ${AUTO_APPROVE_THRESHOLD}")

    reimbursement = reimbursement_repository.create(
        member_id=member_id,
        appointment_id=appointment_id,
        amount=amount,
        receipt_url=receipt_url,
        description=description,
        status=status
    )
    db.session.commit()

    logger.info(f"Claim submitted with id: {reimbursement.id}, status: {status}")
    return reimbursement


def get_member_claims(member_id: int) -> list[Reimbursement]:
    """Get all claims for a member."""
    return reimbursement_repository.find_by_member_id(member_id)


def get_all_claims() -> list[Reimbursement]:
    """Get all claims (admin only)."""
    return reimbursement_repository.get_all()


def get_pending_claims() -> list[Reimbursement]:
    """Get all pending claims (admin only)."""
    return reimbursement_repository.get_pending()


def approve_claim(reimbursement_id: int, admin_notes: str = None) -> Reimbursement:
    """Approve a reimbursement claim (admin only)."""
    logger.info(f"Approving claim {reimbursement_id}")

    reimbursement = reimbursement_repository.find_by_id(reimbursement_id)
    if not reimbursement:
        raise AppException("Reimbursement not found")

    if reimbursement.status != "PENDING":
        raise AppException("Can only approve pending claims")

    reimbursement.status = "APPROVED"
    reimbursement.admin_notes = admin_notes
    db.session.commit()

    logger.info(f"Claim {reimbursement_id} approved")
    return reimbursement


def reject_claim(reimbursement_id: int, admin_notes: str = None) -> Reimbursement:
    """Reject a reimbursement claim (admin only)."""
    logger.info(f"Rejecting claim {reimbursement_id}")

    reimbursement = reimbursement_repository.find_by_id(reimbursement_id)
    if not reimbursement:
        raise AppException("Reimbursement not found")

    if reimbursement.status != "PENDING":
        raise AppException("Can only reject pending claims")

    reimbursement.status = "REJECTED"
    reimbursement.admin_notes = admin_notes
    db.session.commit()

    logger.info(f"Claim {reimbursement_id} rejected")
    return reimbursement
