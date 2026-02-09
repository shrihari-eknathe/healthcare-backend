import logging
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError

from backend.common.rbac import require_roles
from backend.common.exceptions import AppException
from backend.common.feature_flags import require_feature
from backend.reimbursements.schemas import ReimbursementCreateSchema, ReimbursementReviewSchema
from backend.reimbursements.service import (
    submit_claim,
    get_member_claims,
    get_all_claims,
    get_pending_claims,
    approve_claim,
    reject_claim
)

logger = logging.getLogger(__name__)

reimbursements_bp = Blueprint("reimbursements", __name__, url_prefix="/reimbursements")


@reimbursements_bp.route("", methods=["POST"])
@require_feature("reimbursement_module", "Reimbursement feature is not available")
@require_roles("MEMBER")
def submit_claim_api():
    """Submit a reimbursement claim (member only)."""
    logger.info("Received request to submit claim")

    member_id = get_jwt_identity()

    schema = ReimbursementCreateSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        logger.warning(f"Validation error: {err.messages}")
        raise AppException(str(err.messages))

    reimbursement = submit_claim(
        member_id=member_id,
        appointment_id=data["appointment_id"],
        amount=data["amount"],
        receipt_url=data["receipt_url"],
        description=data.get("description")
    )

    logger.info(f"Claim submitted: {reimbursement.id}")
    return {
        "id": reimbursement.id,
        "appointment_id": reimbursement.appointment_id,
        "amount": reimbursement.amount,
        "receipt_url": reimbursement.receipt_url,
        "status": reimbursement.status,
        "created_at": str(reimbursement.created_at)
    }, 201


@reimbursements_bp.route("/my", methods=["GET"])
@require_feature("reimbursement_module", "Reimbursement feature is not available")
@require_roles("MEMBER")
def get_my_claims_api():
    """Get logged-in member's claims."""
    logger.info("Received request to get own claims")

    member_id = get_jwt_identity()
    claims = get_member_claims(member_id)

    return [
        {
            "id": c.id,
            "appointment_id": c.appointment_id,
            "amount": c.amount,
            "receipt_url": c.receipt_url,
            "status": c.status,
            "admin_notes": c.admin_notes,
            "created_at": str(c.created_at)
        }
        for c in claims
    ]


@reimbursements_bp.route("", methods=["GET"])
@require_feature("reimbursement_module", "Reimbursement feature is not available")
@require_roles("ADMIN")
def get_all_claims_api():
    """Get all claims (admin only)."""
    logger.info("Received request to get all claims")

    claims = get_all_claims()

    return [
        {
            "id": c.id,
            "member_id": c.member_id,
            "appointment_id": c.appointment_id,
            "amount": c.amount,
            "receipt_url": c.receipt_url,
            "status": c.status,
            "description": c.description,
            "admin_notes": c.admin_notes,
            "created_at": str(c.created_at)
        }
        for c in claims
    ]


@reimbursements_bp.route("/pending", methods=["GET"])
@require_feature("reimbursement_module", "Reimbursement feature is not available")
@require_roles("ADMIN")
def get_pending_claims_api():
    """Get pending claims (admin only)."""
    logger.info("Received request to get pending claims")

    claims = get_pending_claims()

    return [
        {
            "id": c.id,
            "member_id": c.member_id,
            "appointment_id": c.appointment_id,
            "amount": c.amount,
            "receipt_url": c.receipt_url,
            "description": c.description,
            "created_at": str(c.created_at)
        }
        for c in claims
    ]


@reimbursements_bp.route("/<int:reimbursement_id>/approve", methods=["PATCH"])
@require_feature("reimbursement_module", "Reimbursement feature is not available")
@require_roles("ADMIN")
def approve_claim_api(reimbursement_id):
    """Approve a claim (admin only)."""
    logger.info(f"Received request to approve claim {reimbursement_id}")

    schema = ReimbursementReviewSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        logger.warning(f"Validation error: {err.messages}")
        raise AppException(str(err.messages))

    reimbursement = approve_claim(reimbursement_id, data.get("admin_notes"))

    logger.info(f"Claim {reimbursement_id} approved")
    return {
        "id": reimbursement.id,
        "status": reimbursement.status,
        "admin_notes": reimbursement.admin_notes
    }


@reimbursements_bp.route("/<int:reimbursement_id>/reject", methods=["PATCH"])
@require_feature("reimbursement_module", "Reimbursement feature is not available")
@require_roles("ADMIN")
def reject_claim_api(reimbursement_id):
    """Reject a claim (admin only)."""
    logger.info(f"Received request to reject claim {reimbursement_id}")

    schema = ReimbursementReviewSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        logger.warning(f"Validation error: {err.messages}")
        raise AppException(str(err.messages))

    reimbursement = reject_claim(reimbursement_id, data.get("admin_notes"))

    logger.info(f"Claim {reimbursement_id} rejected")
    return {
        "id": reimbursement.id,
        "status": reimbursement.status,
        "admin_notes": reimbursement.admin_notes
    }
