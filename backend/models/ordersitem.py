from core.extensions import db
from models.menu import Menu

class OrderItem(db.Model):
    __tablename__ = "OrderItems"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.id'))
    food_id = db.Column(
        db.Integer,
        db.ForeignKey("Menu.id"),
        nullable=False
    )
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    
    db.relationship(Menu, backref="OrderItems")

