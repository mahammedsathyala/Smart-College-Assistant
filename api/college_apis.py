"""
Smart College Assistant — Remaining API Blueprints
Admission, Exam, Placement, Policy, Notification, Upload, Search, Dashboard, Timetable APIs.
"""

from datetime import date
from flask import Blueprint, request, jsonify, session
from database.models import (
    Admission, Department, Notification, Policy, FAQ,
    PlacementDrive, PlacementRecord, Student, Mark, Course,
    Timetable, Document, get_session as db_session,
)
from services.auth_service import login_required, role_required
from utils.validators import sanitize_string, validate_required_fields
from utils.logger import setup_logger

logger = setup_logger(__name__)


# ── Admission API ─────────────────────────────────────────────
admission_bp = Blueprint("admission", __name__, url_prefix="/api/admission")


@admission_bp.route("/info", methods=["GET"])
def get_admission_info():
    """GET /api/admission/info — Public admission information."""
    return jsonify({
        "success": True,
        "info": {
            "programs": [
                {"name": "B.E. Computer Science & Engineering", "code": "CS", "seats": 60},
                {"name": "B.E. Electronics & Communication Engineering", "code": "ECE", "seats": 60},
                {"name": "B.E. Mechanical Engineering", "code": "MECH", "seats": 60},
                {"name": "B.E. Information Technology", "code": "IT", "seats": 60},
                {"name": "B.E. Civil Engineering", "code": "CIVIL", "seats": 60},
            ],
            "fee_structure": {
                "tuition_fee": 85000,
                "development_fee": 15000,
                "exam_fee": 2500,
                "total": 104000,
            },
            "important_dates": {
                "application_start": "2026-06-01",
                "application_end": "2026-07-15",
                "entrance_exam": "2026-07-20",
                "counseling": "2026-07-28",
                "classes_begin": "2026-08-01",
            },
            "required_documents": [
                "10th Standard Mark Sheet",
                "12th Standard Mark Sheet",
                "Transfer Certificate",
                "Migration Certificate",
                "Conduct Certificate",
                "6 Passport Photographs",
                "Aadhar Card",
                "Caste Certificate (if applicable)",
                "Income Certificate (for scholarship)",
            ],
            "scholarships": [
                {"name": "Merit Scholarship", "amount": "50% fee waiver", "eligibility": "Top 10% students"},
                {"name": "SC/ST Scholarship", "amount": "Full fee waiver", "eligibility": "SC/ST category"},
                {"name": "Sports Scholarship", "amount": "25% fee waiver", "eligibility": "National/State level"},
            ],
        },
    })


@admission_bp.route("/apply", methods=["POST"])
def apply_admission():
    """POST /api/admission/apply — Submit admission application."""
    data = request.get_json(silent=True) or {}
    required = ["applicant_name", "email", "phone", "department_code", "entrance_score", "category"]
    valid, msg = validate_required_fields(data, required)
    if not valid:
        return jsonify({"success": False, "error": msg}), 400

    dbs = db_session()
    try:
        dept = dbs.query(Department).filter_by(code=data["department_code"].upper()).first()
        if not dept:
            return jsonify({"success": False, "error": "Invalid department code."}), 400

        app = Admission(
            applicant_name=sanitize_string(data["applicant_name"]),
            email=sanitize_string(data["email"]),
            phone=sanitize_string(data["phone"]),
            department_id=dept.id,
            entrance_score=float(data["entrance_score"]),
            category=sanitize_string(data["category"]),
            status="pending",
        )
        dbs.add(app)
        dbs.commit()
        return jsonify({"success": True, "message": "Application submitted!", "application_id": app.id})
    except Exception as e:
        dbs.rollback()
        logger.error("Admission apply error: %s", e)
        return jsonify({"success": False, "error": "Failed to submit application."}), 500
    finally:
        dbs.close()


@admission_bp.route("/status/<int:app_id>", methods=["GET"])
def get_admission_status(app_id: int):
    """GET /api/admission/status/<id>"""
    dbs = db_session()
    try:
        app = dbs.query(Admission).filter_by(id=app_id).first()
        if not app:
            return jsonify({"success": False, "error": "Application not found."}), 404
        return jsonify({
            "success": True,
            "application": {
                "id": app.id,
                "applicant_name": app.applicant_name,
                "status": app.status,
                "applied_date": str(app.applied_date),
            },
        })
    finally:
        dbs.close()


