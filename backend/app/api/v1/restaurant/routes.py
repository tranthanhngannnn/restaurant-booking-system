from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.menu import Menu
from models.tables import Tables
from models.booking import Reservation
from models.orders import Order
from models.ordersitem import OrderItem
from core.extensions import db

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

@restaurant_bp.route('/menu', methods=['GET'])
def get_menu_api():
    menus = Menu.query.filter_by(Visible=True).all()
    return jsonify([{
        "id": m.MenuID,
        "name": m.FoodName,
        "price": m.Price,
        "image": m.Image,
        "category": m.Category,
        "description": m.Description,
        "visible": m.Visible
    } for m in menus])

@restaurant_bp.route('/menu/admin', methods=['GET'])
def get_menu_admin():
    menus = Menu.query.all()
    return jsonify([{
        "id": m.MenuID,
        "name": m.FoodName,
        "price": m.Price,
        "image": m.Image,
        "category": m.Category,
        "visible": m.Visible
    } for m in menus])

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

@restaurant_bp.route('/menu/<int:id>/toggle', methods=['PUT'])
def toggle_menu(id):
    menu = Menu.query.get(id)
    if not menu: return jsonify({"error":"Not found"}), 404
    menu.Visible = not menu.Visible
    db.session.commit()
    return jsonify({"message":"updated", "visible": menu.Visible})
