"""
Inventory model for managing stock quantities and stock adjustments.

Handles low stock queries, stock level modifications, and inventory audits.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import PyMongoError

from database import medicines_collection


def _to_object_id(id_val: str | ObjectId) -> ObjectId | None:
    """Helper to convert string or ObjectId into a valid ObjectId instance."""
    if isinstance(id_val, ObjectId):
        return id_val
    if isinstance(id_val, str):
        try:
            return ObjectId(id_val.strip())
        except (InvalidId, TypeError):
            return None
    return None


def update_stock_quantity(medicine_id: str | ObjectId, new_quantity: int) -> bool:
    """Update absolute stock quantity of a medicine item."""
    obj_id = _to_object_id(medicine_id)
    if not obj_id or new_quantity < 0:
        return False

    try:
        result = medicines_collection.update_one(
            {"_id": obj_id},
            {
                "$set": {
                    "quantity": new_quantity,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )
        return result.modified_count > 0
    except PyMongoError:
        return False


def adjust_stock_quantity(medicine_id: str | ObjectId, delta: int) -> bool:
    """Atomically increment or decrement stock quantity."""
    obj_id = _to_object_id(medicine_id)
    if not obj_id:
        return False

    try:
        result = medicines_collection.update_one(
            {"_id": obj_id},
            {
                "$inc": {"quantity": delta},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
        )
        return result.modified_count > 0
    except PyMongoError:
        return False


def get_low_stock_medicines() -> list[dict[str, Any]]:
    """Retrieve medicines where quantity <= minimum_stock."""
    try:
        return list(
            medicines_collection.find({
                "$expr": {"$lte": ["$quantity", "$minimum_stock"]}
            })
        )
    except PyMongoError:
        return []


def get_expiring_medicines(cutoff_date: datetime) -> list[dict[str, Any]]:
    """Retrieve medicines expiring on or before a cutoff date."""
    try:
        return list(
            medicines_collection.find({
                "expiry_date": {"$lte": cutoff_date}
            }).sort("expiry_date", 1)
        )
    except PyMongoError:
        return []
