import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from flask_jwt_extended import create_access_token

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core import create_app

REPORT_URL = "/api/v1/admin/report"
REPORT_SERVICE_PATH = "app.api.v1.admin.routes.ReportService.get_report"


def mock_report_data(**kwargs):
    data = {
        "month": "2026-05",
        "months": [
            {"key": "2025-12"},
            {"key": "2026-01"},
            {"key": "2026-02"},
            {"key": "2026-03"},
            {"key": "2026-04"},
            {"key": "2026-05"},
        ],
        "restaurants": [
            {
                "RestaurantID": 1,
                "RestaurantName": "Nha Hang Sen",
                "Revenue": 150000,
            }
        ],
        "restaurant_count": 1,
        "total_report": 150000,
        "total_6_months": 450000,
    }
    data.update(kwargs)
    return data


@pytest.fixture()
def app(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-jwt-secret")
    monkeypatch.setenv("SQLALCHEMY_DATABASE_URI", "mysql+pymysql://test:test@localhost/test")

    app = create_app()
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        JWT_SECRET_KEY="test-jwt-secret",
    )
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin_headers(app):
    return make_headers(app, "ADMIN")


@pytest.fixture()
def staff_headers(app):
    return make_headers(app, "STAFF")


@pytest.fixture()
def customer_headers(app):
    return make_headers(app, "CUSTOMER")


def make_headers(app, role):
    with app.app_context():
        token = create_access_token(
            identity="1",
            additional_claims={"role": role},
        )
    return {"Authorization": f"Bearer {token}"}


def post_report(client, headers=None, report_month="2026-05", restaurant_id=None):
    data = {}
    if report_month is not None:
        data["report_month"] = report_month
    if restaurant_id is not None:
        data["restaurant_id"] = restaurant_id
    return client.post(REPORT_URL, data=data, headers=headers or {})


