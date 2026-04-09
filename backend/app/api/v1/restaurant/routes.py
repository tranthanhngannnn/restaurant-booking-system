from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from backend.app.api.v1.restaurant.service import RestaurantService
from . import restaurant_bp

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