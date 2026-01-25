from marshmallow import Schema, fields, validate


class DoctorCreateSchema(Schema):
    """Schema for creating a doctor."""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)


class DoctorAssignSchema(Schema):
    """Schema for assigning doctor to department."""
    doctor_id = fields.Int(required=True)
    department_id = fields.Int(required=True)


class DoctorResponseSchema(Schema):
    """Schema for doctor response."""
    id = fields.Int()
    name = fields.Str()
    email = fields.Email()
    department = fields.Str(allow_none=True)
