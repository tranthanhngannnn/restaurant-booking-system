from backend.models.cuisine import Cuisine
from backend.models.restaurant import Restaurant
from backend.core.extensions import db
from backend.models.user import User
from backend.models.booking import Reservation
from backend.models.payment import Payment
from sqlalchemy import func


class AdminUserService:
    @staticmethod
    def get_all_users():
        users = User.query.all()
        return [{"id": u.UserID, "username": u.Username, "role": u.Role, "email": u.Email, "phone": u.Phone} for u in users]

    @staticmethod
    def update_user(user_id, data):
        user = User.query.get(user_id)
        if not user:
            return None

        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return False

        db.session.delete(user)
        db.session.commit()
        return True


class CuisineService:
    @staticmethod
    def create(data):
        cuisine_name = data.get('CuisineName')
        if not cuisine_name:
            return {"message": "Ten khong duoc de trong"}, 400

        if Cuisine.query.filter_by(CuisineName=cuisine_name).first():
            return {"message": "Danh muc da ton tai"}, 400

        new_cuisine = Cuisine(CuisineName=cuisine_name, Status="Hoat dong")
        db.session.add(new_cuisine)
        db.session.commit()
        return {"message": "Them thanh cong!"}, 201

    @staticmethod
    def get_all():
        all_cuisines = Cuisine.query.all()
        result = [{"id": c.CuisineID, "name": c.CuisineName, "status": c.Status} for c in all_cuisines]
        return result, 200

    @staticmethod
    def update(id, data):
        cuisine_obj = Cuisine.query.get(id)
        if not cuisine_obj:
            return {"message": "Khong tim thay"}, 404

        for key, value in data.items():
            if hasattr(Cuisine, key):
                setattr(cuisine_obj, key, value)

        db.session.commit()
        return {"message": "Cap nhat thanh cong!"}, 200

    @staticmethod
    def delete(id):
        cuisine_name = Cuisine.query.get(id)
        if not cuisine_name:
            return {"message": "Khong tim thay"}, 404

        db.session.delete(cuisine_name)
        db.session.commit()
        return {"message": "Da xoa xong!"}, 200


class AdminRestaurantService:
    @staticmethod
    def get_all_restaurants(status=None):
        query = Restaurant.query
        if status:
            query = query.filter(Restaurant.status == status)
        return [r.to_dict() for r in query.order_by(Restaurant.RestaurantID.asc()).all()]

    @staticmethod
    def update_restaurant(restaurant_id, data, image=None):
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            return None

        for key, value in data.items():
            if hasattr(restaurant, key):
                setattr(restaurant, key, value)

        if image and image.filename != '':
            restaurant.image_url = image.filename

        db.session.commit()
        return restaurant

    @staticmethod
    def delete_restaurant(restaurant_id):
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            return False

        restaurant.status = 'Ngưng hoạt động'
        db.session.commit()
        return {"message": "Da an nha hang thanh cong, du lieu van duoc luu tru!", "code": 200}

    @staticmethod
    def approve(restaurant_id):
        try:
            restaurant = Restaurant.query.get(restaurant_id)
            if not restaurant:
                return {"message": "Khong tim thay nha hang nay!"}, 404

            restaurant.status = "Đang hoạt động"
            db.session.commit()
            return {"message": f"Da duyet nha hang {restaurant.RestaurantName} thanh cong!"}, 200
        except Exception as e:
            db.session.rollback()
            return {"message": f"Loi he thong: {str(e)}"}, 500

    @staticmethod
    def reject(restaurant_id):
        try:
            restaurant = Restaurant.query.get(restaurant_id)
            if not restaurant:
                return {"message": "Khong tim thay nha hang nay!"}, 404

            restaurant.status = "Từ chối"
            db.session.commit()
            return {"message": f"Da tu choi nha hang {restaurant.RestaurantName}!"}, 200
        except Exception as e:
            db.session.rollback()
            return {"message": f"Loi he thong: {str(e)}"}, 500


