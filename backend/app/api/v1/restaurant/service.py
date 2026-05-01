from models.restaurant import Restaurant
from core.extensions import db
from datetime import datetime, timedelta
from models.food import Food
from models.menu import Menu
from models.tables import Tables
from models.booking import Reservation

from models.ordersitem import OrderItem
from models.food import Food
from schemas.menu_schema import MenuSchema
from schemas.table_schema import TableSchema
from schemas.booking_schema import BookingSchema
import os
from werkzeug.utils import secure_filename

menu_schema = MenuSchema()
menus_schema = MenuSchema(many=True)

table_schema = TableSchema()
tables_schema = TableSchema(many=True)

booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)


#DÀNH CHO MENU NHÂN VIÊN
def get_menu_res_admin(res_id):
    try:
        from image import MENU_DATA #tránh lỗi vòng lặp lúc khởi động
    except ImportError:
        from backend.image import MENU_DATA

    menus = Food.query.filter_by(RestaurantID=res_id).all() #LẤY ĐÚNG MENU CỦA NHÀ HÀNG ĐÓ

    result = []
    for m in menus:
        # 1. Mặc định lấy ảnh từ DB (nếu có)
        image_url = m.Image_URL if m.Image_URL else ""

        if not image_url:
            for item in MENU_DATA:
                if item['name'] == m.FoodName:  # So khớp theo tên món ăn
                    image_url = item['image']
                    break

        result.append({
            "id": m.FoodID,
            "name": m.FoodName,
            "price": float(m.Price) if m.Price else 0,
            "image": image_url,
            "restaurant_id": m.RestaurantID,
            "Visible": m.Visible
        })
    return result

#DÀNH CHO ORDER MÓN
def get_res_menu(restaurant_id):
    menus = Food.query.filter_by(RestaurantID=restaurant_id, Visible=True).all()

    try:
        from image import MENU_DATA
    except ImportError:
        from backend.image import MENU_DATA

    result = []
    for m in menus:
        # 1. Khai báo image_url ngay đầu vòng lặp cho mỗi món
        image_url = m.Image_URL if hasattr(m, 'Image_URL') and m.Image_URL else ""

        # 2. Nếu DB trống, đi tìm trong MENU_DATA (vẫn nằm TRONG vòng lặp for m)
        if not image_url:
            for item in MENU_DATA:
                if item['name'] == m.FoodName:
                    image_url = item['image']
                    break

        # 3. Add món đó vào list result
        result.append({
            "id": m.FoodID,
            "name": m.FoodName,
            "price": float(m.Price) if m.Price else 0,
            "image": image_url,
            "category": m.Category if hasattr(m, 'Category') else "",
            "description": m.Description if hasattr(m, 'Description') else "",
            "Visible": m.Visible
        })
    return result




def get_tables(res_id):
    all_tables = Tables.query.filter_by(RestaurantID=res_id).all()
    result = []

    for t in all_tables:
        booking = Reservation.query.filter_by(
            TableID=t.TableID,
            Status="Confirmed"
        ).order_by(Reservation.BookingTime.desc()).first()

        result.append({
            "id": t.TableID,
            "name": t.TableNumber,
            "capacity": t.Capacity,
            "status": t.Status,
            "customer_name": booking.CustomerName if booking else None,
            "customer_count": booking.GuestCount if booking else 0
        })

    return result


def create_table(data, res_id):
    existing = Tables.query.filter_by(TableNumber=data.get('TableNumber')).first()
    if existing:
        return {"error": "Table already exists"}

    table = Tables(
        TableNumber=data.get('TableNumber'),
        Capacity=int(data.get('Capacity', 4) or 4),
        Status=data.get('Status', 'Available'),
        RestaurantID=res_id
    )
    db.session.add(table)
    db.session.commit()
    return {
        "message": "Table created",
        "data": table_schema.dump(table)
    }


def create_booking(data):
    try:
        booking_date = datetime.strptime(data['BookingDate'], "%Y-%m-%d").date()
        booking_time = datetime.strptime(data['BookingTime'], "%H:%M").time()
    except:
        return {"error": "Wrong datetime format"}

    table = Tables.query.get(data['TableID'])
    if not table:
        return {"error": "Table not found"}

    booking = Reservation(
        TableID=data['TableID'],
        CustomerName=data['CustomerName'],
        phone=data.get('phone', ''),
        GuestCount=data.get('GuestCount', 1),
        BookingDate=booking_date,
        BookingTime=booking_time,
        RestaurantID=data.get('RestaurantID'),
        Deposit=data.get('Deposit', 0),
        Status="Pending"
    )

    db.session.add(booking)
    table.Status = "Reserved"
    db.session.commit()

    return {
        "message": "Booking created",
        "data": booking_schema.dump(booking)
    }


