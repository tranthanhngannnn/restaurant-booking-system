import uuid
from backend.core.extensions import db
from backend.models.restaurant import Restaurant
from backend.models.food import Food
from backend.app.api.v1.restaurant.service import (
    create_order,
    merge_order_quantity
)

# HELPER

def create_test_restaurant():
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


def create_test_food(restaurant_id):

    unique = str(uuid.uuid4())[:5]

    food = Food(
        FoodID=unique,
        FoodName="Pizza",
        RestaurantID=restaurant_id,
        Price=100000,
        Description="Test food",
        Visible=True
    )

    db.session.add(food)
    db.session.commit()

    return food

# TEST CREATE ORDER
def test_create_order_success(app):
    """
    Tạo order thành công
    """
    with app.app_context():
        restaurant = create_test_restaurant()
        food = create_test_food(restaurant.RestaurantID)
        data={"table_id": 1, "items": [{"food_id": food.FoodID, "qty": 2}]}

        result = create_order(data)
        assert result["message"] == "Order created"
        assert result["table_id"] == 1
        assert result["total"] == 200000
        assert len(result["items"]) == 1
def test_create_order_quantity_string(app):
    """
    qty truyền dạng string
    """

    with app.app_context():
        restaurant = create_test_restaurant()
        food = create_test_food(restaurant.RestaurantID)
        result = create_order({"table_id": 1, "items": [{"food_id":food.FoodID,"qty": 3}]})
        assert result["message"] == "Order created"
        assert result["total"] == 300000

def test_create_order_multiple_items(app):
    """
    Order nhiều món
    """
    with app.app_context():

        restaurant = create_test_restaurant()

        food1 = create_test_food(restaurant.RestaurantID)
        food2 = create_test_food(restaurant.RestaurantID)

        food2.Price = 50000
        db.session.commit()

        result = create_order({
            "table_id": 1,
            "items": [
                {
                    "food_id": food1.FoodID,
                    "qty": 2
                },
                {
                    "food_id": food2.FoodID,
                    "qty": 1
                }
            ]
        })

        assert result["message"] == "Order created"
        assert result["total"] == 250000
        assert len(result["items"]) == 2

def test_create_order_missing_table_id(app):
    """
    Thiếu table_id
    """
    with app.app_context():
        result=create_order({"items":[]})
        assert result["error"] == "Missing table_id"


def test_create_order_no_items(app):
    """
    Order không có món
    """

    with app.app_context():
        result =create_order({"table_id": 1,"items": []})
        assert result["error"] == "No items"


def test_create_order_invalid_quantity(app):
    """
    Quantity <= 0
    """
    with app.app_context():

        restaurant = create_test_restaurant()
        food = create_test_food(restaurant.RestaurantID)
        data={"table_id": 1, "items": [{"food_id": food.FoodID, "qty": 0}]}
        result = create_order(data)
        assert result["error"] == "Invalid quantity"

def test_create_order_negative_quantity(app):
    """
    Quantity < 0
    """

    with app.app_context():
        restaurant = create_test_restaurant()
        food = create_test_food(restaurant.RestaurantID)
        result = create_order({"table_id": 1, "items": [{"food_id": food.FoodID,"qty": -2}]})
        assert result["error"] == "Invalid quantity"


def test_create_order_food_not_found(app):
    """
    Food không tồn tại
    """
    with app.app_context():
        data={"table_id": 1, "items": [{"food_id": "XXXXX", "qty": 1}]}
        result = create_order(data)
        assert result["error"] == "Food not found"

def test_create_order_missing_food_id(app):
    """
    Không truyền food_id
    """
    with app.app_context():
        result = create_order({"table_id": 1, "items": [{"qty": 1}]})
        assert result["error"] == "Food not found"

# TEST MERGE ORDER QUANTITY
def test_merge_order_quantity():
    """
    Merge quantity cũ + mới
    """
    result = merge_order_quantity(2, 3)
    assert result == 5


def test_merge_order_quantity_zero():
    """
    Merge với quantity = 0
    """

    result = merge_order_quantity(5, 0)

    assert result == 5


def test_merge_order_quantity_large_number():
    """
    Merge số lượng lớn
    """
    result = merge_order_quantity(100, 200)
    assert result == 300

