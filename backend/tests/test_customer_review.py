import pytest
from flask_jwt_extended import create_access_token

# AUTH HELPER
def auth_headers(client, user_id="1"):
    with client.application.app_context():
        token = create_access_token(identity=user_id)
    return {"Authorization": f"Bearer {token}"}


# SUCCESS: CREATE NEW REVIEW
def test_review_create_success(client, monkeypatch):
    headers = auth_headers(client)

    # fake chưa có review
    class FakeQuery:
        def filter_by(self, **kwargs):
            return self
        def first(self):
            return None

    class FakeReview:
        query = FakeQuery()

        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.Review",
        FakeReview
    )

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.db.session.add",
        lambda x: None
    )

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.db.session.commit",
        lambda: None
    )

    res = client.post(
        "/api/v1/customer/review",
        headers=headers,
        json={
            "RestaurantID": 1,
            "ReservationID": 1,
            "Rating": 5,
            "Comment": "Good service"
        }
    )

    assert res.status_code == 200
    assert "thành công" in res.json["message"]

# SUCCESS: UPDATE REVIEW EXISTING
def test_review_update_existing(client, monkeypatch):
    headers = auth_headers(client)

    fake_review = type("R", (), {
        "Rating": 3,
        "Comment": "Old comment"
    })()

    class FakeQuery:
        def filter_by(self, **kwargs):
            return self
        def first(self):
            return fake_review

    class FakeReview:
        query = FakeQuery()

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.Review",
        FakeReview
    )

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.db.session.commit",
        lambda: None
    )

    res = client.post(
        "/api/v1/customer/review",
        headers=headers,
        json={
            "RestaurantID": 1,
            "ReservationID": 1,
            "Rating": 5,
            "Comment": "Updated comment"
        }
    )

    assert res.status_code == 200
    assert "thành công" in res.json["message"]


# VALIDATION: INVALID RATING
def test_review_invalid_rating(client):
    headers = auth_headers(client)

    res = client.post(
        "/api/v1/customer/review",
        headers=headers,
        json={
            "RestaurantID": 1,
            "ReservationID": 1,
            "Rating": 10,
            "Comment": "Bad rating"
        }
    )

    assert res.status_code == 400


def test_review_invalid_rating_zero(client):
    headers = auth_headers(client)

    res = client.post(
        "/api/v1/customer/review",
        headers=headers,
        json={
            "RestaurantID": 1,
            "ReservationID": 1,
            "Rating": 0
        }
    )

    assert res.status_code == 400


def test_review_invalid_rating_string(client):
    headers = auth_headers(client)

    res = client.post(
        "/api/v1/customer/review",
        headers=headers,
        json={
            "RestaurantID": 1,
            "ReservationID": 1,
            "Rating": "abc"
        }
    )

    assert res.status_code == 400


# VALIDATION: COMMENT LENGTH
def test_review_comment_too_long(client):
    headers = auth_headers(client)

    long_comment = "A" * 300  # vượt 255

    res = client.post(
        "/api/v1/customer/review",
        headers=headers,
        json={
            "RestaurantID": 1,
            "ReservationID": 1,
            "Rating": 5,
            "Comment": long_comment
        }
    )

    assert res.status_code == 400


# VALIDATION: MISSING DATA
def test_review_missing_rating(client):
    headers = auth_headers(client)

    res = client.post(
        "/api/v1/customer/review",
        headers=headers,
        json={
            "RestaurantID": 1,
            "ReservationID": 1
        }
    )

    assert res.status_code == 400


def test_review_missing_reservation(client, monkeypatch):
    headers = auth_headers(client)

    # giả lập chưa có review
    class FakeQuery:
        def filter_by(self, **kwargs):
            return self

        def first(self):
            return None

    class FakeReview:
        query = FakeQuery()

        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.Review",
        FakeReview
    )
    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.db.session.add",
        lambda x: None
    )
    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.db.session.commit",
        lambda: None
    )
    res = client.post(
        "/api/v1/customer/review",
        headers=headers,
        json={
            "RestaurantID": 1,
            "Rating": 5
        }
    )
    # nên BE vẫn tạo review thành công
    assert res.status_code == 200

# EDGE CASE: EMPTY COMMENT (VALID)
def test_review_empty_comment(client, monkeypatch):
    headers = auth_headers(client)

    class FakeQuery:
        def filter_by(self, **kwargs):
            return self
        def first(self):
            return None

    class FakeReview:
        query = FakeQuery()

        def __init__(self, **kwargs):
            pass

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.Review",
        FakeReview
    )

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.db.session.add",
        lambda x: None
    )

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.db.session.commit",
        lambda: None
    )

    res = client.post(
        "/api/v1/customer/review",
        headers=headers,
        json={
            "RestaurantID": 1,
            "ReservationID": 1,
            "Rating": 5
        }
    )

    assert res.status_code == 200


# EDGE CASE: UNAUTHORIZED
def test_review_unauthorized(client):
    res = client.post(
        "/api/v1/customer/review",
        json={
            "RestaurantID": 1,
            "ReservationID": 1,
            "Rating": 5
        }
    )

    assert res.status_code in (401, 422)


# EDGE CASE: DATA ERROR FROM DB
def test_review_data_error(client, monkeypatch):
    headers = auth_headers(client)

    def fake_commit():
        from sqlalchemy.exc import DataError
        raise DataError("test", None, None)

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.db.session.commit",
        fake_commit
    )

    res = client.post(
        "/api/v1/customer/review",
        headers=headers,
        json={
            "RestaurantID": 1,
            "ReservationID": 1,
            "Rating": 5,
            "Comment": "ok"
        }
    )

    assert res.status_code == 400