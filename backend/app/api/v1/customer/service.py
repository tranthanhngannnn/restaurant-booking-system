from backend.models.menu import Food
from backend.models.table import Table
from backend.models.booking import Reservation
from backend.core.extensions import db
from datetime import datetime, timedelta
from backend.models.payment import Payment
from backend.models.restaurant import Restaurant

# ================== SEARCH ==================
def search_restaurant(address, cuisine):
    query = Restaurant.query

    if address:
        query = query.filter(Restaurant.Address.ilike(f"%{address}%"))

    if cuisine:
        query = query.filter(Restaurant.CuisineID == int(cuisine))

    restaurants = query.all()

    result = []
    for r in restaurants:
        empty_tables = Table.query.filter_by(
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
    foods = Food.query.filter_by(RestaurantID=restaurant_id).all()

    return [{
        "FoodName": f.FoodName,
        "Price": float(f.Price),
        "Description": f.Description
    } for f in foods]


# ================== CHECK TABLE ==================
def check_table(restaurant_id, date, time, people):
    people = int(people)
    booking_date = datetime.strptime(date, "%Y-%m-%d").date()
    booking_time = datetime.strptime(time, "%H:%M").time()

    tables = Table.query.filter_by(RestaurantID=restaurant_id).all()
    result = []

    for t in tables:
        if t.Capacity >= people:
            exist = Reservation.query.filter(
                Reservation.TableID == t.TableID,
                Reservation.BookingDate == booking_date,
                Reservation.BookingTime == booking_time,
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
    cancel_expired_bookings()  # chuyển sang đây

    if not data.get("name"):
        return {"error": "Customer name is required"}

    # chống double booking
    exist = Reservation.query.filter(
        Reservation.TableID == int(data.get("table_id")),
        Reservation.BookingDate == data.get("date"),
        Reservation.BookingTime == data.get("time"),
        Reservation.Status.in_(["Pending", "Confirmed"])
    ).first()

    if exist:
        return {"error": "Bàn đã được đặt"}

    guest_count = int(data.get("people"))
    #  tính tiền cọc ở backend
    deposit = calculate_deposit(guest_count)

    reservation = Reservation(
        UserID=data.get("user_id") if data.get("user_id") else None,
        CustomerName=data.get("name"),
        phone=data.get("phone"),
        RestaurantID=int(data.get("restaurant_id")),
        TableID=int(data.get("table_id")),
        BookingDate=data.get("date"),
        BookingTime=data.get("time"),
        GuestCount=guest_count,
        Deposit=deposit,
        Status="Pending"
    )

    db.session.add(reservation)
    db.session.commit()

    qr = generate_vietqr(reservation.Deposit, reservation.ReservationID)

    return { "reservation_id": reservation.ReservationID,
             "qr":qr,
             "deposit": deposit }


def get_all_restaurants():
    restaurants = Restaurant.query.all()

    return [
        {
            "RestaurantID": r.RestaurantID,
            "RestaurantName": r.RestaurantName,
            "Opentime": r.Opentime.strftime("%H:%M"),
            "Closetime": r.Closetime.strftime("%H:%M")
        }
        for r in restaurants
    ]

def get_restaurant_by_id(restaurant_id):
    r = Restaurant.query.get(restaurant_id)
    if not r:
        return {}
    return {
        "RestaurantID": r.RestaurantID,
        "RestaurantName": r.RestaurantName,
        "Opentime": r.Opentime.strftime("%H:%M"),
        "Closetime": r.Closetime.strftime("%H:%M")
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
        Amounts=float(amount),
        Status="Paid",
        PaymentMethod="QR",
        CreatedAt=datetime.now()
    )

    booking.Status = "Confirmed"

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

        if booking_datetime < now - timedelta(minutes=5):
            b.Status = "Cancelled"
    db.session.commit()


# ================== HISTORY ==================
def get_history(user_id):
    bookings = Reservation.query.filter_by(UserID=user_id).all()

    result = []
    for b in bookings:
        result.append({
            "ReservationID": b.ReservationID,
            "CustomerName": b.CustomerName,
            "phone": b.phone,
            "BookingDate": b.BookingDate.strftime("%Y-%m-%d"),
            "BookingTime": b.BookingTime.strftime("%H:%M"),
            "GuestCount": b.GuestCount,
            "Status": b.Status,
            "RestaurantID": b.RestaurantID,
            "RestaurantName": b.restaurant.RestaurantName if b.restaurant else None,
            "TableNumber": b.table.TableNumber if b.table else None
        })
    return result