import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from flask_jwt_extended import create_access_token

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from backend.core import create_app

ADMIN_RESTAURANTS_URL = "/api/v1/admin/restaurants"
REGISTER_RESTAURANT_URL = "/api/v1/restaurants/registerRestaurant"

ADMIN_SERVICE_PATH = "app.api.v1.admin.routes.AdminRestaurantService"
ADMIN_CREATE_PATH = "app.api.v1.admin.routes.RestaurantService.create"
STAFF_REGISTER_PATH = "app.api.v1.restaurant.routes.RestaurantService.create"


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
def staff_headers(app):
    return make_headers(app, "STAFF")


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


def restaurant_data(**kwargs):
    data = {
        "RestaurantID": 1,
        "RestaurantName": "Nha Hang Sen",
        "Address": "123 Le Loi",
        "Phone": "0901234567",
        "Email": "sen@gmail.com",
        "status": "Dang hoat dong",
    }
    data.update(kwargs)
    return data


def restaurant_form(**kwargs):
    data = {
        "RestaurantName": "Nha Hang Sen",
        "Address": "123 Le Loi",
        "Phone": "0901234567",
        "Email": "sen@gmail.com",
        "Opentime": "08:00",
        "Closetime": "22:00",
        "description": "Nha hang gia dinh",
        "CuisineID": "1",
    }
    data.update(kwargs)
    return data


def post_restaurant(client, headers, data=None):
    return client.post(
        ADMIN_RESTAURANTS_URL,
        data=data or restaurant_form(),
        headers=headers,
    )


#Xem danh sách nhà hàng thành công
@patch(f"{ADMIN_SERVICE_PATH}.get_all_restaurants")
def test_get_restaurants_success(mock_get_all, client):
    mock_get_all.return_value = [restaurant_data()]

    response = client.get(ADMIN_RESTAURANTS_URL)
    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert data[0]["RestaurantName"] == "Nha Hang Sen"
    mock_get_all.assert_called_once_with()


