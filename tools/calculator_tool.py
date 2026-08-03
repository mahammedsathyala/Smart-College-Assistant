"""
Smart College Assistant — Custom Tools
Reusable calculation and utility tools for AI agents.
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Any
from utils.logger import setup_logger

logger = setup_logger(__name__)


# ── CGPA Calculator ──────────────────────────────────────────

def calculate_cgpa(subjects: list[dict]) -> dict:
    """
    Calculate CGPA from subject grades.

    Args:
        subjects: List of {"name": str, "grade": str, "credits": int}

    Returns:
        {"cgpa": float, "total_credits": int, "details": list}
    """
    grade_map = {
        "O": 10.0, "A+": 9.0, "A": 8.0,
        "B+": 7.0, "B": 6.0, "C": 5.0, "F": 0.0,
    }
    total_credits = 0
    total_points = 0.0
    details = []

    for sub in subjects:
        grade = sub.get("grade", "").upper()
        credits = int(sub.get("credits", 0))
        gp = grade_map.get(grade, 0.0)
        pts = gp * credits
        total_credits += credits
        total_points += pts
        details.append({
            "subject": sub.get("name", "Unknown"),
            "grade": grade,
            "grade_point": gp,
            "credits": credits,
            "points": pts,
        })

    cgpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
    logger.info("CGPA calculated: %.2f from %d subjects.", cgpa, len(subjects))
    return {"cgpa": cgpa, "total_credits": total_credits, "details": details}


# ── Attendance Calculator ─────────────────────────────────────

def calculate_attendance(
    present: int,
    total: int,
    needed_percentage: float = 75.0,
) -> dict:
    """
    Calculate attendance and determine if requirement is met.

    Args:
        present: Number of classes attended.
        total: Total number of classes conducted.
        needed_percentage: Minimum required percentage.

    Returns:
        dict with percentage, status, classes_needed, can_miss
    """
    if total == 0:
        return {"error": "Total classes cannot be zero."}

    percentage = round((present / total) * 100, 2)
    status = "✅ Eligible" if percentage >= needed_percentage else "❌ Detained Risk"

    # Classes needed to reach required percentage
    classes_needed = 0
    if percentage < needed_percentage:
        # (present + x) / (total + x) >= needed_percentage/100
        # Solve: x >= (needed_percentage * total - 100 * present) / (100 - needed_percentage)
        numerator = (needed_percentage / 100) * total - present
        denominator = 1 - (needed_percentage / 100)
        classes_needed = max(0, int(numerator / denominator) + 1)

    # Classes can miss while staying above threshold
    can_miss = 0
    if percentage >= needed_percentage:
        # (present) / (total + x) >= needed_percentage/100
        # x <= present * 100/needed_percentage - total
        can_miss = max(0, int(present * 100 / needed_percentage - total))

    return {
        "present": present,
        "total": total,
        "percentage": percentage,
        "required": needed_percentage,
        "status": status,
        "classes_needed": classes_needed,
        "can_miss": can_miss,
    }


# ── Date Tool ─────────────────────────────────────────────────

def get_current_date_info() -> dict:
    """Return current date, academic year, and semester info."""
    today = date.today()
    year = today.year
    month = today.month

    # Academic year runs July–June
    if month >= 7:
        academic_year = f"{year}-{year + 1}"
        semester_season = "Odd Semester"
    else:
        academic_year = f"{year - 1}-{year}"
        semester_season = "Even Semester"

    return {
        "date": today.isoformat(),
        "day": today.strftime("%A"),
        "formatted": today.strftime("%d %B %Y"),
        "academic_year": academic_year,
        "semester_season": semester_season,
    }


# ── Placement Eligibility Checker ────────────────────────────

def check_placement_eligibility(
    cgpa: float,
    backlogs: int,
    required_cgpa: float = 6.0,
) -> dict:
    """
    Check if a student is eligible for placement.

    Args:
        cgpa: Student's current CGPA.
        backlogs: Number of active backlogs.
        required_cgpa: Company's minimum CGPA requirement.

    Returns:
        dict with eligible, reason, suggestions
    """
    reasons = []
    suggestions = []

    if cgpa < required_cgpa:
        reasons.append(f"CGPA {cgpa} is below required {required_cgpa}")
        deficit = round(required_cgpa - cgpa, 2)
        suggestions.append(f"Improve CGPA by {deficit} points through better exam performance.")

    if backlogs > 0:
        reasons.append(f"You have {backlogs} active backlog(s)")
        suggestions.append("Clear all backlogs in the upcoming supplementary exams.")

    eligible = len(reasons) == 0
    return {
        "eligible": eligible,
        "cgpa": cgpa,
        "required_cgpa": required_cgpa,
        "backlogs": backlogs,
        "reasons": reasons,
        "suggestions": suggestions,
        "message": (
            "✅ You are eligible for placement drives!"
            if eligible
            else f"❌ Not eligible: {'; '.join(reasons)}"
        ),
    }


# ── Resume Analyzer (Rule-Based) ─────────────────────────────

def analyze_resume(resume_text: str) -> dict:
    """
    Rule-based resume analyzer.

    Args:
        resume_text: Plain text of the resume.

    Returns:
        dict with score, strengths, improvements
    """
    text_lower = resume_text.lower()
    score = 0
    strengths = []
    improvements = []

    # Check sections
    sections = {
        "education": ["education", "academic"],
        "experience": ["experience", "internship", "work"],
        "skills": ["skills", "technical skills"],
        "projects": ["project", "projects"],
        "contact": ["email", "phone", "linkedin"],
        "achievements": ["achievement", "award", "certification"],
    }

    for section, keywords in sections.items():
        if any(kw in text_lower for kw in keywords):
            score += 10
            strengths.append(f"{section.title()} section present")
        else:
            improvements.append(f"Add a {section.title()} section")

    # Check length
    word_count = len(resume_text.split())
    if 300 <= word_count <= 700:
        score += 10
        strengths.append("Good resume length (1 page)")
    elif word_count < 300:
        improvements.append("Resume is too short; add more details")
    else:
        improvements.append("Consider condensing to 1-2 pages")

    # Check for action verbs
    action_verbs = ["developed", "built", "implemented", "designed", "led",
                    "achieved", "improved", "created", "managed", "collaborated"]
    found_verbs = [v for v in action_verbs if v in text_lower]
    if len(found_verbs) >= 3:
        score += 10
        strengths.append("Good use of action verbs")
    else:
        improvements.append("Use more action verbs: developed, built, implemented, led...")

    # Normalize score
    max_score = (len(sections) + 2) * 10
    normalized = round((score / max_score) * 100)

    rating = "Excellent" if normalized >= 80 else ("Good" if normalized >= 60 else "Needs Improvement")

    return {
        "score": normalized,
        "rating": rating,
        "strengths": strengths,
        "improvements": improvements,
        "word_count": word_count,
    }


# ── Notification Tool ─────────────────────────────────────────

def get_latest_notifications(limit: int = 5) -> list[dict]:
    """Fetch latest active notifications from DB."""
    try:
        from database.models import get_session, Notification
        session = get_session()
        notifs = (
            session.query(Notification)
            .filter_by(is_active=True)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )
        result = [
            {
                "id": n.id,
                "title": n.title,
                "category": n.category,
                "priority": n.priority,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notifs
        ]
        session.close()
        return result
    except Exception as e:
        logger.error("Notification fetch error: %s", e)
        return []
