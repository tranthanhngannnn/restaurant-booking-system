from backend.core.extensions import db


class Table(db.Model):
    __tablename__ = "RestaurantTables"

    TableID = db.Column(db.Integer, primary_key=True)
    RestaurantID = db.Column(
        db.Integer,
        db.ForeignKey("Restaurant.RestaurantID"))
    TableNumber = db.Column(db.String(10))
    Capacity = db.Column(db.Integer)
    Status = db.Column(db.String(50))

    restaurant = db.relationship("Restaurant", backref="tables")
