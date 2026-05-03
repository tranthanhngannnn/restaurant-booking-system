import os
from core.extensions import db, login_manager, jwt, ma
from flask import Flask, render_template
from core.config import Config
from flask_cors import CORS

from models.user import User
from models.review import Review
from models.cuisine import Cuisine
from models.restaurant import Restaurant
from models.tables import Tables
from models.booking import Reservation
from models.menu import Menu
from models.payment import Payment

from app.api.v1.auth.routes import auth_bp
from app.api.v1.admin.routes import admin_bp
from app.api.v1.restaurant import restaurant_bp
from app.api.v1.customer.routes import customer_bp


def create_app(config_class=Config):  # 👈 hỗ trợ TestConfig luôn
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "../../frontend/templates"),
        static_folder=os.path.join(BASE_DIR, "../../frontend/static")
    )

    # Config
    app.config.from_object(config_class)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'SQLALCHEMY_DATABASE_URI',
        app.config.get('SQLALCHEMY_DATABASE_URI')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret')

    # Init extensions
    db.init_app(app)
    ma.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)

    CORS(app, supports_credentials=True, origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ])

    # Register blueprint
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(restaurant_bp, url_prefix='/api/v1/restaurant')
    app.register_blueprint(customer_bp, url_prefix="/api/v1/customer")

    # 👇 giữ lại nếu bạn dùng API này
    app.add_url_rule(
        '/api/v1/restaurants/registerRestaurant',
        view_func=app.view_functions['restaurant.staff_register_restaurant'],
        methods=['POST']
    )

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route("/")
    def root():
        return render_template("customer/home.html")

    return app