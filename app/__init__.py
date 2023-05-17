from flask import Flask, jsonify
from flask_cors import CORS

from app.auth0.auth_error import AuthError
from app.database import mongodb_client
from misc.config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_class)
    mongodb_client.init_app(app)

    # Initialize Flask extensions here

    # Register blueprints here
    for api in Config.apis:
        app.register_blueprint(api["bp"], url_prefix=api["prefix"])

    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response

    return app
