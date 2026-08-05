"""
Report controller for managing analytics and activity logs.

Acts as the controller layer for report generation.
"""

from __future__ import annotations

from typing import Any

from middlewares.auth_middleware import get_current_user, require_auth
from middlewares.exception_handler import handle_exceptions
from middlewares.role_middleware import require_role
from models import report_model
from services import report_service
from utils.constants import ACTION_GENERATE_REPORT, ROLE_ADMIN
from utils.helpers import stringify_object_id


@require_auth
@handle_exceptions("Failed to generate inventory report.")
def generate_inventory_report() -> tuple[bool, str, dict[str, Any]]:
    """Generate executive analytical inventory summary report."""
    report_data = report_service.generate_inventory_report()

    current_user = get_current_user()
    if current_user:
        report_model.save_report(
            report_type="INVENTORY_SUMMARY",
            title=report_data["title"],
            data=report_data["items"],
            generated_by=current_user["username"],
        )
        report_model.log_activity(
            current_user["_id"],
            current_user["username"],
            ACTION_GENERATE_REPORT,
            "Generated Warehouse Inventory Summary Report.",
        )

    return True, "Inventory report generated successfully.", report_data


@require_role(ROLE_ADMIN)
@handle_exceptions("Failed to fetch activity logs.")
def get_activity_logs(limit: int = 100) -> tuple[bool, str, list[dict[str, Any]]]:
    """Retrieve system audit activity logs (Admin only)."""
    raw_logs = report_model.get_activity_logs(limit=limit)
    sanitized = [stringify_object_id(log) for log in raw_logs if log]
    return True, "Activity logs retrieved.", [log for log in sanitized if log is not None]
