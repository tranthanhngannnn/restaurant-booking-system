from backend.core.extensions import ma
from backend.models.restaurant import Restaurant   # sửa đúng path model

class RestaurantSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Restaurant
        load_instance = True

restaurant_schema = RestaurantSchema()
restaurants_schema = RestaurantSchema(many=True)