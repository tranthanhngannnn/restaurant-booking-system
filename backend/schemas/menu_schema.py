from marshmallow import Schema, fields

class MenuSchema(Schema):
    id = fields.Int()
    name = fields.Str(required=True)
    price = fields.Float(required=True)
    description = fields.Str()
    image = fields.Str()
    category = fields.Str()

    restaurant_id = fields.Int(required=True)