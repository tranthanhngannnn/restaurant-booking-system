from core import create_app
from flask import Flask
from flask_cors import CORS


app = create_app()
CORS(app, resources={r"/api/*": {"origins": "*"}}, methods=["GET","POST","PUT","DELETE","OPTIONS"])



if __name__ == "__main__":
    app.run(debug=True)
