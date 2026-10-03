"""Fábrica de la aplicación Flask."""

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(MAX_CONTENT_LENGTH=20 * 1024 * 1024)
    app.json.ensure_ascii = False
    if test_config:
        app.config.update(test_config)

    from .routes.api import api
    from .routes.pages import pages

    app.register_blueprint(pages)
    app.register_blueprint(api)

    @app.errorhandler(HTTPException)
    def http_error(error):
        if request.path.startswith("/api/"):
            messages = {
                400: "JSON inválido.",
                413: "La petición supera 20 MB.",
                415: "Envía los datos con Content-Type: application/json.",
            }
            return jsonify(ok=False, error=messages.get(error.code, error.description)), error.code
        return error

    @app.after_request
    def response_headers(response):
        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    return app
