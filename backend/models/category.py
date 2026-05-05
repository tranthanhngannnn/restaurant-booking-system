from backend.core.extensions import db

class Category(db.Model):
    __tablename__ = "Category"

    CategoryID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CategoryName = db.Column(db.String(100))