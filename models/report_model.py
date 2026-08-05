"""
Report model for activity logging and analytical aggregation queries.

Provides operations to log user actions, query system logs, and generate
aggregated report metrics.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Sequence

from bson import ObjectId
from pymongo.errors import PyMongoError

from database import activity_logs_collection, reports_collection


def log_activity(
    user_id: str | ObjectId,
    username: str,
    action: str,
    details: str
) -> bool:
    """
    Insert an audit activity log record.

    Args:
        user_id: ObjectId or string representation of acting user.
        username: Username string.
        action: System action constant.
        details: Human-readable detail message.

    Returns:
        True if inserted successfully, False otherwise.
    """
    try:
        log_doc = {
            "user_id": str(user_id) if isinstance(user_id, ObjectId) else str(user_id or ""),
            "username": str(username or "").strip(),
            "action": str(action or "").strip(),
            "details": str(details or "").strip(),
            "timestamp": datetime.now(timezone.utc),
        }
        activity_logs_collection.insert_one(log_doc)
        return True
    except PyMongoError:
        return False


def get_activity_logs(limit: int = 100) -> list[dict[str, Any]]:
    """
    Retrieve recent activity logs sorted by timestamp descending.

    Args:
        limit: Maximum number of log records to return.

    Returns:
        List of log dictionaries.
    """
    try:
        safe_limit = max(1, limit) if isinstance(limit, int) else 100
        return list(
            activity_logs_collection.find()
            .sort("timestamp", -1)
            .limit(safe_limit)
        )
    except PyMongoError:
        return []


def save_report(
    report_type: str,
    title: str,
    data: Sequence[Any],
    generated_by: str
) -> ObjectId | None:
    """
    Save a generated report document to database.

    Args:
        report_type: Category of report.
        title: Report display title.
        data: Sequence of report data rows or metrics.
        generated_by: Username of report generator.

    Returns:
        ObjectId | None: Inserted ID on success, None on failure.
    """
    try:
        report_doc = {
            "report_type": str(report_type or "").strip(),
            "title": str(title or "").strip(),
            "data": list(data) if data is not None else [],
            "generated_by": str(generated_by or "").strip(),
            "created_at": datetime.now(timezone.utc),
        }
        result = reports_collection.insert_one(report_doc)
        return result.inserted_id
    except PyMongoError:
        return None


def get_saved_reports(limit: int = 50) -> list[dict[str, Any]]:
    """
    Retrieve list of saved report records.

    Args:
        limit: Maximum reports to return.

    Returns:
        List of report records.
    """
    try:
        safe_limit = max(1, limit) if isinstance(limit, int) else 50
        return list(
            reports_collection.find()
            .sort("created_at", -1)
            .limit(safe_limit)
        )
    except PyMongoError:
        return []
