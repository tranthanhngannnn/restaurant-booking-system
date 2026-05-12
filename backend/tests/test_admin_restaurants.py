import pytest
from flask_jwt_extended import create_access_token
from backend.core import create_app
from backend.app.api.v1.admin.service import AdminRestaurantService as AdminResSrv
from backend.app.api.v1.restaurant.service import RestaurantService

@pytest.fixture
def client():
    app = create_app()
    app.config.update(TESTING=True, JWT_SECRET_KEY="test-secret")
    return app.test_client()

@pytest.fixture
def admin_token(client):
    with client.application.app_context():
        return {"Authorization": f"Bearer {create_access_token(identity='1', additional_claims={'role': 'ADMIN'})}"}

@pytest.fixture
def staff_token(client):
    with client.application.app_context():
        return {"Authorization": f"Bearer {create_access_token(identity='2', additional_claims={'role': 'STAFF'})}"}

# 1-2. GET Scenarios
@pytest.mark.parametrize("status, mock_val", [
    (None, [{"id": 1}]),      # 1. Lấy toàn bộ
    ("Active", [{"id": 1}])   # 2. Lọc theo status
])
def test_get_restaurants(client, admin_token, monkeypatch, status, mock_val):
    monkeypatch.setattr(AdminResSrv, "get_all_restaurants", lambda status=None: mock_val)
    res = client.get("/api/v1/admin/restaurants", query_string={"status": status}, headers=admin_token)
    assert res.status_code == 200

# 3-18. Action Scenarios (Update, Approve, Reject, Delete)
@pytest.mark.parametrize("method, url, payload, mock_ret, expected_status", [
    ("PUT", "/api/v1/admin/restaurants/1", {"RestaurantName": "Lẩu băng chuyền"}, ({"msg": "OK"}, 200), 200),                                            # 3. Update OK
    ("PUT", "/api/v1/admin/restaurants/99", {"RestaurantName": "Chi nhánh 1"}, ({"msg": "Không tìm thấy nhà hàng"}, 404), 404),                          # 4. Update 404
    ("PUT", "/api/v1/admin/restaurants/3", {"RestaurantName": " "}, ({"msg": "Tên nhà hàng không được để trống"}, 400), 400),                          # 5. Update tên trống
    ("PUT", "/api/v1/admin/restaurants/3", {"RestaurantName": "Hotpot @ 123"}, ({"msg": "Tên nhà hàng không hợp lệ"}, 400), 400),                          # 6. Update tên lạ
    ("PUT", "/api/v1/admin/restaurants/3", {"Phone": ""}, ({"msg": "Số điện thoại không được để trống"}, 400), 400),                                   # 7. Update Phone trống
    ("PUT", "/api/v1/admin/restaurants/3", {"Phone": "123456789"}, ({"msg": "Số điện thoại phải là định dạng số, đúng 10 chữ số và bắt đầu bằng số 0"}, 400), 400), # 8. Update Phone sai
    ("PUT", "/api/v1/admin/restaurants/3", {"Address": ""}, ({"msg": "Địa chỉ không được để trống"}, 400), 400),                                         # 9. Update Địa chỉ trống
    ("PUT", "/api/v1/admin/restaurants/3", {"Address": "HCM !!!"}, ({"msg": "Khong tim thay"}, 400), 400),                                               # 10. Update Địa chỉ lạ
    ("PUT", "/api/v1/admin/restaurants/3", {"Email": "contact_hotpot.vn"}, ({"msg": "Email không hợp lệ"}, 400), 400),                                 # 11. Update Email sai
    ("PUT", "/api/v1/admin/restaurants/1", {"description": "New"}, ({"msg": "OK"}, 200), 200),                                                         # 12. Update mô tả OK
    ("PUT", "/api/v1/admin/restaurants/1/approve", {}, ({"msg": "Duyệt thành công!"}, 200), 200),                                                      # 13. Duyệt OK
    ("PUT", "/api/v1/admin/restaurants/99/approve", {}, ({"msg": "Không tìm thấy nhà hàng"}, 404), 404),                                               # 14. Duyệt 404
    ("PUT", "/api/v1/admin/restaurants/1/reject", {}, ({"msg": "Từ chối thành công!"}, 200), 200),                                                     # 15. Từ chối OK
    ("PUT", "/api/v1/admin/restaurants/99/reject", {}, ({"msg": "Không tìm thấy nhà hàng"}, 404), 404),                                                # 16. Từ chối 404
    ("DELETE", "/api/v1/admin/restaurants/1", {}, ({"msg": "OK"}, 200), 200),                                                                          # 17. Xóa OK
    ("DELETE", "/api/v1/admin/restaurants/99", {}, ({"msg": "Không tìm thấy nhà hàng"}, 404), 404),                                                    # 18. Xóa 404
])
def test_restaurant_actions(client, admin_token, monkeypatch, method, url, payload, mock_ret, expected_status):
    monkeypatch.setattr(AdminResSrv, "update_restaurant", lambda id, data, img: mock_ret)
    monkeypatch.setattr(AdminResSrv, "approve", lambda id: mock_ret)
    monkeypatch.setattr(AdminResSrv, "reject", lambda id: mock_ret)
    monkeypatch.setattr(AdminResSrv, "delete_restaurant", lambda id: mock_ret)
    res = client.open(url, method=method, data=payload, headers=admin_token)
    assert res.status_code == expected_status

