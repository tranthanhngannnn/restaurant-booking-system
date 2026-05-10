
from backend.core.extensions import ma
from backend.models.booking import Reservation

class BookingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Reservation
        load_instance = True

    TableID = ma.auto_field()
    RestaurantName = ma.Function(
        lambda obj: obj.restaurant.RestaurantName if obj.restaurant else ""
    )
    TableNumber = ma.Function(
        lambda obj: obj.table.TableNumber if obj.table else ""
    )
    customer_name = ma.Function(
        lambda obj: obj.CustomerName if obj.CustomerName else (obj.user.Username if obj.user else "")
    )
booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)