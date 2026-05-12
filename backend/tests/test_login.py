import sys
from pathlib import Path

import pytest
from flask import jsonify
from flask_jwt_extended import create_access_token

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from backend.core import create_app
from backend.app.api.v1.auth.service import AuthService

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client()

@pytest.mark.parametrize("input_data, mock_response, expected_status", [
    # 1. Thành công
    ({"username": "admin", "password": "123456"}, {"message": "Đăng nhập thành công", "access_token": "token_123"}, 200),
    # 2. Sai mật khẩu
    ({"username": "admin", "password": "1"}, {"message": "Sai mật khẩu"}, 401),
    # 3. Trống username
    ({"username": "", "password": "123456"}, {"message": "username không được để trống"}, 400),
    # 4. Trống password
    ({"username": "admin", "password": ""}, {"message": "password không được để trống"}, 400),
    # 5. Sai tài khoản
    ({"username": "sai", "password": "123456"}, {"message": "Sai tài khoản"}, 404),
    # 6. STAFF đăng nhập
    ({"username": "restaurant1", "password": "1"}, {"message": "Đăng nhập thành công", "role": "STAFF", "access_token": "token_456"}, 200),
    # 7. Sai tài khoản hoặc mật khẩu
    ({"username": "sai", "password": "1234"}, {"message": "Sai tài khoản hoặc mật khẩu"}, 401),
    # 8. Dữ liệu null
    ({"username": "", "password": ""}, {"message": "Vui lòng nhập tài khoản và mật khẩu"}, 400),
    # 9. Chứa khoảng trắng thừa
    ({"username": " admin ", "password": " 123456 "}, {"message": "Sai tài khoản hoặc mật khẩu"}, 401),
])
def test_login(client, monkeypatch, input_data, mock_response, expected_status):
    # Dùng monkeypatch để mock AuthService.login trả về kết quả mong muốn
    monkeypatch.setattr(AuthService, "login", lambda u, p: (mock_response, expected_status))
    
    # Gửi request POST tới API login
    response = client.post("/api/v1/auth/login", data=input_data)
    
    # Kiểm tra status code và nội dung trả về
    assert response.status_code == expected_status
    assert response.get_json() == mock_response
