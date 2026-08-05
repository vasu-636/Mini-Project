"""
Report service for analytical report formatting.

Generates report datasets for inventory summaries, low stock alerts,
and system activity logs.
"""

from __future__ import annotations

from typing import Any

from models import medicine_model
from services import alert_service, inventory_service
from utils.helpers import stringify_object_id


def generate_inventory_report() -> dict[str, Any]:
    """
    Generate complete analytical inventory report data payload.

    Returns:
        Report payload dictionary containing summary metrics and full item table.
    """
    summary = inventory_service.get_inventory_summary()
    medicines = [stringify_object_id(m) for m in medicine_model.get_all_medicines() if m]

    return {
        "title": "Warehouse Inventory Summary Report",
        "summary": summary,
        "items": [m for m in medicines if m is not None],
    }
