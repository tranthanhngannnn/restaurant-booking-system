from core import create_app, db
from models.restaurant import Restaurant
from models.table import Table
from sqlalchemy import text

app = create_app()

with app.app_context():

    # 🔥 1. RESET DATABASE (xóa sạch + reset ID)
    db.session.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    db.session.execute(text("TRUNCATE TABLE tables"))
    db.session.execute(text("TRUNCATE TABLE Restaurant"))
    db.session.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    db.session.commit()

    print("Đã reset DB")

    # 🔥 2. TẠO RESTAURANT
    restaurant = Restaurant(RestaurantName="Nhà hàng A")
    db.session.add(restaurant)
    db.session.commit()

    print("Đã tạo Restaurant")

    # 🔥 3. TẠO 17 BÀN
    for i in range(1, 18):

        # mặc định 4 người
        capacity = 4

        # bàn 6 người
        if i in [4, 6, 13]:
            capacity = 6

        # bàn 8 người (bàn dài nhất)
        if i == 17:
            capacity = 8

        table = Table(
            name=f"Bàn {i}",
            capacity=capacity,
            seats=capacity,
            status="available",
            restaurant_id=restaurant.RestaurantID
        )

        db.session.add(table)

    db.session.commit()

    print("Đã tạo 17 bàn thành công!")

    # 🔍 4. IN RA CHECK
    for t in Table.query.all():
        print(t.name, "-", t.capacity, "người")