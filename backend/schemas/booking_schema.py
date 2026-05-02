from core.extensions import ma
<<<<<<< HEAD
from models.booking import Reservation

class BookingSchema(ma.Schema):
    id = ma.Integer()
    TableID = ma.Integer()
    CustomerName = ma.String()
    phone = ma.String()
    GuestCount = ma.Integer()
    BookingDate = ma.Method("get_date")
    BookingTime = ma.Method("get_time")
    RestaurantID = ma.Integer()
    Deposit = ma.Float()
    Status = ma.String()

    RestaurantName = ma.Method("get_restaurant_name")
    TableNumber = ma.Method("get_table_number")

    def get_date(self, obj):
        return str(obj.BookingDate) if obj.BookingDate else None

    def get_time(self, obj):
        return str(obj.BookingTime) if obj.BookingTime else None

    def get_restaurant_name(self, obj):
        return obj.restaurant.RestaurantName if getattr(obj, "restaurant", None) else ""

    def get_table_number(self, obj):
        return obj.table.TableNumber if getattr(obj, "table", None) else ""


booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)
=======
from models.booking import Reservation   # sửa đúng path

class BookingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Reservation
        load_instance = True

    RestaurantName = ma.Function(lambda obj: obj.restaurant.RestaurantName if obj.restaurant else "")
    TableNumber = ma.Function(lambda obj: obj.table.TableNumber if obj.table else "")
bookings_schema = BookingSchema(many=True)
>>>>>>> origin/main
