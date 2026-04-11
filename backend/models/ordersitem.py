from core.extensions import db

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    name = db.Column(db.String(100))
    price = db.Column(db.Integer)
    quantity = db.Column(db.Integer)