from flask import Flask
from routes.routes import bp as routes_bp


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_pyfile('config.py')

    app.register_blueprint(routes_bp)

    return app
