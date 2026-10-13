"""
Flask application factory for ZDN GST Verification Microservice.
"""

import os
from flask import Flask, send_from_directory, jsonify
from .config import Config
from .routes.api import api_bp
from .routes.health import health_bp


def create_app() -> Flask:
    static_folder = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "static")
    )

    app = Flask(__name__, static_folder=static_folder)
    app.config.from_object(Config)

    # Register Blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(health_bp)

    # Simple CORS handler
    @app.after_request
    def add_cors_headers(response):
        origins = Config.CORS_ORIGINS
        response.headers["Access-Control-Allow-Origin"] = origins
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-API-Key, Accept, Origin"
        )
        return response

    # Serve Interactive Dashboard UI
    @app.route("/", methods=["GET"])
    def index():
        return send_from_directory(static_folder, "index.html")

    @app.route("/<path:path>", methods=["GET"])
    def static_proxy(path):
        return send_from_directory(static_folder, path)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "NOT_FOUND", "message": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"success": False, "error": "INTERNAL_ERROR", "message": "Internal server error"}), 500

    return app
