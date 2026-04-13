from core.extensions import db

class OrderItem(db.Model):
    __tablename__ = "OrderItems"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    food_id = db.Column(
        db.Integer,
        db.ForeignKey("Menu.MenuID"),
        nullable=False
    )
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    
    food = db.relationship("Menu")
