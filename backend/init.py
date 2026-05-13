from core import create_app
from core.extensions import db

# IMPORT TẤT CẢ MODEL
from models.user import User
from models.restaurant import Restaurant
from models.review import Review
from models.table import Table
from models.booking import Reservation
from models.food import Food
from models.payment import Payment
from models.cuisine import Cuisine
from models.confirmbooking import Booking
from models.orders import Order
from models.ordersitem import OrderItem
from models.menu import Menu

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    print(" DB OK - tạo toàn bộ bảng thành công!")