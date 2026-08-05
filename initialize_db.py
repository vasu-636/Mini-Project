"""
Database initialization and seed script for MWIMS.

Creates necessary MongoDB collection indexes and seeds the default admin user.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pymongo import ASCENDING
from pymongo.errors import PyMongoError

from config import (
    DEFAULT_ADMIN_EMAIL,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_USERNAME,
)
from database import (
    activity_logs_collection,
    medicines_collection,
    reports_collection,
    users_collection,
)
from utils.hash import hash_password


def setup_indexes() -> None:
    """Create MongoDB indexes for database collections."""
    try:
        # Users Collection Indexes
        users_collection.create_index([("username", ASCENDING)], unique=True)
        users_collection.create_index([("email", ASCENDING)], unique=True)
        print("Users collection indexes verified.")

        # Medicines Collection Indexes
        medicines_collection.create_index([("batch_number", ASCENDING)], unique=True)
        medicines_collection.create_index([("medicine_name", ASCENDING)])
        medicines_collection.create_index([("expiry_date", ASCENDING)])
        medicines_collection.create_index([("category", ASCENDING)])
        print("Medicines collection indexes verified.")

        # Activity Logs Indexes
        activity_logs_collection.create_index([("timestamp", ASCENDING)])
        activity_logs_collection.create_index([("user_id", ASCENDING)])
        print("Activity logs collection indexes verified.")

        # Reports Collection Indexes
        reports_collection.create_index([("created_at", ASCENDING)])
        print("Reports collection indexes verified.")

    except PyMongoError as exc:
        print(f"Error creating database indexes: {exc}")


def seed_admin_user() -> bool:
    """
    Seed default administrator user account if no admin user exists.

    Returns:
        True if admin was seeded or already exists, False on failure.
    """
    try:
        existing_admin = users_collection.find_one({"role": "admin"})
        if existing_admin:
            print("Admin user already exists. Skipping seed.")
            return True

        hashed_password = hash_password(DEFAULT_ADMIN_PASSWORD)
        now = datetime.now(timezone.utc)

        admin_payload = {
            "username": DEFAULT_ADMIN_USERNAME,
            "email": DEFAULT_ADMIN_EMAIL.lower(),
            "password": hashed_password,
            "role": "admin",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }

        result = users_collection.insert_one(admin_payload)
        print(f"Default admin user created successfully with ID: {result.inserted_id}")
        return True

    except Exception as exc:
        print(f"Failed to seed admin user: {exc}")
        return False


def initialize_database() -> None:
    """Run index setup and data seeding."""
    print("Starting MWIMS database initialization...")
    setup_indexes()
    seed_admin_user()
    print("Database initialization completed successfully.")


if __name__ == "__main__":
    initialize_database()
