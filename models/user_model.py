"""
User model for managing user-related database operations.

This module provides CRUD operations for the users collection.
It is responsible only for database interaction and does not
contain business logic such as authentication or password hashing.
"""

from datetime import datetime
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import PyMongoError

from database import users_collection


def create_user(user_data: dict[str, Any]) -> ObjectId | None:
    """
    Create a new user.

    Args:
        user_data: Dictionary containing user information.

    Returns:
        ObjectId | None:
            The inserted user's ObjectId if successful,
            otherwise None.
    """
    try:
        user_data["created_at"] = datetime.utcnow()
        user_data["updated_at"] = datetime.utcnow()

        result = users_collection.insert_one(user_data)
        return result.inserted_id

    except PyMongoError:
        return None


def get_user_by_username(username: str) -> dict[str, Any] | None:
    """
    Retrieve a user by username.

    Args:
        username: Username to search.

    Returns:
        User document if found, otherwise None.
    """
    try:
        return users_collection.find_one({"username": username})

    except PyMongoError:
        return None


def get_user_by_email(email: str) -> dict[str, Any] | None:
    """
    Retrieve a user by email.

    Args:
        email: Email address.

    Returns:
        User document if found, otherwise None.
    """
    try:
        return users_collection.find_one({"email": email})

    except PyMongoError:
        return None


def get_user_by_id(user_id: str) -> dict[str, Any] | None:
    """
    Retrieve a user using MongoDB ObjectId.

    Args:
        user_id: User ObjectId as string.

    Returns:
        User document if found, otherwise None.
    """
    try:
        return users_collection.find_one(
            {"_id": ObjectId(user_id)}
        )

    except (InvalidId, PyMongoError):
        return None


def update_user(user_id: str, update_data: dict[str, Any]) -> bool:
    """
    Update an existing user.

    Args:
        user_id: User ObjectId.
        update_data: Fields to update.

    Returns:
        True if updated successfully, otherwise False.
    """
    try:
        update_data["updated_at"] = datetime.utcnow()

        result = users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data},
        )

        return result.modified_count > 0

    except (InvalidId, PyMongoError):
        return False


def delete_user(user_id: str) -> bool:
    """
    Delete a user.

    Args:
        user_id: User ObjectId.

    Returns:
        True if deleted successfully, otherwise False.
    """
    try:
        result = users_collection.delete_one(
            {"_id": ObjectId(user_id)}
        )

        return result.deleted_count > 0

    except (InvalidId, PyMongoError):
        return False


def username_exists(username: str) -> bool:
    """
    Check whether a username already exists.

    Args:
        username: Username to check.

    Returns:
        True if username exists, otherwise False.
    """
    return get_user_by_username(username) is not None


def email_exists(email: str) -> bool:
    """
    Check whether an email already exists.

    Args:
        email: Email to check.

    Returns:
        True if email exists, otherwise False.
    """
    return get_user_by_email(email) is not None