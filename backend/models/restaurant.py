from core.extensions import db
from datetime import datetime


class Restaurant(db.Model):
    __tablename__ = 'Restaurant'

    RestaurantID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    RestaurantName = db.Column(db.String(100), nullable=False)
    Address = db.Column(db.String(200))
    Phone = db.Column(db.String(11))
    Email = db.Column(db.String(100))
    Opentime = db.Column(db.Time)
    Closetime = db.Column(db.Time)
    description = db.Column(db.String(500))
    status = db.Column(db.String(50), nullable=False, default='Pending')  # Mặc định là chờ duyệt

    # Khóa ngoại
    UserID = db.Column(db.Integer)  # ID của chủ nhà hàng
    CuisineID = db.Column(db.Integer, db.ForeignKey('Cuisine.CuisineID'))

    # Thiết lập relationship để lấy dữ liệu từ bảng Cuisine dễ dàng hơn
    cuisine = db.relationship('Cuisine', backref='restaurants')

    def __init__(self, RestaurantName, status='Đang chờ duyệt', Address=None, Phone=None,
                 Email=None, Opentime=None, Closetime=None, description=None,
                 UserID=None, CuisineID=None):
        self.RestaurantName = RestaurantName
        self.Address = Address
        self.Phone = Phone
        self.Email = Email
        self.Opentime = Opentime
        self.Closetime = Closetime
        self.description = description
        self.status = status
        self.UserID = UserID
        self.CuisineID = CuisineID

    def to_dict(self):
        return {
            'RestaurantID': self.RestaurantID,
            'RestaurantName': self.RestaurantName,
            'Address': self.Address,
            'Phone': self.Phone,
            'Email': self.Email,
            'Opentime': self.Opentime.strftime('%H:%M') if self.Opentime else None,
            'Closetime': self.Closetime.strftime('%H:%M') if self.Closetime else None,
            'description': self.description,
            'status': self.status,
            'UserID': self.UserID,
            'CuisineID': self.CuisineID
        }
