from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from backend.models.menu import Menu
from backend.models.tables import Tables
from backend.models.booking import Reservation
from backend.models.orders import Order
from backend.models.food import Food
from backend.models.ordersitem import OrderItem
from backend.core.extensions import db
from backend.models.user import User
from backend.app.api.v1.restaurant.service import RestaurantService
from backend.app.api.v1.customer.service import create_booking
from .service import *
from backend.app.api.v1.restaurant.service import update_food

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
        "Email": request.form.get('Email'),
        "CuisineID": request.form.get('CuisineID'),
        "Opentime": request.form.get('Opentime'),
        "Closetime": request.form.get('Closetime'),
        "description": request.form.get('description'),
        "UserID": get_jwt_identity()
    }
    result, status = RestaurantService.create(data, is_admin=False)
    return jsonify(result), status

@restaurant_bp.route("/tables/<int:id>/status", methods=["PUT"])
def update_table_status(id):
    return jsonify(update_table_status_service(id, request.json))

#dành cho KH
@restaurant_bp.route('/menu', methods=['GET'])
@jwt_required()
def get_menu_api():
    # Lấy ID nhà hàng từ tham số truyền lên
    current_user_id = get_jwt_identity()
    user_info = get_jwt()
    res_id = user_info.get("restaurant_id")

    try:
        menu_data = get_res_menu(res_id)
        return jsonify(menu_data)
    except Exception as e:
        return jsonify({"message": f"Lỗi server: {str(e)}"}), 500


#dành cho nhân viên
@restaurant_bp.route('/menu/admin', methods=['GET'])
@jwt_required()
def get_menu_admin():
    #print("JWT DEBUG:", get_jwt())
    # 1. Kiểm tra xem có phải nhân viên/chủ không
    token_data = get_jwt()
    if token_data.get("role") != "STAFF":
        return jsonify({"message": "Chỉ nhân viên mới được xem!"}), 403

    current_user_id = get_jwt_identity() #NẾU ĐÚNG ROLE NHÀ HÀNG -> LẤY ID VÀ QUERY MENU
    user_info = User.query.get(current_user_id) #Tìm thông tin user để suy ra nhà hàng họ đang làm việc
    print("USER:", user_info)
    print("RestaurantID:", getattr(user_info, "RestaurantID", None))

    # Kiểm tra xem nhân viên này đã được phân công về nhà hàng nào chưa
    if not user_info or not user_info.RestaurantID:
        return jsonify({"message": "Nhân viên này chưa được phân công nhà hàng!"}), 400

    try:
        menu_data = get_menu_res_admin(user_info.RestaurantID)
        return jsonify(menu_data)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"message": str(e)}), 500


@restaurant_bp.route('/list', methods=['GET'])
def get_restaurant_list():
    restaurants = Restaurant.query.all()
    return jsonify([
        {"id": r.RestaurantID, "name": r.RestaurantName}
        for r in restaurants
    ])


@restaurant_bp.route('/menu', methods=['POST'])
@jwt_required()
def create_food_api():
    current_user_id = get_jwt_identity()
    user_info = User.query.get(current_user_id)

    if not user_info or not user_info.RestaurantID:
        return jsonify({"message": "Nhân viên chưa được phân công nhà hàng!"}), 400

    return jsonify(create_food(request.json, user_info.RestaurantID))


@restaurant_bp.route('/menu/<id>', methods=['PUT'])
def update_food_api(id):
    if request.is_json:
        data = request.json
    else:
        # Xử lý form-data (gửi từ frontend khi có file)
        data = request.form.to_dict()
        image_file = request.files.get('image')
        if image_file:
            data['image_file'] = image_file
            
    return jsonify(update_food(id, data))

@restaurant_bp.route('/menu/<id>', methods=['DELETE'])
def delete_food_api(id):
    return jsonify(delete_food(id))

@restaurant_bp.route('/tables', methods=['GET'])
@jwt_required()
def get_tables_api():
    current_user_id = get_jwt_identity()
    user_info = User.query.get(current_user_id)
    # Lấy đúng ID nhà hàng của người đang đăng nhập
    print("USER:", user_info)
    res_id = user_info.RestaurantID
    tables = get_tables(res_id)
    return jsonify(tables)

