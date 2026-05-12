import pytest
from backend.core import create_app
from backend.app.api.v1.auth.service import AuthService

@pytest.fixture
def client():
    # Khởi tạo app test
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client()

@pytest.mark.parametrize("input_data, mock_response, expected_status", [
    # 1. Đăng ký thành công
    ({"username": "ngan11", "password": "123", "phone": "0901234567", "email": "n@gmail.com", "role": "CUSTOMER"}, 
     {"message": "Đăng ký thành công", "user_id": 101}, 201),
    
    # 2. Username từ 3-20 ký tự (Trường hợp quá ngắn)
    ({"username": "ng", "password": "123", "phone": "0901234567", "email": "n@gmail.com", "role": "CUSTOMER"}, 
     {"message": "Username phải từ 3 đến 20 ký tự"}, 400),
    
    # 3. Username chỉ chứa chữ và số (Trường hợp chứa ký tự đặc biệt)
    ({"username": "ngan @!", "password": "123", "phone": "0901234567", "email": "n@gmail.com", "role": "STAFF"}, 
     {"message": "Username chỉ được chứa chữ cái và số"}, 400),
    
    # 4. Tên đăng nhập đã tồn tại (Conflict)
    ({"username": "admin", "password": "123", "phone": "0901234567", "email": "n@gmail.com", "role": "STAFF"}, 
     {"message": "Tên đăng nhập đã tồn tại"}, 409),
    
    # 5. Password không chứa khoảng trắng
    ({"username": "ngan11", "password": "123 456", "phone": "0901234567", "email": "n@gmail.com", "role": "STAFF"}, 
     {"message": "Mật khẩu không được chứa khoảng trắng"}, 400),
    
    # 6. SĐT chỉ chứa chữ số
    ({"username": "ngan11", "password": "123", "phone": "090abc", "email": "n@gmail.com", "role": "STAFF"}, 
     {"message": "Số điện thoại chỉ được chứa chữ số"}, 400),
    
    # 7. SĐT phải có 10-11 số
    ({"username": "ngan11", "password": "123", "phone": "090123", "email": "n@gmail.com", "role": "STAFF"}, 
     {"message": "Số điện thoại phải có 10-11 chữ số"}, 400),
    
    # 8. SĐT bắt đầu bằng số 0
    ({"username": "ngan11", "password": "123", "phone": "9991234567", "email": "n@gmail.com", "role": "STAFF"}, 
     {"message": "Số điện thoại phải bắt đầu bằng số 0"}, 400),
    
    # 9. Email sai định dạng
    ({"username": "ngan11", "password": "123", "phone": "0901234567", "email": "ngan_gmail.com", "role": "STAFF"}, 
     {"message": "Định dạng email không hợp lệ"}, 400),
])
def test_register(client, monkeypatch, input_data, mock_response, expected_status):
    # Mock AuthService.register trả về dữ liệu tương ứng theo từng case
    monkeypatch.setattr(AuthService, "register", lambda data: (mock_response, expected_status))
    
    # Gửi request POST tới API registerRequest
    response = client.post("/api/v1/auth/registerRequest", data=input_data)
    
    # Kiểm tra Status Code và nội dung phản hồi
    assert response.status_code == expected_status
    assert response.get_json() == mock_response