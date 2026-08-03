"""
Smart College Assistant — Student API Blueprint
"""

from flask import Blueprint, jsonify, session, request
from services.student_service import StudentService
from services.auth_service import login_required
from utils.logger import setup_logger

logger = setup_logger(__name__)
student_bp = Blueprint("student", __name__, url_prefix="/api/student")


@student_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    """GET /api/student/profile"""
    s = StudentService.get_student_by_user(session["user_id"])
    if not s:
        return jsonify({"success": False, "error": "Student profile not found."}), 404
    return jsonify({"success": True, "student": s})


@student_bp.route("/attendance", methods=["GET"])
@login_required
def get_attendance():
    """GET /api/student/attendance"""
    s = StudentService.get_student_by_user(session["user_id"])
    if not s:
        return jsonify({"success": False, "error": "Student not found."}), 404
    data = StudentService.get_attendance_summary(s["id"])
    return jsonify({"success": True, **data})


@student_bp.route("/marks", methods=["GET"])
@login_required
def get_marks():
    """GET /api/student/marks"""
    s = StudentService.get_student_by_user(session["user_id"])
    if not s:
        return jsonify({"success": False, "error": "Student not found."}), 404
    data = StudentService.get_marks_summary(s["id"])
    return jsonify({"success": True, **data})


@student_bp.route("/timetable", methods=["GET"])
@login_required
def get_timetable():
    """GET /api/student/timetable"""
    s = StudentService.get_student_by_user(session["user_id"])
    if not s:
        return jsonify({"success": False, "error": "Student not found."}), 404
    data = StudentService.get_timetable(s["id"])
    return jsonify({"success": True, **data})


@student_bp.route("/dashboard", methods=["GET"])
@login_required
def get_dashboard():
    """GET /api/student/dashboard — Full dashboard data"""
    from database.models import Notification, PlacementDrive, FAQ, get_session as db
    from datetime import date

    s = StudentService.get_student_by_user(session["user_id"])
    if not s:
        return jsonify({"success": False, "error": "Student not found."}), 404

    stats = StudentService.get_dashboard_stats(s["id"])

    dbs = db()
    try:
        notifications = (
            dbs.query(Notification)
            .filter_by(is_active=True)
            .order_by(Notification.created_at.desc())
            .limit(5)
            .all()
        )
        notif_list = [
            {"id": n.id, "title": n.title, "category": n.category,
             "priority": n.priority, "created_at": str(n.created_at)}
            for n in notifications
        ]

        drives = (
            dbs.query(PlacementDrive)
            .filter(PlacementDrive.drive_date >= date.today())
            .order_by(PlacementDrive.drive_date)
            .limit(3)
            .all()
        )
        drive_list = [
            {"company": d.company_name, "role": d.role,
             "date": str(d.drive_date), "package": d.package_lpa,
             "min_cgpa": d.eligibility_cgpa}
            for d in drives
        ]

    finally:
        dbs.close()

    return jsonify({
        "success": True,
        "student": s,
        "stats": stats,
        "notifications": notif_list,
        "upcoming_drives": drive_list,
    })
