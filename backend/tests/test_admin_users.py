import pytest
from flask_jwt_extended import create_access_token
from backend.core import create_app
from backend.app.api.v1.admin.service import AdminUserService

@pytest.fixture
def client():
    # Setup Flask app cho testing
    app = create_app()
    app.config.update(TESTING=True, JWT_SECRET_KEY="test-secret")
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    # Tạo JWT Token Role ADMIN để vượt qua kiểm tra phân quyền
    with client.application.app_context():
        token = create_access_token(identity="1", additional_claims={"role": "ADMIN"})
    return {"Authorization": f"Bearer {token}"}

# 1. Test lấy danh sách user
def test_get_all_users(client, auth_headers, monkeypatch):
    monkeypatch.setattr(AdminUserService, "get_all_users", lambda: [{"UserID": 1, "Username": "admin"}])
    res = client.get("/api/v1/admin/users", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.get_json()) == 1

# 2-7. Test cập nhật user (Parametrize 6 trường hợp)
@pytest.mark.parametrize("user_id, input_data, mock_return, expected_status", [
    (1, {"Email": "new@gmail.com"}, {"UserID": 1}, 200),               # 2. Cập nhật thành công
    (99, {"Username": "test"}, None, 404),                          # 3. User không tồn tại
    (2, {"Role": "STAFF", "RestaurantID": "6"}, {"UserID": 2}, 200), # 4. Gán STAFF + ResID
    (2, {"Role": "CUSTOMER"}, {"UserID": 2}, 200),               # 5. Role khác STAFF (ResID -> None)
    (1, {"UnknownField": "value"}, {"UserID": 1}, 200),            # 6. Trường dữ liệu lạ
    (2, {"Role": "STAFF"}, {"UserID": 2}, 200),               # 7. Update Role STAFF thiếu RestaurantID
])
def test_update_user(client, auth_headers, monkeypatch, user_id, input_data, mock_return, expected_status):
    monkeypatch.setattr(AdminUserService, "update_user", lambda uid, data: mock_return)
    res = client.put(f"/api/v1/admin/users/{user_id}", data=input_data, headers=auth_headers)
    assert res.status_code == expected_status

# 8-9. Test xóa user (Parametrize 2 trường hợp)
@pytest.mark.parametrize("user_id, mock_return, expected_status", [
    (1, True, 200),  # 8. Xóa thành công
    (99, False, 404) # 9. Xóa thất bại/Không tồn tại
])
def test_delete_user(client, auth_headers, monkeypatch, user_id, mock_return, expected_status):
    monkeypatch.setattr(AdminUserService, "delete_user", lambda uid: mock_return)
    res = client.delete(f"/api/v1/admin/users/{user_id}", headers=auth_headers)
    assert res.status_code == expected_status
