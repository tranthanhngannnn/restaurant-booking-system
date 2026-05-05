from backend.core.extensions import db

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100))
    status = db.Column(db.String(20), default="pending")
    booking_time = db.Column(db.DateTime)
    people = db.Column(db.Integer)
    table_id = db.Column(db.Integer, db.ForeignKey('table.id'))




