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

