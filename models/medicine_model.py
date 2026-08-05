"""
Medicine model for managing database operations on the medicines collection.

Handles CRUD operations, query filters, location searches, and batch checks.
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


def create_medicine(medicine_data: dict[str, Any]) -> ObjectId | None:
    """
    Insert a new medicine document.

    Args:
        medicine_data: Dictionary containing medicine document fields.

    Returns:
        ObjectId | None: Inserted ID on success, None on failure.
    """
    try:
        now = datetime.now(timezone.utc)
        medicine_data["created_at"] = now
        medicine_data["updated_at"] = now

        result = medicines_collection.insert_one(medicine_data)
        return result.inserted_id

    except PyMongoError:
        return None


def get_medicine_by_id(medicine_id: str | ObjectId) -> dict[str, Any] | None:
    """
    Retrieve medicine document by ObjectId or ObjectId string.

    Args:
        medicine_id: ObjectId instance or string representation.

    Returns:
        Medicine dictionary if found, otherwise None.
    """
    obj_id = _to_object_id(medicine_id)
    if not obj_id:
        return None

    try:
        return medicines_collection.find_one({"_id": obj_id})
    except PyMongoError:
        return None


def get_medicine_by_batch(batch_number: str) -> dict[str, Any] | None:
    """
    Retrieve medicine document by unique batch number.

    Args:
        batch_number: Batch identifier string.

    Returns:
        Medicine dictionary if found, otherwise None.
    """
    if not isinstance(batch_number, str) or not batch_number.strip():
        return None

    try:
        return medicines_collection.find_one({"batch_number": batch_number.strip()})
    except PyMongoError:
        return None


def get_all_medicines(query_filter: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """
    Retrieve all medicine documents matching an optional filter.

    Args:
        query_filter: Optional MongoDB query dictionary.

    Returns:
        List of medicine document dictionaries.
    """
    try:
        filter_dict = query_filter if query_filter is not None else {}
        return list(medicines_collection.find(filter_dict))
    except PyMongoError:
        return []


def update_medicine(medicine_id: str | ObjectId, update_data: dict[str, Any]) -> bool:
    """
    Update fields in an existing medicine document.

    Args:
        medicine_id: Medicine ObjectId or string.
        update_data: Dictionary of fields to update.

    Returns:
        True if updated, False on error or no modification.
    """
    obj_id = _to_object_id(medicine_id)
    if not obj_id or not update_data:
        return False

    try:
        update_data["updated_at"] = datetime.now(timezone.utc)

        result = medicines_collection.update_one(
            {"_id": obj_id},
            {"$set": update_data},
        )
        return result.modified_count > 0

    except PyMongoError:
        return False


def delete_medicine(medicine_id: str | ObjectId) -> bool:
    """
    Delete a medicine document by ObjectId or string.

    Args:
        medicine_id: Medicine ObjectId or string.

    Returns:
        True if deleted, False otherwise.
    """
    obj_id = _to_object_id(medicine_id)
    if not obj_id:
        return False

    try:
        result = medicines_collection.delete_one({"_id": obj_id})
        return result.deleted_count > 0
    except PyMongoError:
        return False


def batch_number_exists(batch_number: str) -> bool:
    """Check whether a batch number already exists in database."""
    return get_medicine_by_batch(batch_number) is not None


def get_medicines_by_location(rack: str, shelf: str, cabinet: str) -> list[dict[str, Any]]:
    """
    Retrieve all medicines stored at a specific rack, shelf, and cabinet location.

    Args:
        rack: Rack identifier.
        shelf: Shelf identifier.
        cabinet: Cabinet identifier.

    Returns:
        List of matching medicine documents.
    """
    try:
        return list(
            medicines_collection.find({
                "rack": rack.strip(),
                "shelf": shelf.strip(),
                "cabinet": cabinet.strip(),
            })
        )
    except PyMongoError:
        return []
