import pytest
from backend.core import create_app
from flask_jwt_extended import create_access_token
# FIXTURE: Tạo app test + database tạm
@pytest.fixture
def client():
    app = create_app()

    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "this-is-a-very-long-secret-key-for-testing-123456"

    with app.test_client() as client:
        yield client
# HELPER: tạo JWT token
def get_headers(app, user_id=1):
    with app.app_context():
        token = create_access_token(identity=user_id)
    return {"Authorization": f"Bearer {token}"}


# CUS_SEARCH

def test_search_empty(client, monkeypatch):
    """
    TEST: search không có filter
    EXPECT: trả về list (có thể rỗng)
    """
    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.search_restaurant",
        lambda a, b: []
    )

    res = client.get("/api/v1/customer/search")
    assert res.status_code == 200
    assert isinstance(res.json, list)


def test_search_with_address(client, monkeypatch):
    """
    TEST: search theo địa chỉ
    EXPECT: trả về danh sách nhà hàng
    """
    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.search_restaurant",
        lambda a, b: [{"RestaurantName": "Test"}]
    )

    res = client.get("/api/v1/customer/search?address=HCM")
    assert res.status_code == 200
    assert len(res.json) == 1

# CUS_BOOKING
def test_check_missing_params(client):
    """
    TEST: thiếu params check table
    EXPECT: 400
    """
    res = client.get("/api/v1/customer/check")
    assert res.status_code == 400


def test_check_invalid_people(client):
    """
    TEST: số khách > 10
    EXPECT: lỗi validation
    """
    res = client.get(
        "/api/v1/customer/check?restaurant_id=1&date=2025-12-12&time=10:00&people=20"
    )
    assert res.status_code == 400


def test_book_invalid_phone(client):
    """
    TEST: số điện thoại sai format
    EXPECT: báo lỗi SĐT
    """
    res = client.post("/api/v1/customer/book", json={
        "name": "Test",
        "phone": "123456",
        "restaurant_id": 1,
        "table_id": 1,
        "date": "2025-12-12",
        "time": "10:00",
        "people": 2
    })

    assert res.status_code == 400
    assert "SĐT" in res.json["error"]


def test_book_invalid_people(client):
    """
    TEST: số khách vượt giới hạn
    EXPECT: lỗi
    """
    res = client.post("/api/v1/customer/book", json={
        "name": "Test",
        "phone": "0912345678",
        "restaurant_id": 1,
        "table_id": 1,
        "date": "2025-12-12",
        "time": "10:00",
        "people": 20
    })

    assert res.status_code == 400


def test_book_past_date(client):
    """
    TEST: đặt ngày trong quá khứ
    EXPECT: lỗi
    """
    res = client.post("/api/v1/customer/book", json={
        "name": "Test",
        "phone": "0912345678",
        "restaurant_id": 1,
        "table_id": 1,
        "date": "2020-01-01",
        "time": "10:00",
        "people": 2
    })

    assert res.status_code == 400

def test_book_success(client, monkeypatch):
    """
    TEST: đặt bàn thành công (mock toàn bộ DB + logic phụ thuộc)
    EXPECT: trả về reservation_id
    """

    # ===== MOCK TABLE (db.session.get) =====
    class FakeTable:
        RestaurantID = 1

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.db.session.get",
        lambda model, table_id: FakeTable()
    )

    # ===== MOCK RESTAURANT =====
    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.get_restaurant_by_id",
        lambda x: {
            "Opentime": "08:00:00",
            "Closetime": "22:00:00"
        }
    )

    # ===== MOCK RESERVATION (KHÔNG TRÙNG) =====
    class FakeColumn:
        def __eq__(self, other):
            return True
        def in_(self, arr):
            return True

    class FakeReservationQuery:
        def filter(self, *args, **kwargs):
            return self
        def first(self):
            return None

    class FakeReservation:
        TableID = FakeColumn()
        BookingDate = FakeColumn()
        BookingTime = FakeColumn()
        Status = FakeColumn()
        query = FakeReservationQuery()

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.Reservation",
        FakeReservation
    )

    # ===== MOCK CREATE BOOKING =====
    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.create_booking",
        lambda data: {
            "reservation_id": 1,
            "deposit": 100000,
            "qr": "abc"
        }
    )

    # ===== CALL API =====
    res = client.post("/api/v1/customer/book", json={
        "name": "Test",
        "phone": "0912345678",
        "restaurant_id": 1,
        "table_id": 1,
        "date": "2099-12-12",
        "time": "10:00",
        "people": 2
    })

    # ===== ASSERT =====
    assert res.status_code == 200
    assert res.json["reservation_id"] == 1

# CUS_HISTORY
def test_history_not_login(client):
    """
    TEST: chưa đăng nhập
    EXPECT: 401
    """
    res = client.get("/api/v1/customer/history")
    assert res.status_code == 401


from flask_jwt_extended import create_access_token

def test_history_success(client, monkeypatch):
    app = client.application

    with app.app_context():
        token = create_access_token(identity="1")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.get_history",
        lambda user_id, keyword: [
            {"ReservationID": 1, "CustomerName": "Test"}
        ]
    )

    res = client.get(
        "/api/v1/customer/history?keyword=",
        headers=headers
    )

    assert res.status_code == 200
    assert res.json[0]["ReservationID"] == 1

# REVIEW
def test_review_invalid_rating(client):
    """
    TEST: rating ngoài khoảng 1-5
    EXPECT: lỗi
    """
    res = client.post("/api/v1/customer/review", json={
        "Rating": 10,
        "RestaurantID": 1
    })
    assert res.status_code in [400, 401]

# PAYMENT
def test_payment_not_found(client, monkeypatch):
    """
    TEST: thanh toán với reservation không tồn tại
    EXPECT: error
    """
    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.confirm_payment",
        lambda reservation_id, amount: (
            {"error": "Reservation không tồn tại"}, 404
        )
    )
    res = client.post("/api/v1/customer/payment", json={
        "reservation_id": 999,
        "amount": 100000
    })
    assert res.status_code == 404