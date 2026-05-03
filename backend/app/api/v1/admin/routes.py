from flask import request, jsonify
from backend.app.api.v1.admin import admin_bp
from flask_jwt_extended import jwt_required, get_jwt
from backend.app.api.v1.restaurant.service import RestaurantService
from .service import *


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def admin_get_all_users():
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Quyen nay cua Admin!"}), 403

    users_list = AdminUserService.get_all_users()
    return jsonify(users_list), 200


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def admin_update_user(user_id):
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Quyen nay cua Admin!"}), 403

    data = request.form.to_dict()
    updated_user = AdminUserService.update_user(user_id, data)

    if updated_user:
        return jsonify({"message": "Cap nhat user thanh cong!"}), 200
    return jsonify({"message": "Khong tim thay nguoi dung"}), 404


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_user(user_id):
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Quyen nay cua Admin!"}), 403

    success = AdminUserService.delete_user(user_id)
    if success:
        return jsonify({"message": "Xoa nguoi dung thanh cong!"}), 200
    return jsonify({"message": "Loi khi xoa nguoi dung"}), 404


@admin_bp.route('/cuisines', methods=['POST'])
@jwt_required()
def add_cuisine():
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Quyen nay cua Admin!"}), 403

    data = {"CuisineName": request.form.get('CuisineName')}
    result, status = CuisineService.create(data)
    return jsonify(result), status


@admin_bp.route('/cuisines/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_cuisine(id):
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Khong co quyen xoa!"}), 403

    result, status = CuisineService.delete(id)
    return jsonify(result), status


@admin_bp.route('/cuisines', methods=['GET'])
@jwt_required()
def get_cuisines():
    result, status = CuisineService.get_all()
    return jsonify(result), status


@admin_bp.route('/cuisines/<int:id>', methods=['PUT'])
@jwt_required()
def update_cuisine(id):
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Quyen nay cua Admin!"}), 403

    data = request.form.to_dict()
    result, status = CuisineService.update(id, data)
    return jsonify(result), status


@admin_bp.route('/restaurants', methods=['POST'])
@jwt_required()
def admin_create_restaurant():
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Quyen nay cua Admin!"}), 403

    data = request.form.to_dict()
    result, status = RestaurantService.create(data, is_admin=True)
    return jsonify(result), status


@admin_bp.route('/restaurants/<int:id>/approve', methods=['PUT'])
@jwt_required()
def approve_restaurant(id):
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Chi Admin moi duyet duoc!"}), 403

    result, status = AdminRestaurantService.approve(id)
    return jsonify(result), status


@admin_bp.route('/restaurants/<int:id>/reject', methods=['PUT'])
@jwt_required()
def reject_restaurant(id):
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Chi Admin moi tu choi duoc!"}), 403

    result, status = AdminRestaurantService.reject(id)
    return jsonify(result), status


@admin_bp.route('/restaurants', methods=['GET'])
def get_all():
    status = request.args.get('status')
    if status:
        restaurants = AdminRestaurantService.get_all_restaurants(status=status)
    else:
        restaurants = AdminRestaurantService.get_all_restaurants()
    return jsonify(restaurants), 200


@admin_bp.route('/restaurants/<int:id>', methods=['PUT'])
@jwt_required()
def admin_update_restaurant(id):
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Quyen nay cua Admin!"}), 403

    data = request.form.to_dict()
    image = request.files.get('image')

    updated = AdminRestaurantService.update_restaurant(id, data, image)
    if updated:
        return jsonify({"message": "Cap nhat thanh cong!"}), 200
    return jsonify({"message": "Khong tim thay nha hang"}), 404


@admin_bp.route('/restaurants/<int:id>', methods=['DELETE'])
@jwt_required()
def admin_delete_restaurant(id):
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Quyen nay cua Admin!"}), 403

    result = AdminRestaurantService.delete_restaurant(id)
    return jsonify({"message": result["message"]}), result["code"]


@admin_bp.route('/report', methods=['POST'])
@jwt_required()
def get_report():
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"message": "Quyen nay cua Admin!"}), 403

    restaurant_id = request.form.get('restaurant_id')
    report_month = request.form.get('report_month')

    if not report_month:
        return jsonify({"status": "error", "message": "Thieu thang can xem bao cao"}), 400

    data = ReportService.get_report(restaurant_id, report_month)

    return jsonify({
        "status": "success",
        "restaurant_id": restaurant_id,
        "month": data["month"],
        "months": data["months"],
        "restaurants": data["restaurants"],
        "restaurant_count": data["restaurant_count"],
        "total_report": data["total_report"],
        "total_6_months": data["total_6_months"]
    }), 200
