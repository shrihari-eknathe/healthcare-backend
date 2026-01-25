from marshmallow import Schema, fields, validate
from backend.common.enums import UserRole


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    role = fields.Str(
        load_default=UserRole.MEMBER.value,
        validate=validate.OneOf([role.value for role in UserRole])
    )


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
