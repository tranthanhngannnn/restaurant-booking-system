from models.cuisine import Cuisine
from models.restaurant import Restaurant
from core.extensions import db
from models.user import User


class AdminUserService:
    @staticmethod
    def get_all_users():
        users = User.query.all()
        #Chuyển ds object sang list dictionary
        return [{"id": u.UserID, "username": u.Username, "role": u.Role, "email": u.Email} for u in users]

    @staticmethod
    def update_user(user_id, data):
        user = User.query.get(user_id)
        if not user:
            return None

        # Dùng setattr để cập nhật mọi thứ gửi từ Form Data
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return False

        db.session.delete(user)
        db.session.commit()
        return True

class CuisineService:
    @staticmethod
    def create(data):
        cuisine_name = data.get('CuisineName')
        if not cuisine_name:
            return {"message": "Tên không được để trống"}, 400

        if Cuisine.query.filter_by(CuisineName=cuisine_name).first():
            return {"message": "Danh mục đã tồn tại"}, 400

        new_cuisine = Cuisine(CuisineName=cuisine_name, Status = "Hoạt động")
        db.session.add(new_cuisine)
        db.session.commit()
        return {"message": "Thêm thành công!"}, 201

    @staticmethod
    def get_all():
        all_cuisines = Cuisine.query.all()
        # Chuyển list object sang list dictionary
        result = [{"id": c.CuisineID, "name": c.CuisineName, "status": c.Status} for c in all_cuisines]
        return result, 200

    @staticmethod
    def update(id, data):
        cuisine_obj = Cuisine.query.get(id)
        if not cuisine_obj:
            return {"message": "Không tìm thấy"}, 404

        for key, value in data.items():
            if hasattr(Cuisine, key):  # Kiểm tra xem bảng Cuisine có cột đó không
                setattr(cuisine_obj, key, value)

        db.session.commit()
        return {"message": "Cập nhật thành công!"}, 200

    @staticmethod
    def delete(id):
        cuisine_name = Cuisine.query.get(id)
        if not cuisine_name:
            return {"message": "Không tìm thấy"}, 404

        db.session.delete(cuisine_name)
        db.session.commit()
        return {"message": "Đã xóa xong!"}, 200


class AdminRestaurantService:
    @staticmethod
    def get_all_restaurants():
        #Lấy tất cả danh sách nhà hàng
        restaurants = Restaurant.query.all()
        # Chuyển đổi list object sang list dictionary để jsonify được
        return [res.to_dict() for res in restaurants]

    @staticmethod
    def update_restaurant(restaurant_id, data, image=None):
        #Cập nhật thông tin nhà hàng từ Form Data
        restaurant = Restaurant.query.get(restaurant_id)

        if not restaurant:
            return None  # Trả về None nếu không tìm thấy ID

        # Cập nhật các trường gửi lên từ Form Data
        for key, value in data.items():
            if hasattr(restaurant, key):  # Kiểm tra xem Model Restaurant có cột này không
                setattr(restaurant, key, value)

        # Xử lý nếu có file ảnh gửi kèm
        if image and image.filename != '':
            # Lưu tên file vào DB
            restaurant.image_url = image.filename

        db.session.commit()
        return restaurant

    @staticmethod
    def delete_restaurant(restaurant_id):
        #Xóa nhà hàng theo ID
        restaurant = Restaurant.query.get(restaurant_id)

        if not restaurant:
            return False

        db.session.delete(restaurant)
        db.session.commit()
        return True

    @staticmethod
    def approve(restaurant_id):
        try:
            #Tìm nhà hàng trong database theo ID
            restaurant = Restaurant.query.get(restaurant_id)
            if not restaurant:
                return {"message": "Không tìm thấy nhà hàng này!"}, 404

            #Cập nhật trạng thái thành Đang hoạt động
            restaurant.status = "Đang hoạt động"
            db.session.commit()

            return {"message": f"Đã duyệt nhà hàng {restaurant.RestaurantName} thành công!"}, 200

        except Exception as e:
            db.session.rollback()
            return {"message": f"Lỗi hệ thống: {str(e)}"}, 500