from core import create_app, db
from models.restaurant import Restaurant
from models.table import Tables
from sqlalchemy import text
from datetime import time

app = create_app()


def seed_restaurants():
    """Tạo danh sách nhà hàng với đầy đủ thông tin"""
    restaurants = [
        Restaurant(
            RestaurantName="Hotpot",
            Address="123 Đường Nguyễn Đình Chiểu, Quận 3, TP.HCM",
            Phone="0901234567",
            Email="contact@hotpot.vn",
            Opentime=time(10, 0),
            Closetime=time(22, 30),
            description="Nhà hàng lẩu Tứ Xuyên siêu cay khổng lồ, không gian ấm cúng phù hợp cho gia đình và nhóm bạn.",
            status="Approved",  # Nên để Approved để dễ test hiển thị
            UserID=1,           # Giả sử ID của user chủ nhà hàng là 1 (nhớ đảm bảo bảng User có ID này nhé)
            CuisineID=1         # 1 là Lẩu - Khớp với thẻ select bên HTML
        ),
        Restaurant(
            RestaurantName="Grill House",
            Address="456 Đường Sư Vạn Hạnh, Quận 10, TP.HCM",
            Phone="0987654321",
            Email="booking@grillhouse.vn",
            Opentime=time(16, 0),
            Closetime=time(23, 59),
            description="Đồ nướng BBQ Hàn Quốc xèo xèo, thịt bò nhập khẩu tươi ngon, view check-in cực xịn.",
            status="Approved",
            UserID=2,           # Giả sử ID của user chủ nhà hàng là 2
            CuisineID=2         # 2 là Nướng - Khớp với thẻ select bên HTML
        )
    ]

    # Thêm vào session và lưu xuống Database
    db.session.add_all(restaurants)
    db.session.commit()

    print("Đã seed thành công 2 nhà hàng: Hotpot và Grill House!")
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
                Tables(
                    TableNumber=f"Bàn {i}",
                    Capacity=capacity,
                    Seats=capacity,

                    Status="available",
                    RestaurantID=restaurant.RestaurantID
                )
            )

    db.session.commit()


def reset_db():
    """Xoá sạch database an toàn"""

    db.session.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    db.session.execute(text("TRUNCATE TABLE `Table`"))
    db.session.execute(text("TRUNCATE TABLE Restaurant"))
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
    for t in Tables.query.all():
        print(t.TableNumber, "-", t.Capacity, "người")
