from backend.models.restaurant import Restaurant
from backend.core.extensions import db


class RestaurantService:
    @staticmethod
    def create(data, is_admin=False):
        # Kịch bản: Admin tạo thì Active luôn, Chủ Nhà Hàng tạo thì chờ duyệt
        status_val = "Đang hoạt động" if is_admin else "Đang chờ duyệt"

        # Kiểm tra tên nhà hàng không được để trống
        restaurant_name = data.get('RestaurantName')
        if not restaurant_name:
            return {"message": "Tên nhà hàng không được để trống"}, 400

        new_res = Restaurant(
            RestaurantName=restaurant_name,
            Address=data.get('Address'),
            Phone=data.get('Phone'),
            Email=data.get('Email'),
            Opentime=data.get('Opentime'),
            Closetime=data.get('Closetime'),
            description=data.get('description'),
            UserID=data.get('UserID'),  # ID của tài khoản chủ nhà hàng
            CuisineID=data.get('CuisineID'),
            status=status_val
        )

        try:
            db.session.add(new_res)
            db.session.commit()
            return {"message": f"Tạo thành công! Trạng thái hiện tại: {status_val}"}, 201
        except Exception as e:
            db.session.rollback()
            return {"message": f"Lỗi hệ thống: {str(e)}"}, 500

