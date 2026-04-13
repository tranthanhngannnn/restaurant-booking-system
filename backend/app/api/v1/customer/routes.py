from flask import Blueprint, session, request, jsonify
from .service import *
from models.review import Review
from core.extensions import db
from models.user import User
from models.tables import Tables
from flask_jwt_extended import jwt_required, get_jwt_identity
from .service import search_restaurant, get_all_restaurants
from models.booking import Reservation
from models.restaurant import Restaurant
from datetime import datetime

customer_bp = Blueprint("customer", __name__, url_prefix="/api/v1/customer")



@customer_bp.route("/search")
def search():
    address = request.args.get("address")
    cuisine = request.args.get("cuisine")

    # Gọi service lấy dữ liệu từ DB
    restaurants = search_restaurant(address, cuisine)  # trả về list dict
    return jsonify(restaurants)

@customer_bp.route("/menu/<int:id>")
def menu(id):
    return jsonify(get_menu(id))

@customer_bp.route("/check")
def check():
    restaurant_id = request.args.get("restaurant_id")
    date = request.args.get("date")
    time = request.args.get("time")
    people = request.args.get("people")
    if not all([restaurant_id, date, time, people]):
        return jsonify({"error": "Vui lòng nhập đầy đủ thông tin"}), 400
    return jsonify(check_table(restaurant_id, date, time, people))

@customer_bp.route("/book", methods=["POST"])
@jwt_required(optional=True)
def book():
    data = request.json
    if not data.get("name") or not data.get("phone"):
        return jsonify({"error": "Tên và SĐT là bắt buộc"}), 400
    
    table_id = data.get("table_id")
    restaurant_id = data.get("restaurant_id")
    table = Tables.query.get(table_id)
    if not table or table.RestaurantID != int(restaurant_id):
        return jsonify({"error": "Bàn không hợp lệ"}), 400

    data["user_id"] = session.get("user_id")
    result = create_booking(data)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

@customer_bp.route("/restaurants", methods=["GET"])
def get_restaurants_api():
    # Gọi hàm bên service và trả về JSON cho frontend
    restaurants = get_all_restaurants()
    return jsonify(restaurants)

@customer_bp.route("/restaurant/<int:id>", methods=["GET"])
def get_restaurant_info(id):
    # Trả thông tin chi tiết nhà hàng cho Frontend hiển thị giờ
    data = get_restaurant_by_id(id)
    if "error" in data:
        return jsonify(data), 404
    return jsonify(data)

# API thanh toán đặt cọc
@customer_bp.route("/payment", methods=["POST"])
def payment():
    data = request.json

    return jsonify(confirm_payment(
        data.get("reservation_id"),
        data.get("amount")
    ))

#lưu đánh giá
@customer_bp.route("/review", methods=["POST"])
@jwt_required()
def create_review():
    user_id = get_jwt_identity()
    if not user_id: return jsonify({"error": "Chưa đăng nhập"}), 401
    data = request.json
    new_review = Review(
        UserID=user_id,
        RestaurantID=data["RestaurantID"],
        Rating=data.get("Rating"),
        Comment=data.get("Comment", "")
    )
    db.session.add(new_review)
    db.session.commit()
    return jsonify({"message": "Review thành công"})

@customer_bp.route("/review/check", methods=["GET"])
@jwt_required()
def check_review_api():
    reservation_id = request.args.get("reservation_id")
    if not reservation_id:
        return jsonify({"reviewed": False})

    review = Review.query.filter_by(ReservationID=reservation_id).first()

    if review:
        return jsonify({"reviewed": True, "rating": review.Rating, "comment": review.Comment}), 200
    return jsonify({"reviewed": False}), 200


@customer_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history_api():
    # 1. Lấy ID từ Token
    user_id = get_jwt_identity()
    print(f"👉 [DEBUG] UserID từ Token: {user_id}", flush=True) #nháp

    keyword = request.args.get("keyword", "")

    print(f"👉 [DEBUG] Keyword từ Frontend: {keyword}", flush=True)

    # 3. Truyền cả ID và SĐT vào service
    data = get_history(user_id, keyword)

    return jsonify(data), 200

@customer_bp.route("/me")
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    # có thể query DB để lấy thêm tên user nếu muốn
    return jsonify({"logged_in": True, "user_id": user_id})
