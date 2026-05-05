from core.extensions import db


class Tables(db.Model):
    __tablename__ = "Table"
    TableID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    RestaurantID = db.Column(
        db.Integer,
        db.ForeignKey("Restaurant.RestaurantID"))
    TableNumber = db.Column(db.String(10))
    Capacity = db.Column(db.Integer)
    Status = db.Column(db.String(50))
    Seats = db.Column(db.Integer)
    restaurant = db.relationship("Restaurant", backref="tables")