class ReportService:
    @staticmethod
    def _parse_month(report_month):
        #Parse chuỗi 'YYYY-MM' thành year và month
        year, month = map(int, report_month.split('-'))
        return year, month

    @staticmethod
    def _shift_month(year, month, offset):
        #Tính tháng mới sau khi dịch chuyển offset tháng
        month_index = (year * 12 + month - 1) + offset
        shifted_year = month_index // 12
        shifted_month = month_index % 12 + 1
        return shifted_year, shifted_month

    @staticmethod
    def _month_key(year, month):
        #Tạo key dạng 'YYYY-MM'
        return f"{year}-{month:02d}"

    @staticmethod
    def _month_label(year, month):
        #Tạo label hiển thị dạng 'Thang MM/YYYY'
        return f"Thang {month:02d}/{year}"

    @staticmethod
    def _build_months(report_month, months_back=6):
        #Xây dựng danh sách 6 tháng gần nhất từ tháng được chọn
        year, month = ReportService._parse_month(report_month)
        months = []
        start_offset = -(months_back - 1)
        for offset in range(start_offset, 1):
            item_year, item_month = ReportService._shift_month(year, month, offset)
            months.append({
                "key": ReportService._month_key(item_year, item_month),
                "label": ReportService._month_label(item_year, item_month)
            })
        return months

    @staticmethod
    def get_report(restaurant_id, report_month):
        # Xây dựng danh sách 6 tháng gần nhất
        months = ReportService._build_months(report_month, months_back=6)
        month_keys = [item["key"] for item in months]
        month_labels = {item["key"]: item["label"] for item in months}
        selected_month = month_keys[-1]  # Tháng được chọn (tháng cuối)

        # Query nhà hàng đang hoạt động
        restaurant_query = Restaurant.query.filter(Restaurant.status != 'Ngưng hoạt động')
        if restaurant_id:
            restaurant_query = restaurant_query.filter(Restaurant.RestaurantID == int(restaurant_id))

        base_restaurants = restaurant_query.order_by(Restaurant.RestaurantName.asc()).all()

        # Khởi tạo map nhà hàng với doanh thu = 0
        restaurant_map = {
            restaurant.RestaurantID: {
                "restaurant_id": restaurant.RestaurantID,
                "restaurant_name": restaurant.RestaurantName,
                "monthly_revenue": {key: 0.0 for key in month_keys},  # Doanh thu từng tháng
                "selected_month_revenue": 0.0,  # Doanh thu tháng được chọn
                "total_6_months": 0.0  # Tổng doanh thu 6 tháng
            }
            for restaurant in base_restaurants
        }

        # Query doanh thu từ database - Lấy doanh thu THỰC TẾ từ bảng Payment
        # Join: Restaurant -> Reservation -> Payment để lấy số tiền khách đã thanh toán
        query = (
            db.session.query(
                Restaurant.RestaurantID.label("restaurant_id"),
                Restaurant.RestaurantName.label("restaurant_name"),
                func.year(Payment.CreatedAt).label("year"),
                func.month(Payment.CreatedAt).label("month"),
                func.coalesce(func.sum(Payment.Amount), 0).label("revenue")  # Tổng tiền khách đã trả
            )
            .join(Reservation, Reservation.RestaurantID == Restaurant.RestaurantID)  # Liên kết nhà hàng với đặt bàn
            .join(Payment, Payment.ReservationID == Reservation.ReservationID)  # Liên kết đặt bàn với thanh toán
            .filter(Payment.CreatedAt.isnot(None))  # Chỉ lấy giao dịch đã thanh toán
            .filter(Payment.Status == 'Paid')  # Chỉ lấy payment đã thành công (không tính pending/failed)
            .filter(func.date_format(Payment.CreatedAt, "%Y-%m").in_(month_keys))  # Lọc theo 6 tháng
            .filter(Restaurant.status != 'Ngưng hoạt động')  # Chỉ lấy nhà hàng đang hoạt động
        )

        if restaurant_id:
            query = query.filter(Restaurant.RestaurantID == int(restaurant_id))

        # Group by để tính tổng doanh thu từng tháng
        rows = (
            query.group_by(
                Restaurant.RestaurantID,
                Restaurant.RestaurantName,
                func.year(Payment.CreatedAt),
                func.month(Payment.CreatedAt)
            )
            .order_by(Restaurant.RestaurantName.asc())
            .all()
        )

        # Cập nhật doanh thu vào restaurant_map
        for row in rows:
            res_id = int(row.restaurant_id)
            month_key = ReportService._month_key(int(row.year), int(row.month))
            revenue = float(row.revenue or 0)
            if res_id in restaurant_map:
                restaurant_map[res_id]["monthly_revenue"][month_key] = revenue

        # Tính toán tổng doanh thu cho từng nhà hàng
        for restaurant in restaurant_map.values():
            restaurant["selected_month_revenue"] = float(restaurant["monthly_revenue"].get(selected_month, 0))
            restaurant["total_6_months"] = float(sum(restaurant["monthly_revenue"].values()))

            # Chuyển monthly_revenue thành list để trả về
            restaurant["monthly_revenue"] = [
                {
                    "key": key,
                    "label": month_labels[key],
                    "revenue": float(restaurant["monthly_revenue"][key])
                }
                for key in month_keys
            ]

        # Sắp xếp nhà hàng theo doanh thu thực tế từ cao xuống thấp:
        # 1. Ưu tiên tổng doanh thu 6 tháng (giảm dần) - nhà hàng nào có doanh thu cao nhất sẽ lên đầu
        # 2. Nếu tổng 6 tháng bằng nhau, xem doanh thu tháng được chọn (giảm dần)
        restaurants = sorted(
            restaurant_map.values(),
            key=lambda item: (float(item["total_6_months"]), float(item["selected_month_revenue"])),
            reverse=True  # Sắp xếp giảm dần để nhà hàng có doanh thu cao nhất lên đầu
        )

        return {
            "month": selected_month,
            "months": months,
            "restaurants": restaurants,
            "total_report": float(sum(item["selected_month_revenue"] for item in restaurants)),
            "total_6_months": float(sum(item["total_6_months"] for item in restaurants)),
            "restaurant_count": len(restaurants)
        }
