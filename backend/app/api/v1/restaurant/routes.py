from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.menu import Menu
from models.tables import Tables
from models.booking import Reservation
from models.orders import Order
from models.food import Food
from models.ordersitem import OrderItem
from core.extensions import db
from models.user import User
from app.api.v1.restaurant.service import RestaurantService


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
        "UserID": get_jwt_identity()
    }
    result, status = RestaurantService.create(data, is_admin=False)
    return jsonify(result), status

@restaurant_bp.route("/tables/<int:id>/status", methods=["PUT"])
def update_table_status(id):
    return jsonify(update_table_status_service(id, request.json))

#dành cho KH
@restaurant_bp.route('/menu', methods=['GET'])
def get_menu_api():
    # Lấy ID nhà hàng từ tham số truyền lên
    res_id = request.args.get('restaurant_id')
    if res_id:
        res_id = int(res_id)

    menus = Food.query.filter_by(RestaurantID=res_id).all()

    try:
        from image import MENU_DATA
    except ImportError:
        from backend.image import MENU_DATA

    result = []
    for m in menus:
        # 1. Khai báo image_url ngay đầu vòng lặp cho mỗi món
        # Dùng m.Image_URL (nếu DB Ngân là Image_URL) hoặc m.Image
        image_url = m.Image_URL if hasattr(m, 'Image_URL') and m.Image_URL else ""

        # 2. Nếu DB trống, đi tìm trong MENU_DATA (vẫn nằm TRONG vòng lặp for m)
        if not image_url:
            for item in MENU_DATA:
                if item['name'] == m.FoodName:
                    image_url = item['image']
                    break

        # 3. Add món đó vào list result
        result.append({
            "id": m.FoodID,
            "name": m.FoodName,
            "price": float(m.Price) if m.Price else 0,
            "image": image_url,
            "category": m.Category if hasattr(m, 'Category') else "",
            "description": m.Description if hasattr(m, 'Description') else ""
        })

    return jsonify(result)

#dành cho nhân viên
@restaurant_bp.route('/menu/admin', methods=['GET'])
@jwt_required()
def get_menu_admin():
    # 1. Kiểm tra xem có phải nhân viên/chủ không
    token_data = get_jwt()
    if token_data.get("role") != "STAFF":
        return jsonify({"message": "Chỉ nhân viên mới được xem!"}), 403

    current_user_id = get_jwt_identity() #NẾU ĐÚNG ROLE NHÀ HÀNG -> LẤY ID VÀ QUERY MENU
    user_info = User.query.get(current_user_id) #Tìm thông tin user để suy ra nhà hàng họ đang làm việc

    # Kiểm tra xem nhân viên này đã được phân công về nhà hàng nào chưa
    if not user_info or not user_info.RestaurantID:
        return jsonify({"message": "Nhân viên này chưa được phân công nhà hàng!"}), 400
    try:
        from image import MENU_DATA #tránh lỗi vòng lặp lúc khởi động
    except ImportError:
        from backend.image import MENU_DATA

    restaurant_id = user_info.RestaurantID
    menus = Food.query.filter_by(RestaurantID=restaurant_id).all() #LẤY ĐÚNG MENU CỦA NHÀ HÀNG ĐÓ

    result = []
    for m in menus:
        # 1. Mặc định lấy ảnh từ DB (nếu có)
        image_url = m.Image_URL if m.Image_URL else ""

        if not image_url:
            for item in MENU_DATA:
                if item['name'] == m.FoodName:  # So khớp theo tên món ăn
                    image_url = item['image']
                    break

        result.append({
            "id": m.FoodID,
            "name": m.FoodName,
            "price": float(m.Price) if m.Price else 0,
            "image": image_url,
            "restaurant_id": m.RestaurantID
        })
    return jsonify(result)

@restaurant_bp.route('/list', methods=['GET'])
def get_restaurant_list():
    restaurants = Restaurant.query.all()
    return jsonify([
        {"id": r.RestaurantID, "name": r.RestaurantName}
        for r in restaurants
    ])

@restaurant_bp.route('/menu', methods=['POST'])
def create_food_api():
    return jsonify(create_food(request.json))

@restaurant_bp.route('/menu/<int:id>', methods=['DELETE'])
def delete_food_api(id):
    return jsonify(delete_food(id))

@restaurant_bp.route('/tables', methods=['GET'])
def get_tables_api():
    return jsonify(get_tables())

@restaurant_bp.route('/tables', methods=['POST'])
def create_table_api():
    return jsonify(create_table(request.json))

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

@restaurant_bp.route("/orders", methods=["POST"])
def create_order():
    data = request.json
    table_id = data["table_id"]
    table = Tables.query.get(table_id)
    if not table:
        return {"error": "Table not found"}, 404

    order = Order.query.filter_by(table_id=table_id, status="active").first()
    if not order:
        order = Order(table_id=table_id, status="active")
        db.session.add(order)
        db.session.commit()
        table.Status = "Reserved"

    for item in data["items"]:
        existing = OrderItem.query.filter_by(
            order_id=order.id,
            food_id=item["food_id"]
        ).first()
        if existing:
            existing.quantity += item["qty"]
        else:
            oi = OrderItem(order_id=order.id, food_id=item["food_id"], quantity=item["qty"])
            db.session.add(oi)
    db.session.commit()
    return {"message": "Order updated"}

@restaurant_bp.route("/orders/pay/<int:table_id>", methods=["PUT"])
def pay_order(table_id):
    order = Order.query.filter_by(table_id=table_id, status="active").first()
    if not order: return {"error": "No active order"}
    order.status = "paid"
    table = Tables.query.get(table_id)
    if table: table.Status = "Available"
    db.session.commit()
    return {"message": "Paid"}

@restaurant_bp.route('/menu/<id>/toggle', methods=['PUT', 'OPTIONS'])
def toggle_menu(id):
    menu = Food.query.get(id)
    if not menu:
        return jsonify({"error": "Not found"}), 404
    menu.Visible = not menu.Visible
    db.session.commit()
    return jsonify({"message": "updated", "visible": menu.Visible})
