from marshmallow import Schema, fields, validate
from backend.common.enums import UserRole


class RegisterSchema(Schema):
    """Schema for user registration. Role is NOT allowed here - all users start as MEMBER."""
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    # Role removed - users cannot choose their role on registration


class LoginSchema(Schema):
    """Schema for user login."""
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class RoleAssignmentSchema(Schema):
    """Schema for admin to assign roles to users."""
    role = fields.Str(
        required=True,
        validate=validate.OneOf([role.value for role in UserRole])
    )
