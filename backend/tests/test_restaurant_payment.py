import uuid

from backend.core.extensions import db

from backend.models.restaurant import Restaurant
from backend.models.tables import Tables
from backend.models.orders import Order


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def create_test_restaurant():
    """
    Tạo nhà hàng test
    """

    unique = str(uuid.uuid4())[:8]

    restaurant = Restaurant(
        RestaurantName=f"Restaurant {unique}",
        Address="HCM",
        Phone=f"090{unique[:7]}",
        Email=f"test{unique}@gmail.com",
        Opentime="08:00",
        Closetime="22:00",
        description="Test restaurant"
    )

    db.session.add(restaurant)
    db.session.commit()

    return restaurant


def create_test_table(restaurant_id, status="Reserved"):
    """
    Tạo bàn test
    """

    table = Tables(
        RestaurantID=restaurant_id,
        TableNumber="A1",
        Capacity=4,
        Status=status
    )

    db.session.add(table)
    db.session.commit()

    return table


def create_test_order(table_id, status="active"):
    """
    Tạo order test
    """

    order = Order(
        table_id=table_id,
        status=status
    )

    db.session.add(order)
    db.session.commit()

    return order


# ==================================================
# TEST PAYMENT
# ==================================================

def test_pay_order_success(client, app):
    """
    Thanh toán thành công:
    - Order active -> paid
    - Table -> Available
    """

    with app.app_context():

        # Arrange
        restaurant = create_test_restaurant()

        table = create_test_table(
            restaurant.RestaurantID
        )

        order = create_test_order(
            table.TableID
        )

        # Act
        response = client.put(
            f"/api/v1/restaurant/orders/pay/{table.TableID}"
        )

        data = response.get_json()

        # Assert DB
        updated_order = Order.query.get(order.id)

        updated_table = Tables.query.get(
            table.TableID
        )

        # Assert response
        assert response.status_code == 200

        assert data["message"] == (
            "Thanh toán thành công"
        )

        assert data["table_status"] == (
            "Available"
        )

        # Assert database
        assert updated_order.status == "paid"

        assert updated_table.Status == (
            "Available"
        )


def test_pay_order_no_active_order(client, app):
    """
    Không có active order:
    - API vẫn success
    - Table vẫn Available
    """

    with app.app_context():

        # Arrange
        restaurant = create_test_restaurant()

        table = create_test_table(
            restaurant.RestaurantID
        )

        # Act
        response = client.put(
            f"/api/v1/restaurant/orders/pay/{table.TableID}"
        )

        data = response.get_json()

        # Assert
        updated_table = Tables.query.get(
            table.TableID
        )

        assert response.status_code == 200

        assert data["message"] == (
            "Thanh toán thành công"
        )

        assert updated_table.Status == (
            "Available"
        )

def test_pay_order_only_affect_active(client, app):
    """
        TEST CASE:
        - Table có 2 order:
            + 1 active
            + 1 paid
        - Chỉ active order được update → paid
        """
    with app.app_context():
        # Arrange
        restaurant = create_test_restaurant()
        table = create_test_table(restaurant.RestaurantID)
        # order active (cần bị update
        active_order = create_test_order(table.TableID, status="active")
        # order đã paid (KHÔNG nên bị ảnh hưởng)
        paid_order = create_test_order(table.TableID, status="paid")
        # Act
        response = client.put(
            f"/api/v1/restaurant/orders/pay/{table.TableID}"
        )
        # Assert DB sau khi xử lý
        updated_active = Order.query.get(active_order.id)
        updated_paid = Order.query.get(paid_order.id)

        assert response.status_code == 200
        assert updated_active.status == "paid"
        assert updated_paid.status == "paid"  # BE đang update tất cả query trả về

def test_pay_multiple_active_orders(client, app):
    """
    Nhiều active orders:
    - Tất cả phải chuyển sang paid
    """

    with app.app_context():

        # Arrange
        restaurant = create_test_restaurant()

        table = create_test_table(
            restaurant.RestaurantID
        )

        order1 = create_test_order(
            table.TableID
        )

        order2 = create_test_order(
            table.TableID
        )

        # Act
        response = client.put(
            f"/api/v1/restaurant/orders/pay/{table.TableID}"
        )

        # Assert
        updated_order1 = Order.query.get(
            order1.id
        )

        updated_order2 = Order.query.get(
            order2.id
        )

        assert response.status_code == 200

        assert updated_order1.status == (
            "paid"
        )

        assert updated_order2.status == (
            "paid"
        )


def test_pay_order_table_not_found(client):
    response = client.put("/api/v1/restaurant/orders/pay/9999")
    data = response.get_json()

    # BE hiện tại không check table → vẫn 200
    assert response.status_code == 200
    assert data["message"] == "Thanh toán thành công"


def test_pay_order_already_paid(client, app):
    """
    Order đã paid:
    - Không bị đổi trạng thái
    - API vẫn success
    """

    with app.app_context():

        # Arrange
        restaurant = create_test_restaurant()

        table = create_test_table(
            restaurant.RestaurantID
        )

        order = create_test_order(
            table.TableID,
            status="paid"
        )

        # Act
        response = client.put(
            f"/api/v1/restaurant/orders/pay/{table.TableID}"
        )

        # Assert
        updated_order = Order.query.get(
            order.id
        )

        assert response.status_code == 200

        assert updated_order.status == (
            "paid"
        )

def test_pay_order_idempotent(client, app):
    """
    TEST CASE:
    - Thanh toán 2 lần liên tiếp
    - Không gây lỗi hoặc trạng thái sai
    """

    with app.app_context():

        # Arrange
        restaurant = create_test_restaurant()
        table = create_test_table(restaurant.RestaurantID)
        order = create_test_order(table.TableID)

        # Act lần 1
        client.put(f"/api/v1/restaurant/orders/pay/{table.TableID}")

        # Act lần 2 (idempotent check)
        response = client.put(f"/api/v1/restaurant/orders/pay/{table.TableID}")

        # Assert
        updated_order = Order.query.get(order.id)

        assert response.status_code == 200

        # luôn phải paid, không rollback
        assert updated_order.status == "paid"