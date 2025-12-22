import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask
from flask_cors import CORS

from backend.controller.sensor_controller import sensor_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(sensor_bp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)