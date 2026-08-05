"""
Inventory service for metrics compilation and stock management rules.

Calculates stock valuation, category totals, and inventory health metrics.
"""

from __future__ import annotations

from typing import Any

from models import inventory_model, medicine_model
from services import alert_service
from utils.helpers import stringify_object_id


def get_inventory_summary() -> dict[str, Any]:
    """
    Compile complete dashboard and analytical summary metrics for inventory.

    Returns:
        Dictionary containing total items, total units, low stock count, expired count.
    """
    all_medicines = medicine_model.get_all_medicines()
    low_stock_alerts = alert_service.check_low_stock_alerts()
    expiry_alerts = alert_service.check_expiry_alerts()

    total_items = len(all_medicines)
    total_quantity = sum(med.get("quantity", 0) for med in all_medicines)
    expired_count = sum(1 for item in expiry_alerts if item.get("expiry_status") == "EXPIRED")

    return {
        "total_unique_medicines": total_items,
        "total_stock_quantity": total_quantity,
        "low_stock_alert_count": len(low_stock_alerts),
        "expiring_alert_count": len(expiry_alerts),
        "expired_item_count": expired_count,
    }


def validate_stock_adjustment(
    current_quantity: int,
    adjustment_delta: int
) -> tuple[bool, str, int]:
    """
    Validate whether a stock quantity change is valid.

    Args:
        current_quantity: Current quantity in warehouse.
        adjustment_delta: Quantity adjustment (positive or negative).

    Returns:
        tuple[bool, str, int]: (Valid status, Error message, Resulting new quantity).
    """
    new_quantity = current_quantity + adjustment_delta
    if new_quantity < 0:
        return (
            False,
            f"Insufficient stock. Cannot subtract {-adjustment_delta} from current stock of {current_quantity}.",
            current_quantity,
        )

    return True, "Stock adjustment valid.", new_quantity
