import pytest
from flask_jwt_extended import create_access_token
from backend.core import create_app
from backend.app.api.v1.admin.service import CuisineService

@pytest.fixture
def client():
    # Khởi tạo app test
    app = create_app()
    app.config.update(TESTING=True, JWT_SECRET_KEY="test-secret")
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    # Mock admin headers
    with client.application.app_context():
        token = create_access_token(identity="1", additional_claims={"role": "ADMIN"})
    return {"Authorization": f"Bearer {token}"}

# 1-4. Test thêm mới Cuisine
@pytest.mark.parametrize("input_data, mock_return, expected_status", [
    ({"CuisineName": "Hấp"}, ({"message": "Thêm thành công"}, 201), 201),                                                   # 1. Thành công
    ({"CuisineName": ""}, ({"message": "Tên loại ẩm thực không được để trống"}, 400), 400),                                 # 2. Trống tên
    ({"CuisineName": "Mon An 123"}, ({"message": "Tên loại ẩm thực không được chứa số hoặc ký tự đặc biệt"}, 400), 400),     # 3. Ký tự lạ/Số
    ({"CuisineName": "Lẩu"}, ({"message": "Loại ẩm thực đã tồn tại"}, 400), 400),                                           # 4. Đã tồn tại
])
def test_create_cuisine(client, auth_headers, monkeypatch, input_data, mock_return, expected_status):
    monkeypatch.setattr(CuisineService, "create", lambda data: mock_return)
    res = client.post("/api/v1/admin/cuisines", data=input_data, headers=auth_headers)
    assert res.status_code == expected_status
    assert res.get_json() == mock_return[0]

# 5. Test lấy danh sách Cuisine
def test_get_all_cuisines(client, auth_headers, monkeypatch):
    mock_data = [{"CuisineID": 1, "CuisineName": "Lẩu"}]
    monkeypatch.setattr(CuisineService, "get_all", lambda: (mock_data, 200))
    res = client.get("/api/v1/admin/cuisines", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json() == mock_data

# 6-8. Test cập nhật Cuisine
@pytest.mark.parametrize("cuisine_id, input_data, mock_return, expected_status", [
    (1, {"CuisineName": "Asian Food"}, ({"message": "Cập nhật thành công"}, 200), 200), # 6. Thành công
    (99, {"CuisineName": "Test"}, ({"message": "Không tìm thấy"}, 404), 404),          # 7. ID không tồn tại
    (1, {"CuisineName": "Food@!"}, ({"message": "Tên loại ẩm thực không được chứa số hoặc ký tự đặc biệt"}, 400), 400),    # 8. Tên sai định dạng
])
def test_update_cuisine(client, auth_headers, monkeypatch, cuisine_id, input_data, mock_return, expected_status):
    monkeypatch.setattr(CuisineService, "update", lambda cid, data: mock_return)
    res = client.put(f"/api/v1/admin/cuisines/{cuisine_id}", data=input_data, headers=auth_headers)
    assert res.status_code == expected_status
    assert res.get_json() == mock_return[0]

# 9-10. Test xóa Cuisine
@pytest.mark.parametrize("cuisine_id, mock_return, expected_status", [
    (1, ({"message": "Da xoa xong"}, 200), 200),   # 9. Thành công
    (99, ({"message": "Khong tim thay"}, 404), 404),  # 10. Không tồn tại
])
def test_delete_cuisine(client, auth_headers, monkeypatch, cuisine_id, mock_return, expected_status):
    monkeypatch.setattr(CuisineService, "delete", lambda cid: mock_return)
    res = client.delete(f"/api/v1/admin/cuisines/{cuisine_id}", headers=auth_headers)
    assert res.status_code == expected_status
    assert res.get_json() == mock_return[0]
