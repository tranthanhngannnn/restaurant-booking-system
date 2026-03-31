from flask import Flask
from backend.core.config import Config
from backend.core.extensions import db, ma
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)
    app.secret_key = "super_secret_key"

    db.init_app(app)
    ma.init_app(app)

    CORS(app, supports_credentials=True)

    from backend.app.api.v1.customer.routes import customer_bp
    app.register_blueprint(customer_bp, url_prefix="/api")

    return app