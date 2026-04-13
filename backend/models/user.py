from core.extensions import db
from flask_login import UserMixin
from werkzeug.security import check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = "users"
    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Username = db.Column(db.String(50), nullable=False, unique=True)
    Password = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(100), nullable=True)
    Phone = db.Column(db.String(20), nullable=True)
    Role = db.Column(db.String(50), nullable=False)

    def check_password(self, password):
        return self.Password == password 

    def get_id(self):
        return str(self.UserID)