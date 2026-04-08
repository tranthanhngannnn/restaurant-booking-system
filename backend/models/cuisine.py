from core.extensions import db


class Cuisine(db.Model):
    __tablename__ = 'Cuisine'

    CuisineID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CuisineName = db.Column(db.String(100), nullable=False, unique=True)
    Status = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<Cuisine {self.CuisineName}>'