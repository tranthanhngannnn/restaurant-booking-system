
from flask import Flask, template_rendered
from flask import render_template
from backend.core.config import Config
from backend.core.extensions import db, ma
from flask_cors import CORS
from backend.models.user import User
from backend.models.review import Review
"""""
def create_app():
    app = Flask(__name__,
                template_folder="..//..//frontend/templates",
                static_url_path="..//..//frontend/static")
    app.config.from_object(Config)

    db.init_app(app)
    ma.init_app(app)
    CORS(app)

    from backend.app.api.v1.customer.routes import customer_bp
    app.register_blueprint(customer_bp, url_prefix="/api/v1/customer")

    return app
"""""
import os

def create_app():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "../../frontend/templates"),
        static_folder=os.path.join(BASE_DIR, "../../frontend/static")
    )

    app.config.from_object(Config)
    app.secret_key = "super_secret_key"
    db.init_app(app)
    ma.init_app(app)
    CORS(app, supports_credentials=True)

    from backend.app.api.v1.customer.routes import customer_bp
    app.register_blueprint(customer_bp, url_prefix="/api/v1/customer")

    @app.route("/")
    def root():
        return render_template("customer/home.html")

    return app