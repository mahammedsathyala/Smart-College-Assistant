"""
Smart College Assistant — Error Handlers (updated)
Registers Flask error handlers and defines custom exceptions.
"""

from __future__ import annotations
from flask import jsonify, render_template, request
from utils.logger import setup_logger

logger = setup_logger(__name__)


# ── Custom Exceptions ─────────────────────────────────────────

class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, 403)


class NotFoundError(AppError):
    def __init__(self, message: str = "Not Found"):
        super().__init__(message, 404)


class ValidationError(AppError):
    def __init__(self, message: str = "Validation Error"):
        super().__init__(message, 400)


class AIServiceError(AppError):
    def __init__(self, message: str = "AI service unavailable"):
        super().__init__(message, 503)


# ── Register Handlers ─────────────────────────────────────────

def register_error_handlers(app) -> None:
    """Register Flask error handlers."""

    def is_api_request() -> bool:
        return request.path.startswith("/api/")

    @app.errorhandler(AppError)
    def handle_app_error(e: AppError):
        if is_api_request():
            return jsonify({"success": False, "error": e.message}), e.status_code
        return render_template("index.html"), e.status_code

    @app.errorhandler(400)
    def bad_request(e):
        if is_api_request():
            return jsonify({"success": False, "error": "Bad request."}), 400
        return render_template("index.html"), 400

    @app.errorhandler(401)
    def unauthorized(e):
        if is_api_request():
            return jsonify({"success": False, "error": "Authentication required."}), 401
        from flask import redirect, url_for
        return redirect(url_for("login_page"))

    @app.errorhandler(403)
    def forbidden(e):
        if is_api_request():
            return jsonify({"success": False, "error": "Access denied."}), 403
        return render_template("index.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        if is_api_request():
            return jsonify({"success": False, "error": "Resource not found."}), 404
        return render_template("index.html"), 404

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"success": False, "error": "File too large. Max 16MB."}), 413

    @app.errorhandler(500)
    def server_error(e):
        logger.error("Internal server error: %s", e)
        if is_api_request():
            return jsonify({"success": False, "error": "Internal server error."}), 500
        return render_template("index.html"), 500

    @app.errorhandler(503)
    def service_unavailable(e):
        if is_api_request():
            return jsonify({"success": False, "error": "Service temporarily unavailable."}), 503
        return render_template("index.html"), 503
