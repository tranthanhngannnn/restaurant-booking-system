from datetime import datetime, timedelta
from backend.models.booking import Reservation
#CHECK API

def test_check_missing_params(client):
    """
    CASE: thiếu param
    EXPECT: 400
    """
    res = client.get("/api/v1/customer/check")
    assert res.status_code == 400


def test_check_invalid_people(client):
    """
    CASE: people > 10
    EXPECT: lỗi validation
    """
    res = client.get(
        "/api/v1/customer/check?restaurant_id=1&date=2025-12-12&time=10:00&people=20"
    )
    assert res.status_code == 400


# BOOK API

def test_book_invalid_phone(client):
    """
    CASE: phone sai format
    EXPECT: lỗi
    """
    res = client.post("/api/v1/customer/book", json={
        "name": "Test",
        "phone": "123",
        "restaurant_id": 1,
        "table_id": 1,
        "date": "2099-01-01",
        "time": "10:00",
        "people": 2
    })

    assert res.status_code == 400
    assert "SĐT" in res.json["error"]


def test_book_people_boundary(client):
    """
    CASE: boundary people
    EXPECT: reject
    """
    for p in [0, -1, 11]:
        res = client.post("/api/v1/customer/book", json={
            "name": "Test",
            "phone": "0912345678",
            "restaurant_id": 1,
            "table_id": 1,
            "date": "2099-01-01",
            "time": "10:00",
            "people": p
        })
        assert res.status_code == 400


