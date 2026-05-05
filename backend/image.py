from core import create_app, db
from models.menu import Menu

app = create_app()

MENU_DATA = [
    {
        "name": "Lẩu Thái",
        "category": "lau",
        "price": 50000,
        "image": "/static/images/Food/Lau/lauthai.jpg",
        "stock": 10
    },
    {
        "name": "Lẩu Mala",
        "category": "lau",
        "price": 50000,
        "image": "/static/images/Food/Lau/laumala.jpg",
        "stock": 10
    },
    {
        "name": "Lẩu Cua Đồng",
        "category": "lau",
        "price": 50000,
        "image": "/static/images/Food/Lau/laucuadong.jpg",
        "stock": 10
    },
    {
        "name": "Lẩu Kimchi",
        "category": "lau",
        "price": 60000,
        "image": "/static/images/Food/Lau/laukimchi.jpg",
        "stock": 10
    },
    {
        "name": "Lẩu Tứ Xuyên",
        "category": "lau",
        "price": 50000,
        "image": "/static/images/Food/Lau/lautuxuyen.jpg",
        "stock": 10
    },
    {
        "name": "Lẩu Bò Nhúng Giấm",
        "category": "lau",
        "price": 50000,
        "image": "/static/images/Food/Lau/laubonhunggiam.jpg",
        "stock": 10
    },
{
        "name": "Set Thịt Nhỏ",
        "category": "lau",
        "price": 120000,
        "image": "/static/images/Food/Lau/setthitnho.jpg",
        "stock": 10
    },
    {
    "name": "Hải Sản Tổng Hợp",
    "category": "lau",
    "price": 150000,
    "image": "/static/images/Food/Lau/haisantonghop.jpg",
    "stock": 10
},
{
        "name": "Combo Rau Nấm",
        "category": "lau",
        "price": 100000,
        "image": "/static/images/Food/Lau/comboraunam.jpg",
        "stock": 10
    },
{
        "name": "Set Thịt Lớn",
        "category": "lau",
        "price": 240000,
        "image": "/static/images/Food/Lau/setthitlon.jpg",
        "stock": 10
    },
    {
        "name": "Set Viên Thả Lẩu",
        "category": "lau",
        "price": 100000,
        "image": "/static/images/Food/Lau/setvienthalau.jpg",
        "stock": 10
    },
{
        "name": "Buffet Tráng Miệng",
        "category": "lau",
        "price": 50000,
        "image": "/static/images/Food/Lau/buffettrangmieng.jpg",
        "stock": 10
    },

    # Nướng
    {
        "name": "Ba Chỉ Bò Mỹ",
        "category": "nuong",
        "price": 90000,
        "image": "/static/images/Food/Nuong/bachibomy.png",
        "stock": 10
    },
    {
        "name": "Lõi Vai Bò",
        "category": "nuong",
        "price": 90000,
        "image": "/static/images/Food/Nuong/loivaibo.jpg",
        "stock": 10
    },
    {
        "name": "Thịt Heo Iberico",
        "category": "nuong",
        "price": 70000,
        "image": "/static/images/Food/Nuong/thitheoiberico.jpg",
        "stock": 10
    },
    {
        "name": "Kimchi",
        "category": "nuong",
        "price": 25000,
        "image": "/static/images/Food/Nuong/kimchi.jpg",
        "stock": 10
    },
    {
        "name": "Bạch Tuộc Mini",
        "category": "nuong",
        "price": 85000,
        "image": "/static/images/Food/Nuong/bachtuocmini.jpg",
        "stock": 10
    },
    {
        "name": "Sò Điệp Mỡ Hành",
        "category": "nuong",
        "price": 85000,
        "image": "/static/images/Food/Nuong/sodiepnuongmohanh.jpg",
        "stock": 10
    },
    {
        "name": "Sườn Non Ướp Mật Ong",
        "category": "nuong",
        "price": 120000,
        "image": "/static/images/Food/Nuong/suonnonuopmatong.jpg",
        "stock": 10
    },
    {
        "name": "Rau Sống Ăn Kèm",
        "category": "nuong",
        "price": 90000,
        "image": "/static/images/Food/Nuong/rausongankem.jpg",
        "stock": 10
    },
    {
        "name": "Combo Nấm",
        "category": "nuong",
        "price": 100000,
        "image": "/static/images/Food/Nuong/combonam.png",
        "stock": 10
    },
    {
        "name": "Tôm Nướng Sa Tế",
        "category": "nuong",
        "price": 240000,
        "image": "/static/images/Food/Nuong/tomnuongsate.jpg",
        "stock": 10
    },
    {
        "name": "Nạc Vai Heo",
        "category": "nuong",
        "price": 100000,
        "image": "/static/images/Food/Nuong/nacvaiheo.jpg",
        "stock": 10
    },
    {
        "name": "Trái Cây Tổng Hợp",
        "category": "nuong",
        "price": 100000,
        "image": "/static/images/Food/Nuong/traicaytonghop.jpg",
        "stock": 10
    }
]

with app.app_context():

    db.session.query(Menu).delete()
    db.session.commit()

    for item in MENU_DATA:
        menu = Menu(
            name=item["name"],
            price=item["price"],
            image=item["image"],
            category=item["category"],
            visible=True
        )
        db.session.add(menu)

    db.session.commit()

    print("Seed menu thành công!")
