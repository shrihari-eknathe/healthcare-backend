from marshmallow import Schema, fields, validate


class AppointmentCreateSchema(Schema):
    """Schema for booking an appointment."""
    availability_id = fields.Int(required=True)


class AppointmentResponseSchema(Schema):
    """Schema for appointment response."""
    id = fields.Int()
    member_id = fields.Int()
    doctor_id = fields.Int()
    date = fields.Date()
    start_time = fields.Time()
    end_time = fields.Time()
    status = fields.Str()


class AppointmentCancelSchema(Schema):
    """Schema for cancelling appointment."""
    reason = fields.Str(required=False)