def test_book_past_date(client):
    """
    CASE: ngày quá khứ
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


def test_book_invalid_table(client, monkeypatch):
    """
    CASE: table không tồn tại
    EXPECT: lỗi
    """

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.db.session.get",
        lambda model, table_id: None
    )

    res = client.post("/api/v1/customer/book", json={
        "name": "Test",
        "phone": "0912345678",
        "restaurant_id": 1,
        "table_id": 99,
        "date": "2099-01-01",
        "time": "10:00",
        "people": 2
    })

    assert res.status_code == 400

def test_book_success(client, monkeypatch):
    """
    CASE: booking thành công
    EXPECT: trả reservation_id
    """

    #  MOCK TABLE
    class FakeTable:
        RestaurantID = 1

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.db.session.get",
        lambda model, table_id: FakeTable()
    )

    #  MOCK RESERVATION (KHÔNG TRÙNG)
    class FakeColumn:
        def __eq__(self, other): return True
        def in_(self, arr): return True
        def between(self, start, end):
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

    #  MOCK CREATE BOOKING
    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.create_booking",
        lambda data: {"reservation_id": 1}
    )

    res = client.post("/api/v1/customer/book", json={
        "name": "Test",
        "phone": "0912345678",
        "restaurant_id": 1,
        "table_id": 1,
        "date": "2099-01-01",
        "time": "10:00",
        "people": 2
    })

    # ASSERT
    assert res.status_code == 200
    assert res.json["reservation_id"] == 1

def test_book_missing_name(client):
    res = client.post("/api/v1/customer/book", json={
        "phone": "0912345678"
    })
    assert res.status_code == 400


def test_book_invalid_date_format(client):
    res = client.post("/api/v1/customer/book", json={
        "name": "Test",
        "phone": "0912345678",
        "restaurant_id": 1,
        "table_id": 1,
        "date": "wrong",
        "time": "10:00",
        "people": 2
    })
    assert res.status_code == 400


def test_book_restaurant_not_found(client, monkeypatch):
    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.get_restaurant_by_id",
        lambda x: None
    )

    res = client.post("/api/v1/customer/book", json={
        "name": "Test",
        "phone": "0912345678",
        "restaurant_id": 1,
        "table_id": 1,
        "date": "2099-01-01",
        "time": "10:00",
        "people": 2
    })

    assert res.status_code == 404

def mock_booking_conflict(monkeypatch, has_conflict):
    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self
        def filter_by(self, *args, **kwargs):
            return self
        def first(self):
            return object() if has_conflict else None
        def all(self):
            return []

    class FakeColumn:
        def __eq__(self, other): return True
        def in_(self, arr): return True
        def between(self, a, b): return True

    class FakeReservation:
        TableID = FakeColumn()
        BookingDate = FakeColumn()
        BookingTime = FakeColumn()
        Status = FakeColumn()
        query = FakeQuery()

        def __init__(self, *args, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
            self.ReservationID = 1

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.Reservation",
        FakeReservation
    )
    monkeypatch.setattr(
        "backend.app.api.v1.customer.service.Reservation",
        FakeReservation
    )
    monkeypatch.setattr(
        "backend.app.api.v1.customer.service.db.session.add",
        lambda x: None
    )
    monkeypatch.setattr(
        "backend.app.api.v1.customer.service.db.session.commit",
        lambda: None
    )

def test_booking_outside_60min_allowed(client, monkeypatch):
    mock_booking_conflict(monkeypatch, has_conflict=False)
    fixed_now = datetime(2026, 5, 10, 18, 0)
    class MockDateTime(datetime):
        @classmethod
        def now(cls):
            return fixed_now

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.datetime",
        MockDateTime
    )

    res = client.post("/api/v1/customer/book", json={
        "name": "A",
        "phone": "0912345678",
        "people": 2,
        "date": "2026-05-10",
        "time": "19:01",  # +61 phút
        "table_id": 1,
        "restaurant_id": 1
    })

    assert res.status_code == 200

def test_booking_within_60min_blocked(client, monkeypatch):
    mock_booking_conflict(monkeypatch, has_conflict=True)

    res = client.post("/api/v1/customer/book", json={
        "name": "A",
        "phone": "0912345678",
        "people": 2,
        "date": "2026-05-10",
        "time": "18:30",
        "table_id": 1,
        "restaurant_id": 1
    })

    assert res.status_code == 400

def test_booking_exact_60min_blocked(client, monkeypatch):
    mock_booking_conflict(monkeypatch, has_conflict=True)

    res = client.post("/api/v1/customer/book", json={
        "name": "A",
        "phone": "0912345678",
        "people": 2,
        "date": "2026-05-10",
        "time": "19:00",
        "table_id": 1,
        "restaurant_id": 1
    })

    assert res.status_code == 400

def test_expired_pending_not_block(client, monkeypatch):
    mock_booking_conflict(monkeypatch, has_conflict=False)

    res = client.get("/api/v1/customer/check", query_string={
        "restaurant_id": 1,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "people": 2
    })

    assert res.status_code == 200


def test_booking_under_30min_blocked(client, monkeypatch):

    mock_booking_conflict(monkeypatch, has_conflict=False)

    fixed_now = datetime(2026, 5, 10, 18, 0)

    class MockDateTime(datetime):
        @classmethod
        def now(cls):
            return fixed_now

    # ✔ MOCK ĐÚNG CHỖ QUAN TRỌNG
    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.datetime",
        MockDateTime
    )

    res = client.post("/api/v1/customer/book", json={
        "name": "A",
        "phone": "0912345678",
        "people": 2,
        "date": "2026-05-10",
        "time": "18:10",  # 10 phút → FAIL
        "table_id": 1,
        "restaurant_id": 1
    })

    assert res.status_code == 400
    assert "30 phút" in res.get_json()["error"]

def test_booking_over_30min_allowed(client, monkeypatch):

    mock_booking_conflict(monkeypatch, has_conflict=False)

    fixed_now = datetime(2026, 5, 10, 18, 0)

    class MockDateTime(datetime):
        @classmethod
        def now(cls):
            return fixed_now

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.datetime",
        MockDateTime
    )

    res = client.post("/api/v1/customer/book", json={
        "name": "A",
        "phone": "0912345678",
        "people": 2,
        "date": "2026-05-10",
        "time": "18:40",  # 40 phút → OK
        "table_id": 1,
        "restaurant_id": 1
    })

    assert res.status_code in [200, 201]

def test_booking_note_too_long(client):
    data = {
        "name": "Test",
        "phone": "0123456789",
        "restaurant_id": 1,
        "table_id": 1,
        "date": "2099-12-30",
        "time": "18:00",
        "people": 2,
        "note": "a" * 301  # vượt 300
    }

    res = client.post("/api/v1/customer/book", json=data)

    assert res.status_code == 400
    assert "Ghi chú tối đa 300 ký tự" in res.json["error"]