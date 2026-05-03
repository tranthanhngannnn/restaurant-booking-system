
from backend.core.extensions import ma
from backend.models.booking import Reservation

class BookingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Reservation
        load_instance = True

    RestaurantName = ma.Function(
        lambda obj: obj.restaurant.RestaurantName if obj.restaurant else ""
    )
    TableNumber = ma.Function(
        lambda obj: obj.table.TableNumber if obj.table else ""
    )
booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)