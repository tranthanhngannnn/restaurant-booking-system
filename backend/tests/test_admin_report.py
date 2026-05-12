import pytest
from unittest.mock import MagicMock
from backend.app.api.v1.admin.service import ReportService
from backend.models.restaurant import Restaurant
from backend.core import db, create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")
    return app

@pytest.fixture
def app_context(app):
    with app.app_context():
        yield

# --- Nhóm xử lý thời gian (Test Utility Functions) ---
@pytest.mark.parametrize("func, args, expected", [
    ("_parse_month", ("2024-05",), (2024, 5)),                # Parse chuỗi năm-tháng hợp lệ
    ("_shift_month", (2023, 12, 1), (2024, 1)),               # Dịch chuyển tiến (chuyển năm)
    ("_shift_month", (2024, 1, -1), (2023, 12)),              # Dịch chuyển lùi (về năm cũ)
    ("_month_key", (2024, 5), "2024-05"),                     # Kiểm tra định dạng key YYYY-MM
    ("_month_label", (2024, 5), "Thang 05/2024"),             # Kiểm tra định dạng label có số 0
])
def test_time_utilities(func, args, expected):
    f = getattr(ReportService, func)
    assert f(*args) == expected

def test_build_months_logic():
    # Xây dựng danh sách 6 tháng gần nhất từ 2024-03
    months = ReportService._build_months("2024-03")
    assert len(months) == 6
    assert months[0]["key"] == "2023-10"
    assert months[-1]["key"] == "2024-03"

# --- Nhóm logic báo cáo (Test Report Logic) ---
@pytest.mark.parametrize("restaurant_id, mock_db_rows, expected_total, top_res_name", [
    # 1. Lấy toàn bộ, tính tổng 500k + 300k = 800k, sắp xếp BBQ (cao nhất) lên đầu
    (None, [
        MagicMock(restaurant_id=1, year=2024, month=5, revenue=300000.0),
        MagicMock(restaurant_id=2, year=2024, month=5, revenue=500000.0)
    ], 800000.0, "BBQ"),
    
    # 2. Lọc theo nhà hàng ID=1 (Hotpot), doanh thu 300k
    ("1", [
        MagicMock(restaurant_id=1, year=2024, month=5, revenue=300000.0)
    ], 300000.0, "Hotpot"),

    # 3. Nhà hàng không có doanh thu (không có đơn paid), mặc định trả về 0.0
    (None, [], 0.0, "BBQ")
])
def test_get_report_logic(monkeypatch, app_context, restaurant_id, mock_db_rows, expected_total, top_res_name):
    # Mock danh sách nhà hàng (Lọc 'Đang hoạt động', bỏ qua 'Ngưng hoạt động')
    mock_res = [
        MagicMock(RestaurantID=2, RestaurantName="BBQ", status="Đang hoạt động"),
        MagicMock(RestaurantID=1, RestaurantName="Hotpot", status="Đang hoạt động")
    ]
    
    # Giả lập SQLAlchemy query cho Restaurant
    def mock_query_chain(*args, **kwargs):
        res_list = mock_res
        if restaurant_id: res_list = [r for r in mock_res if r.RestaurantID == int(restaurant_id)]
        return MagicMock(filter=mock_query_chain, order_by=lambda *a: MagicMock(all=lambda: res_list))

    monkeypatch.setattr(Restaurant, "query", MagicMock(filter=mock_query_chain))

    # Giả lập SQLAlchemy query cho doanh thu (Chỉ tính đơn 'paid')
    mock_query = MagicMock()
    for method in ["join", "filter", "group_by", "order_by"]:
        getattr(mock_query, method).return_value = mock_query
    mock_query.all.return_value = mock_db_rows
    
    monkeypatch.setattr(db.session, "query", lambda *a: mock_query)

    # Thực thi logic báo cáo
    result = ReportService.get_report(restaurant_id, "2024-05")

    # Kiểm tra các khẳng định (Asserts)
    assert result["total_report"] == expected_total
    if result["restaurants"]:
        # Kiểm tra sắp xếp (Nhà hàng doanh thu cao hơn phải đứng trước)
        assert result["restaurants"][0]["restaurant_name"] == top_res_name
        # Kiểm tra lọc status (Không chứa nhà hàng 'Ngưng hoạt động')
        assert all(r["restaurant_name"] != "Ngưng hoạt động" for r in result["restaurants"])
        # Kiểm tra định dạng trả về của monthly_revenue (phải là list)
        assert isinstance(result["restaurants"][0]["monthly_revenue"], list)
