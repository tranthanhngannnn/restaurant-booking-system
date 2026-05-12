import pytest
from unittest.mock import MagicMock
from backend.app.api.v1.restaurant import service
from backend.models.food import Food
from backend.core.extensions import db
from backend.core import create_app

# Mock MENU_DATA cho trường hợp fallback ảnh
MOCK_MENU_DATA = [{"name": "Lau Ca", "image": "lauca.jpg"}]

@pytest.fixture
def app():
    app = create_app()
    app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")
    return app

@pytest.fixture
def app_context(app):
    with app.app_context():
        yield

# 1. Validation cho create_food
@pytest.mark.parametrize("data, expected", [
    ({"name": "", "price": 100}, {"error": "Missing name"}),           # Tên trống
    ({"name": "Com", "price": None}, {"error": "Missing price"}),      # Giá trống
    ({"name": "Com", "price": "abc"}, {"error": "Invalid price"}),     # Giá không phải số
    ({"name": "Com", "price": -500}, {"error": "Invalid price"}),      # Giá <= 0
])
def test_create_food_validation(data, expected):
    res = service.create_food(data, 1)
    assert res == expected

# 2. Thêm món thành công (ID ngẫu nhiên 5 ký tự)
def test_create_food_success(monkeypatch, app_context):
    # Giả lập ID ngẫu nhiên "A1B2C"
    monkeypatch.setattr("random.choices", lambda *a, **kw: ["A", "1", "B", "2", "C"])
    monkeypatch.setattr(Food, "query", MagicMock(get=lambda id: None))
    monkeypatch.setattr(db.session, "add", lambda x: None)
    monkeypatch.setattr(db.session, "commit", lambda: None)
    
    res = service.create_food({"name": "Lẩu Thái", "price": 250000}, 1)
    assert res == {"msg": "Thêm thành công", "id": "A1B2C"}

# 3-4. Xóa món ăn (Thành công & Không tồn tại)
def test_delete_food_success(monkeypatch, app_context):
    monkeypatch.setattr(Food, "query", MagicMock(get=lambda id: MagicMock()))
    monkeypatch.setattr(db.session, "delete", lambda x: None)
    monkeypatch.setattr(db.session, "commit", lambda: None)
    res = service.delete_food("LKC")
    assert res == {"msg": "Deleted"}

def test_delete_food_not_found(monkeypatch, app_context):
    monkeypatch.setattr(Food, "query", MagicMock(get=lambda id: None))
    res = service.delete_food("99999")
    assert res == {"error": "Food not found"}

# 5-6. Cập nhật món ăn (Thành công & Không tồn tại)
def test_update_food_success(monkeypatch, app_context):
    mock_food = MagicMock()
    monkeypatch.setattr(Food, "query", MagicMock(get=lambda id: mock_food))
    monkeypatch.setattr(db.session, "commit", lambda: None)
    res = service.update_food("LKC", {"name": "Lẩu Hải Sản", "price": 300000})
    assert res["msg"] == "Updated"
    assert mock_food.FoodName == "Lẩu Hải Sản"

def test_update_food_not_found(monkeypatch, app_context):
    monkeypatch.setattr(Food, "query", MagicMock(get=lambda id: None))
    res = service.update_food("NONAME", {"name": "X"})
    assert res == {"error": "Food not found"}

# 7. Cập nhật hình ảnh (URL trực tiếp & Bỏ qua null/undefined)
def test_update_food_image_logic(monkeypatch, app_context):
    mock_food = MagicMock(Image_URL="old_img.png")
    monkeypatch.setattr(Food, "query", MagicMock(get=lambda id: mock_food))
    monkeypatch.setattr(db.session, "commit", lambda: None)
    
    # Cập nhật URL trực tiếp
    service.update_food("LKC", {"image": "http://img.png"})
    assert mock_food.Image_URL == "http://img.png"
    
    # Bỏ qua nếu là "null" hoặc "undefined"
    service.update_food("LKC", {"image": "null"})
    assert mock_food.Image_URL == "http://img.png"

# 8. Lấy menu Admin (Logic Visible, Float Price, Fallback Image)
def test_get_menu_res_admin_logic(monkeypatch, app_context):
    # Mock data từ DB
    mock_food_items = [
        MagicMock(FoodID="F1", FoodName="Phở", Price=50000, Image_URL="food_db.jpg", RestaurantID=1, Visible=True),
        MagicMock(FoodID="F2", FoodName="Lau Ca", Price=30000, Image_URL=None, RestaurantID=1, Visible=False), # Fallback to lauca.jpg
        MagicMock(FoodID="F3", FoodName="Lạ", Price=20000, Image_URL="", RestaurantID=1, Visible=True),    # No match
        MagicMock(FoodID=None, FoodName="", Price=None, Image_URL=None, RestaurantID=1, Visible=True)     # Defaults
    ]
    
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = mock_food_items
    monkeypatch.setattr(Food, "query", mock_query)
    
    # Mock MENU_DATA trong module service
    import sys
    sys.modules["image"] = MagicMock(MENU_DATA=MOCK_MENU_DATA)

    res = service.get_menu_res_admin(1)
    
    assert len(res) == 4
    assert res[0]["price"] == 50000.0          # Ép kiểu float
    assert res[1]["Visible"] is False         # Xử lý Visible=False
    assert res[0]["image"] == "food_db.jpg"   # Ưu tiên lấy từ DB
    assert res[1]["image"] == "pho.jpg"       # Fallback sang MENU_DATA
    assert res[2]["image"] == ""              # Không tìm thấy -> rỗng
    assert res[3]["id"] is None               # Default ID
    assert res[3]["price"] == 0.0             # Default Price

# 9. Kiểm tra lỗi Import ảnh (Try-Except logic)
def test_get_menu_res_admin_import_exception(monkeypatch, app_context):
    # Giả lập lỗi Import khi load module image
    import sys
    if "image" in sys.modules: del sys.modules["image"]
    
    monkeypatch.setattr(Food, "query", MagicMock(filter=lambda *a: MagicMock(all=lambda: [])))
    
    # Hệ thống phải bắt được lỗi Import và thử fallback sang backend.image hoặc không crash
    try:
        res = service.get_menu_res_admin(1)
        assert isinstance(res, list)
    except Exception as e:
        pytest.fail(f"Hệ thống bị crash khi gặp lỗi ImportError: {e}")