# ── Exam API ──────────────────────────────────────────────────
exam_bp = Blueprint("exam", __name__, url_prefix="/api/exam")


@exam_bp.route("/schedule", methods=["GET"])
def get_exam_schedule():
    """GET /api/exam/schedule"""
    schedule = [
        {"subject": "Artificial Intelligence", "code": "CS501", "date": "2026-10-15", "time": "09:00 AM", "room": "Hall A"},
        {"subject": "Machine Learning", "code": "CS502", "date": "2026-10-17", "time": "09:00 AM", "room": "Hall A"},
        {"subject": "Database Management Systems", "code": "CS503", "date": "2026-10-19", "time": "09:00 AM", "room": "Hall B"},
        {"subject": "Computer Networks", "code": "CS504", "date": "2026-10-21", "time": "09:00 AM", "room": "Hall A"},
        {"subject": "Software Engineering", "code": "CS505", "date": "2026-10-23", "time": "09:00 AM", "room": "Hall C"},
    ]
    return jsonify({"success": True, "schedule": schedule})


@exam_bp.route("/cgpa-calculator", methods=["POST"])
def calculate_cgpa_api():
    """POST /api/exam/cgpa-calculator"""
    data = request.get_json(silent=True) or {}
    subjects = data.get("subjects", [])
    if not subjects:
        return jsonify({"success": False, "error": "No subjects provided."}), 400

    from tools.calculator_tool import calculate_cgpa
    result = calculate_cgpa(subjects)
    return jsonify({"success": True, **result})


@exam_bp.route("/attendance-calculator", methods=["POST"])
def calculate_attendance_api():
    """POST /api/exam/attendance-calculator"""
    data = request.get_json(silent=True) or {}
    try:
        present = int(data.get("present", 0))
        total = int(data.get("total", 0))
        needed = float(data.get("needed_percentage", 75.0))
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid numeric input."}), 400

    from tools.calculator_tool import calculate_attendance
    result = calculate_attendance(present, total, needed)
    return jsonify({"success": True, **result})


@exam_bp.route("/faqs", methods=["GET"])
def get_exam_faqs():
    """GET /api/exam/faqs"""
    dbs = db_session()
    try:
        faqs = dbs.query(FAQ).filter_by(category="exam", is_active=True).all()
        return jsonify({
            "success": True,
            "faqs": [{"id": f.id, "question": f.question, "answer": f.answer} for f in faqs],
        })
    finally:
        dbs.close()


# ── Placement API ─────────────────────────────────────────────
placement_bp = Blueprint("placement", __name__, url_prefix="/api/placement")


@placement_bp.route("/drives", methods=["GET"])
def get_drives():
    """GET /api/placement/drives"""
    dbs = db_session()
    try:
        drives = (
            dbs.query(PlacementDrive)
            .filter(PlacementDrive.drive_date >= date.today())
            .order_by(PlacementDrive.drive_date)
            .all()
        )
        return jsonify({
            "success": True,
            "drives": [
                {
                    "id": d.id, "company": d.company_name, "role": d.role,
                    "package": d.package_lpa, "date": str(d.drive_date),
                    "min_cgpa": d.eligibility_cgpa, "departments": d.departments,
                    "registration_deadline": str(d.registration_deadline),
                    "description": d.description, "status": d.status,
                }
                for d in drives
            ],
        })
    finally:
        dbs.close()


@placement_bp.route("/statistics", methods=["GET"])
def get_placement_stats():
    """GET /api/placement/statistics"""
    dbs = db_session()
    try:
        total = dbs.query(PlacementRecord).count()
        placed = dbs.query(PlacementRecord).filter_by(status="placed").count()
        records = dbs.query(PlacementRecord).filter_by(status="placed").all()
        packages = [r.package_lpa for r in records if r.package_lpa]
        avg_pkg = round(sum(packages) / len(packages), 2) if packages else 0
        max_pkg = max(packages) if packages else 0

        return jsonify({
            "success": True,
            "stats": {
                "total_eligible": total,
                "placed": placed,
                "placement_percentage": round(placed / total * 100, 1) if total else 0,
                "average_package_lpa": avg_pkg,
                "highest_package_lpa": max_pkg,
                "top_recruiters": ["Amazon", "TCS", "Infosys", "Wipro", "Google"],
            },
        })
    finally:
        dbs.close()


