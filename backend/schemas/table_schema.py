from marshmallow import Schema, fields, validates, ValidationError

class TableSchema(Schema):
    id = fields.Int(dump_only=True)

    name = fields.Str(required=True)
    seats = fields.Int(required=True)

    status = fields.Str(dump_only=True)

    restaurant_id = fields.Int(required=True)  # ✅ thêm

    #  validate số ghế
    @validates("seats")
    def validate_seats(self, value):
        if value <= 0:
            raise ValidationError("Số ghế phải > 0")
