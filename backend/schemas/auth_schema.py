from marshmallow import Schema, fields

class RegisterSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    role = fields.Str(required=True) # Truyền vào 'Admin', 'Restaurant', hoặc 'Customer'
    email = fields.Email()
    phone = fields.Str()
