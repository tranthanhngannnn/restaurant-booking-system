from core import create_app, db
from models.menu import Menu

app = create_app()

MENU_DATA = [
    {
        "name": "Lẩu Thái",
        "category": "lau",
        "price": 50000,
        "image": "https://brand-pcms.ggg.systems/media/catalog/product/60001564-lau-thai.jpg",
        "stock": 10
    },
    {
        "name": "Lẩu Mala",
        "category": "lau",
        "price": 50000,
        "image": "https://brand-pcms.ggg.systems/media/catalog/product/60001563-lau-mala.jpg",
        "stock": 10
    },
    {
        "name": "Lẩu Cua Đồng",
        "category": "lau",
        "price": 50000,
        "image": "https://tiki.vn/lau-cua-dong.jpg",
        "stock": 10
    },
    {
        "name": "Lẩu Kimchi",
        "category": "lau",
        "price": 60000,
        "image": "https://thichlaunuong.com/lau-kimchi.jpg",
        "stock": 10
    },
    {
        "name": "Lẩu Tứ Xuyên",
        "category": "lau",
        "price": 50000,
        "image": "https://brand-pcms.ggg.systems/lau-tu-xuyen.jpg",
        "stock": 10
    },
    {
        "name": "Lẩu Bò Nhúng Giấm",
        "category": "lau",
        "price": 50000,
        "image": "https://i.pinimg.com/lau-bo.jpg",
        "stock": 10
    },
{
        "name": "Set Thịt Nhỏ",
        "category": "lau",
        "price": 120000,
        "image": "https://i.pinimg.com/1200x/10/84/9a/10849a51b3a4716655ab197944a1d995.jpg",
        "stock": 10
    },
    {
    "name": "Hải Sản Tổng Hợp",
"category": "lau",
"price": 150000,
"image": "https://i.pinimg.com/736x/f2/c0/41/f2c04156507b638dd7710a393405840e.jpg",
"stock": 10
},
{
        "name": "Combo Rau Nấm",
        "category": "lau",
        "price": 100000,
        "image": "https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/r/a/rau_nam_tong_hop.jpg",
        "stock": 10
    },
{
        "name": "Set Thịt Lớn",
        "category": "lau",
        "price": 240000,
        "image": "https://i.pinimg.com/736x/cd/2f/59/cd2f59d1d3406af4e0c80cbe8b726799.jpg",
        "stock": 10
    },
    {
        "name": "Set Viên Thả Lẩu",
        "category": "lau",
        "price": 100000,
        "image": "http://anvatngon.vn/upload/images/set-vien-tha-lau-eb-steamboat-5in1-nk-malaysia-mon-an-che-bien-tai-nha-hotline-093-8828-553.jpg",
        "stock": 10
    },
{
        "name": "Buffet Tráng Miệng",
        "category": "lau",
        "price": 50000,
        "image": "https://i.pinimg.com/736x/93/21/0c/93210c9b608c619be5495e4253d95fbd.jpg",
        "stock": 10
    },

    # Nướng
    {
        "name": "Ba Chỉ Bò Mỹ",
        "category": "nuong",
        "price": 90000,
        "image": "https://brand-pcms.ggg.systems/ba-chi-bo.jpg",
        "stock": 10
    },
    {
        "name": "Lõi Vai Bò",
        "category": "nuong",
        "price": 90000,
        "image": "https://brand-pcms.ggg.systems/loi-vai-bo.jpg",
        "stock": 10
    },
    {
        "name": "Thịt Heo Iberico",
        "category": "nuong",
        "price": 70000,
        "image": "https://brand-pcms.ggg.systems/heo-iberico.jpg",
        "stock": 10
    },
    {
        "name": "Kimchi",
        "category": "nuong",
        "price": 25000,
        "image": "https://i.pinimg.com/kimchi.jpg",
        "stock": 10
    },
    {
        "name": "Bạch Tuộc Mini",
        "category": "nuong",
        "price": 85000,
        "image": "https://brand-pcms.ggg.systems/bach-tuoc.jpg",
        "stock": 10
    },
{
        "name": "Sò Điệp Mỡ Hành",
        "category": "nuong",
        "price": 85000,
        "image": "https://i.pinimg.com/1200x/c4/b6/34/c4b634ee4f04c0cf4fe83a9fba39dd19.jpg",
        "stock": 10
    },
{
        "name": "Sườn Non Ướp Mật Ong",
        "category": "nuong",
        "price": 120000,
        "image": "https://i.pinimg.com/736x/3e/58/15/3e58156f6d4f5efba5ec8c72f52d5ff3.jpg",
        "stock": 10
    },
{
        "name": "Rau Sống Ăn Kèm",
        "category": "nuong",
        "price": 90000,
        "image": "https://cdn.yeutre.vn/medias/uploads/228/228658-rau-an-do-nuong-han-quoc.jpg",
        "stock": 10
    },
{
        "name": "Combo Nấm",
        "category": "nuong",
        "price": 100000,
        "image": "https://image.foodbook.vn/upload/20220503/1651551345115_blob.png",
        "stock": 10
    },
{
        "name": "Tôm Nướng Sa ế",
        "category": "nuong",
        "price": 240000,
        "image": "https://i.pinimg.com/1200x/94/03/bf/9403bf0a4317828cc0d50e30d493c189.jpg",
        "stock": 10
    },
{
        "name": "Nạc Vai Heo",
        "category": "nuong",
        "price": 100000,
        "image": "https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/3/1/31_1.jpg",
        "stock": 10
    },
{
        "name": "Trái Cây Tổng Hợp",
        "category": "nuong",
        "price": 100000,
        "image": "https://i.pinimg.com/1200x/51/e9/00/51e90025e4f0f776b454617976400147.jpg",
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