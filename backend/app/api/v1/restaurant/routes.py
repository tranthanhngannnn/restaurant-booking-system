from flask import request, jsonify ,Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.api.v1.restaurant.service import RestaurantService
from . import restaurant_bp

from .service import *

restaurant_bp = Blueprint('restaurant', __name__)

@restaurant_bp.route('/registerRestaurant', methods=['POST'])
@jwt_required()
def staff_register_restaurant():
    claims = get_jwt()
    if claims.get("role") != "STAFF":
        return jsonify({"message": "Quyền này của Staff!"}), 403
    data = {
        "RestaurantName": request.form.get('RestaurantName'),
        "Address": request.form.get('Address'),
        "Phone": request.form.get('Phone'),
        "CuisineID": request.form.get('CuisineID'),
        "UserID": get_jwt_identity() # Lấy ID người đang login làm chủ
    }
    result, status = RestaurantService.create(data, is_admin=False)
    return jsonify(result), status

@restaurant_bp.route("/tables/<int:id>/status", methods=["PUT"])
def update_table_status(id):
    return jsonify(update_table_status_service(id, request.json))


@restaurant_bp.route('/menu', methods=['GET'])
def get_menu():
    return jsonify(get_all_menu())

@restaurant_bp.route('/menu', methods=['POST'])
def create_food_api():
    data = request.json
    return jsonify(create_food(data))

@restaurant_bp.route('/menu/<int:id>', methods=['PUT'])
def update_food_api(id):
    data = request.json
    return jsonify(update_food(id, data))

@restaurant_bp.route('/menu/<int:id>', methods=['DELETE'])
def delete_food_api(id):
    return jsonify(delete_food(id))


# ===== TABLE =====
@restaurant_bp.route('/tables', methods=['GET'])
def get_tables_api():
    return jsonify(get_tables())

@restaurant_bp.route('/tables', methods=['POST'])
def create_table_api():
    data = request.json
    return jsonify(create_table(data))

@restaurant_bp.route("/bookings", methods=["POST"])
def add_booking():
    return jsonify(create_booking(request.json))

@restaurant_bp.route('/bookings', methods=['GET'])
def get_bookings_api():
    return jsonify(get_bookings())

@restaurant_bp.route('/bookings/<int:id>/confirm', methods=['POST'])
def confirm_booking_api(id):
    return jsonify(confirm_booking(id))

@restaurant_bp.route('/bookings/<int:id>/reject', methods=['POST'])
def reject_booking_api(id):
    return jsonify(reject_booking(id))

@restaurant_bp.route("/bookings/<int:id>", methods=["DELETE"])
def delete_booking_api(id):
    return jsonify(delete_booking(id))

@restaurant_bp.route("/tables/<int:id>/bookings", methods=["GET"])
def get_booking_by_table(id):
    return jsonify(get_booking_by_table_service(id))