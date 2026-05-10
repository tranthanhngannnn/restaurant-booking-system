from backend.core.extensions import db

class Reservation(db.Model):
    __tablename__ = "Reservations"

    ReservationID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.String(100), db.ForeignKey('users.UserID'), nullable=True)
    CustomerName = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(11), nullable=False)
    RestaurantID = db.Column(
        db.Integer,
        db.ForeignKey("Restaurant.RestaurantID"))
    TableID = db.Column(
        db.Integer,
        db.ForeignKey("RestaurantTables.TableID"))

    BookingDate = db.Column(db.Date, nullable=False)
    BookingTime = db.Column(db.Time, nullable=False)
    GuestCount = db.Column(db.Integer, nullable=False)
    Deposit = db.Column(db.Float, nullable=False)

    Note = db.Column(db.String(300))
    Status = db.Column(db.String(50))
    # relationship
    restaurant = db.relationship("Restaurant", backref="reservations")
    table = db.relationship("Tables", backref="reservations")
    user = db.relationship("User", backref="reservations")
