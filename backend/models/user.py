from backend.core.extensions import db

class User(db.Model):
    __tablename__ = "Users"

    UserID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50), nullable=False)
    Phone = db.Column(db.String(11))
    Email = db.Column(db.String(90))

    # ⚠️ DB chỉ 50 ký tự → OK cho hash ngắn
    Password = db.Column(db.String(255), nullable=False)

    Role = db.Column(db.String(50))