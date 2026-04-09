from flask import request, jsonify
from backend.app.api.v1.admin import admin_bp
from flask_jwt_extended import jwt_required, get_jwt
from backend.app.api.v1.admin.service import CuisineService
from backend.app.api.v1.admin.service import AdminRestaurantService
from backend.app.api.v1.admin.service import AdminUserService
from backend.app.api.v1.restaurant.service import RestaurantService
from backend.models.restaurant import Restaurant



#Quản Lý Users
#Xem danh sách User
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def admin_get_all_users():
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Quyền này của Admin!"}), 403

    users_list = AdminUserService.get_all_users()
    return jsonify(users_list), 200


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def admin_update_user(user_id):
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Quyền này của Admin!"}), 403

    # Lấy dữ liệu từ Form Data
    data = request.form.to_dict()

    updated_user = AdminUserService.update_user(user_id, data)

    if updated_user:
        return jsonify({"message": "Cập nhật user thành công!"}), 200
    return jsonify({"message": "Không tìm thấy người dùng"}), 404


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_user(user_id):
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Quyền này của Admin!"}), 403

    success = AdminUserService.delete_user(user_id)
    if success:
        return jsonify({"message": "Xóa người dùng thành công!"}), 200
    return jsonify({"message": "Lỗi khi xóa người dùng"}), 404

#Quản Lý Cuisine
#Thêm cuisine (POST)
@admin_bp.route('/cuisines', methods=['POST'])
@jwt_required()
def add_cuisine():
    # Kiểm tra quyền Admin
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Quyền này của Admin!"}), 403

        # Gom dữ liệu từ Form Data vào dictionary
    data = {"CuisineName": request.form.get('CuisineName')}
    result, status = CuisineService.create(data)
    return jsonify(result), status


#Xóa cuisine (DELETE)
@admin_bp.route('/cuisines/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_cuisine(id):
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Không có quyền xóa!"}), 403

    result, status = CuisineService.delete(id)
    return jsonify(result), status


#Xem cuisine (GET)
@admin_bp.route('/cuisines', methods=['GET'])
@jwt_required()
def get_cuisines():
    result, status = CuisineService.get_all()
    return jsonify(result), status


#Sửa cuisine (PUT)
@admin_bp.route('/cuisines/<int:id>', methods=['PUT'])
@jwt_required()
def update_cuisine(id):
    # Kiểm tra quyền Admin
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Quyền này của Admin!"}), 403

    data = request.form.to_dict()
    result, status = CuisineService.update(id, data)
    return jsonify(result), status

#Quản lý nhà hàng
#Admin tạo nhà hàng mới
@admin_bp.route('/restaurants', methods=['POST'])
@jwt_required()
def admin_create_restaurant():
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Quyền này của Admin!"}), 403

    # Lấy toàn bộ dữ liệu từ form-data
    data = request.form.to_dict()

    result, status = RestaurantService.create(data, is_admin=True)
    return jsonify(result), status


#Admin duyệt nhà hàng
@admin_bp.route('/restaurants/<int:id>/approve', methods=['PUT'])
@jwt_required()
def approve_restaurant(id):
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Chỉ Admin mới duyệt được!"}), 403

    result, status = AdminRestaurantService.approve(id)
    return jsonify(result), status

#Xem danh sách nhà hàng
@admin_bp.route('/restaurants', methods=['GET'])
def get_all():
    status = request.args.get('status')
    if status:
        restaurants = AdminRestaurantService.get_all_restaurants(status=status)
    else:
        # Nếu không truyền status thì lấy hết tất cả
        restaurants = AdminRestaurantService.get_all_restaurants()
    return jsonify(restaurants), 200

#Admin Sửa thông tin nhà hàng
@admin_bp.route('/restaurants/<int:id>', methods=['PUT'])
@jwt_required()
def admin_update_restaurant(id):
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Quyền này của Admin!"}), 403

    # Lấy dữ liệu từ Form Data
    data = request.form.to_dict()
    image = request.files.get('image')  # Nếu có gửi ảnh

    updated = AdminRestaurantService.update_restaurant(id, data, image)
    if updated:
        return jsonify({"message": "Cập nhật thành công!"}), 200
    return jsonify({"message": "Không tìm thấy nhà hàng"}), 404


#ADMIN XÓA NHÀ HÀNG
@admin_bp.route('/restaurants/<int:id>', methods=['DELETE'])
@jwt_required()
def admin_delete_restaurant(id):
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Quyền này của Admin!"}), 403

    success = AdminRestaurantService.delete_restaurant(id)
    if success:
        return jsonify({"message": "Xóa thành công!"}), 200
    return jsonify({"message": "Lỗi khi xóa"}), 404




