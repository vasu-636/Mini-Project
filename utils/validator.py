"""
Validation utilities for input data sanitization and rule checking.

Provides clean, reusable validation functions for emails, dates, quantities,
usernames, and medicine properties.
"""

from __future__ import annotations

from datetime import datetime
import re
from typing import Any

from utils.constants import MEDICINE_CATEGORIES, MEDICINE_TYPES, VALID_ROLES


def is_non_empty_string(value: Any) -> bool:
    """Check if value is a non-empty, non-whitespace string."""
    return isinstance(value, str) and bool(value.strip())


def is_valid_email(email: str) -> bool:
    """Validate email address format using standard regex."""
    if not isinstance(email, str):
        return False
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(email_pattern, email.strip()))


def is_valid_username(username: str) -> bool:
    """Validate username length and alphanumeric character constraint."""
    if not isinstance(username, str):
        return False
    username = username.strip()
    return len(username) >= 3 and username.isalnum()


def is_valid_password(password: str) -> bool:
    """Validate password minimum length."""
    if not isinstance(password, str):
        return False
    return len(password.strip()) >= 6


def is_valid_role(role: str) -> bool:
    """Check if role is a valid recognized system role."""
    if not isinstance(role, str):
        return False
    return role.strip().lower() in VALID_ROLES


def is_non_negative_integer(value: Any) -> bool:
    """Check if value is an integer greater than or equal to zero."""
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value >= 0
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip()) >= 0
    return False


def is_positive_integer(value: Any) -> bool:
    """Check if value is an integer strictly greater than zero."""
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value > 0
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip()) > 0
    return False


def parse_iso_date(date_str: str) -> datetime | None:
    """
    Parse a date string formatted as YYYY-MM-DD into a datetime object.

    Args:
        date_str: Date string in 'YYYY-MM-DD' format.

    Returns:
        datetime object if valid, otherwise None.
    """
    if not isinstance(date_str, str):
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d")
    except ValueError:
        return None


def is_valid_date_format(date_str: str) -> bool:
    """Check if a date string is in valid 'YYYY-MM-DD' format."""
    return parse_iso_date(date_str) is not None


def is_valid_category(category: str) -> bool:
    """Validate medicine category against recognized list."""
    if not isinstance(category, str):
        return False
    return category.strip() in MEDICINE_CATEGORIES


def is_valid_type(type_name: str) -> bool:
    """Validate medicine type against recognized list."""
    if not isinstance(type_name, str):
        return False
    return type_name.strip() in MEDICINE_TYPES
