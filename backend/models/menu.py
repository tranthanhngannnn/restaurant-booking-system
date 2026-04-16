from core.extensions import db


class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    image = db.Column(db.String(255))
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    visible = db.Column(db.Boolean, default=True)
    RestaurantID = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default='active')


restaurant = db.relationship("Restaurant", backref="foods")
