from backend.core.extensions import db

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('RestaurantTables.TableID'))
    status = db.Column(db.String(20), default='active')
