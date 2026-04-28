from core.extensions import db
from models.menu import Menu

class OrderItem(db.Model):
    __tablename__ = "order_item"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    name = db.Column(db.String(100))
    food_id = db.Column(
        db.Integer,
        db.ForeignKey("menu.id"),
        nullable=False
    )

    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    
    db.relationship(Menu, backref="order_items")

