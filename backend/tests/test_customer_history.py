from flask_jwt_extended import create_access_token

"""
- Test authentication
- Test response khi có dữ liệu
"""

def test_history_not_login(client):
    """
    CASE: chưa đăng nhập
    EXPECT: trả về 401 Unauthorized
    """
    res = client.get("/api/v1/customer/history")

    assert res.status_code == 401


def test_history_success(client, monkeypatch):
    """
    CASE: đã đăng nhập + có dữ liệu

    MOCK:
        get_history -> trả dữ liệu giả

    EXPECT:
        - status 200
        - trả về list
        - có ReservationID đúng
    """

    # TẠO TOKEN
    app = client.application
    with app.app_context():
        token = create_access_token(identity="1")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    #  MOCK SERVICE
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

    #  ASSERT
    assert res.status_code == 200
    assert isinstance(res.json, list)
    assert len(res.json) > 0
    assert "ReservationID" in res.json[0]
    assert len(res.json) > 0
    assert res.json[0]["ReservationID"] == 1

def test_history_with_keyword(client, monkeypatch):
    app = client.application

    with app.app_context():
        token = create_access_token(identity="1")

    headers = {"Authorization": f"Bearer {token}"}

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.get_history",
        lambda user_id, keyword: [
            {"ReservationID": 2, "CustomerName": "Nguyen Van A"}
        ]
    )

    res = client.get(
        "/api/v1/customer/history?keyword=Nguyen",
        headers=headers
    )

    assert res.status_code == 200
    assert res.json[0]["CustomerName"] == "Nguyen Van A"

def test_history_empty(client, monkeypatch):
    app = client.application

    with app.app_context():
        token = create_access_token(identity="1")

    headers = {"Authorization": f"Bearer {token}"}

    monkeypatch.setattr(
        "backend.app.api.v1.customer.service.get_history",
        lambda user_id, keyword: []
    )

    res = client.get(
        "/api/v1/customer/history",
        headers=headers
    )

    assert res.status_code == 200
    assert res.json == []

def test_history_invalid_token(client):
    headers = {
        "Authorization": "Bearer invalid_token"
    }

    res = client.get("/api/v1/customer/history", headers=headers)

    assert res.status_code in [401, 422]