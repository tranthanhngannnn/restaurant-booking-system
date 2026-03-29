"""""
from backend.core.extensions import ma

class FoodSchema(ma.Schema):
    class Meta:
        fields = ("FoodID", "FoodName", "Price")

foods_schema = FoodSchema(many=True)

"""""
from backend.core.extensions import ma
from backend.models.menu import Food   # sửa đúng path model của bạn

class FoodSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Food
        load_instance = True

foods_schema = FoodSchema(many=True)