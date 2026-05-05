from core import create_app, db
from models.cuisine import Cuisine
from models.user import User

app = create_app()

with app.app_context():
    # tạo bảng nếu chưa có
    db.create_all()

    # ======================
    # SEED CUISINE
    # ======================
    if not Cuisine.query.first():
        c1 = Cuisine(CuisineName="Hotpot", Status="Active")
        c2 = Cuisine(CuisineName="Korean", Status="Active")
        c3 = Cuisine(CuisineName="Japanese", Status="Active")

        db.session.add_all([c1, c2, c3])
        db.session.commit()

        print("Seed Cuisine DONE!")
    else:
        print("Cuisine already exists")

    # ======================
    # SEED USER (THÊM Ở ĐÂY)
    # ======================
    if not User.query.first():
        u1 = User(
            Username="restaurant1",
            Password="1",
            Role="staff",
            RestaurantID=1
        )

        u2 = User(
            Username="restaurant2",
            Password="2",
            Role="staff",
            RestaurantID=2
        )

        db.session.add_all([u1, u2])
        db.session.commit()

        print("Seed Users DONE!")
    else:
        print("Users already exists")