# 19-33. Create Scenarios (POST)
@pytest.mark.parametrize("url, payload, mock_ret, expected_status, use_admin", [
    ("/api/v1/restaurants/registerRestaurant", {"RestaurantName": "Nhà Hàng Mới"}, ({"id": 2}, 201), 201, False),                                                   # 19. Register
    ("/api/v1/admin/restaurants", {"RestaurantName": "Nhà Hàng Mới"}, ({"id": 1}, 201), 201, True),                                                                 # 20. Admin Add
    ("/api/v1/admin/restaurants", {"RestaurantName": ""}, ({"msg": "Tên nhà hàng không được để trống"}, 400), 400, True),                                           # 21. Tên trống
    ("/api/v1/admin/restaurants", {"RestaurantName": "BBQ @ Home"}, ({"msg": "Tên nhà hàng chứa kí tự không hợp lệ"}, 400), 400, True),                             # 22. Tên lạ
    ("/api/v1/admin/restaurants", {"Address": ""}, ({"msg": "Địa chỉ không được để trống"}, 400), 400, True),                                                       # 23. Địa chỉ trống
    ("/api/v1/admin/restaurants", {"Address": "123 CMT8 #$%"}, ({"msg": "Địa chỉ chứa kí tự không hợp lệ"}, 400), 400, True),                                       # 24. Địa chỉ lạ
    ("/api/v1/admin/restaurants", {"Phone": "091234567"}, ({"msg": "Số điện thoại phải là định dạng số, đúng 10 chữ số và bắt đầu bằng số 0"}, 400), 400, True),    # 25. SĐT ngắn
    ("/api/v1/admin/restaurants", {"Phone": "1912345678"}, ({"msg": "Số điện thoại phải là định dạng số, đúng 10 chữ số và bắt đầu bằng số 0"}, 400), 400, True),   # 26. Đầu ko 0
    ("/api/v1/admin/restaurants", {"Phone": "090123456a"}, ({"msg": "Số điện thoại phải là định dạng số, đúng 10 chữ số và bắt đầu bằng số 0"}, 400), 400, True),   # 27. Phone chữ
    ("/api/v1/admin/restaurants", {"Email": "contact_hotpot.vn"}, ({"msg": "Email không hợp lệ"}, 400), 400, True),                                                 # 28. Thiếu domain
    ("/api/v1/admin/restaurants", {"Email": "contact@d"}, ({"msg": "Email không hợp lệ"}, 400), 400, True),                                                         # 29. Email sai
    ("/api/v1/admin/restaurants", {"description": ""}, ({"msg": "Mô tả không hợp lệ và không được để trống"}, 400), 400, True),                                     # 30. Mô tả trống
    ("/api/v1/admin/restaurants", {"description": "Ngon lắm !!!"}, ({"msg": "Mô tả không hợp lệ và không được để trống"}, 400), 400, True),                         # 31. Mô tả lạ
    ("/api/v1/admin/restaurants", {"RestaurantName": " Hotpot "}, ({"id": 2}, 201), 201, True),                                                                     # 32. Trim
    ("/api/v1/admin/restaurants", {"UserID": 12, "CuisineID": 1}, ({"id": 1}, 201), 201, True),                                                                     # 33. Keys
])
def test_create_restaurant(client, admin_token, staff_token, monkeypatch, url, payload, mock_ret, expected_status, use_admin):
    monkeypatch.setattr(RestaurantService, "create", lambda data, is_admin=False: mock_ret)
    res = client.post(url, data=payload, headers=admin_token if use_admin else staff_token)
    assert res.status_code == expected_status
