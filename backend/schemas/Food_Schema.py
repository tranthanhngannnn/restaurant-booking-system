from core.extensions import ma
from models.menu import Food

class FoodSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Food
        load_instance = True

foods_schema = FoodSchema(many=True)
