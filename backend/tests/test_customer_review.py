from flask_jwt_extended import create_access_token


def get_auth_header(client):
    app = client.application
    with app.app_context():
        token = create_access_token(identity="1")
    return {"Authorization": f"Bearer {token}"}


# ================== SUCCESS ==================
def test_review_success(client, monkeypatch):
    headers = get_auth_header(client)

    # Mock Review chưa tồn tại
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

    res = client.post("/api/v1/customer/review",
        headers=headers,
        json={
            "RestaurantID": 1,
            "ReservationID": 1,
            "Rating": 5,
            "Comment": "Good"
        }
    )

    assert res.status_code == 200


# ================== INVALID RATING ==================
def test_review_invalid_rating(client):
    headers = get_auth_header(client)

    res = client.post("/api/v1/customer/review",
        headers=headers,
        json={
            "Rating": 10,
            "RestaurantID": 1
        }
    )

    assert res.status_code == 400


# ================== EMPTY COMMENT ==================
def test_review_empty_comment(client, monkeypatch):
    headers = get_auth_header(client)

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

    res = client.post("/api/v1/customer/review",
        headers=headers,
        json={
            "RestaurantID": 1,
            "ReservationID": 1,
            "Rating": 5
        }
    )

    assert res.status_code == 200


# ================== COMMENT TOO LONG ==================
def test_review_comment_too_long(client):
    headers = get_auth_header(client)

    long_comment = "A" * 501

    res = client.post("/api/v1/customer/review",
        headers=headers,
        json={
            "RestaurantID": 1,
            "ReservationID": 1,
            "Rating": 5,
            "Comment": long_comment
        }
    )

    assert res.status_code == 400


# ================== MISSING RATING ==================
def test_review_missing_rating(client):
    headers = get_auth_header(client)

    res = client.post("/api/v1/customer/review",
        headers=headers,
        json={
            "RestaurantID": 1,
            "ReservationID": 1
        }
    )

    assert res.status_code == 400


# ================== UPDATE REVIEW ==================
def test_review_update_existing(client, monkeypatch):
    headers = get_auth_header(client)

    fake_review = type("", (), {
        "Rating": 3,
        "Comment": "Old"
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

    res = client.post("/api/v1/customer/review",
        headers=headers,
        json={
            "RestaurantID": 1,
            "ReservationID": 1,
            "Rating": 5,
            "Comment": "New"
        }
    )

    assert res.status_code == 200