def get_bookings(res_id):
    query = Reservation.query.filter_by(RestaurantID=res_id).order_by(Reservation.BookingTime.desc()).all()
    return bookings_schema.dump(query)


def confirm_booking(id):
    booking = Reservation.query.get(id)
    if not booking:
        return {"error": "Booking not found"}
    booking.Status = "Confirmed"
    table = Tables.query.get(booking.TableID)
    if table:
        table.Status = "Reserved"
    db.session.commit()
    return booking_schema.dump(booking)


def reject_booking(id):
    b = Reservation.query.get(id)
    if not b: return {"error": "Not found"}
    b.Status = "Rejected"
    db.session.commit()
    return booking_schema.dump(b)


def update_table_status_service(id, data):
    table = Tables.query.get(id)
    if not table:
        return {"error": "Table not found"}
    table.Status = data.get("Status", table.Status)
    db.session.commit()
    return table_schema.dump(table)


def delete_booking(id):
    booking = Reservation.query.get(id)
    if not booking: return {"error": "Not found"}
    db.session.delete(booking)
    db.session.commit()
    return {"msg": "Deleted"}


def get_booking_by_table_service(id):
    bookings = Reservation.query.filter_by(TableID=id).all()
    return bookings_schema.dump(bookings)

def create_food(data, res_id):
    try:
        import random
        import string
        
        # Tạo FoodID ngẫu nhiên 5 ký tự (vì trong model là String(5))
        food_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        while Food.query.get(food_id):
            food_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

        food = Food(
            FoodID=food_id,
            FoodName=data.get("name"),
            Price=data.get("price"),
            Image_URL=data.get("image"),
            Category=data.get("category"),
            RestaurantID=res_id,
            Visible=True
        )

        db.session.add(food)
        db.session.commit()

        print(f"ĐÃ THÊM MÓN: {food.FoodName} (ID: {food.FoodID})")

        return {
            "msg": "Thêm thành công",
            "id": food.FoodID
        }

    except Exception as e:
        db.session.rollback()
        print("LỖI DB KHI THÊM MÓN:", e)
        return {"error": str(e)}


def delete_food(id):
    food = Food.query.get(id)
    if not food:
        return {"error": "Food not found"}

    db.session.delete(food)
    db.session.commit()
    return {"msg": "Deleted"}

def update_food(id, data):
    food = Food.query.get(id)

    if not food:
        return {"error": "Food not found"}

    # cập nhật dữ liệu (sử dụng đúng tên field của model Food)
    if data.get("name"):
        food.FoodName = data.get("name")
    
    if data.get("price"):
        food.Price = data.get("price")
        
    if data.get("category"):
        food.Category = data.get("category")

    # Xử lý hình ảnh
    image_file = data.get("image_file")
    if image_file and image_file.filename != '':
        filename = secure_filename(image_file.filename)
        # Đường dẫn lưu file (Dựa vào cấu trúc thư mục của bạn)
        # backend/app/api/v1/restaurant/service.py -> frontend/static/images
        upload_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../frontend/static/images"))
        
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
            
        file_path = os.path.join(upload_path, filename)
        image_file.save(file_path)
        
        # Lưu đường dẫn tương đối để frontend hiển thị
        food.Image_URL = f"/static/images/{filename}"
    elif data.get("image"):
        # Nếu gửi link ảnh trực tiếp (như cũ)
        food.Image_URL = data.get("image")

    # Nếu không có image_file và không có data.get("image"), 
    # thì food.Image_URL vẫn giữ nguyên giá trị cũ.

    db.session.commit()

    return {
        "msg": "Updated",
        "data": {
            "id": food.FoodID,
            "name": food.FoodName,
            "price": food.Price,
            "image": food.Image_URL,
            "category": food.Category
        }
    }


class RestaurantService:
    @staticmethod
    def create(data, is_admin=False):
        status_val = "Đang hoạt động" if is_admin else "Đang chờ duyệt"
        restaurant_name = data.get('RestaurantName')
        if not restaurant_name:
            return {"message": "Tên nhà hàng không được để trống"}, 400

        new_res = Restaurant(
            RestaurantName=restaurant_name,
            Address=data.get('Address'),
            Phone=data.get('Phone'),
            Email=data.get('Email'),
            Opentime=data.get('Opentime'),
            Closetime=data.get('Closetime'),
            description=data.get('description'),
            UserID=data.get('UserID'),
            CuisineID=data.get('CuisineID'),
            status=status_val
        )
        try:
            db.session.add(new_res)
            db.session.commit()
            return {"message": f"Tạo thành công! Trạng thái hiện tại: {status_val}"}, 201
        except Exception as e:
            db.session.rollback()
            return {"message": f"Lỗi hệ thống: {str(e)}"}, 500
