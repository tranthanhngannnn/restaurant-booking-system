from marshmallow import Schema, fields

class BookingSchema(Schema):
    id = fields.Int(dump_only=True)

    customer_name = fields.Str(required=True)
    status = fields.Str(dump_only=True)

    table_id = fields.Int(required=True)

    booking_time = fields.DateTime(
        required=True,
        format="%Y-%m-%d %H:%M"
    )
