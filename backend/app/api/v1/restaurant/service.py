from models.restaurant import Restaurant
from core.extensions import db
from datetime import datetime, timedelta

from models.menu import Menu
from models.table import Table
from models.confirmbooking import Booking
from models.orders import Order
from models.ordersitem import OrderItem

from schemas.menu_schema import MenuSchema
from schemas.table_schema import TableSchema
from schemas.booking_schema import BookingSchema

menu_schema = MenuSchema()
menus_schema = MenuSchema(many=True)

table_schema = TableSchema()
tables_schema = TableSchema(many=True)

booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)

def get_all_menu():
    return menus_schema.dump(Menu.query.all())

def create_food(data):
    errors = menu_schema.validate(data)
    if errors:
        return {"error": errors}

    food = Menu(**data)
    db.session.add(food)
    db.session.commit()
    return menu_schema.dump(food)

def delete_food(id):
    food = Menu.query.get(id)
    if not food:
        return {"error": "Food not found"}

    db.session.delete(food)
    db.session.commit()
    return {"msg": "Deleted"}

def get_tables():
    tables = Table.query.all()
    result = []

    for t in tables:
        booking = Booking.query.filter_by(
            table_id=t.id,
            status="confirmed"   # chỉ lấy bàn đã đặt
        ).order_by(Booking.booking_time.desc()).first()

        result.append({
            "id": t.id,
            "name": t.name,
            "capacity": t.capacity,
            "status": t.status,
            "customer_name": booking.customer_name if booking else None,
            "customer_count": booking.customer_count if booking else 0
        })

    return result

def create_table(data):

        # fix dữ liệu trước khi insert
        existing = Table.query.filter_by(name=data.get('name')).first()
        if existing:
            return {"error": "Table already exists"}
        if data.get('capacity') == '' or data.get('capacity') is None:
            data['capacity'] = 4
        else:
            data['capacity'] = int(data['capacity'])

        if data.get('seats') == '' or data.get('seats') is None:
            data['seats'] = data['capacity']
        else:
            data['seats'] = int(data['seats'])

        table = Table(**data)
        db.session.add(table)
        db.session.commit()
        return {
        "message": "Table created",
        "data": table_schema.dump(table)}

def create_booking(data):
    errors = booking_schema.validate(data)
    if errors:
        return {"error": errors}

    # parse datetime
    try:
        booking_time = datetime.strptime(
            data['booking_time'], "%Y-%m-%d %H:%M"
        )
    except:
        return {"error": "Wrong datetime format (YYYY-MM-DD HH:MM)"}

    # mặc định 2 tiếng
    duration = data.get("duration", 2)
    end_time = booking_time + timedelta(hours=duration)

    # check bàn tồn tại
    table = Table.query.get(data['table_id'])
    if not table:
        return {"error": "Table not found"}

    # ✅ check trùng thời gian (QUAN TRỌNG)
    existing = Booking.query.filter(
        Booking.table_id == data['table_id'],
        Booking.booking_time < end_time,
        Booking.end_time > booking_time
    ).first()

    if existing:
        return {"error": "Table already booked in this time"}

    # tạo booking
    booking = Booking(
        table_id=data['table_id'],
        customer_name=data['customer_name'],
        customer_count=data['customer_count'],
        booking_time=booking_time,
        end_time=end_time
    )

    db.session.add(booking)

    # ✅ cập nhật trạng thái bàn
    table.status = "reserved"

    db.session.commit()

    return {
        "message": "Booking created",
        "data": booking_schema.dump(booking)
    }

def get_bookings():
    return bookings_schema.dump(Booking.query.all())

def confirm_booking(id):
    booking = Booking.query.get(id)

    if not booking:
        return {"error": "Booking not found"}

    if booking.status == "confirmed":
        return {"error": "Already confirmed"}

    booking.status = "confirmed"

    table = Table.query.get(booking.table_id)
    if table:
        table.status = "reserved"

    db.session.commit()

    return booking_schema.dump(booking)

def reject_booking(id):
    b = Booking.query.get(id)
    b.status = "rejected"
    db.session.commit()
    return booking_schema.dump(b)

def update_table_status_service(id, data):
    table = Table.query.get(id)

    if not table:
        return {"error": "Table not found"}

    table.status = data.get("status", table.status)

    db.session.commit()
    return table_schema.dump(table)

def delete_booking(id):
    booking = Booking.query.get(id)

    if not booking:
        return {"error": "Booking not found"}

    db.session.delete(booking)
    db.session.commit()

    return {"msg": "Deleted"}


def get_booking_by_table_service(id):
    bookings = Booking.query.filter_by(table_id=id).all()
    return bookings_schema.dump(bookings)

class RestaurantService:
    @staticmethod
    def create(data, is_admin=False):
        # Kịch bản: Admin tạo thì Active luôn, Chủ Nhà Hàng tạo thì chờ duyệt
        status_val = "Đang hoạt động" if is_admin else "Đang chờ duyệt"

        # Kiểm tra tên nhà hàng không được để trống
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
            UserID=data.get('UserID'),  # ID của tài khoản chủ nhà hàng
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

