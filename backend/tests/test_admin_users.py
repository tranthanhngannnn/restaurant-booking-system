import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from flask_jwt_extended import create_access_token

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from backend.core import create_app

USERS_URL = "/api/v1/admin/users"
USER_SERVICE_PATH = "app.api.v1.admin.routes.AdminUserService"
LOGOUT_URL = "/api/v1/auth/logout"


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
    return make_headers(app, "ADMIN")


@pytest.fixture()
def customer_headers(app):
    return make_headers(app, "CUSTOMER")


def make_headers(app, role):
    with app.app_context():
        token = create_access_token(
            identity="1",
            additional_claims={"role": role},
        )
    return {"Authorization": f"Bearer {token}"}


def user_data(**kwargs): #Nhận nhiều tham số dạng key=value không giới hạn số lượng
    data = {
        "UserID": 1,
        "Username": "admin",
        "Email": "admin@gmail.com",
        "Phone": "0901234567",
        "Role": "ADMIN",
    }
    data.update(kwargs)
    return data

# Xem danh sách user thành công
@patch(f"{USER_SERVICE_PATH}.get_all_users")
def test_get_users_success(mock_get_all, client, admin_headers):
    mock_get_all.return_value = [
        user_data(),
        user_data(UserID=2, Username="staff", Role="STAFF"),
    ]

    response = client.get(USERS_URL, headers=admin_headers)
    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert data[0]["Username"] == "admin"
    assert data[1]["Role"] == "STAFF"
    mock_get_all.assert_called_once_with()


#Chặn xem user khi không phải ADMIN
@patch(f"{USER_SERVICE_PATH}.get_all_users")
def test_get_users_forbidden(mock_get_all, client, customer_headers):
    response = client.get(USERS_URL, headers=customer_headers)
    data = response.get_json()

    assert response.status_code == 403
    assert data["message"] == "Quyen nay cua Admin!"
    mock_get_all.assert_not_called()

#Chặn xem user khi thiếu token
@patch(f"{USER_SERVICE_PATH}.get_all_users")
def test_get_users_missing_token(mock_get_all, client):
    response = client.get(USERS_URL)
    data = response.get_json()

    assert response.status_code == 401
    assert "msg" in data
    mock_get_all.assert_not_called()


# UPDATE
@pytest.mark.parametrize(
    "form_data",
    [
        {"Username": "new_admin"},
        {"Role": "STAFF"},
        {"Role": "ADMIN"},
        {"Phone": "0912345678"},
    ],
)

