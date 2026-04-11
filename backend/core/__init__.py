from flask import Flask
from core.extensions import db, login_manager, jwt
from app.api.v1.auth.routes import auth_bp
from app.api.v1.admin.routes import admin_bp
from app.api.v1.restaurant.routes import restaurant_bp
from flask_cors import CORS

from models.table import Table
from models.booking import Booking
from models.menu import Menu

def create_app():
    app = Flask(__name__)

    CORS(app)
    app.config['SECRET_KEY'] = '123456'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/restaurant_booking'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = '6a2c53c83b86197f722e555454742656a926b1ae6de96f27'

    # init extensions
    db.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)



    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(restaurant_bp, url_prefix='/api/v1/restaurant/')

    with app.app_context():
        db.create_all()
    return app