from backend.models.menu import Menu
from backend.models.tables import Tables
from backend.models.booking import Reservation
from backend.core.extensions import db
from datetime import datetime, timedelta
from backend.models.payment import Payment
from backend.models.restaurant import Restaurant
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import or_
from sqlalchemy import func
import re
import unicodedata

#  SEARCH
def normalize_text(text):
    if not text:
        return ""
    text = text.lower()
    # bỏ dấu tiếng Việt
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    # bỏ ký tự đặc biệt (# , . ...)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    # bỏ khoảng trắng dư
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def search_restaurant(address, cuisine):
    query = Restaurant.query

    if address:
        keyword = normalize_text(address).replace(" ", "")

        query = query.filter(
            or_(
                func.replace(func.lower(Restaurant.RestaurantName), " ", "").ilike(f"%{keyword}%"),
                func.replace(func.lower(Restaurant.Address), " ", "").ilike(f"%{keyword}%")
            )
        )

    if cuisine:
        query = query.filter(Restaurant.CuisineID == int(cuisine))

    restaurants = query.all()

    result = []
    for r in restaurants:
        empty_tables = Tables.query.filter_by(
            RestaurantID=r.RestaurantID,
            Status="Trống"
        ).count()

        result.append({
            "RestaurantID": r.RestaurantID,
            "RestaurantName": r.RestaurantName,
            "Address": r.Address,
            "Phone": r.Phone,
            "Available": "Còn bàn" if empty_tables > 0 else "Hết bàn"
        })

    return result


# ================== MENU ==================
def get_menu(restaurant_id):
    foods = Menu.query.filter_by(RestaurantID=restaurant_id).all()

    return [{
        "FoodName": f.FoodName,
        "Price": float(f.Price),
        "Description": f.Description,
        "Image": f.Image
    } for f in foods]


# ================== CHECK TABLE ==================
def check_table(restaurant_id, date, time, people):
    cancel_expired_bookings()
    people = int(people)
    booking_date = datetime.strptime(date, "%Y-%m-%d").date()
    booking_time = datetime.strptime(time, "%H:%M").time()
    booking_dt = datetime.combine(booking_date, booking_time)
    start = (booking_dt - timedelta(minutes=30)).time()
    end = (booking_dt + timedelta(minutes=30)).time()
    tables = Tables.query.filter_by(RestaurantID=restaurant_id).all()
    result = []

    for t in tables:
        if t.Capacity >= people:
            exist = Reservation.query.filter(
                Reservation.TableID == t.TableID,
                Reservation.BookingDate == booking_date,
                Reservation.BookingTime.between(start, end),
                Reservation.Status.in_(["Pending", "Confirmed"])
            ).first()

            if not exist:
                result.append({
                    "TableID": t.TableID,
                    "Capacity": t.Capacity
                })

    return result


# ================== CREATE BOOKING ==================
def create_booking(data):
    # 1. Dọn dẹp booking cũ
    cancel_expired_bookings()

    # 2. Rút trích tất cả dữ liệu từ cục 'data' frontend gửi lên
    try:
        customer_name = data.get("name")
        phone = data.get("phone")
        restaurant_id = int(data.get("restaurant_id"))
        table_id = int(data.get("table_id"))
        people_str = int(data.get("people"))
        note = data.get("note", "")

        booking_date = datetime.strptime(data.get("date"), "%Y-%m-%d").date()
        booking_time = datetime.strptime(data.get("time"), "%H:%M").time()
    except:
        return {"error": "Dữ liệu không hợp lệ"}

    # 3. Bẫy lỗi dữ liệu trống
    if not customer_name:
        return {"error": "Thiếu tên khách"}
    if not phone:
        return {"error": "Thiếu số điện thoại"}
    table = Tables.query.get(table_id)
    if not table or table.RestaurantID != restaurant_id:
        return {"error": "Bàn không hợp lệ"}
    if not table_id or not restaurant_id:
        return {"error": "Thiếu thông tin nhà hàng hoặc bàn"}
    # Ép kiểu dữ liệu để so sánh trong SQL
    table_id = int(table_id)
    guest_count = int(people_str)
    booking_dt = datetime.combine(booking_date, booking_time)
    start = (booking_dt - timedelta(minutes=30)).time()
    end = (booking_dt + timedelta(minutes=30)).time()
    # 4. Chống double booking
    exist = Reservation.query.filter(
        Reservation.TableID == table_id,
        Reservation.BookingDate == booking_date,
        Reservation.BookingTime.between(start, end),
        Reservation.Status.in_(["Pending", "Confirmed"])
    ).first()

    if exist:
        return {"error": "Bàn đã được đặt trong khung giờ này"}

    # 5. Tính tiền cọc ở backend
    deposit = calculate_deposit(guest_count)

    # 6. Xử lý ID cho khách Login & Khách vãng lai
    user_id = get_jwt_identity()  # không có token nó ra None

    if user_id:
        user_id = str(user_id)  # Ép kiểu string cho đúng Model
    else:
        user_id = None  # Khách vãng lai, chấp nhận cột UserID bị NULL

    # 7. Tạo đối tượng Reservation
    reservation = Reservation(
        UserID=user_id,
        CustomerName=customer_name,
        phone=phone,
        RestaurantID=int(restaurant_id),
        TableID=table_id,
        BookingDate=booking_date,
        BookingTime=booking_time,
        GuestCount=guest_count,
        Note=note,
        Deposit=deposit,
        Status="Pending"
    )

    # 8. Lưu xuống Database
    try:
        db.session.add(reservation)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Lỗi SQL lúc lưu đặt bàn:", str(e))  # In ra terminal để debug
        return {"error": "Đặt bàn thất bại do lỗi hệ thống"}

    # 9. Tạo QR và trả về kết quả
    qr = generate_vietqr(reservation.Deposit, reservation.ReservationID)

    return {
        "reservation_id": reservation.ReservationID,
        "qr": qr,
        "deposit": deposit
    }


