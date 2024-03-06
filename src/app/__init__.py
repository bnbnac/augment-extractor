from flask import Flask
from src.app.routes.routes import bp


def create_app(test_config=None):
    app = Flask(__name__)

    app.register_blueprint(bp)

    return app
