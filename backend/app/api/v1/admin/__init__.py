from flask import Blueprint

# 1. Khai báo định danh cho phân khu Admin
# 'admin_api' là tên của Blueprint, dùng để tạo đường dẫn (url)
admin_bp = Blueprint('admin_api', __name__)

# 2. "Kết nối" file routes.py vào Blueprint này
from . import routes
