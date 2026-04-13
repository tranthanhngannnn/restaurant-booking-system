from flask import Blueprint, session, request, jsonify
from .service import *
from werkzeug.security import generate_password_hash, check_password_hash
from models.review import Review
from core.extensions import db
from models.user import User
from models.tables import Tables
from models.booking import Reservation
from models.restaurant import Restaurant
from datetime import datetime

customer_bp = Blueprint("customer", __name__, url_prefix="/api/v1/customer")

@customer_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    existing_user = User.query.filter_by(Username=data["username"]).first()
    if existing_user:
        return jsonify({"error": "Username đã tồn tại"}), 400
    new_user = User(
        Username=data["username"],
        Password=generate_password_hash(data["password"]),
        Email=data.get("email"),
        Phone=data.get("phone"),
        Role="CUSTOMER"
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Đăng ký thành công"})

@customer_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    if not data: return jsonify({"error": "Không có dữ liệu"}), 400
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(Username=username).first()
    if not user or not check_password_hash(user.Password, password):
        return jsonify({"error": "Sai tài khoản mật khẩu"}), 400
    session["user_id"] = user.UserID
    return jsonify({"message": "Đăng nhập thành công", "role": user.Role})

@customer_bp.route("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Đã đăng xuất"})

@customer_bp.route("/search")
def search():
    address = request.args.get("address")
    cuisine = request.args.get("cuisine")
    return jsonify(search_restaurant(address, cuisine))

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

@customer_bp.route("/history")
def get_history_route():
    user_id = session.get("user_id")
    if not user_id: return jsonify([])
    return jsonify(get_history(user_id))

@customer_bp.route("/review", methods=["POST"])
def create_review():
    user_id = session.get("user_id")
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
def check_review_api():
    user_id = session.get("user_id")
    if not user_id: return jsonify({"reviewed": False})
    restaurant_id = request.args.get("restaurant_id")
    review = Review.query.filter_by(UserID=user_id, RestaurantID=restaurant_id).first()
    if review:
        return jsonify({"reviewed": True, "rating": review.Rating, "comment": review.Comment})
    return jsonify({"reviewed": False})

@customer_bp.route("/me")
def get_me():
    if "user_id" in session: return jsonify({"logged_in": True})
    return jsonify({"logged_in": False})
