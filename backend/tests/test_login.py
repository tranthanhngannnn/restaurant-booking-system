import sys
from pathlib import Path

import pytest
from flask import jsonify
from flask_jwt_extended import create_access_token

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from backend.core import create_app
from backend.app.api.v1.auth import routes as auth_routes

LOGIN_URL = "/api/v1/auth/login"
LOGOUT_URL = "/api/v1/auth/logout"
PROTECTED_URL = "/api/v1/users/me"

TEST_USERS = {
    "admin": {
        "user_id": 1,
        "username": "admin",
        "password": "1",
        "role": "ADMIN",
        "restaurant_id": None,
    },
    "Ngan": {
        "user_id": 2,
        "username": "Ngan",
        "password": "1",
        "role": "CUSTOMER",
        "restaurant_id": None,
    },
    "restaurant1": {
        "user_id": 3,
        "username": "restaurant1",
        "password": "1",
        "role": "STAFF",
        "restaurant_id": 1,
    },
}


@pytest.fixture()
def app(monkeypatch):
    app = create_app()
    app.config.update(
        TESTING=True,
        JWT_SECRET_KEY="test-jwt-secret",
        SECRET_KEY="test-secret-key",
    )

    def fake_login(username, password):
        if not username:
            return {"message": "Validation error: username is required"}, 400

        if not password:
            return {"message": "Validation error: password is required"}, 400

        if not username.replace("_", "").isalnum():
            return {"message": "Validation error: username is invalid"}, 400

        user = TEST_USERS.get(username)
        if not user or user["password"] != password:
            return {"message": "Sai tai khoan hoac mat khau"}, 401

        access_token = create_access_token(
            identity=str(user["user_id"]),
            additional_claims={
                "role": user["role"],
                "restaurant_id": user["restaurant_id"],
            },
        )
        return {
            "message": "Dang nhap thanh cong",
            "access_token": access_token,
            "role": user["role"],
            "user_info": {
                "id": user["user_id"],
                "username": user["username"],
            },
        }, 200

    monkeypatch.setattr(auth_routes.AuthService, "login", staticmethod(fake_login))

    @app.post(PROTECTED_URL)
    def protected_me():
        from flask_jwt_extended import get_jwt_identity, jwt_required

        @jwt_required()
        def current_user():
            return jsonify({"logged_in": True, "user_id": get_jwt_identity()})

        return current_user()

    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def login_customer(client):
    response = client.post(
        LOGIN_URL,
        data={"username": "Ngan", "password": "1"},
    )
    assert response.status_code == 200
    return response.get_json()


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def assert_error_message(response, *expected_parts):
    payload = response.get_json()
    assert payload is not None

    message = str(payload.get("message") or payload.get("error") or "").lower()
    assert message
    assert any(part.lower() in message for part in expected_parts)


def test_login_success_admin(client):
    response = client.post(
        LOGIN_URL,
        data={"username": "admin", "password": "1"},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert "access_token" in payload
    assert payload["role"] == "ADMIN"


def test_login_success_customer(client):
    response = client.post(
        LOGIN_URL,
        data={"username": "Ngan", "password": "1"},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload is not None
    assert payload["access_token"]
    assert payload["role"] == "CUSTOMER"
    assert payload["user_info"]["username"] == "Ngan"


def test_login_success_staff(client):
    response = client.post(
        LOGIN_URL,
        data={"username": "restaurant1", "password": "1"},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload is not None
    assert payload["access_token"]
    assert payload["role"] == "STAFF"
    assert payload["user_info"]["username"] == "restaurant1"


def test_login_fails_when_password_is_wrong(client):
    response = client.post(
        LOGIN_URL,
        data={"username": "Ngan", "password": "wrong-password"},
    )

    assert response.status_code in (400, 401)
    assert_error_message(response, "sai", "invalid", "mat khau", "password")


def test_login_fails_when_username_is_empty(client):
    response = client.post(
        LOGIN_URL,
        data={"username": "", "password": "1"},
    )

    assert response.status_code == 400
    assert_error_message(response, "validation", "username")


def test_login_fails_when_password_is_empty(client):
    response = client.post(
        LOGIN_URL,
        data={"username": "Ngan", "password": ""},
    )

    assert response.status_code == 400
    assert_error_message(response, "validation", "password")


def test_login_fails_when_username_has_special_characters(client):
    response = client.post(
        LOGIN_URL,
        data={"username": "@@@###", "password": "1"},
    )

    assert response.status_code == 400
    assert_error_message(response, "validation", "username")


def test_logout_after_login_success(client, login_customer):
    response = client.get(
        LOGOUT_URL,
        headers=auth_headers(login_customer["access_token"]),
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload is not None
    assert "đã đăng xuất" in str(payload).lower()