@restaurant_bp.route('/tables', methods=['POST'])
@jwt_required()
def create_table_api():
    current_user_id = get_jwt_identity()
    user_info = User.query.get(current_user_id)

    if not user_info or not user_info.RestaurantID:
        return jsonify({
            "error": "User chưa được gán nhà hàng (RestaurantID = NULL)"
        }), 400

    res_id = user_info.RestaurantID
    data = request.json

    return jsonify(create_table(data, res_id))

@restaurant_bp.route("/bookings", methods=["POST"])
@jwt_required()
def delete_table_api(id):
    return jsonify(delete_table(id))


@restaurant_bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_bookings_api():
    current_user_id = get_jwt_identity()
    user_info = User.query.get(current_user_id)
    data = get_bookings(user_info.RestaurantID)
    return jsonify(data)

@restaurant_bp.route('/bookings/<int:id>/confirm', methods=['POST'])
@jwt_required()
def confirm_booking_api(id):
    return jsonify(confirm_booking(id))

@restaurant_bp.route('/bookings/<int:id>/reject', methods=['POST'])
@jwt_required()
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
        return jsonify({"error": "Table not found"}), 404

    order = Order.query.filter_by(table_id=table_id, status="active").first()

    if not order:
        order = Order(table_id=table_id, status="active")
        db.session.add(order)
        db.session.commit()

    for item in data["items"]:
        food = Food.query.get(item["food_id"])
        if not food:
            continue

        existing = OrderItem.query.filter_by(
            order_id=order.id,
            food_id=item["food_id"]
        ).first()

        if existing:
            existing.quantity += item["qty"]
        else:
            oi = OrderItem(
                order_id=order.id,
                food_id=item["food_id"],
                name=food.FoodName,
                quantity=item["qty"],
                price=float(food.Price)
            )
            db.session.add(oi)

    table.Status = "Reserved"
    db.session.commit()

    return jsonify({
        "message": "Order created",
        "order_id": order.id
    }), 200

@restaurant_bp.route("/orders/<int:table_id>", methods=["GET"])
def get_order_by_table(table_id):
    order = Order.query.filter(
        Order.table_id == table_id,
        Order.status.in_(["active", "Active", "ACTIVE"])
    ).first()

    if not order:
        return {"items": []}

    items = OrderItem.query.filter_by(order_id=order.id).all()

    return {
        "items": [
            {
                "food_id": i.food_id,
                "name": i.name,
                "price": float(i.price),
                "qty": i.quantity
            } for i in items
        ]
    }
@restaurant_bp.route("/orders/pay/<int:table_id>", methods=["PUT"])
def pay_order(table_id):

    # 1. Lấy tất cả order active
    orders = Order.query.filter_by(
        table_id=table_id,
        status="active"
    ).all()

    # 2. Update hết thành paid
    for o in orders:
        o.status = "paid"

    # 3. Update trạng thái bàn
    table = Tables.query.get(table_id)
    if table:
        table.Status = "Available"

    # 4. Commit
    db.session.commit()

    return jsonify({
        "message": "Thanh toán thành công",
        "table_status": "Available"
    }), 200



@restaurant_bp.route('/menu/<id>/toggle', methods=['PUT', 'OPTIONS'])
def toggle_menu(id):

    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        return response, 200

    menu = Food.query.get(id)
    if not menu:
        return jsonify({"error": "Not found"}), 404

    # FIX: Kiểm tra rõ ràng, nếu là None hoặc 1 (True) thì chuyển thành 0 (False)
    # Cách này loại bỏ hoàn toàn sự nhập nhằng của giá trị NULL
    if menu.Visible is None or menu.Visible == True or menu.Visible == 1:
        menu.Visible = False
    else:
        menu.Visible = True

    db.session.commit()

    # Refresh để lấy giá trị chính xác nhất vừa lưu vào DB
    db.session.refresh(menu)

    return jsonify({
        "message": "updated",
        "visible": bool(menu.Visible)
    }), 200