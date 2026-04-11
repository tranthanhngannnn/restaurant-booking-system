from flask import request, jsonify ,Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
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
        "UserID": get_jwt_identity() # Lấy ID người đang login làm chủ
    }
    result, status = RestaurantService.create(data, is_admin=False)
    return jsonify(result), status

@restaurant_bp.route("/tables/<int:id>/status", methods=["PUT"])
def update_table_status(id):
    return jsonify(update_table_status_service(id, request.json))


@restaurant_bp.route('/menu', methods=['GET'])
def get_menu():
    menus = Menu.query.filter_by(visible=True).all()  # chỉ lấy món hiển thị
    return jsonify([{
        "id": m.id,
        "name": m.name,
        "price": m.price,
        "image": m.image,
        "category": m.category,
        "description": m.description,
        "visible": m.visible
    } for m in menus])

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


@restaurant_bp.route("/orders", methods=["POST"])
def create_order():
    data = request.json
    table_id = data["table_id"]

    # 🔥 check bàn
    table = Table.query.get(table_id)
    if not table:
        return {"error": "Table not found"}, 404

    # 🔥 lấy order active (nếu có)
    order = Order.query.filter_by(table_id=table_id, status="active").first()

    if not order:
        order = Order(table_id=table_id, status="active")
        db.session.add(order)
        db.session.commit()

        # cập nhật bàn
        table.status = "reserved"

    # 🔥 thêm món
    for item in data["items"]:
        existing = OrderItem.query.filter_by(
            order_id=order.id,
            menu_id=item["menu_id"]
        ).first()

        if existing:
            existing.quantity += item["qty"]
        else:
            oi = OrderItem(
                order_id=order.id,
                menu_id=item["menu_id"],
                quantity=item["qty"]
            )
            db.session.add(oi)

    db.session.commit()

    return {"message": "Order updated"}

@restaurant_bp.route("/orders/pay/<int:table_id>", methods=["PUT"])
def pay_order(table_id):
    order = Order.query.filter_by(table_id=table_id, status="active").first()

    if not order:
        return {"error": "No active order"}

    order.status = "paid"

    table = Table.query.get(table_id)
    table.status = "available"

    db.session.commit()

    return {"message": "Paid"}

@restaurant_bp.route("/orders/table/<int:table_id>", methods=["GET"])
def get_order_by_table(table_id):
    order = Order.query.filter_by(table_id=table_id, status="active").first()

    if not order:
        return jsonify(None)

    items = OrderItem.query.filter_by(order_id=order.id).all()

    return jsonify({
        "id": order.id,
        "items": [
            {
                "menu_id": i.menu_id,
                "qty": i.quantity
            } for i in items
        ]
    })

@restaurant_bp.route("/menu/<int:id>/visible", methods=["PUT"])
def toggle_menu_visibility(id):
    menu = Menu.query.get(id)
    if not menu:
        return {"error": "Menu not found"}, 404

    data = request.json
    if "visible" in data:
        menu.visible = data["visible"]
    else:
        menu.visible = not menu.visible  # toggle

    db.session.commit()
    return {"id": menu.id, "visible": menu.visible}