#Lọc nhà hàng theo trạng thái
@patch(f"{ADMIN_SERVICE_PATH}.get_all_restaurants")
def test_get_restaurants_filter_by_status(mock_get_all, client):
    mock_get_all.return_value = [restaurant_data(status="Dang cho duyet")]

    response = client.get(
        ADMIN_RESTAURANTS_URL,
        query_string={"status": "Dang cho duyet"},
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data[0]["status"] == "Dang cho duyet"
    mock_get_all.assert_called_once_with(status="Dang cho duyet")



#Thêm nhà hàng bởi admin thành công
@patch(ADMIN_CREATE_PATH)
def test_create_restaurant_success(mock_create, client, admin_headers):
    mock_create.return_value = ({"message": "Tao thanh cong!"}, 201)

    response = post_restaurant(client, admin_headers)
    data = response.get_json()

    assert response.status_code == 201
    assert data["message"] == "Tao thanh cong!"
    mock_create.assert_called_once_with(restaurant_form(), is_admin=True)


# Không thêm nhà hàng khi bỏ trống tên
@patch(ADMIN_CREATE_PATH)
def test_create_restaurant_missing_name(mock_create, client, admin_headers):
    form_data = restaurant_form(RestaurantName="")
    mock_create.return_value = ({"message": "Ten nha hang khong duoc de trong"}, 400)

    response = post_restaurant(client, admin_headers, form_data)
    data = response.get_json()

    assert response.status_code == 400
    assert "message" in data
    mock_create.assert_called_once_with(form_data, is_admin=True)


@pytest.mark.parametrize(
    "form_data",
    [
        restaurant_form(Email="email-sai-dinh-dang"),
        restaurant_form(Phone="012345678901"),
    ],
)

# Thêm nhà hàng với email sai định dạng
# Thêm nhà hàng với phone quá 11 ký tự
# Thêm nhà hàng giờ mở cửa sau giờ đóng cửa
@patch(ADMIN_CREATE_PATH)
def test_create_restaurant_invalid_data(mock_create, client, admin_headers, form_data):
    mock_create.return_value = ({"message": "Du lieu khong hop le"}, 400)

    response = post_restaurant(client, admin_headers, form_data)
    data = response.get_json()

    assert response.status_code == 400
    assert "message" in data
    mock_create.assert_called_once_with(form_data, is_admin=True)


# Cập nhật nhà hàng thành công
@patch(f"{ADMIN_SERVICE_PATH}.update_restaurant")
def test_update_restaurant_success(mock_update, client, admin_headers):
    update_mock = MagicMock(return_value=restaurant_data(RestaurantName="Nha Hang Moi"))
    mock_update.side_effect = update_mock

    response = client.put(
        f"{ADMIN_RESTAURANTS_URL}/1",
        data={"RestaurantName": "Nha Hang Moi"},
        headers=admin_headers,
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "Cap nhat thanh cong!"
    update_mock.assert_called_once_with(1, {"RestaurantName": "Nha Hang Moi"}, None)

# Cập nhật nhà hàng không tồn tại
@patch(f"{ADMIN_SERVICE_PATH}.update_restaurant")
def test_update_restaurant_not_found(mock_update, client, admin_headers):
    mock_update.return_value = None

    response = client.put(
        f"{ADMIN_RESTAURANTS_URL}/999",
        data={"RestaurantName": "Khong Ton Tai"},
        headers=admin_headers,
    )
    data = response.get_json()

    assert response.status_code == 404
    assert data["message"] == "Khong tim thay nha hang"
    mock_update.assert_called_once_with(999, {"RestaurantName": "Khong Ton Tai"}, None)

# Duyệt nhà hàng đang chờ
@patch(f"{ADMIN_SERVICE_PATH}.approve")
def test_approve_restaurant_success(mock_approve, client, admin_headers):
    mock_approve.return_value = ({"message": "Da duyet thanh cong!"}, 200)

    response = client.put(f"{ADMIN_RESTAURANTS_URL}/1/approve", headers=admin_headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "Da duyet thanh cong!"
    mock_approve.assert_called_once_with(1)

# Chặn duyệt nhà hàng khi không phải ADMIN
@patch(f"{ADMIN_SERVICE_PATH}.approve")
def test_approve_restaurant_forbidden(mock_approve, client, staff_headers):
    response = client.put(f"{ADMIN_RESTAURANTS_URL}/1/approve", headers=staff_headers)
    data = response.get_json()

    assert response.status_code == 403
    assert data["message"] == "Chi Admin moi duyet duoc!"
    mock_approve.assert_not_called()


# Từ chối nhà hàng đang chờ
@patch(f"{ADMIN_SERVICE_PATH}.reject")
def test_reject_restaurant_success(mock_reject, client, admin_headers):
    mock_reject.return_value = ({"message": "Da tu choi!"}, 200)

    response = client.put(f"{ADMIN_RESTAURANTS_URL}/1/reject", headers=admin_headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "Da tu choi!"
    mock_reject.assert_called_once_with(1)

# Ẩn nhà hàng bằng thao tác xóa
@patch(f"{ADMIN_SERVICE_PATH}.delete_restaurant")
def test_delete_restaurant_success(mock_delete, client, admin_headers):
    mock_delete.return_value = {"message": "Da an nha hang thanh cong!", "code": 200}

    response = client.delete(f"{ADMIN_RESTAURANTS_URL}/1", headers=admin_headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "Da an nha hang thanh cong!"
    mock_delete.assert_called_once_with(1)


# Xóa nhà hàng không tồn tại
@patch(f"{ADMIN_SERVICE_PATH}.delete_restaurant")
def test_delete_restaurant_not_found(mock_delete, client, admin_headers):
    mock_delete.return_value = {"message": "Khong tim thay nha hang", "code": 404}

    response = client.delete(f"{ADMIN_RESTAURANTS_URL}/999", headers=admin_headers)
    data = response.get_json()

    assert response.status_code == 404
    assert data["message"] == "Khong tim thay nha hang"
    mock_delete.assert_called_once_with(999)


#Đăng ký nhà hàng bởi STAFF chờ duyệt
@patch(STAFF_REGISTER_PATH)
def test_staff_register_restaurant_success(mock_create, client, staff_headers):
    mock_create.return_value = (
        {"message": "Tao thanh cong! Trang thai hien tai: Dang cho duyet"},
        201,
    )

    response = client.post(
        REGISTER_RESTAURANT_URL,
        data=restaurant_form(),
        headers=staff_headers,
    )
    data = response.get_json()

    expected_data = restaurant_form(UserID="1")

    assert response.status_code == 201
    assert "message" in data
    assert "cho duyet" in data["message"].lower()
    mock_create.assert_called_once_with(expected_data, is_admin=False)


# CUSTOMER không được phép đăng ký nhà hàng
@patch(STAFF_REGISTER_PATH)
def test_staff_register_restaurant_forbidden_customer(mock_create, client, customer_headers):
    response = client.post(
        REGISTER_RESTAURANT_URL,
        data=restaurant_form(),
        headers=customer_headers,
    )
    data = response.get_json()

    assert response.status_code == 403
    assert "message" in data
    mock_create.assert_not_called()
