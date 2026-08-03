"""
Smart College Assistant — Helper Utilities
General-purpose utility functions.
"""

import hashlib
import json
import math
import uuid
from datetime import datetime, date
from typing import Any

from utils.logger import setup_logger

logger = setup_logger(__name__)


def generate_id() -> str:
    """Generate a unique UUID string."""
    return str(uuid.uuid4())


def current_timestamp() -> str:
    """Return ISO-8601 UTC timestamp string."""
    return datetime.utcnow().isoformat()


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.

    Args:
        password: Plain-text password.

    Returns:
        Bcrypt-hashed string.
    """
    import bcrypt
    from config.settings import ActiveConfig
    salt = bcrypt.gensalt(rounds=ActiveConfig.BCRYPT_ROUNDS)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify plain-text password against bcrypt hash."""
    import bcrypt
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def calculate_cgpa(marks: list[dict]) -> float:
    """
    Calculate CGPA from a list of subject marks.

    Args:
        marks: List of {"grade_point": float, "credits": int} dicts.

    Returns:
        CGPA rounded to 2 decimal places.
    """
    total_credits = sum(m["credits"] for m in marks)
    if total_credits == 0:
        return 0.0
    weighted = sum(m["grade_point"] * m["credits"] for m in marks)
    return round(weighted / total_credits, 2)


def calculate_attendance_percentage(
    present: int, total: int
) -> float:
    """Return attendance percentage."""
    if total == 0:
        return 0.0
    return round((present / total) * 100, 2)


def grade_to_point(grade: str) -> float:
    """Convert letter grade to grade point (10-point scale)."""
    mapping = {
        "O": 10.0, "A+": 9.0, "A": 8.0,
        "B+": 7.0, "B": 6.0, "C": 5.0,
        "F": 0.0,
    }
    return mapping.get(grade.upper(), 0.0)


def paginate(items: list, page: int, per_page: int) -> dict:
    """
    Paginate a list.

    Returns:
        Dict with items, page, per_page, total, pages.
    """
    total = len(items)
    pages = math.ceil(total / per_page) if per_page > 0 else 1
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "items": items[start:end],
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages,
    }


def safe_json(data: Any) -> str:
    """Safely serialize data to JSON string."""
    try:
        return json.dumps(data, default=str, ensure_ascii=False)
    except Exception as e:
        logger.error("JSON serialization failed: %s", e)
        return "{}"


def days_until(target_date: date) -> int:
    """Return number of days until target_date."""
    delta = target_date - date.today()
    return max(0, delta.days)


def format_date(dt: datetime | date | str, fmt: str = "%d %b %Y") -> str:
    """Format a date object or ISO string to a readable string."""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return dt
    return dt.strftime(fmt)


def truncate_text(text: str, max_chars: int = 200) -> str:
    """Truncate text to max_chars and append ellipsis if needed."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "…"
