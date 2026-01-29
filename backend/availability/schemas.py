from marshmallow import Schema, fields, validate


class AvailabilityCreateSchema(Schema):
    """Schema for creating availability slot."""
    doctor_id = fields.Int(required=True)
    date = fields.Date(required=True)
    start_time = fields.Time(required=True)
    end_time = fields.Time(required=True)


class AvailabilityResponseSchema(Schema):
    """Schema for availability response."""
    id = fields.Int()
    doctor_id = fields.Int()
    date = fields.Date()
    start_time = fields.Time()
    end_time = fields.Time()
    is_booked = fields.Bool()
