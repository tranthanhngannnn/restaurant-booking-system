import re
from backend.models.user import User
from backend.core.extensions import db
from flask_jwt_extended import create_access_token
from datetime import timedelta

class AuthService:
    @staticmethod
    def register(data):
        # 1. Lấy và Trim dữ liệu
        username = str(data.get('username', '')).strip()
        email = str(data.get('email', '')).strip()
        phone = str(data.get('phone', '')).strip()
        password = str(data.get('password', '')).strip()
        role = data.get('role', 'CUSTOMER')

        # 2. Validate Username: 3-20 ký tự, chỉ chữ và số
        if not (3 <= len(username) <= 20):
            return {"message": "Username phải từ 3 đến 20 ký tự"}, 400
        if not username.isalnum():
            return {"message": "Username chỉ được chứa chữ cái và số, không có ký tự đặc biệt hoặc khoảng trắng"}, 400

        # 3. Validate Password: Không khoảng trắng, ít nhất 1 ký tự
        raw_password = str(data.get('password', ''))
        if " " in raw_password:
            return {"message": "Mật khẩu không được chứa khoảng trắng"}, 400
        if len(password) < 1:
            return {"message": "Mật khẩu không được để trống"}, 400

        # 4. Validate Phone: Số, 10-11 chữ số, bắt đầu bằng 0
        if not phone.isdigit():
            return {"message": "Số điện thoại chỉ được chứa chữ số"}, 400
        if not (10 <= len(phone) <= 11):
            return {"message": "Số điện thoại phải có 10-11 chữ số"}, 400
        if not phone.startswith('0'):
            return {"message": "Số điện thoại phải bắt đầu bằng số 0"}, 400

        # 5. Validate Email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return {"message": "Định dạng email không hợp lệ"}, 400

        # 6. Kiểm tra username đã tồn tại chưa
        if User.query.filter_by(Username=username).first():
            return {"message": "Tên đăng nhập đã tồn tại"}, 400

        res_id = data.get('restaurant_id')

        # Ép kiểu về số (vì FormData gửi qua luôn là chuỗi)
        if res_id and str(res_id).strip() != "":
            try:
                res_id = int(res_id)
            except ValueError:
                res_id = None
        else:
            res_id = None

        new_user = User(
            Username=username,
            Password=password,
            Role=role,
            Email=email,
            Phone=phone,
            RestaurantID=res_id
        )
        db.session.add(new_user)
        db.session.commit()

        #Tạo token ngay sau khi đăng kí
        access_token = create_access_token(
            identity=str(new_user.UserID),
            expires_delta=timedelta(days=1)
        )
        return {
            "message": "Tạo tài khoản thành công",
            "access_token": access_token,
            "user_id": new_user.UserID
        }, 201

    @staticmethod
    def login(username, password):
        # 1. Tìm user trong Database
        user = User.query.filter_by(Username=username).first()


        # 2. Kiểm tra mật khẩu
        if user and user.Password == password:
            # Tạo Token
            access_token = create_access_token(
                identity=str(user.UserID),
                expires_delta=timedelta(days=1),
                additional_claims={
                    "role": user.Role,
                    "restaurant_id": user.RestaurantID
                } # Thêm tham số additional_claims để đưa Role vào Token
            )

            # Trả về kết quả thành công
            return {
                "message": "Đăng nhập thành công",
                "access_token": access_token,
                "role": user.Role,
                "user_info": {
                    "id": user.UserID,
                    "username": user.Username,
                    "restaurant_id": user.RestaurantID
                }
            }, 200

        return {"message": "Sai tài khoản hoặc mật khẩu"}, 401


