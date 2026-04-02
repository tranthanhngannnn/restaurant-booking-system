from core.extensions import db

class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    seats = db.Column(db.Integer)
    status = db.Column(db.String(20), default="available")

