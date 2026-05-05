from flask import Blueprint, request, jsonify, session

from backend.app.api.v1.auth.service import AuthService  # Import class logic từ file service

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/registerRequest', methods=['POST'])
def register():
    # Lấy toàn bộ dữ liệu từ Form gửi lên
    data = {
        "username": request.form.get('username'),
        "password": request.form.get('password'),
        "email": request.form.get('email'),
        "phone": request.form.get('phone'),
        "role": request.form.get('role'),
        "restaurant_id": request.form.get('restaurant_id')
    }

    # Đẩy data qua Service xử lý
    result, status_code = AuthService.register(data)

    return jsonify(result), status_code


@auth_bp.route('/login', methods=['POST'])
def login():
    # Bước 1: Lấy dữ liệu từ Form
    username = request.form.get('username')
    password = request.form.get('password')

    # Bước 2: Đẩy dữ liệu cho Service xử lý và nhận kết quả
    result, status_code = AuthService.login(username, password)

    # Bước 3: Trả về kết quả cho Client thông qua jsonify
    return jsonify(result), status_code

@auth_bp.route("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Đã đăng xuất"})

