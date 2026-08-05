"""
Inventory controller for stock adjustments, stock level tracking, and alert triggers.

Acts as the controller layer for stock adjustments and inventory alerts.
"""

from __future__ import annotations

from typing import Any

from middlewares.auth_middleware import get_current_user, require_auth
from middlewares.exception_handler import handle_exceptions
from models import inventory_model, medicine_model, report_model
from services import alert_service, inventory_service
from utils.constants import ACTION_ADJUST_STOCK
from utils.helpers import stringify_object_id


@require_auth
@handle_exceptions("Failed to adjust stock quantity.")
def adjust_stock(
    medicine_id: str,
    delta: int
) -> tuple[bool, str, dict[str, Any] | None]:
    """
    Adjust quantity of a medicine by delta amount (+ to add, - to subtract).
    """
    medicine = medicine_model.get_medicine_by_id(medicine_id)
    if not medicine:
        return False, "Medicine not found.", None

    current_qty = medicine.get("quantity", 0)
    valid, msg, new_qty = inventory_service.validate_stock_adjustment(current_qty, delta)

    if not valid:
        return False, msg, None

    updated = inventory_model.update_stock_quantity(medicine_id, new_qty)
    if not updated:
        return False, "Failed to update stock quantity in database.", None

    updated_doc = stringify_object_id(medicine_model.get_medicine_by_id(medicine_id))

    current_user = get_current_user()
    if current_user:
        action_desc = f"Added {delta}" if delta > 0 else f"Subtracted {-delta}"
        report_model.log_activity(
            current_user["_id"],
            current_user["username"],
            ACTION_ADJUST_STOCK,
            f"{action_desc} units for '{medicine.get('medicine_name')}' (New Qty: {new_qty}).",
        )

    return True, f"Stock adjusted successfully. New quantity: {new_qty}", updated_doc


@require_auth
@handle_exceptions("Failed to fetch low stock alerts.")
def get_low_stock_alerts() -> tuple[bool, str, list[dict[str, Any]]]:
    """Retrieve list of low stock medicine alerts."""
    alerts = alert_service.check_low_stock_alerts()
    return True, "Low stock alerts retrieved.", alerts


@require_auth
@handle_exceptions("Failed to fetch expiry alerts.")
def get_expiry_alerts(warning_days: int = 30) -> tuple[bool, str, list[dict[str, Any]]]:
    """Retrieve list of medicines expiring within warning window."""
    alerts = alert_service.check_expiry_alerts(warning_days)
    return True, "Expiry alerts retrieved.", alerts


@require_auth
@handle_exceptions("Failed to fetch inventory dashboard metrics.")
def get_inventory_dashboard_metrics() -> tuple[bool, str, dict[str, Any]]:
    """Fetch complete summary metrics for dashboard UI."""
    summary = inventory_service.get_inventory_summary()
    return True, "Dashboard metrics compiled.", summary
