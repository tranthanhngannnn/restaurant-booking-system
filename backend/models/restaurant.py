from backend.core.extensions import db

class Restaurant(db.Model):
    __tablename__ = "Restaurant"

    RestaurantID = db.Column(db.Integer, primary_key=True)
    RestaurantName = db.Column(db.String(100))
    Address = db.Column(db.String(200))
    CuisineID = db.Column(db.Integer)
    Phone = db.Column(db.String(11))
    Email = db.Column(db.String(100))
    Opentime = db.Column(db.Time)
    Closetime = db.Column(db.Time)







