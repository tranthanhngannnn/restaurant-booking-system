import pytest
from backend.core import create_app
from backend.core.extensions import db
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "this-is-a-very-long-secret-key-for-testing-123456"
    return app


@pytest.fixture
def client(app):
    return app.test_client()


# Helper tạo JWT
@pytest.fixture
def auth_header(app):
    def _get(user_id=1):
        with app.app_context():
            token = create_access_token(identity=user_id)
        return {"Authorization": f"Bearer {token}"}
    return _get



import uuid

from backend.models.restaurant import Restaurant
from backend.core.extensions import db


def create_test_restaurant():

    unique = str(uuid.uuid4())[:8]

    restaurant = Restaurant(
        RestaurantName=f"Test Restaurant {unique}",
        Address="HCM",
        Phone=f"090{unique[:7]}",
        Email=f"test{unique}@gmail.com",
        Opentime="08:00",
        Closetime="22:00",
        description="Test restaurant"
    )

    db.session.add(restaurant)
    db.session.commit()

    return restaurant

