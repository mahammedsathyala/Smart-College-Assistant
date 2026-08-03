"""
Smart College Assistant — Validators (complete)
Input sanitization and validation for security.
"""

from __future__ import annotations
import re
import html


def sanitize_string(value: str, max_length: int = 255) -> str:
    """Escape HTML and truncate string."""
    if not isinstance(value, str):
        value = str(value)
    cleaned = html.escape(value.strip())
    return cleaned[:max_length]


def sanitize_chat_input(value: str, max_length: int = 2000) -> str:
    """Sanitize chat input: strip, escape, limit length."""
    if not value:
        return ""
    cleaned = value.strip()
    cleaned = re.sub(r"[<>\"';&]", "", cleaned)
    return cleaned[:max_length]


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength.

    Rules:
    - At least 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return False, "Password must contain at least one special character."
    return True, "Password is strong."


def validate_required_fields(data: dict, fields: list[str]) -> tuple[bool, str]:
    """Check all required fields are present and non-empty."""
    for field in fields:
        if field not in data or data[field] is None or str(data[field]).strip() == "":
            return False, f"Field '{field}' is required."
    return True, "OK"


def validate_file_extension(filename: str) -> bool:
    """Validate uploaded file extension."""
    allowed = {".pdf", ".docx", ".txt", ".csv"}
    from pathlib import Path
    return Path(filename).suffix.lower() in allowed


def validate_phone(phone: str) -> bool:
    """Validate Indian phone number (10 digits)."""
    return bool(re.match(r"^[6-9]\d{9}$", phone.strip()))
