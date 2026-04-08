import os
from core.extensions import db, login_manager, jwt, ma
from flask import Flask, template_rendered
from flask import render_template
from core.config import Config
from flask_cors import CORS
from models.user import User
from models.review import Review


def create_app():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "../../frontend/templates"),
        static_folder=os.path.join(BASE_DIR, "../../frontend/static")
    )

    # Cấu hình Database & Security
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = '123456'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/restaurant_booking'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = '6a2c53c83b86197f722e555454742656a926b1ae6de96f27'
    app.secret_key = "super_secret_key"

    # khởi tạo extensions
    db.init_app(app)
    ma.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)
    CORS(app, supports_credentials=True)

    from app.api.v1.auth.routes import auth_bp
    from app.api.v1.admin.routes import admin_bp
    from app.api.v1.restaurant import restaurant_bp
    from app.api.v1.customer.routes import customer_bp

    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(restaurant_bp, url_prefix='/api/v1/restaurant')
    app.register_blueprint(customer_bp, url_prefix="/api/v1/customer")

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Route chính
    @app.route("/")
    def root():
        return render_template("customer/home.html")

    return app





