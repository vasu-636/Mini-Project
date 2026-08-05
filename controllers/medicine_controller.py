"""
Medicine controller for managing medicine records, CRUD business rules, and validation.

Acts as the controller layer orchestrating medicine data between services and medicine_model.
"""

from __future__ import annotations

from typing import Any

from middlewares.auth_middleware import get_current_user, require_auth
from middlewares.exception_handler import handle_exceptions
from middlewares.role_middleware import require_role
from models import medicine_model, report_model
from utils.constants import ACTION_ADD_MEDICINE, ACTION_DELETE_MEDICINE, ACTION_UPDATE_MEDICINE, ROLE_ADMIN
from utils.helpers import stringify_object_id
from utils.validator import (
    is_non_negative_integer,
    is_non_empty_string,
    is_valid_category,
    is_valid_date_format,
    is_valid_type,
    parse_iso_date,
)


@require_auth
@handle_exceptions("Failed to add medicine.")
def add_medicine(
    medicine_name: str,
    batch_number: str,
    category: str,
    type_name: str,
    quantity: int,
    minimum_stock: int,
    expiry_date: str,
    rack: str,
    shelf: str,
    cabinet: str
) -> tuple[bool, str, dict[str, Any] | None]:
    """Add a new medicine record to inventory."""
    medicine_name = medicine_name.strip()
    batch_number = batch_number.strip()
    category = category.strip()
    type_name = type_name.strip()
    expiry_date_str = expiry_date.strip()
    rack = rack.strip()
    shelf = shelf.strip()
    cabinet = cabinet.strip()

    if not is_non_empty_string(medicine_name):
        return False, "Medicine name is required.", None

    if not is_non_empty_string(batch_number):
        return False, "Batch number is required.", None

    if not is_valid_category(category):
        return False, f"Invalid category: '{category}'.", None

    if not is_valid_type(type_name):
        return False, f"Invalid medicine type: '{type_name}'.", None

    if not is_non_negative_integer(quantity):
        return False, "Quantity must be a non-negative integer.", None

    if not is_non_negative_integer(minimum_stock):
        return False, "Minimum stock must be a non-negative integer.", None

    parsed_expiry = parse_iso_date(expiry_date_str)
    if not parsed_expiry:
        return False, "Expiry date must be in YYYY-MM-DD format.", None

    if not is_non_empty_string(rack) or not is_non_empty_string(shelf) or not is_non_empty_string(cabinet):
        return False, "Warehouse location (Rack, Shelf, Cabinet) is required.", None

    if medicine_model.batch_number_exists(batch_number):
        return False, f"Medicine batch number '{batch_number}' already exists.", None

    medicine_payload = {
        "medicine_name": medicine_name,
        "batch_number": batch_number,
        "category": category,
        "type": type_name,
        "quantity": int(quantity),
        "minimum_stock": int(minimum_stock),
        "expiry_date": parsed_expiry,
        "rack": rack,
        "shelf": shelf,
        "cabinet": cabinet,
    }

    inserted_id = medicine_model.create_medicine(medicine_payload)
    if not inserted_id:
        return False, "Database insertion failed.", None

    sanitized = stringify_object_id(medicine_model.get_medicine_by_id(str(inserted_id)))

    current_user = get_current_user()
    if current_user:
        report_model.log_activity(
            current_user["_id"],
            current_user["username"],
            ACTION_ADD_MEDICINE,
            f"Added medicine '{medicine_name}' (Batch: {batch_number}).",
        )

    return True, "Medicine added successfully.", sanitized


@require_auth
@handle_exceptions("Failed to fetch medicines.")
def get_all_medicines() -> tuple[bool, str, list[dict[str, Any]]]:
    """Retrieve all medicine items."""
    raw_medicines = medicine_model.get_all_medicines()
    sanitized = [stringify_object_id(m) for m in raw_medicines if m]
    return True, "Medicines retrieved successfully.", [m for m in sanitized if m is not None]


@require_auth
@handle_exceptions("Failed to fetch medicine.")
def get_medicine_by_id(medicine_id: str) -> tuple[bool, str, dict[str, Any] | None]:
    """Retrieve a single medicine item by ObjectId string."""
    raw = medicine_model.get_medicine_by_id(medicine_id.strip())
    if not raw:
        return False, "Medicine not found.", None
    return True, "Medicine found.", stringify_object_id(raw)


@require_auth
@handle_exceptions("Failed to update medicine.")
def update_medicine(
    medicine_id: str,
    update_fields: dict[str, Any]
) -> tuple[bool, str]:
    """Update medicine fields."""
    existing = medicine_model.get_medicine_by_id(medicine_id)
    if not existing:
        return False, "Medicine record not found."

    clean_updates: dict[str, Any] = {}

    if "medicine_name" in update_fields:
        val = str(update_fields["medicine_name"]).strip()
        if not is_non_empty_string(val):
            return False, "Medicine name cannot be empty."
        clean_updates["medicine_name"] = val

    if "category" in update_fields:
        val = str(update_fields["category"]).strip()
        if not is_valid_category(val):
            return False, "Invalid category."
        clean_updates["category"] = val

    if "type" in update_fields:
        val = str(update_fields["type"]).strip()
        if not is_valid_type(val):
            return False, "Invalid medicine type."
        clean_updates["type"] = val

    if "quantity" in update_fields:
        val = update_fields["quantity"]
        if not is_non_negative_integer(val):
            return False, "Quantity must be non-negative integer."
        clean_updates["quantity"] = int(val)

    if "minimum_stock" in update_fields:
        val = update_fields["minimum_stock"]
        if not is_non_negative_integer(val):
            return False, "Minimum stock must be non-negative integer."
        clean_updates["minimum_stock"] = int(val)

    if "expiry_date" in update_fields:
        val = str(update_fields["expiry_date"]).strip()
        parsed = parse_iso_date(val)
        if not parsed:
            return False, "Expiry date must be YYYY-MM-DD."
        clean_updates["expiry_date"] = parsed

    for loc_field in ("rack", "shelf", "cabinet"):
        if loc_field in update_fields:
            val = str(update_fields[loc_field]).strip()
            if not is_non_empty_string(val):
                return False, f"Location '{loc_field}' cannot be empty."
            clean_updates[loc_field] = val

    if not clean_updates:
        return False, "No valid update fields provided."

    success = medicine_model.update_medicine(medicine_id, clean_updates)
    if not success:
        return False, "Database update failed."

    current_user = get_current_user()
    if current_user:
        report_model.log_activity(
            current_user["_id"],
            current_user["username"],
            ACTION_UPDATE_MEDICINE,
            f"Updated medicine ID {medicine_id}.",
        )

    return True, "Medicine updated successfully."


@require_role(ROLE_ADMIN)
@handle_exceptions("Failed to delete medicine.")
def delete_medicine(medicine_id: str) -> tuple[bool, str]:
    """Delete a medicine record (Admin only)."""
    existing = medicine_model.get_medicine_by_id(medicine_id)
    if not existing:
        return False, "Medicine record not found."

    deleted = medicine_model.delete_medicine(medicine_id)
    if not deleted:
        return False, "Database delete failed."

    current_user = get_current_user()
    if current_user:
        report_model.log_activity(
            current_user["_id"],
            current_user["username"],
            ACTION_DELETE_MEDICINE,
            f"Deleted medicine '{existing.get('medicine_name')}' (Batch: {existing.get('batch_number')}).",
        )

    return True, "Medicine deleted successfully."
