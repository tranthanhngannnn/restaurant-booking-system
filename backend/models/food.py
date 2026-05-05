from backend.core.extensions import db
from backend.models.category import Category
class Food(db.Model):
    __tablename__ = "Food"
    FoodID = db.Column(db.String(5), primary_key=True)
    FoodName = db.Column(db.String(100))

    RestaurantID = db.Column(
        db.Integer,
        db.ForeignKey("Restaurant.RestaurantID")
    )

    Price = db.Column(db.Float)
    Description = db.Column(db.String(255))
    Image_URL = db.Column("Image_URL",db.String(255))
    restaurant = db.relationship("Restaurant", backref="foods")
    Visible = db.Column(db.Boolean, default=True)
    CategoryID = db.Column(db.Integer, db.ForeignKey('Category.CategoryID'))
    category = db.relationship("Category")