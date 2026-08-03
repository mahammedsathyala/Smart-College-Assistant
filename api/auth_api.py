"""
Smart College Assistant — Authentication API Blueprint
Handles login, logout, and session management.
"""

from flask import Blueprint, request, jsonify, session
from services.auth_service import AuthService
from utils.validators import sanitize_string, validate_required_fields
from utils.logger import setup_logger, get_audit_logger
from utils.error_handlers import UnauthorizedError, ValidationError

logger = setup_logger(__name__)
audit = get_audit_logger()

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    POST /api/auth/login
    Body: {"username": str, "password": str}
    Returns: user data and sets session cookie.
    """
    data = request.get_json(silent=True) or {}
    valid, msg = validate_required_fields(data, ["username", "password"])
    if not valid:
        return jsonify({"success": False, "error": msg}), 400

    username = sanitize_string(data["username"], 100)
    password = data["password"]  # Don't sanitize password (special chars allowed)

    try:
        user_data = AuthService.login(username, password)

        # Set server-side session
        session.permanent = True
        session["user_id"] = user_data["user_id"]
        session["username"] = user_data["username"]
        session["role"] = user_data["role"]

        ip = request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr)
        audit.info("LOGIN: user=%s role=%s ip=%s", username, user_data["role"], ip)

        return jsonify({
            "success": True,
            "message": f"Welcome, {user_data['profile'].get('name', username)}!",
            "user": {
                "username": user_data["username"],
                "email": user_data["email"],
                "role": user_data["role"],
                "profile": user_data["profile"],
            },
        })

    except UnauthorizedError as e:
        return jsonify({"success": False, "error": e.message}), 401
    except Exception as e:
        logger.error("Login error: %s", e)
        return jsonify({"success": False, "error": "Login failed. Please try again."}), 500


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """POST /api/auth/logout — Clear session."""
    username = session.get("username", "unknown")
    session.clear()
    audit.info("LOGOUT: user=%s", username)
    return jsonify({"success": True, "message": "Logged out successfully."})


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """GET /api/auth/me — Get current session user info."""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not authenticated."}), 401

    user_data = AuthService.get_user_by_id(session["user_id"])
    if not user_data:
        session.clear()
        return jsonify({"success": False, "error": "User not found."}), 404

    return jsonify({"success": True, "user": user_data})


@auth_bp.route("/change-password", methods=["POST"])
def change_password():
    """POST /api/auth/change-password"""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Authentication required."}), 401

    data = request.get_json(silent=True) or {}
    valid, msg = validate_required_fields(data, ["current_password", "new_password"])
    if not valid:
        return jsonify({"success": False, "error": msg}), 400

    try:
        AuthService.change_password(
            session["user_id"],
            data["current_password"],
            data["new_password"],
        )
        return jsonify({"success": True, "message": "Password changed successfully."})
    except (UnauthorizedError, ValidationError) as e:
        return jsonify({"success": False, "error": e.message}), e.status_code
    except Exception as e:
        logger.error("Change password error: %s", e)
        return jsonify({"success": False, "error": "Failed to change password."}), 500