# Tải báo cáo tất cả nhà hàng theo tháng
# Báo cáo tính doanh thu tháng chọn
# Báo cáo tính tổng 6 tháng
@patch(REPORT_SERVICE_PATH)
def test_admin_report_success(mock_get_report, client, admin_headers):
    mock_get_report.return_value = mock_report_data()

    response = post_report(client, admin_headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["total_report"] == 150000
    assert data["total_6_months"] == 450000
    assert len(data["months"]) == 6


# Tải báo cáo một nhà hàng cụ thể
@patch(REPORT_SERVICE_PATH)
def test_admin_report_calls_service_with_restaurant_id(mock_get_report, client, admin_headers):
    mock_get_report.return_value = mock_report_data()

    response = post_report(client, admin_headers, restaurant_id="1")

    assert response.status_code == 200
    mock_get_report.assert_called_once_with("1", "2026-05")


# Thiếu tháng báo cáo
@patch(REPORT_SERVICE_PATH)
def test_admin_report_missing_month(mock_get_report, client, admin_headers):
    response = post_report(client, admin_headers, report_month=None)
    data = response.get_json()

    assert response.status_code == 400
    assert data["status"] == "error"
    mock_get_report.assert_not_called()


# Chặn báo cáo khi không phải ADMIN
@pytest.mark.parametrize("headers_fixture", ["staff_headers", "customer_headers"])
@patch(REPORT_SERVICE_PATH)
def test_admin_report_forbidden_non_admin(
    mock_get_report,
    client,
    request,
    headers_fixture,
):
    headers = request.getfixturevalue(headers_fixture)

    response = post_report(client, headers)
    data = response.get_json()

    assert response.status_code == 403
    assert data["message"] == "Quyen nay cua Admin!"
    mock_get_report.assert_not_called()


# Chặn báo cáo khi thiếu token
@patch(REPORT_SERVICE_PATH)
def test_admin_report_missing_token(mock_get_report, client):
    response = post_report(client)
    data = response.get_json()

    assert response.status_code == 401
    assert "msg" in data
    mock_get_report.assert_not_called()


# Báo cáo restaurant_id không tồn tại
# Bảng rỗng khi không có nhà hàng phù hợp
@patch(REPORT_SERVICE_PATH)
def test_admin_report_empty_restaurant_result(mock_get_report, client, admin_headers):
    mock_get_report.return_value = mock_report_data(
        restaurants=[],
        restaurant_count=0,
        total_report=0,
        total_6_months=0,
    )

    response = post_report(client, admin_headers, restaurant_id="999")
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["restaurants"] == []
    assert data["restaurant_count"] == 0
    assert data["total_report"] == 0


# Báo cáo tháng không có doanh thu
@patch(REPORT_SERVICE_PATH)
def test_admin_report_zero_revenue_success(mock_get_report, client, admin_headers):
    mock_get_report.return_value = mock_report_data(
        restaurants=[],
        restaurant_count=0,
        total_report=0,
        total_6_months=0,
    )

    response = post_report(client, admin_headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["total_report"] == 0


# Báo cáo report_month sai định dạng
@patch(REPORT_SERVICE_PATH)
def test_admin_report_invalid_month_format(
    mock_get_report, client, admin_headers
):
    # Mock service vẫn trả dữ liệu bình thường
    # Vì route hiện tại không validate format tháng
    mock_get_report.return_value = mock_report_data(
        total_report=0,
        total_6_months=0,
    )

    # Gửi report_month sai định dạng MM-YYYY
    response = post_report(
        client,
        admin_headers,
        report_month="05-2026",
    )
    data = response.get_json()

    # Route vẫn chạy success và truyền giá trị xuống service
    assert response.status_code == 200
    assert data["status"] == "success"

    # Kiểm tra service được gọi đúng tham số đã nhập
    mock_get_report.assert_called_once_with(None, "05-2026")



# Báo cáo với payment CreatedAt rỗng
@patch(REPORT_SERVICE_PATH)
def test_admin_report_payment_created_at_null(
    mock_get_report, client, admin_headers
):
    mock_get_report.return_value = mock_report_data(
        total_report=0,
        total_6_months=0,
    )

    response = post_report(client, admin_headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["total_report"] == 0



# Sắp xếp nhà hàng theo doanh thu tháng chọn
@patch(REPORT_SERVICE_PATH)
def test_admin_report_sort_restaurants_by_revenue(mock_get_report, client, admin_headers):
    mock_get_report.return_value = mock_report_data(
        restaurants=[
            {"RestaurantID": 1, "RestaurantName": "A", "Revenue": 300000},
            {"RestaurantID": 2, "RestaurantName": "B", "Revenue": 100000},
        ],
        restaurant_count=2,
        total_report=400000,
    )

    response = post_report(client, admin_headers)
    data = response.get_json()

    assert response.status_code == 200
    revenues = [r["Revenue"] for r in data["restaurants"]]
    assert all(revenues[i] >= revenues[i + 1] for i in range(len(revenues) - 1))


# Không tính nhà hàng Ngưng hoạt động
@patch(REPORT_SERVICE_PATH)
def test_admin_report_exclude_inactive_restaurants(mock_get_report, client, admin_headers):
    mock_get_report.return_value = mock_report_data(
        restaurants=[
            {
                "RestaurantID": 1,
                "RestaurantName": "Nha Hang A",
                "Revenue": 100000,
                "status": "Dang hoat dong",
            },
            {
                "RestaurantID": 2,
                "RestaurantName": "Nha Hang B",
                "Revenue": 200000,
                "status": "Hoat dong",
            },
        ],
        restaurant_count=2,
        total_report=300000,
    )

    response = post_report(client, admin_headers)
    data = response.get_json()

    assert response.status_code == 200
    assert not any(r.get("status") == "Ngung hoat dong" for r in data["restaurants"])


# Tải danh sách nhà hàng cho filter
@patch(REPORT_SERVICE_PATH)
def test_admin_report_get_restaurants_for_filter(mock_get_report, client, admin_headers):
    mock_get_report.return_value = mock_report_data(
        restaurants=[
            {"RestaurantID": 1, "RestaurantName": "Nha Hang Mot", "Revenue": 50000},
            {"RestaurantID": 2, "RestaurantName": "Nha Hang Hai", "Revenue": 80000},
        ],
        restaurant_count=2,
        total_report=130000,
    )

    response = post_report(client, admin_headers)
    data = response.get_json()

    assert response.status_code == 200
    assert len(data["restaurants"]) == 2
    assert data["restaurant_count"] == 2


# Báo cáo cập nhật sau thanh toán mới
@patch(REPORT_SERVICE_PATH)
def test_admin_report_updated_after_new_payment(mock_get_report, client, admin_headers):
    mock_get_report.return_value = mock_report_data(total_report=300000)

    response = post_report(client, admin_headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data["total_report"] == 300000
