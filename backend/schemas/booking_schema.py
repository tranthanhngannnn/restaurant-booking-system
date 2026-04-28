from core.extensions import ma
from models.booking import Reservation   # sửa đúng path

class BookingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Reservation
        load_instance = True

    RestaurantName = ma.Function(lambda obj: obj.restaurant.RestaurantName if obj.restaurant else "")
    TableNumber = ma.Function(lambda obj: obj.table.TableNumber if obj.table else "")
bookings_schema = BookingSchema(many=True)