def get_all_restaurants():
    # Lấy hết dữ liệu từ bảng Restaurant
    restaurants = Restaurant.query.all()
    result = []
    for r in restaurants:
        result.append({
            "RestaurantID": r.RestaurantID,
            "RestaurantName": r.RestaurantName,
            "Opentime": str(r.Opentime),
            "Closetime": str(r.Closetime)
        })
    return result


def get_restaurant_by_id(restaurant_id):
    r = Restaurant.query.get(restaurant_id)
    if not r:
        return {}
    return {
        "RestaurantID": r.RestaurantID,
        "RestaurantName": r.RestaurantName,
        "Opentime": str(r.Opentime),
        "Closetime": str(r.Closetime)
    }


# ================== PAYMENT ==================
def calculate_deposit(people):
    return people * 50000  # 50k/người


def confirm_payment(reservation_id, amount):
    booking = Reservation.query.get(reservation_id)

    if not booking:
        return {"error": "Not found"}

    if booking.Status != "Pending":
        return {"error": "Booking already processed"}

    # check số tiền
    if float(amount) != float(booking.Deposit):
        return {"error": "Sai số tiền"}

    payment = Payment(
        ReservationID=reservation_id,
        Amount=float(amount),
        Status="Paid",
        PaymentMethod="QR",
        CreatedAt=datetime.now()
    )

    db.session.add(payment)
    db.session.commit()

    return {"message": "Payment success"}


# ================== QR CODE (VIETQR) ==================
def generate_vietqr(amount, reservation_id):
    bank_id = "970422"  # MB Bank
    account_no = "123456789"
    account_name = "NGUYEN VAN A"

    description = f"DATBAN_{reservation_id}"

    return f"https://img.vietqr.io/image/{bank_id}-{account_no}-compact2.png?amount={amount}&addInfo={description}&accountName={account_name}"


# ================== AUTO CANCEL ==================
def cancel_expired_bookings():
    now = datetime.now()
    bookings = Reservation.query.filter_by(Status="Pending").all()

    for b in bookings:
        booking_datetime = datetime.combine(b.BookingDate, b.BookingTime)

        if booking_datetime < now + timedelta(minutes=2):
            b.Status = "Cancelled"
    db.session.commit()


# ================== HISTORY ==================
def get_history(user_id, keyword):
    if not user_id:
        return []

    # Chỉ lấy các booking thuộc về user đang đăng nhập
    query = db.session.query(
        Reservation,
        Restaurant.RestaurantName
    ).outerjoin(
        Restaurant, Reservation.RestaurantID == Restaurant.RestaurantID
    ).filter(
        Reservation.UserID == str(user_id)
    )

    # Nếu có keyword (tìm theo tên khách hoặc ID booking)
    if keyword:
        filters = [Reservation.CustomerName.ilike(f"%{keyword}%")]
        if keyword.isdigit():
            filters.append(Reservation.ReservationID == int(keyword))
        
        query = query.filter(or_(*filters))

    results = query.order_by(Reservation.ReservationID.desc()).all()


    result = []
    for r, restaurant_name in results:
        result.append({
            "ReservationID": r.ReservationID,
            "RestaurantName": restaurant_name,
            "RestaurantID": r.RestaurantID,
            "CustomerName": r.CustomerName,
            "BookingDate": str(r.BookingDate) if r.BookingDate else "",
            "BookingTime": str(r.BookingTime) if r.BookingTime else "",
            "GuestCount": r.GuestCount,
            "TableNumber": r.TableID,
            "Status": r.Status
        })

    return result
