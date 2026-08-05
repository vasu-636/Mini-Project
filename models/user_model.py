"""
User model for managing user-related database operations.

This module provides CRUD operations for the users collection.
It is responsible only for database interaction and does not
contain business logic such as authentication or password hashing.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import PyMongoError

from database import users_collection


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


def create_user(user_data: dict[str, Any]) -> ObjectId | None:
    """
    Create a new user document in MongoDB.

    Args:
        user_data: Dictionary containing user information.

    Returns:
        ObjectId | None: Inserted ObjectId if successful, otherwise None.
    """
    try:
        now = datetime.now(timezone.utc)
        user_data["created_at"] = now
        user_data["updated_at"] = now

        result = users_collection.insert_one(user_data)
        return result.inserted_id

    except PyMongoError:
        return None


def get_user_by_username(username: str) -> dict[str, Any] | None:
    """Retrieve a user document by username."""
    if not isinstance(username, str) or not username.strip():
        return None
    try:
        return users_collection.find_one({"username": username.strip()})
    except PyMongoError:
        return None


def get_user_by_email(email: str) -> dict[str, Any] | None:
    """Retrieve a user document by email address."""
    if not isinstance(email, str) or not email.strip():
        return None
    try:
        return users_collection.find_one({"email": email.strip().lower()})
    except PyMongoError:
        return None


def get_user_by_id(user_id: str | ObjectId) -> dict[str, Any] | None:
    """Retrieve a user document using MongoDB ObjectId or string."""
    obj_id = _to_object_id(user_id)
    if not obj_id:
        return None
    try:
        return users_collection.find_one({"_id": obj_id})
    except PyMongoError:
        return None


def get_all_users() -> list[dict[str, Any]]:
    """Retrieve all user documents."""
    try:
        return list(users_collection.find())
    except PyMongoError:
        return []


def update_user(user_id: str | ObjectId, update_data: dict[str, Any]) -> bool:
    """Update an existing user document."""
    obj_id = _to_object_id(user_id)
    if not obj_id or not update_data:
        return False

    try:
        update_data["updated_at"] = datetime.now(timezone.utc)

        result = users_collection.update_one(
            {"_id": obj_id},
            {"$set": update_data},
        )
        return result.modified_count > 0

    except PyMongoError:
        return False


def delete_user(user_id: str | ObjectId) -> bool:
    """Delete a user document by ID."""
    obj_id = _to_object_id(user_id)
    if not obj_id:
        return False

    try:
        result = users_collection.delete_one({"_id": obj_id})
        return result.deleted_count > 0
    except PyMongoError:
        return False


def username_exists(username: str) -> bool:
    """Check whether a username already exists."""
    return get_user_by_username(username) is not None


def email_exists(email: str) -> bool:
    """Check whether an email already exists."""
    return get_user_by_email(email) is not None