from core.extensions import db

class Payment(db.Model):
    __tablename__ = "Payments"
    PaymentID = db.Column(db.Integer, primary_key=True)
    ReservationID = db.Column(
        db.Integer,
        db.ForeignKey("Reservations.ReservationID"))
    Amounts = db.Column(db.Float)
    Status = db.Column(db.String(50))
    PaymentMethod = db.Column(db.String(50))
    CreatedAt = db.Column(db.DateTime)

    reservation = db.relationship("Reservation", backref="payments")