@placement_bp.route("/eligibility-check", methods=["POST"])
def check_eligibility():
    """POST /api/placement/eligibility-check"""
    data = request.get_json(silent=True) or {}
    try:
        cgpa = float(data.get("cgpa", 0))
        backlogs = int(data.get("backlogs", 0))
        req_cgpa = float(data.get("required_cgpa", 6.0))
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid input."}), 400

    from tools.calculator_tool import check_placement_eligibility
    result = check_placement_eligibility(cgpa, backlogs, req_cgpa)
    return jsonify({"success": True, **result})


# ── Policy API ────────────────────────────────────────────────
policy_bp = Blueprint("policy", __name__, url_prefix="/api/policy")


@policy_bp.route("/", methods=["GET"])
def get_policies():
    """GET /api/policy/ — List all policies."""
    dbs = db_session()
    try:
        category = request.args.get("category")
        query = dbs.query(Policy)
        if category:
            query = query.filter_by(category=category)
        policies = query.order_by(Policy.category).all()
        return jsonify({
            "success": True,
            "policies": [
                {"id": p.id, "title": p.title, "category": p.category,
                 "content": p.content, "last_updated": str(p.last_updated)}
                for p in policies
            ],
        })
    finally:
        dbs.close()


@policy_bp.route("/<int:policy_id>", methods=["GET"])
def get_policy(policy_id: int):
    """GET /api/policy/<id>"""
    dbs = db_session()
    try:
        p = dbs.query(Policy).filter_by(id=policy_id).first()
        if not p:
            return jsonify({"success": False, "error": "Policy not found."}), 404
        return jsonify({"success": True, "policy": {
            "id": p.id, "title": p.title, "category": p.category,
            "content": p.content, "last_updated": str(p.last_updated),
        }})
    finally:
        dbs.close()


# ── Notifications API ─────────────────────────────────────────
notification_bp = Blueprint("notification", __name__, url_prefix="/api/notifications")


@notification_bp.route("/", methods=["GET"])
def get_notifications():
    """GET /api/notifications/ — All active notifications."""
    dbs = db_session()
    try:
        category = request.args.get("category")
        query = dbs.query(Notification).filter_by(is_active=True)
        if category and category != "all":
            query = query.filter_by(category=category)
        notifs = query.order_by(Notification.created_at.desc()).limit(50).all()
        return jsonify({
            "success": True,
            "notifications": [
                {"id": n.id, "title": n.title, "content": n.content,
                 "category": n.category, "priority": n.priority,
                 "created_at": str(n.created_at)}
                for n in notifs
            ],
        })
    finally:
        dbs.close()


# ── FAQs API ──────────────────────────────────────────────────
faq_bp = Blueprint("faq", __name__, url_prefix="/api/faqs")


@faq_bp.route("/", methods=["GET"])
def get_faqs():
    """GET /api/faqs/ — All FAQs, optionally filtered by category."""
    dbs = db_session()
    try:
        category = request.args.get("category")
        query = dbs.query(FAQ).filter_by(is_active=True)
        if category:
            query = query.filter_by(category=category)
        faqs = query.all()
        return jsonify({
            "success": True,
            "faqs": [
                {"id": f.id, "question": f.question, "answer": f.answer,
                 "category": f.category, "helpful_count": f.helpful_count}
                for f in faqs
            ],
        })
    finally:
        dbs.close()


# ── Upload API ────────────────────────────────────────────────
upload_bp = Blueprint("upload", __name__, url_prefix="/api/upload")


