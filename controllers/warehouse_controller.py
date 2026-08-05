"""
Warehouse controller for managing location structures (racks, shelves, cabinets).

Acts as the controller layer for warehouse location allocation and movement.
"""

from __future__ import annotations

from typing import Any

from middlewares.auth_middleware import get_current_user, require_auth
from middlewares.exception_handler import handle_exceptions
from models import medicine_model, report_model, warehouse_model
from utils.constants import ACTION_UPDATE_MEDICINE
from utils.helpers import stringify_object_id
from utils.validator import is_non_empty_string


@require_auth
@handle_exceptions("Failed to fetch warehouse locations.")
def get_warehouse_locations() -> tuple[bool, str, dict[str, list[str]]]:
    """Retrieve lists of distinct racks, shelves, and cabinets in use."""
    racks = warehouse_model.get_distinct_racks()
    shelves = warehouse_model.get_distinct_shelves()
    cabinets = warehouse_model.get_distinct_cabinets()

    return True, "Warehouse locations retrieved.", {
        "racks": racks,
        "shelves": shelves,
        "cabinets": cabinets,
    }


@require_auth
@handle_exceptions("Failed to fetch location summary.")
def get_location_summary() -> tuple[bool, str, list[dict[str, Any]]]:
    """Retrieve summary aggregation of medicine stock per location."""
    summary = warehouse_model.get_location_summary()
    return True, "Location summary retrieved.", summary


@require_auth
@handle_exceptions("Failed to transfer medicine location.")
def transfer_medicine_location(
    medicine_id: str,
    new_rack: str,
    new_shelf: str,
    new_cabinet: str
) -> tuple[bool, str]:
    """Relocate a medicine to a new rack, shelf, and cabinet."""
    new_rack = new_rack.strip()
    new_shelf = new_shelf.strip()
    new_cabinet = new_cabinet.strip()

    if not is_non_empty_string(new_rack) or not is_non_empty_string(new_shelf) or not is_non_empty_string(new_cabinet):
        return False, "Rack, shelf, and cabinet identifiers are required."

    medicine = medicine_model.get_medicine_by_id(medicine_id)
    if not medicine:
        return False, "Medicine not found."

    updated = medicine_model.update_medicine(
        medicine_id,
        {"rack": new_rack, "shelf": new_shelf, "cabinet": new_cabinet},
    )

    if not updated:
        return False, "Failed to update location in database."

    current_user = get_current_user()
    if current_user:
        report_model.log_activity(
            current_user["_id"],
            current_user["username"],
            ACTION_UPDATE_MEDICINE,
            f"Relocated '{medicine.get('medicine_name')}' to Rack {new_rack} / Shelf {new_shelf} / Cabinet {new_cabinet}.",
        )

    return True, f"Medicine successfully relocated to Rack {new_rack} / Shelf {new_shelf} / Cabinet {new_cabinet}."
