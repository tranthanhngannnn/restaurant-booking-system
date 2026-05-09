from backend.models.user import User
from backend.core.extensions import db
from flask_jwt_extended import create_access_token
from datetime import timedelta

class AuthService:
    @staticmethod
    def register(data):
        # Kiểm tra username đã tồn tại chưa
        if User.query.filter_by(Username=data.get('username')).first():
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
            Username=data.get('username'),
            Password=data.get('password'),
            Role=data.get('role'),
            Email=data.get('email'),
            Phone=data.get('phone'),
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


