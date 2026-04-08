from backend.core.extensions import db

class Food(db.Model):
    __tablename__ = "Food"

    FoodID = db.Column(db.String(8), primary_key=True)
    FoodName = db.Column(db.String(100))

    RestaurantID = db.Column(
        db.Integer,
        db.ForeignKey("Restaurant.RestaurantID")
    )

    Price = db.Column(db.Float)
    Description = db.Column(db.String(255))
    Image = db.Column(db.String(255))
    restaurant = db.relationship("Restaurant", backref="foods")