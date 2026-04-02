from marshmallow import Schema, fields

class TableSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    seats = fields.Int()
    status = fields.Str()