"""
Smart College Assistant — Main Flask Application
Enterprise-grade AI platform for college information and student support.

Author: Smart College AI Team
Version: 2.0.0
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, render_template, session, jsonify, redirect, url_for
from flask_cors import CORS
from flask_session import Session

# ── Path setup ───────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config.settings import ActiveConfig
from utils.logger import setup_logger
from utils.error_handlers import register_error_handlers

logger = setup_logger("smart_college.app")


def create_app() -> Flask:
    """
    Application factory function.

    Creates and configures the Flask application with all
    blueprints, extensions, and error handlers registered.

    Returns:
        Configured Flask application instance.
    """
    # ── Ensure required directories ──────────────────────────
    ActiveConfig.ensure_directories()

    # ── Create Flask app ─────────────────────────────────────
    app = Flask(
        __name__,
        template_folder="ui/templates",
        static_folder="ui/static",
    )

    # ── App config ───────────────────────────────────────────
    app.config["SECRET_KEY"] = ActiveConfig.SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = ActiveConfig.MAX_CONTENT_LENGTH
    app.config["SESSION_TYPE"] = ActiveConfig.SESSION_TYPE
    app.config["SESSION_FILE_DIR"] = ActiveConfig.SESSION_FILE_DIR
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
        minutes=ActiveConfig.SESSION_LIFETIME_MINUTES
    )
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # ── Extensions ───────────────────────────────────────────
    CORS(app, supports_credentials=True)
    Session(app)

    # ── Initialize Database ──────────────────────────────────
    _init_database(app)

    # ── Register Blueprints ──────────────────────────────────
    _register_blueprints(app)

    # ── Register Error Handlers ──────────────────────────────
    register_error_handlers(app)

    # ── Register Template Context ────────────────────────────
    _register_context(app)

    # ── Register Page Routes ─────────────────────────────────
    _register_page_routes(app)

    logger.info("✅ Smart College Assistant initialized.")
    return app


def _init_database(app: Flask) -> None:
    """Initialize database tables and seed data."""
    from database.models import init_db, get_engine

    engine = get_engine()
    init_db(engine)

    # Seed data only if DB is empty
    from database.models import Role, get_session
    session = get_session(engine)
    try:
        if session.query(Role).count() == 0:
            logger.info("Empty database detected — running seed data...")
            from database.seed_data import run_seed
            run_seed()
        else:
            logger.info("Database already seeded.")
    finally:
        session.close()


def _register_blueprints(app: Flask) -> None:
    """Register all API blueprints."""
    from api.auth_api import auth_bp
    from api.chat_api import chat_bp
    from api.student_api import student_bp
    from api.college_apis import (
        admission_bp, exam_bp, placement_bp, policy_bp,
        notification_bp, faq_bp, upload_bp, search_bp,
        dashboard_bp, timetable_bp,
    )

    blueprints = [
        auth_bp, chat_bp, student_bp,
        admission_bp, exam_bp, placement_bp, policy_bp,
        notification_bp, faq_bp, upload_bp, search_bp,
        dashboard_bp, timetable_bp,
    ]

    for bp in blueprints:
        app.register_blueprint(bp)
        logger.debug("Registered blueprint: %s", bp.name)


def _register_context(app: Flask) -> None:
    """Register Jinja2 template context processors."""

    @app.context_processor
    def inject_globals():
        return {
            "current_year": datetime.now().year,
            "app_name": "Smart College Assistant",
            "app_version": "2.0.0",
            "current_user": {
                "username": session.get("username"),
                "role": session.get("role"),
                "user_id": session.get("user_id"),
            } if "user_id" in session else None,
        }


def _register_page_routes(app: Flask) -> None:
    """Register HTML page routes."""

    # ── Public pages ─────────────────────────────────────────

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/login")
    def login_page():
        if "user_id" in session:
            return redirect(url_for("dashboard"))
        return render_template("login.html")

    @app.route("/about")
    def about():
        return render_template("index.html")

    # ── Auth-protected pages ─────────────────────────────────

    @app.route("/dashboard")
    def dashboard():
        if "user_id" not in session:
            return redirect(url_for("login_page"))
        role = session.get("role", "student")
        if role == "admin":
            return render_template("admin_dashboard.html")
        elif role == "faculty":
            return render_template("faculty_dashboard.html")
        return render_template("dashboard.html")

    @app.route("/chatbot")
    def chatbot():
        return render_template("chatbot.html")

    @app.route("/admission")
    def admission():
        return render_template("admission.html")

    @app.route("/exam")
    def exam():
        return render_template("exam.html")

    @app.route("/timetable")
    def timetable():
        return render_template("timetable.html")

    @app.route("/placement")
    def placement():
        return render_template("placement.html")

    @app.route("/policies")
    def policies():
        return render_template("policies.html")

    @app.route("/notifications")
    def notifications():
        return render_template("notifications.html")

    @app.route("/upload")
    def upload():
        return render_template("upload.html")

    @app.route("/smart-tools")
    def smart_tools():
        return render_template("smart_tools.html")

    # ── Health check ─────────────────────────────────────────

    @app.route("/api/health")
    def health_check():
        from config.settings import ActiveConfig
        return jsonify({
            "status": "healthy",
            "app": "Smart College Assistant",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "ai_configured": ActiveConfig.is_watsonx_configured(),
        })


# ── Entry point ───────────────────────────────────────────────
if __name__ == "__main__":
    app = create_app()
    logger.info(
        "Starting Smart College Assistant on http://%s:%d",
        ActiveConfig.HOST,
        ActiveConfig.PORT,
    )
    app.run(
        host=ActiveConfig.HOST,
        port=ActiveConfig.PORT,
        debug=ActiveConfig.DEBUG,
        use_reloader=False,
    )
