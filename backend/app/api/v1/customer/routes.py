from flask import Blueprint, session, request, jsonify
from .service import *
from backend.models.review import Review
from backend.core.extensions import db
import re
from backend.models.tables import Tables
from flask_jwt_extended import jwt_required, get_jwt_identity
from .service import search_restaurant, get_all_restaurants
from backend.models.booking import Reservation
from sqlalchemy.exc import DataError
customer_bp = Blueprint("customer", __name__, url_prefix="/api/v1/customer")
from datetime import datetime, timedelta

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
    try:
        people = int(people)
        if people < 1 or people > 10:
            return jsonify({"error": "Chỉ được đặt từ 1-10 khách"}), 400
    except:
        return jsonify({"error": "Số khách không hợp lệ"}), 400
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        return jsonify({"error": "Restaurant không tồn tại"}), 404
    return jsonify(check_table(restaurant_id, date, time, people))

@customer_bp.route("/book", methods=["POST"])
@jwt_required(optional=True)
def book():
    data = request.json
    if not data.get("name") or not data.get("phone"):
        return jsonify({"error": "Tên và SĐT là bắt buộc"}), 400
        # Phone: 10 số, bắt đầu bằng 0
    phone = data.get("phone")
    if not re.match(r"^0\d{9}$", phone):
        return jsonify({"error": "SĐT phải gồm 10 số và bắt đầu bằng 0"}), 400

        # ===== VALIDATE PEOPLE =====
    try:
        people = int(data.get("people"))
        if people < 1 or people > 10:
            return jsonify({"error": "Chỉ được đặt từ 1-10 khách"}), 400
    except:
        return jsonify({"error": "Số khách không hợp lệ"}), 400
    note = data.get("note", "")
    if note and len(note) > 300:
        return jsonify({"error": "Ghi chú tối đa 300 ký tự"}), 400

    table_id = data.get("table_id")
    restaurant_id = data.get("restaurant_id")
    table = db.session.get(Tables, table_id)
    if not table or table.RestaurantID != int(restaurant_id):
        return jsonify({"error": "Bàn không hợp lệ"}), 400
    try:
        booking_date = datetime.strptime(data.get("date"), "%Y-%m-%d").date()
        booking_time = datetime.strptime(data.get("time"), "%H:%M").time()
        booking_datetime = datetime.combine(booking_date, booking_time)
        now = datetime.now()

        if booking_datetime < now:
            return jsonify({"error": "Không thể đặt bàn trong quá khứ"}), 400

        if booking_datetime < now + timedelta(minutes=30):
            return jsonify({"error": "Phải đặt trước ít nhất 30 phút"}), 400
    except:
        return jsonify({"error": "Sai format ngày/giờ"}), 400
    #Check restaurant time
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        return jsonify({"error": "Restaurant không tồn tại"}), 404
    open_time = datetime.strptime(restaurant["Opentime"], "%H:%M:%S").time()
    close_time = datetime.strptime(restaurant["Closetime"], "%H:%M:%S").time()

    if not (open_time <= booking_time <= close_time):
        return jsonify({
            "error": f"Chỉ đặt từ {open_time} đến {close_time}"
        }), 400
        # Double booking
    exist = Reservation.query.filter(
        Reservation.TableID == table_id,
        Reservation.BookingDate == booking_date,
        Reservation.BookingTime == booking_time,
        Reservation.Status.in_(["Pending", "Confirmed"])
    ).first()

    if exist:
        return jsonify({"error": "Bàn đã được đặt"}), 400

    data["user_id"] = session.get("user_id")
    data["status"] = "Pending" #Ép cứng trạng thái là Pending (đợi duyệt)
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

    result = confirm_payment(
        data.get("reservation_id"),
        data.get("amount")
    )
    # Nếu service trả (data, status)
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]

    return jsonify(result), 200


# gửi đánh giá
@customer_bp.route("/review", methods=["POST"])
@jwt_required()
def create_review():
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Chưa đăng nhập"}), 401

    data = request.json
    reservation_id = data.get("ReservationID")
    rating = data.get("Rating")


    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"error": "Rating phải là số nguyên từ 1 đến 5"}), 400


    comment = data.get("Comment", "")
    if comment and len(comment) > 255:
        return jsonify({"error": "Bình luận tối đa 255 ký tự"}), 400

    existing_review = Review.query.filter_by(ReservationID=reservation_id).first()

    try:
        if existing_review:
            # UPDATE
            existing_review.Rating = rating
            existing_review.Comment = comment

            db.session.commit()
            return jsonify({"message": "Cập nhật đánh giá thành công!"})

        else:
            # CREATE
            new_review = Review(
                UserID=user_id,
                RestaurantID=data["RestaurantID"],
                ReservationID=reservation_id,
                Rating=rating,
                Comment=comment
            )

            db.session.add(new_review)
            db.session.commit()

            return jsonify({"message": "Đã gửi đánh giá thành công!"})

    except DataError:
        db.session.rollback()
        return jsonify({"error": "Bình luận vượt quá 255 ký tự"}), 400

    except Exception as e:
        db.session.rollback()
        print("Lỗi review:", str(e))
        return jsonify({"error": "Lỗi hệ thống"}), 500


# lưu đánh giá
@customer_bp.route("/review/check", methods=["GET"])
@jwt_required()
def check_review_api():
    reservation_id = request.args.get("reservation_id")
    if not reservation_id:
        return jsonify({"reviewed": False})

    review = Review.query.filter_by(ReservationID=int(reservation_id)).first()

    if review:
        return jsonify({"reviewed": True, "rating": review.Rating, "comment": review.Comment}), 200
    return jsonify({"reviewed": False}), 200


@customer_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history_api():
    # 1. Lấy ID từ Token
    user_id = get_jwt_identity()
    keyword = request.args.get("keyword", "")

    #Truyền cả ID và SĐT vào service
    data = get_history(user_id, keyword)

    return jsonify(data), 200


@customer_bp.route("/me")
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    # có thể query DB để lấy thêm tên user nếu muốn
    return jsonify({"logged_in": True, "user_id": user_id})