@upload_bp.route("/document", methods=["POST"])
def upload_document():
    """POST /api/upload/document — Upload and index a document for RAG."""
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file provided."}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"success": False, "error": "No file selected."}), 400

    from utils.validators import validate_file_extension
    from config.settings import ActiveConfig
    from pathlib import Path
    import os

    if not validate_file_extension(file.filename):
        return jsonify({
            "success": False,
            "error": "Unsupported file type. Allowed: PDF, DOCX, TXT, CSV",
        }), 400

    # Save file
    upload_dir = Path(ActiveConfig.UPLOAD_FOLDER)
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = Path(file.filename).name
    file_path = str(upload_dir / safe_name)
    file.save(file_path)

    # Index in RAG pipeline
    try:
        from rag.pipeline import get_rag_pipeline
        pipeline = get_rag_pipeline()
        category = request.form.get("category", "general")
        chunk_count = pipeline.ingest_file(
            file_path,
            metadata={"category": category, "filename": safe_name},
        )

        # Save to DB
        dbs = db_session()
        doc = Document(
            filename=safe_name,
            file_path=file_path,
            category=category,
            chunk_count=chunk_count,
            indexed=True,
            uploaded_by=session.get("user_id"),
        )
        dbs.add(doc)
        dbs.commit()
        doc_id = doc.id
        dbs.close()

        return jsonify({
            "success": True,
            "message": f"Document '{safe_name}' indexed successfully!",
            "document_id": doc_id,
            "chunks_indexed": chunk_count,
        })
    except Exception as e:
        logger.error("Document indexing error: %s", e)
        return jsonify({"success": False, "error": "Failed to index document."}), 500


# ── Search API ────────────────────────────────────────────────
search_bp = Blueprint("search", __name__, url_prefix="/api/search")


@search_bp.route("/", methods=["POST"])
def semantic_search():
    """POST /api/search/ — Semantic search across uploaded documents."""
    data = request.get_json(silent=True) or {}
    query = sanitize_string(data.get("query", ""), 500)
    if not query:
        return jsonify({"success": False, "error": "Query is required."}), 400

    try:
        from rag.pipeline import get_rag_pipeline
        pipeline = get_rag_pipeline()
        result = pipeline.query(query)
        return jsonify({"success": True, **result})
    except Exception as e:
        logger.error("Search error: %s", e)
        return jsonify({"success": False, "error": "Search failed."}), 500


# ── Dashboard API ─────────────────────────────────────────────
dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/admin", methods=["GET"])
@role_required("admin")
def get_admin_dashboard():
    """GET /api/dashboard/admin — Admin analytics dashboard."""
    dbs = db_session()
    try:
        from database.models import User, Student, Faculty, PlacementRecord
        total_students = dbs.query(Student).count()
        total_faculty = dbs.query(Faculty).count()
        total_users = dbs.query(User).count()
        placed = dbs.query(PlacementRecord).filter_by(status="placed").count()
        total_notifs = dbs.query(Notification).filter_by(is_active=True).count()
        pending_admissions = dbs.query(Admission).filter_by(status="pending").count()

        return jsonify({
            "success": True,
            "stats": {
                "total_students": total_students,
                "total_faculty": total_faculty,
                "total_users": total_users,
                "placed_students": placed,
                "active_notifications": total_notifs,
                "pending_admissions": pending_admissions,
            },
        })
    finally:
        dbs.close()


# ── Timetable API ─────────────────────────────────────────────
timetable_bp = Blueprint("timetable", __name__, url_prefix="/api/timetable")


@timetable_bp.route("/", methods=["GET"])
def get_timetable():
    """GET /api/timetable/?dept=CS&semester=5"""
    dept_code = request.args.get("dept", "CS").upper()
    semester = int(request.args.get("semester", 5))

    dbs = db_session()
    try:
        dept = dbs.query(Department).filter_by(code=dept_code).first()
        if not dept:
            return jsonify({"success": False, "error": "Department not found."}), 404

        slots = (
            dbs.query(Timetable)
            .filter_by(department_id=dept.id, semester=semester)
            .order_by(Timetable.day, Timetable.start_time)
            .all()
        )

        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        by_day: dict[str, list] = {d: [] for d in days_order}

        for slot in slots:
            by_day[slot.day].append({
                "time": f"{slot.start_time} - {slot.end_time}",
                "course": slot.course.name if slot.course else "N/A",
                "code": slot.course.code if slot.course else "N/A",
                "faculty": slot.faculty.name if slot.faculty else "N/A",
                "room": slot.room,
                "type": slot.type,
            })

        return jsonify({
            "success": True,
            "department": dept_code,
            "semester": semester,
            "timetable": {day: s for day, s in by_day.items() if s},
        })
    finally:
        dbs.close()
