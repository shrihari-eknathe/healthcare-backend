from marshmallow import Schema, fields, validate


class DepartmentCreateSchema(Schema):
    """Schema for creating a department."""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))


class DepartmentResponseSchema(Schema):
    """Schema for department response."""
    id = fields.Int()
    name = fields.Str()
