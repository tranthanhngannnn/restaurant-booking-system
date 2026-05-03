import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from flask_jwt_extended import create_access_token

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core import create_app

CUISINES_URL = "/api/v1/admin/cuisines"
CUISINE_SERVICE_PATH = "app.api.v1.admin.routes.CuisineService"


@pytest.fixture()
def app(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-jwt-secret")
    monkeypatch.setenv("SQLALCHEMY_DATABASE_URI", "mysql+pymysql://test:test@localhost/test")

    app = create_app()
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        JWT_SECRET_KEY="test-jwt-secret",
    )
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin_headers(app):
    return auth_headers(app, "ADMIN")


@pytest.fixture()
def customer_headers(app):
    return auth_headers(app, "CUSTOMER")


def auth_headers(app, role):
    with app.app_context():
        token = create_access_token(
            identity="1",
            additional_claims={"role": role},
        )
    return {"Authorization": f"Bearer {token}"}


def cuisine_list():
    return [
        {"id": 1, "name": "Mon Viet", "status": "Hoat dong"},
        {"id": 2, "name": "Mon Han", "status": "Hoat dong"},
    ]

# Xem danh sách cuisine thành công
@patch(f"{CUISINE_SERVICE_PATH}.get_all")
def test_get_cuisines_success(mock_get_all, client, admin_headers):
    mock_get_all.return_value = (cuisine_list(), 200)

    response = client.get(CUISINES_URL, headers=admin_headers)
    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert data == cuisine_list()
    mock_get_all.assert_called_once_with()


# Load cuisine khi thiếu token
@patch(f"{CUISINE_SERVICE_PATH}.get_all")
def test_get_cuisines_missing_token(mock_get_all, client):
    response = client.get(CUISINES_URL)
    data = response.get_json()

    assert response.status_code == 401
    assert "msg" in data
    mock_get_all.assert_not_called()


# Thêm cuisine mới thành công
@patch(f"{CUISINE_SERVICE_PATH}.create")
def test_create_cuisine_success(mock_create, client, admin_headers):
    mock_create.return_value = ({"message": "Them thanh cong!"}, 201)

    response = client.post(
        CUISINES_URL,
        data={"CuisineName": "Mon Thai"},
        headers=admin_headers,
    )
    data = response.get_json()

    assert response.status_code == 201
    assert data["message"] == "Them thanh cong!"
    mock_create.assert_called_once_with({"CuisineName": "Mon Thai"})


# Không thêm cuisine trùng tên
@patch(f"{CUISINE_SERVICE_PATH}.create")
def test_create_cuisine_duplicate_name(mock_create, client, admin_headers):
    mock_create.return_value = ({"message": "Cuisine da ton tai"}, 400)

    response = client.post(
        CUISINES_URL,
        data={"CuisineName": "Mon Thai"},
        headers=admin_headers,
    )
    data = response.get_json()

    assert response.status_code == 400
    assert data["message"] == "Cuisine da ton tai"
    mock_create.assert_called_once_with({"CuisineName": "Mon Thai"})


# Thêm cuisine với khoảng trắng đầu cuối
@patch(f"{CUISINE_SERVICE_PATH}.create")
def test_create_cuisine_trim_whitespace(mock_create, client, admin_headers):
    mock_create.return_value = (
        {"message": "Them cuisine thanh cong"},
        201,
    )

    response = client.post(
        CUISINES_URL,
        data={"CuisineName": "  Mon Thai  "},
        headers=admin_headers,
    )
    data = response.get_json()

    assert response.status_code == 201
    assert data["message"] == "Them cuisine thanh cong"
    mock_create.assert_called_once_with({"CuisineName": "Mon Thai"})


#Thêm cuisine tên rất dài
@patch(f"{CUISINE_SERVICE_PATH}.create")
def test_create_cuisine_name_too_long(mock_create, client, admin_headers):
    long_name = "A" * 300
    mock_create.return_value = (
        {"message": "Ten cuisine qua dai"},
        400,
    )

    response = client.post(
        CUISINES_URL,
        data={"CuisineName": long_name},
        headers=admin_headers,
    )
    data = response.get_json()

    assert response.status_code == 400
    assert data["message"] == "Ten cuisine qua dai"
    mock_create.assert_called_once_with({"CuisineName": long_name})

# Không thêm cuisine khi bỏ trống tên
@patch(f"{CUISINE_SERVICE_PATH}.create")
def test_create_cuisine_missing_name(mock_create, client, admin_headers):
    mock_create.return_value = ({"message": "Ten khong duoc de trong"}, 400)

    response = client.post(CUISINES_URL, data={"CuisineName": ""}, headers=admin_headers)
    data = response.get_json()

    assert response.status_code == 400
    assert data["message"] == "Ten khong duoc de trong"
    mock_create.assert_called_once_with({"CuisineName": ""})


