"""
Smart College Assistant — Test Suite
Tests for API, database, chatbot, RAG, and utilities.
"""

import os
import sys
import json
import pytest
from pathlib import Path

# ── Set test environment ──────────────────────────────────────
os.environ["FLASK_ENV"] = "development"
os.environ["FLASK_SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["DATABASE_URL"] = "sqlite:///test_college.db"

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ── Fixtures ──────────────────────────────────────────────────

@pytest.fixture(scope="session")
def app():
    """Create test Flask app."""
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    return app


@pytest.fixture(scope="session")
def client(app):
    """Test client."""
    return app.test_client()


@pytest.fixture(scope="session")
def auth_headers(client):
    """Login and return session."""
    res = client.post(
        "/api/auth/login",
        json={"username": "cs001", "password": "Student@123"},
        content_type="application/json",
    )
    return res


# ── Test: Health Check ────────────────────────────────────────

def test_health_check(client):
    """API should return healthy status."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "healthy"
    assert "version" in data


# ── Test: Authentication ──────────────────────────────────────

def test_login_success(client):
    """Valid credentials should succeed."""
    res = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "Admin@123"},
        content_type="application/json",
    )
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["success"] is True
    assert data["user"]["role"] == "admin"


def test_login_wrong_password(client):
    """Wrong password should return 401."""
    res = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "wrongpassword"},
        content_type="application/json",
    )
    assert res.status_code == 401
    data = json.loads(res.data)
    assert data["success"] is False


def test_login_missing_fields(client):
    """Missing fields should return 400."""
    res = client.post(
        "/api/auth/login",
        json={"username": "admin"},
        content_type="application/json",
    )
    assert res.status_code == 400


def test_logout(client):
    """Logout should clear session."""
    res = client.post("/api/auth/logout")
    assert res.status_code == 200


# ── Test: Public APIs ─────────────────────────────────────────

def test_admission_info(client):
    """Admission info should return programs and fees."""
    res = client.get("/api/admission/info")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["success"] is True
    assert "programs" in data["info"]
    assert len(data["info"]["programs"]) > 0


def test_exam_schedule(client):
    """Exam schedule should return list of exams."""
    res = client.get("/api/exam/schedule")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["success"] is True
    assert isinstance(data["schedule"], list)
    assert len(data["schedule"]) > 0


def test_placement_drives(client):
    """Placement drives should return upcoming drives."""
    res = client.get("/api/placement/drives")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["success"] is True
    assert "drives" in data


def test_placement_statistics(client):
    """Placement stats should include key metrics."""
    res = client.get("/api/placement/statistics")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["success"] is True
    stats = data["stats"]
    assert "placed" in stats
    assert "placement_percentage" in stats


def test_notifications(client):
    """Notifications endpoint should return list."""
    res = client.get("/api/notifications/")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["success"] is True
    assert isinstance(data["notifications"], list)


def test_policies(client):
    """Policies should return list."""
    res = client.get("/api/policy/")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["success"] is True
    assert len(data["policies"]) > 0


def test_faqs(client):
    """FAQs should return list."""
    res = client.get("/api/faqs/")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["success"] is True
    assert len(data["faqs"]) > 0


def test_timetable(client):
    """Timetable should return schedule."""
    res = client.get("/api/timetable/?dept=CS&semester=5")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["success"] is True


# ── Test: Calculators ─────────────────────────────────────────

def test_cgpa_calculator(client):
    """CGPA should be calculated correctly."""
    subjects = [
        {"name": "AI", "grade": "O", "credits": 4},
        {"name": "ML", "grade": "A+", "credits": 4},
        {"name": "DBMS", "grade": "A", "credits": 3},
    ]
    res = client.post(
        "/api/exam/cgpa-calculator",
        json={"subjects": subjects},
        content_type="application/json",
    )
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["success"] is True
    # O(10)*4 + A+(9)*4 + A(8)*3 = 40+36+24 = 100 / (4+4+3=11) = 9.09
    assert abs(data["cgpa"] - 9.09) < 0.1


def test_attendance_calculator(client):
    """Attendance calculator should return correct percentage."""
    res = client.post(
        "/api/exam/attendance-calculator",
        json={"present": 18, "total": 24, "needed_percentage": 75},
        content_type="application/json",
    )
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["success"] is True
    assert data["percentage"] == 75.0


def test_placement_eligibility(client):
    """Eligibility checker should work correctly."""
    # Eligible
    res = client.post(
        "/api/placement/eligibility-check",
        json={"cgpa": 8.5, "backlogs": 0, "required_cgpa": 7.0},
        content_type="application/json",
    )
    data = json.loads(res.data)
    assert data["eligible"] is True

    # Not eligible
    res = client.post(
        "/api/placement/eligibility-check",
        json={"cgpa": 5.5, "backlogs": 2, "required_cgpa": 7.0},
        content_type="application/json",
    )
    data = json.loads(res.data)
    assert data["eligible"] is False


# ── Test: Chat API ────────────────────────────────────────────

def test_chat_message(client):
    """Chat endpoint should return a response."""
    res = client.post(
        "/api/chat/message",
        json={"message": "Hello, what is the attendance requirement?", "session_id": "test-session"},
        content_type="application/json",
    )
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["success"] is True
    assert "response" in data
    assert len(data["response"]) > 10


def test_chat_empty_message(client):
    """Empty chat message should return 400."""
    res = client.post(
        "/api/chat/message",
        json={"message": ""},
        content_type="application/json",
    )
    assert res.status_code == 400


def test_chat_suggestions(client):
    """Chat suggestions should return list."""
    res = client.get("/api/chat/suggestions")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["success"] is True
    assert len(data["suggestions"]) > 0


# ── Test: Utilities ───────────────────────────────────────────

def test_calculate_cgpa_util():
    """CGPA calculation utility test."""
    from tools.calculator_tool import calculate_cgpa
    subjects = [
        {"name": "Math", "grade": "O", "credits": 4},
        {"name": "Physics", "grade": "A+", "credits": 3},
    ]
    result = calculate_cgpa(subjects)
    # (10*4 + 9*3) / (4+3) = 67/7 = 9.57
    assert abs(result["cgpa"] - 9.57) < 0.01
    assert result["total_credits"] == 7


def test_calculate_attendance_util():
    """Attendance calculation utility test."""
    from tools.calculator_tool import calculate_attendance
    result = calculate_attendance(18, 24, 75.0)
    assert result["percentage"] == 75.0
    assert result["can_miss"] == 0

    result2 = calculate_attendance(10, 24, 75.0)
    assert result2["percentage"] < 75.0
    assert result2["classes_needed"] > 0


def test_placement_eligibility_util():
    """Placement eligibility utility test."""
    from tools.calculator_tool import check_placement_eligibility
    result = check_placement_eligibility(8.0, 0, 7.0)
    assert result["eligible"] is True

    result2 = check_placement_eligibility(5.0, 1, 7.0)
    assert result2["eligible"] is False
    assert len(result2["reasons"]) > 0


# ── Test: Database ────────────────────────────────────────────

def test_database_models():
    """Database tables should be created."""
    from database.models import get_engine, Base, Role, User, Student
    engine = get_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    assert session.query(Role).count() == 0  # Empty fresh DB
    session.close()


def test_validators():
    """Input validators should work correctly."""
    from utils.validators import validate_email, validate_password_strength, sanitize_string

    assert validate_email("test@example.com") is True
    assert validate_email("notanemail") is False

    ok, _ = validate_password_strength("Secure@123")
    assert ok is True

    ok, _ = validate_password_strength("weak")
    assert ok is False

    cleaned = sanitize_string("<script>alert('xss')</script>Hello")
    assert "<script>" not in cleaned


# ── Test: Chunker ─────────────────────────────────────────────

def test_text_chunker():
    """Text chunker should split correctly."""
    from rag.chunker import TextChunker
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    text = "A" * 300
    chunks = chunker.split_text(text)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
