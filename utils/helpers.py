"""
General helper functions for data transformation and string handling.

Provides ObjectId conversion, datetime formatting, dictionary sanitization,
and common string formatting logic.
"""

from __future__ import annotations

from datetime import datetime, date
from typing import Any

from bson import ObjectId


def stringify_object_id(doc: dict[str, Any] | None) -> dict[str, Any] | None:
    """
    Convert '_id' field of MongoDB document from ObjectId to string.

    Args:
        doc: MongoDB dictionary document.

    Returns:
        Sanitized dictionary with string '_id', or None if doc is None.
    """
    if doc is None:
        return None

    sanitized = dict(doc)
    if "_id" in sanitized and isinstance(sanitized["_id"], ObjectId):
        sanitized["_id"] = str(sanitized["_id"])

    return sanitized


def format_datetime(dt: datetime | date | None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime or date object to string.

    Args:
        dt: datetime or date object.
        fmt: Target format string.

    Returns:
        Formatted string, or empty string if dt is None.
    """
    if dt is None:
        return ""
    if isinstance(dt, (datetime, date)):
        return dt.strftime(fmt)
    return str(dt)


def sanitize_user_doc(user_doc: dict[str, Any] | None) -> dict[str, Any] | None:
    """
    Sanitize user document by removing sensitive fields (password hash).

    Args:
        user_doc: Raw user dictionary from MongoDB.

    Returns:
        Sanitized user dictionary without password field.
    """
    if not user_doc:
        return None

    sanitized = stringify_object_id(user_doc)
    if sanitized and "password" in sanitized:
        del sanitized["password"]

    return sanitized
