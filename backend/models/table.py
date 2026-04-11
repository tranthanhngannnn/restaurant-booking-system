from core.extensions import db

class Table(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    seats = db.Column(db.Integer)
    status = db.Column(db.String(20), default="available")
    capacity = db.Column(db.Integer)


    bookings = db.relationship('Booking', backref='table', lazy=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('Restaurant.RestaurantID'), nullable=False)
