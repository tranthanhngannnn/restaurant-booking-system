from core import create_app
from flask import Flask
from flask_cors import CORS
from core.extensions import db

app = create_app()
CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

