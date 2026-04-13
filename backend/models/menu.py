from core.extensions import db

class Menu(db.Model):
    __tablename__ = "Menu"
    MenuID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FoodName = db.Column(db.String(100), nullable=False)
    Price = db.Column(db.Float, nullable=False)
    Description = db.Column(db.String(255))
    Image = db.Column(db.String(255))
    Category = db.Column(db.String(50))
    Visible = db.Column(db.Boolean, default=True)
    Status = db.Column(db.String(20), default='active')
    
    RestaurantID = db.Column(
        db.Integer,
        db.ForeignKey("Restaurant.RestaurantID")
    )

    restaurant = db.relationship("Restaurant", backref="foods")
