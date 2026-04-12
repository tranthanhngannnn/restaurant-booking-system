from core import create_app, db
from models.restaurant import Restaurant
from models.table import Table
from sqlalchemy import text

app = create_app()


def seed_restaurants():
    """Tạo danh sách nhà hàng"""
    data = [
        "Nhà hàng lẩu",
        "Nhà hàng nướng"
    ]

    restaurants = [
        Restaurant(RestaurantName=name)
        for name in data
    ]

    db.session.add_all(restaurants)
    db.session.commit()

    return restaurants


def seed_tables(restaurants):
    """Tạo bàn cho từng nhà hàng"""

    for restaurant in restaurants:

        for i in range(1, 18):

            capacity = 4

            if i in [4, 6, 13]:
                capacity = 6

            if i == 17:
                capacity = 8

            db.session.add(
                Table(
                    name=f"Bàn {i}",
                    capacity=capacity,
                    seats=capacity,
                    status="available",
                    restaurant_id=restaurant.RestaurantID
                )
            )

    db.session.commit()


def reset_db():
    """Xoá sạch database an toàn"""

    db.session.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    db.session.execute(text("TRUNCATE TABLE `table`"))
    db.session.execute(text("TRUNCATE TABLE restaurant"))
    db.session.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    db.session.commit()


with app.app_context():

    # 🔥 STEP 1: RESET DB
    reset_db()
    print("✔ Đã reset DB")

    # 🔥 STEP 2: SEED RESTAURANT
    restaurants = seed_restaurants()
    print("✔ Đã tạo restaurant")

    # 🔥 STEP 3: SEED TABLE
    seed_tables(restaurants)
    print("✔ Đã tạo bàn")

    # 🔍 CHECK
    for t in Table.query.all():
        print(t.name, "-", t.capacity, "người")