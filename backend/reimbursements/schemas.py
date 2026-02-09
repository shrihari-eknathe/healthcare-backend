from marshmallow import Schema, fields, validate


class ReimbursementCreateSchema(Schema):
    """Schema for creating a reimbursement claim."""
    appointment_id = fields.Int(required=True)
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    receipt_url = fields.Str(required=True, validate=validate.Length(min=5, max=500))
    description = fields.Str(required=False, validate=validate.Length(max=500))


class ReimbursementReviewSchema(Schema):
    """Schema for admin review of reimbursement."""
    admin_notes = fields.Str(required=False, validate=validate.Length(max=500))