# Cập nhật thông tin user thành công
# Cập nhật role user sang STAFF
# Cập nhật role user sang ADMIN
# Cập nhật chỉ một trường user (nếu có từng field riêng)
@patch(f"{USER_SERVICE_PATH}.update_user")
def test_update_user_success(mock_update, client, admin_headers, form_data):
    mock_update.return_value = user_data()

    response = client.put(f"{USERS_URL}/1", data=form_data, headers=admin_headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "Cap nhat user thanh cong!"
    mock_update.assert_called_once_with(1, form_data)


#Cập nhật user không tồn tại
@patch(f"{USER_SERVICE_PATH}.update_user")
def test_update_user_not_found(mock_update, client, admin_headers):
    mock_update.return_value = None

    response = client.put(
        f"{USERS_URL}/999",
        data={"Username": "not_found"},
        headers=admin_headers,
    )
    data = response.get_json()

    assert response.status_code == 404
    assert data["message"] == "Khong tim thay nguoi dung"
    mock_update.assert_called_once_with(999, {"Username": "not_found"})


# Chặn cập nhật user khi không phải ADMIN
@patch(f"{USER_SERVICE_PATH}.update_user")
def test_update_user_forbidden(mock_update, client, customer_headers):
    response = client.put(
        f"{USERS_URL}/1",
        data={"Username": "customer_update"},
        headers=customer_headers,
    )
    data = response.get_json()

    assert response.status_code == 403
    assert data["message"] == "Quyen nay cua Admin!"
    mock_update.assert_not_called()


# Xóa user thành công
@patch(f"{USER_SERVICE_PATH}.delete_user")
def test_delete_user_success(mock_delete, client, admin_headers):
    mock_delete.return_value = True

    response = client.delete(f"{USERS_URL}/1", headers=admin_headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "Xoa nguoi dung thanh cong!"
    mock_delete.assert_called_once_with(1)

# Xóa user không tồn tại
@patch(f"{USER_SERVICE_PATH}.delete_user")
def test_delete_user_not_found(mock_delete, client, admin_headers):
    mock_delete.return_value = False

    response = client.delete(f"{USERS_URL}/999", headers=admin_headers)
    data = response.get_json()

    assert response.status_code == 404
    assert data["message"] == "Loi khi xoa nguoi dung"
    mock_delete.assert_called_once_with(999)

# Chặn xóa user khi không phải ADMIN
@patch(f"{USER_SERVICE_PATH}.delete_user")
def test_delete_user_forbidden(mock_delete, client, customer_headers):
    response = client.delete(f"{USERS_URL}/1", headers=customer_headers)
    data = response.get_json()

    assert response.status_code == 403
    assert data["message"] == "Quyen nay cua Admin!"
    mock_delete.assert_not_called()

# Cập nhật email không hợp lệ
@patch(f"{USER_SERVICE_PATH}.update_user")
def test_update_user_invalid_email_format(mock_update, client, admin_headers):
    payload = {"Email": "invalid-email"}
    mock_update.return_value = ({"message": "Email khong hop le"}, 400)

    response = client.put(f"{USERS_URL}/1", data=payload, headers=admin_headers)
    data = response.get_json()

    assert response.status_code == 400
    assert "message" in data
    mock_update.assert_called_once_with(1, payload)

# Cập nhật phone quá 11 ký tự
@patch(f"{USER_SERVICE_PATH}.update_user")
def test_update_user_phone_too_long(mock_update, client, admin_headers):
    payload = {"Phone": "091234567890"}
    mock_update.return_value = ({"message": "Phone khong hop le"}, 400)

    response = client.put(f"{USERS_URL}/1", data=payload, headers=admin_headers)
    data = response.get_json()

    assert response.status_code == 400
    assert "message" in data
    mock_update.assert_called_once_with(1, payload)

# Cập nhật username trống
@patch(f"{USER_SERVICE_PATH}.update_user")
def test_update_user_empty_username(mock_update, client, admin_headers):
    payload = {"Username": ""}
    mock_update.return_value = ({"message": "Username khong duoc de trong"}, 400)

    response = client.put(f"{USERS_URL}/1", data=payload, headers=admin_headers)
    data = response.get_json()

    assert response.status_code == 400
    assert "message" in data
    mock_update.assert_called_once_with(1, payload)

# Không hiển thị password trong danh sách user
@patch(f"{USER_SERVICE_PATH}.get_all_users")
def test_get_users_not_show_password(mock_get_all, client, admin_headers):
    mock_get_all.return_value = [
        {
            "UserID": 1,
            "Username": "admin",
            "Email": "admin@gmail.com",
            "Phone": "0901234567",
            "Role": "ADMIN",
        },
        {
            "UserID": 2,
            "Username": "staff",
            "Email": "staff@gmail.com",
            "Phone": "0911111111",
            "Role": "STAFF",
        },
    ]

    response = client.get(USERS_URL, headers=admin_headers)
    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data, list)
    for user in data:
        assert "Password" not in user
    mock_get_all.assert_called_once_with()

# Cập nhật chỉ một trường user (nếu có từng field riêng)
@patch(f"{USER_SERVICE_PATH}.update_user")
def test_update_user_only_one_field_phone(mock_update, client, admin_headers):
    payload = {"Phone": "0912345678"}
    mock_update.return_value = user_data(Phone="0912345678")

    response = client.put(f"{USERS_URL}/1", data=payload, headers=admin_headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "Cap nhat user thanh cong!"
    mock_update.assert_called_once_with(1, payload)

# Reload danh sách sau cập nhật
@patch(f"{USER_SERVICE_PATH}.get_all_users")
@patch(f"{USER_SERVICE_PATH}.update_user")
def test_reload_users_list_after_update(mock_update, mock_get_all, client, admin_headers):
    update_payload = {"Phone": "0912345678"}
    mock_update.return_value = user_data(Phone="0912345678")
    mock_get_all.return_value = [
        user_data(Phone="0912345678"),
        user_data(UserID=2, Username="staff", Role="STAFF"),
    ]

    update_response = client.put(f"{USERS_URL}/1", data=update_payload, headers=admin_headers)
    get_response = client.get(USERS_URL, headers=admin_headers)
    get_data = get_response.get_json()

    assert update_response.status_code == 200
    assert get_response.status_code == 200
    assert isinstance(get_data, list)
    assert get_data[0]["Phone"] == "0912345678"
    mock_update.assert_called_once_with(1, update_payload)
    mock_get_all.assert_called_once_with()

# Đăng xuất khỏi màn quản lý user
def test_logout_from_user_management(client):
    response = client.post(LOGOUT_URL)
    if response.status_code == 405:
        response = client.get(LOGOUT_URL)
    data = response.get_json()

    assert response.status_code == 200
    assert "message" in data
