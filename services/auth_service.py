"""
Smart College Assistant — Authentication Service
Handles login, registration, password management, and session security.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from database.models import User, Role, get_session
from utils.helpers import hash_password, verify_password
from utils.validators import validate_email, validate_password_strength
from utils.error_handlers import UnauthorizedError, ValidationError, NotFoundError
from utils.logger import setup_logger, get_audit_logger

logger = setup_logger(__name__)
audit = get_audit_logger()


class AuthService:
    """Service for user authentication and account management."""

    @staticmethod
    def login(username: str, password: str) -> dict:
        """
        Authenticate a user.

        Args:
            username: Username or email.
            password: Plain-text password.

        Returns:
            dict with user info on success.

        Raises:
            UnauthorizedError if credentials are invalid.
        """
        session = get_session()
        try:
            user = (
                session.query(User)
                .filter(
                    (User.username == username) | (User.email == username)
                )
                .first()
            )

            if not user:
                audit.warning("Failed login attempt for username: %s", username)
                raise UnauthorizedError("Invalid username or password.")

            if not user.is_active:
                raise UnauthorizedError("Account is deactivated. Contact administration.")

            if not verify_password(password, user.password_hash):
                audit.warning("Wrong password for user: %s", username)
                raise UnauthorizedError("Invalid username or password.")

            # Update last login
            user.last_login = datetime.utcnow()
            session.commit()

            # Build response
            profile = AuthService._get_profile(session, user)
            audit.info("Successful login: %s (%s)", username, user.role.name)

            return {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.name,
                "profile": profile,
            }

        finally:
            session.close()

    @staticmethod
    def _get_profile(session, user: User) -> dict:
        """Get role-specific profile data."""
        if user.role.name == "student" and user.student:
            s = user.student
            dept = s.department
            return {
                "name": s.name,
                "roll_number": s.roll_number,
                "department": dept.name if dept else "N/A",
                "department_code": dept.code if dept else "N/A",
                "semester": s.semester,
                "cgpa": s.cgpa,
                "attendance": s.attendance_percentage,
                "placement_eligible": s.placement_eligible,
                "photo_url": s.photo_url or "/static/images/default_avatar.png",
                "batch": s.batch,
            }
        elif user.role.name == "faculty" and user.faculty:
            f = user.faculty
            dept = f.department
            return {
                "name": f.name,
                "employee_id": f.employee_id,
                "department": dept.name if dept else "N/A",
                "designation": f.designation,
                "specialization": f.specialization,
                "photo_url": f.photo_url or "/static/images/default_avatar.png",
            }
        elif user.role.name == "admin":
            return {
                "name": "Administrator",
                "role_description": "Full System Access",
            }
        return {}

    @staticmethod
    def change_password(
        user_id: int,
        current_password: str,
        new_password: str,
    ) -> None:
        """
        Change user password.

        Args:
            user_id: ID of the user.
            current_password: Current plain-text password.
            new_password: New plain-text password.

        Raises:
            UnauthorizedError if current password is wrong.
            ValidationError if new password is weak.
        """
        valid, msg = validate_password_strength(new_password)
        if not valid:
            raise ValidationError(msg)

        session = get_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                raise NotFoundError("User not found.")
            if not verify_password(current_password, user.password_hash):
                raise UnauthorizedError("Current password is incorrect.")

            user.password_hash = hash_password(new_password)
            session.commit()
            audit.info("Password changed for user ID: %d", user_id)
        finally:
            session.close()

    @staticmethod
    def get_user_by_id(user_id: int) -> dict | None:
        """Fetch user info by ID."""
        session = get_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return None
            profile = AuthService._get_profile(session, user)
            return {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.name,
                "profile": profile,
            }
        finally:
            session.close()


# ── Auth decorators ───────────────────────────────────────────

def login_required(f):
    """Decorator: require an authenticated session."""
    from functools import wraps
    from flask import session, jsonify

    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"success": False, "error": "Authentication required."}), 401
        return f(*args, **kwargs)

    return decorated


def role_required(*roles: str):
    """Decorator: require one of the given roles."""
    from functools import wraps
    from flask import session, jsonify

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                return jsonify({"success": False, "error": "Authentication required."}), 401
            if session.get("role") not in roles:
                return jsonify({"success": False, "error": "Insufficient permissions."}), 403
            return f(*args, **kwargs)
        return decorated

    return decorator