# Chặn thêm cuisine khi không phải ADMIN
@patch(f"{CUISINE_SERVICE_PATH}.create")
def test_create_cuisine_forbidden(mock_create, client, customer_headers):
    response = client.post(
        CUISINES_URL,
        data={"CuisineName": "Mon Thai"},
        headers=customer_headers,
    )
    data = response.get_json()

    assert response.status_code == 403
    assert data["message"] == "Quyen nay cua Admin!"
    mock_create.assert_not_called()


# Cập nhật tên cuisine thành công
@patch(f"{CUISINE_SERVICE_PATH}.update")
def test_update_cuisine_success(mock_update, client, admin_headers):
    mock_update.return_value = ({"message": "Cap nhat thanh cong!"}, 200)

    response = client.put(
        f"{CUISINES_URL}/1",
        data={"CuisineName": "Mon Viet Nam"},
        headers=admin_headers,
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "Cap nhat thanh cong!"
    mock_update.assert_called_once_with(1, {"CuisineName": "Mon Viet Nam"})


# Cập nhật cuisine không tồn tại
@patch(f"{CUISINE_SERVICE_PATH}.update")
def test_update_cuisine_not_found(mock_update, client, admin_headers):
    mock_update.return_value = ({"message": "Khong tim thay"}, 404)

    response = client.put(
        f"{CUISINES_URL}/999",
        data={"CuisineName": "Mon Moi"},
        headers=admin_headers,
    )
    data = response.get_json()

    assert response.status_code == 404
    assert data["message"] == "Khong tim thay"
    mock_update.assert_called_once_with(999, {"CuisineName": "Mon Moi"})


# Cập nhật trạng thái cuisine
@patch(f"{CUISINE_SERVICE_PATH}.update")
def test_update_cuisine_status_success(mock_update, client, admin_headers):
    mock_update.return_value = (
        {"message": "Cap nhat thanh cong"},
        200,
    )

    response = client.put(
        f"{CUISINES_URL}/1",
        data={"IsActive": False},
        headers=admin_headers,
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "Cap nhat thanh cong"
    mock_update.assert_called_once_with(1, {"IsActive": "False"})


# Cập nhật cuisine với tên trống
@patch(f"{CUISINE_SERVICE_PATH}.update")
def test_update_cuisine_empty_name(mock_update, client, admin_headers):
    mock_update.return_value = (
        {"message": "CuisineName khong duoc rong"},
        400,
    )

    response = client.put(
        f"{CUISINES_URL}/1",
        data={"CuisineName": ""},
        headers=admin_headers,
    )
    data = response.get_json()

    assert response.status_code == 400
    assert data["message"] == "CuisineName khong duoc rong"
    mock_update.assert_called_once_with(1, {"CuisineName": ""})


# Chặn sửa cuisine khi không phải ADMIN
@patch(f"{CUISINE_SERVICE_PATH}.update")
def test_update_cuisine_forbidden_customer(
    mock_update, client, customer_headers
):
    response = client.put(
        f"{CUISINES_URL}/1",
        data={"CuisineName": "Mon Moi"},
        headers=customer_headers,
    )
    data = response.get_json()

    assert response.status_code == 403
    assert data["message"] == "Quyen nay cua Admin!"
    mock_update.assert_not_called()


# Xóa cuisine thành công
@patch(f"{CUISINE_SERVICE_PATH}.delete")
def test_delete_cuisine_success(mock_delete, client, admin_headers):
    delete_mock = MagicMock(return_value=({"message": "Da xoa xong!"}, 200))
    mock_delete.side_effect = delete_mock

    response = client.delete(f"{CUISINES_URL}/1", headers=admin_headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "Da xoa xong!"
    delete_mock.assert_called_once_with(1)


# Xóa cuisine không tồn tại
@patch(f"{CUISINE_SERVICE_PATH}.delete")
def test_delete_cuisine_not_found(mock_delete, client, admin_headers):
    mock_delete.return_value = ({"message": "Khong tim thay"}, 404)

    response = client.delete(f"{CUISINES_URL}/999", headers=admin_headers)
    data = response.get_json()

    assert response.status_code == 404
    assert data["message"] == "Khong tim thay"
    mock_delete.assert_called_once_with(999)


# Chặn xóa cuisine khi không phải ADMIN
@patch(f"{CUISINE_SERVICE_PATH}.delete")
def test_delete_cuisine_forbidden(mock_delete, client, customer_headers):
    response = client.delete(f"{CUISINES_URL}/1", headers=customer_headers)
    data = response.get_json()

    assert response.status_code == 403
    assert data["message"] == "Khong co quyen xoa!"
    mock_delete.assert_not_called()


