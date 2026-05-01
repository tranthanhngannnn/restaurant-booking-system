import sys
from unittest.mock import MagicMock, patch
sys.modules["image"] = MagicMock(MENU_DATA=[])

# ==============================
# MENU TEST
# ==============================

@patch("app.api.v1.restaurant.service.Food")
def test_get_res_menu(mock_food):

    mock_food.query.filter_by.return_value.all.return_value = [
        MagicMock(
            FoodID=1,
            FoodName="Thit bo",
            Price=50,
            Image_URL="",
            Category="Main",
            Description="Ngon",
            Visible=True
        )
    ]

    from app.api.v1.restaurant.service import get_res_menu

    result = get_res_menu(1)

    assert len(result) == 1
    assert result[0]["name"] == "Thit bo"

# ==============================
# TABLE TEST
# ==============================
@patch("app.api.v1.restaurant.service.Reservation")
@patch("app.api.v1.restaurant.service.Tables")
def test_get_tables(mock_tables, mock_reservation):
    mock_tables.query.filter_by.return_value.all.return_value = [
        MagicMock(TableID=1, TableNumber="A1", Capacity=4, Status="Available")
    ]

    mock_reservation.query.filter_by.return_value.order_by.return_value.first.return_value = None

    from app.api.v1.restaurant.service import get_tables
    result = get_tables(1)

    assert result[0]["name"] == "A1"


@patch("app.api.v1.restaurant.service.db")
@patch("app.api.v1.restaurant.service.Tables")
def test_create_table_success(mock_tables, mock_db):
    mock_tables.query.filter_by.return_value.first.return_value = None

    from app.api.v1.restaurant.service import create_table

    data = {"TableNumber": "A1", "Capacity": 4}
    result = create_table(data, 1)

    assert result["message"] == "Table created"


# ==============================
# BOOKING TEST
# ==============================
@patch("app.api.v1.restaurant.service.booking_schema")
@patch("app.api.v1.restaurant.service.Reservation")
@patch("app.api.v1.restaurant.service.db")
@patch("app.api.v1.restaurant.service.Tables")
def test_create_booking_success(mock_tables, mock_db, mock_reservation, mock_schema):

    mock_tables.query.get.return_value = MagicMock(TableID=1, Status="Available")
    mock_reservation.return_value = MagicMock()

    # 👇 bypass marshmallow
    mock_schema.dump.return_value = {"ok": True}

    from app.api.v1.restaurant.service import create_booking

    result = create_booking({
        "TableID": 1,
        "CustomerName": "Thai",
        "BookingDate": "2026-05-01",
        "BookingTime": "18:00"
    })

    assert result["message"] == "Booking created"

def test_create_booking_wrong_date():
    from app.api.v1.restaurant.service import create_booking

    data = {
        "TableID": 1,
        "CustomerName": "Thai",
        "BookingDate": "sai",
        "BookingTime": "sai"
    }

    result = create_booking(data)

    assert "error" in result


@patch("app.api.v1.restaurant.service.booking_schema")
@patch("app.api.v1.restaurant.service.db")
@patch("app.api.v1.restaurant.service.Tables")
@patch("app.api.v1.restaurant.service.Reservation")
def test_confirm_booking(mock_reservation, mock_tables, mock_db, mock_schema):

    mock_booking = MagicMock(TableID=1, Status="Pending")
    mock_reservation.query.get.return_value = mock_booking
    mock_tables.query.get.return_value = MagicMock()

    mock_schema.dump.return_value = {"Status": "Confirmed"}

    from app.api.v1.restaurant.service import confirm_booking

    result = confirm_booking(1)

    assert result["Status"] == "Confirmed"

@patch("app.api.v1.restaurant.service.booking_schema")
@patch("app.api.v1.restaurant.service.db")
@patch("app.api.v1.restaurant.service.Reservation")
def test_reject_booking(mock_reservation, mock_db, mock_schema):

    mock_booking = MagicMock(Status="Pending")
    mock_reservation.query.get.return_value = mock_booking

    mock_schema.dump.return_value = {"Status": "Rejected"}

    from app.api.v1.restaurant.service import reject_booking

    result = reject_booking(1)

    assert result["Status"] == "Rejected"


@patch("app.api.v1.restaurant.service.db")
@patch("app.api.v1.restaurant.service.Reservation")
def test_delete_booking(mock_reservation, mock_db):
    mock_reservation.query.get.return_value = MagicMock()

    from app.api.v1.restaurant.service import delete_booking

    result = delete_booking(1)

    assert result["msg"] == "Deleted"


# ==============================
# FOOD TEST
# ==============================
@patch("app.api.v1.restaurant.service.db")
@patch("app.api.v1.restaurant.service.Food")
def test_create_food(mock_food, mock_db):
    mock_food.query.get.return_value = None

    from app.api.v1.restaurant.service import create_food

    data = {"name": "Thit nac", "price": 100}
    result = create_food(data, 1)

    assert result["msg"] == "Thêm thành công"


@patch("app.api.v1.restaurant.service.db")
@patch("app.api.v1.restaurant.service.Food")
def test_delete_food(mock_food, mock_db):
    mock_food.query.get.return_value = MagicMock()

    from app.api.v1.restaurant.service import delete_food

    result = delete_food("F001")

    assert result["msg"] == "Deleted"


@patch("app.api.v1.restaurant.service.db")
@patch("app.api.v1.restaurant.service.Food")
def test_update_food(mock_food, mock_db):
    mock_obj = MagicMock(FoodID="F1", FoodName="Hai san", Price=10, Category="A")
    mock_food.query.get.return_value = mock_obj

    from app.api.v1.restaurant.service import update_food

    data = {"name": "New", "price": 20}
    result = update_food("F1", data)

    assert result["msg"] == "Updated"
    assert result["data"]["name"] == "New"


# ==============================
# RESTAURANT SERVICE
# ==============================
@patch("app.api.v1.restaurant.service.db")
def test_create_restaurant(mock_db):
    from app.api.v1.restaurant.service import RestaurantService

    data = {"RestaurantName": "Test"}

    result, status = RestaurantService.create(data, is_admin=True)

    assert status == 201


def test_create_restaurant_no_name():
    from app.api.v1.restaurant.service import RestaurantService

    result, status = RestaurantService.create({}, is_admin=True)

    assert status == 400