from marshmallow import Schema, fields, validate

class UserSignupSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    name = fields.Str(required=True, validate=validate.Length(min=2))

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UrlScanSchema(Schema):
    url = fields.Url(required=True, schemes={'http', 'https'})

class OtpVerificationSchema(Schema):
    email = fields.Email(required=True)
    otp = fields.Str(required=True, validate=validate.Length(equal=6))
