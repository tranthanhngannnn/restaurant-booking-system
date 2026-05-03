import pytest
from flask import jsonify
from flask_jwt_extended import create_access_token


REGISTER_URL = "/api/v1/auth/registerRequest"
ADMIN_URL = "/api/v1/admin/users"


TEST_USERS = {
    "Ngan": {
        "user_id": 1,
        "username": "Ngan",
        "password": "123456",
        "role": "CUSTOMER",
        "restaurant_id": None,
    }
}

# FIXTURE: Tạo app test + database tạm
@pytest.fixture()
def app(monkeypatch):
    from core import create_app
    from app.api.v1.auth import routes as auth_routes

    app = create_app()
    app.config.update(
        TESTING=True,
        JWT_SECRET_KEY="test-secret-key"
    )

    # ===== Fake Register =====
    def fake_register(data):
        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()
        email = (data.get("email") or "").strip()
        phone = (data.get("phone") or "").strip()
        role = (data.get("role") or "").strip()
        restaurant_id = data.get("restaurant_id")

        if not username:
            return {"message": "Username is required"}, 400

        if not password:
            return {"message": "Password is required"}, 400

        if username in TEST_USERS:
            return {"message": "Username already exists"}, 409

        if "@" not in email or "." not in email:
            return {"message": "Email invalid"}, 400

        if len(phone) > 11:
            return {"message": "Phone invalid"}, 400

        if role == "STAFF":
            if not str(restaurant_id).isdigit():
                return {"message": "RestaurantID invalid"}, 400

        TEST_USERS[username] = {
            "user_id": len(TEST_USERS) + 1,
            "username": username,
            "password": password,
            "role": role,
            "restaurant_id": restaurant_id
        }

        return {"message": "Register success"}, 201

    monkeypatch.setattr(
        auth_routes.AuthService,
        "register",
        staticmethod(fake_register)
    )

    # ===== Admin Route giả kiểm tra Authorization =====
    @app.get(ADMIN_URL)
    def fake_admin():
        from flask_jwt_extended import jwt_required, get_jwt

        @jwt_required()
        def inner():
            claims = get_jwt()

            if claims["role"] != "ADMIN":
                return jsonify({"message": "Forbidden"}), 403

            return jsonify({"message": "Welcome admin"}), 200

        return inner()

    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}



# REGISTER TEST
def test_register_customer_success(client):
    response = client.post(
        REGISTER_URL,
        data={
            "username": "customer01",
            "password": "123456",
            "email": "cus@gmail.com",
            "phone": "0987654321",
            "role": "CUSTOMER"
        }
    )

    assert response.status_code == 201


def test_register_staff_success(client):
    response = client.post(
        REGISTER_URL,
        data={
        "username": "staff01",
        "password": "123456",
        "email": "staff@gmail.com",
        "phone": "0988888888",
        "role": "STAFF",
        "restaurant_id": 1
    })

    assert response.status_code == 201


def test_register_fail_username_exists(client):
    response = client.post(REGISTER_URL, data={
        "username": "Ngan",
        "password": "123456",
        "email": "test@gmail.com",
        "phone": "0900000000",
        "role": "CUSTOMER"
    })

    assert response.status_code == 409


# Khai báo sẵn các trường hợp muốn test
@pytest.mark.parametrize("bad_data", [
    ({"username": "", "password": "123", "email": "a@a.com", "phone": "0123"}),  # Bỏ trống username
    ({"username": "test", "password": "", "email": "a@a.com", "phone": "0123"}),  # Bỏ trống password
    ({"username": "test", "password": "123", "email": "sai-email", "phone": "0123"}),  # Sai email
    ({"username": "test", "password": "123", "email": "a@a.com", "phone": "0123456789012"}),  # SĐT quá dài
    ({"username": "staff1", "password": "123", "role": "STAFF", "restaurant_id": "ABC"}),  # ID không phải số
])
def test_register_validation_fails(client, bad_data):
    # client là cái giả lập request từ fixture
    response = client.post("/api/v1/auth/registerRequest", data=bad_data)

    assert response.status_code == 400


# ROLE TEST
def test_customer_cannot_access_admin(client,app):
    with app.app_context():
        token = create_access_token(
            identity="1",
            additional_claims={"role": "CUSTOMER"}
        )

        # Gọi thẳng luôn bằng client đã có sẵn fake_admin
    response = client.get(
        ADMIN_URL,
        headers=auth_headers(token)
    )

    assert response.status_code == 403