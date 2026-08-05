"""
Alert service for low stock and expiry date tracking.

Provides domain calculations for medicine expiration status and inventory deficit alerts.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from models import inventory_model, medicine_model
from utils.constants import DEFAULT_EXPIRY_WARNING_DAYS
from utils.helpers import stringify_object_id


def check_low_stock_alerts() -> list[dict[str, Any]]:
    """
    Evaluate medicines experiencing stock levels below minimum thresholds.

    Returns:
        List of low stock alert items with shortage deficit calculation.
    """
    low_stock_items = inventory_model.get_low_stock_medicines()
    alerts: list[dict[str, Any]] = []

    for item in low_stock_items:
        sanitized = stringify_object_id(item)
        if not sanitized:
            continue

        quantity = sanitized.get("quantity", 0)
        min_stock = sanitized.get("minimum_stock", 0)
        shortage = max(0, min_stock - quantity)

        sanitized["deficit"] = shortage
        sanitized["alert_level"] = "CRITICAL" if quantity == 0 else "WARNING"
        alerts.append(sanitized)

    return alerts


def check_expiry_alerts(
    warning_days: int = DEFAULT_EXPIRY_WARNING_DAYS
) -> list[dict[str, Any]]:
    """
    Identify medicines expiring within the specified warning window or already expired.

    Args:
        warning_days: Threshold days until expiration.

    Returns:
        List of expiring medicine items with days_remaining metric.
    """
    now = datetime.now(timezone.utc)
    cutoff_date = now + timedelta(days=warning_days)

    expiring_items = inventory_model.get_expiring_medicines(cutoff_date)
    alerts: list[dict[str, Any]] = []

    for item in expiring_items:
        sanitized = stringify_object_id(item)
        if not sanitized:
            continue

        expiry_date = sanitized.get("expiry_date")
        if isinstance(expiry_date, datetime):
            if expiry_date.tzinfo is None:
                expiry_date = expiry_date.replace(tzinfo=timezone.utc)
            days_remaining = (expiry_date - now).days
        else:
            days_remaining = 0

        sanitized["days_remaining"] = days_remaining
        if days_remaining <= 0:
            sanitized["expiry_status"] = "EXPIRED"
        elif days_remaining <= 7:
            sanitized["expiry_status"] = "CRITICAL"
        else:
            sanitized["expiry_status"] = "WARNING"

        alerts.append(sanitized)

    return alerts
