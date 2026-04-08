from flask import Blueprint, session,request, jsonify
from .service import *
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from sqlalchemy.exc import IntegrityError
from models.review import Review
from core.extensions import db
from models.user import User
from app.api.v1.customer.service import get_all_restaurants, get_restaurant_by_id


# HTML pages
customer_bp = Blueprint("customer", __name__, url_prefix="/api")


# API
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
    data = request.get_json()

    print("DATA:", data)

    if not data:
        return jsonify({"error": "Không có dữ liệu"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Thiếu username/password"}), 400

    user = User.query.filter_by(Username=username).first()

    if not user or not check_password_hash(user.Password, password):
        return jsonify({"error": "Sai tài khoản mật khẩu"}), 400

    session["user_id"] = user.UserID
    return jsonify({"message": "Đăng nhập thành công"})

@customer_bp.route("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Đã đăng xuất"})

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

    # Check thiếu dữ liệu
    if not all([restaurant_id, date, time, people]):
        return jsonify({"error": "Vui lòng nhập đầy đủ thông tin"}), 400
    # Check số người hợp lệ
    try:
        people = int(people)
    except ValueError:
        return jsonify({"error": "Số người không hợp lệ"}), 400

    return jsonify(check_table(
        restaurant_id,
        date,
        time,
        people))

@customer_bp.route("/book", methods=["POST"])
def book():

    data = request.json
    data["user_id"] = session.get("user_id")  # có thể None

    restaurant_id = data.get("restaurant_id")
    time_str = data.get("time")

    try:
        booking_time = datetime.strptime(time_str, "%H:%M").time()
    except:
        return jsonify({"error": "Sai format thời gian"}), 400

    restaurant = get_restaurant_by_id(restaurant_id)

    if not restaurant:
        return jsonify({"error": "Restaurant không tồn tại"}), 404

    open_time = datetime.strptime(restaurant["Opentime"], "%H:%M").time()
    close_time = datetime.strptime(restaurant["Closetime"], "%H:%M").time()

    if not (open_time <= booking_time <= close_time):
        return jsonify({
            "error": f"Chỉ đặt từ {open_time} đến {close_time}"
        }), 400
    result = create_booking(data)
    return jsonify({** result, "deposit":result.get("deposit")})

@customer_bp.route("/restaurants")
def get_restaurants():
    return jsonify(get_all_restaurants())

@customer_bp.route("/restaurant/<int:id>")
def get_restaurant(id):
    return jsonify(get_restaurant_by_id(id))

# API thanh toán đặt cọc
@customer_bp.route("/payment", methods=["POST"])
def payment():
    data = request.json

    return jsonify(confirm_payment(
        data.get("reservation_id"),
        data.get("amount")
    ))

@customer_bp.route("/history")
def get_history_route():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify([])

    return jsonify(get_history(user_id))


@customer_bp.route("/review", methods=["POST"])
@customer_bp.route("/review", methods=["POST"])
def create_review():
    if "user_id" not in session:
        return jsonify({"error": "Chưa đăng nhập"}), 401
    data = request.get_json()
    # CHECK TRƯỚC
    existing = Review.query.filter_by(
        UserID=session["user_id"],
        RestaurantID=data["RestaurantID"]
    ).first()
    if existing:
        return jsonify({
            "error": "Bạn đã thực hiện đánh giá",
            "reviewed": True
        }), 400
    new_review = Review(
        UserID=session["user_id"],
        RestaurantID=data["RestaurantID"],
        Rating=data["Rating"],
        Comment=data["Comment"]
    )
    db.session.add(new_review)
    db.session.commit()
    return jsonify({
        "message": "Review thành công",
        "reviewed": False
    })
@customer_bp.route("/review/check", methods=["GET"])
def check_review():
    if "user_id" not in session:
        return jsonify({"reviewed": False})

    restaurant_id = request.args.get("restaurant_id")

    review = Review.query.filter_by(
        UserID=session["user_id"],
        RestaurantID=restaurant_id
    ).first()

    if review:
        return jsonify({
            "reviewed": True,
            "rating": review.Rating,
            "comment": review.Comment
        })

    return jsonify({"reviewed": False})

@customer_bp.route("/me")
def get_me():
    if "user_id" in session:
        return jsonify({"logged_in": True})
    return jsonify({"logged_in": False})

