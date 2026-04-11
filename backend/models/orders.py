from core.extensions import db

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('table.id'))
    status = db.Column(db.String(20), default='active')