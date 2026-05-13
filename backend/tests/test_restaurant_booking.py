
from datetime import date, time

from backend.core.extensions import db

from backend.models.booking import Reservation
from backend.models.tables import Tables
from backend.models.restaurant import Restaurant

from backend.app.api.v1.restaurant.service import (
    confirm_booking,
    reject_booking,
    delete_booking,
    get_booking_by_table_service
)


# HELPER FUNCTIONS
def create_test_restaurant():
    """
    Tạo restaurant phục vụ foreign key test
    """

    restaurant = Restaurant(
        RestaurantName="Test Restaurant",
        Address="HCM",
        Phone="0123456789",
        Email="test@gmail.com",
        Opentime="08:00",
        Closetime="22:00",
        description="Test restaurant"
    )

    db.session.add(restaurant)
    db.session.commit()

    return restaurant


def create_test_table(restaurant_id):
    """
    Tạo bàn test
    """

    table = Tables(
        RestaurantID=restaurant_id,
        TableNumber="A1",
        Capacity=4,
        Status="Available"
    )

    db.session.add(table)
    db.session.commit()

    return table


def create_test_booking(
        restaurant_id,
        table_id=None,
        status="Pending"
):
    """
    Tạo booking test dùng chung
    """

    booking = Reservation(
        CustomerName="Nguyen Van A",
        phone="0123456789",
        RestaurantID=restaurant_id,
        TableID=table_id,
        BookingDate=date.today(),
        BookingTime=time(18, 30),
        GuestCount=4,
        Deposit=100000,
        Note="Test booking",
        Status=status
    )

    db.session.add(booking)
    db.session.commit()

    return booking


# TEST CONFIRM BOOKING

def test_confirm_booking_success(app):
    """
    Kiểm tra:
    - Confirm booking thành công
    - Booking -> Confirmed
    - Table -> Reserved
    """

    with app.app_context():

        restaurant = create_test_restaurant()

        table = create_test_table(
            restaurant.RestaurantID
        )

        booking = create_test_booking(
            restaurant.RestaurantID,
            table.TableID
        )

        result = confirm_booking(
            booking.ReservationID
        )

        assert result["message"] == "Confirmed"
        assert result["Status"] == "Confirmed"

        updated_booking = Reservation.query.get(
            booking.ReservationID
        )

        updated_table = Tables.query.get(
            table.TableID
        )

        assert updated_booking.Status == "Confirmed"

        assert updated_table.Status == "Reserved"


def test_confirm_booking_not_found(app):
    """
    Confirm booking không tồn tại
    """

    with app.app_context():

        result = confirm_booking(9999)

        assert result["error"] == "Not found"


def test_confirm_rejected_booking(app):
    """
    Không được confirm booking đã reject
    """

    with app.app_context():

        restaurant = create_test_restaurant()

        table = create_test_table(
            restaurant.RestaurantID
        )

        booking = create_test_booking(
            restaurant.RestaurantID,
            table.TableID,
            status="Rejected"
        )

        result = confirm_booking(
            booking.ReservationID
        )

        assert result["error"] == (
            "Cannot confirm rejected booking"
        )
        updated_booking = Reservation.query.get(
            booking.ReservationID
        )

        assert updated_booking.Status == "Rejected"


def test_confirm_booking_without_table(app):
    """
    Booking không có bàn:
    - vẫn confirm được
    - không crash
    """

    with app.app_context():

        restaurant = create_test_restaurant()

        booking = create_test_booking(
            restaurant.RestaurantID,
            table_id=None
        )

        result = confirm_booking(
            booking.ReservationID
        )
        assert result["message"] == "Confirmed"

        updated_booking = Reservation.query.get(
            booking.ReservationID
        )
        assert updated_booking.Status == "Confirmed"

def test_confirm_booking_already_confirmed(app):
    """
    Confirm booking đã confirmed:
    - Không crash
    - Giữ nguyên trạng thái
    """

    with app.app_context():
        restaurant = create_test_restaurant()
        table = create_test_table(
            restaurant.RestaurantID
        )
        booking = create_test_booking(
            restaurant.RestaurantID,
            table.TableID,
            status="Confirmed"
        )
        result = confirm_booking(booking.ReservationID)
        assert result["message"] == "Confirmed"
        assert result["Status"] == "Confirmed"

        updated_booking = Reservation.query.get(booking.ReservationID)
        assert updated_booking.Status == "Confirmed"


def test_confirm_booking_deleted_table(app):
    """
    Booking có table đã bị xóa:
    - vẫn confirm được
    - không crash
    """
    with app.app_context():

        restaurant = create_test_restaurant()
        table = create_test_table(restaurant.RestaurantID)
        booking = create_test_booking(restaurant.RestaurantID,table.TableID)
        # Xóa table sau khi booking đã tạo
        db.session.delete(table)
        db.session.commit()
        result= confirm_booking(booking.ReservationID)
        assert result["message"] == "Confirmed"
        assert result["Status"] == "Confirmed"
        updated_booking = Reservation.query.get(booking.ReservationID)
        assert updated_booking.Status == "Confirmed"

# TEST REJECT BOOKING
def test_reject_booking_success(app):
    """
    Reject booking thành công
    """

    with app.app_context():

        restaurant = create_test_restaurant()
        booking = create_test_booking(restaurant.RestaurantID)

        result = reject_booking(booking.ReservationID)
        assert result["message"] == "Rejected"
        assert result["Status"] == "Rejected"

        updated_booking = Reservation.query.get(booking.ReservationID)
        assert updated_booking.Status == "Rejected"


def test_reject_confirmed_booking(app):
    """
    Không được reject booking đã confirm
    """

    with app.app_context():

        restaurant = create_test_restaurant()

        booking = create_test_booking(
            restaurant.RestaurantID,
            status="Confirmed"
        )

        result = reject_booking(
            booking.ReservationID
        )
        assert result["error"] == (
            "Cannot reject confirmed booking"
        )


def test_reject_booking_not_found(app):
    """
    Reject booking không tồn tại
    """

    with app.app_context():

        result = reject_booking(9999)

        assert result["error"] == "Not found"

# TEST DELETE BOOKING
def test_delete_booking_success(app):
    """
    Xóa booking thành công
    """

    with app.app_context():

        restaurant = create_test_restaurant()

        booking = create_test_booking(
            restaurant.RestaurantID
        )

        booking_id = booking.ReservationID

        result = delete_booking(
            booking_id
        )
        assert result["msg"] == "Deleted"

        deleted_booking = Reservation.query.get(
            booking_id
        )
        assert deleted_booking is None


def test_delete_booking_not_found(app):
    """
    Xóa booking không tồn tại
    """
    with app.app_context():

        result = delete_booking(9999)
        assert result["error"] == "Not found"

# TEST GET BOOKING BY TABLE
def test_get_booking_by_table_success(app):
    """
    Lấy danh sách booking theo bàn
    """

    with app.app_context():

        restaurant = create_test_restaurant()

        table = create_test_table(
            restaurant.RestaurantID
        )

        create_test_booking(
            restaurant.RestaurantID,
            table.TableID
        )

        create_test_booking(
            restaurant.RestaurantID,
            table.TableID
        )

        result = get_booking_by_table_service(table.TableID)
        assert len(result) == 2
        assert result[0]["TableID"] == table.TableID
        assert result[0]["Status"] == "Pending"


def test_get_booking_by_table_empty(app):
    """
    Bàn chưa có booking
    """

    with app.app_context():

        result = get_booking_by_table_service(
            9999
        )
        assert result == []

