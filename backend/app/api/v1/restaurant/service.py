from models.restaurant import Restaurant
from core.extensions import db
from datetime import datetime, timedelta

from models.menu import Menu
from models.tables import Tables
from models.booking import Reservation
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
    food = Menu(
        FoodName=data.get('FoodName'),
        Price=data.get('Price'),
        Description=data.get('Description'),
        Image=data.get('Image'),
        Category=data.get('Category'),
        RestaurantID=data.get('RestaurantID')
    )
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
    all_tables = Tables.query.all()
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

def create_table(data):
    existing = Tables.query.filter_by(TableNumber=data.get('TableNumber')).first()
    if existing:
        return {"error": "Table already exists"}
    
    table = Tables(
        TableNumber=data.get('TableNumber'),
        Capacity=int(data.get('Capacity', 4) or 4),
        Status=data.get('Status', 'Available'),
        RestaurantID=data.get('RestaurantID')
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

def get_bookings():
    return bookings_schema.dump(Reservation.query.all())

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
