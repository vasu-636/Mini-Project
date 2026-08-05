"""
Warehouse model for querying warehouse physical storage allocations.

Provides functions to query location utilization, distinct racks, shelves,
and cabinets occupied by medicine stock.
"""

from __future__ import annotations

from typing import Any
from pymongo.errors import PyMongoError

from database import medicines_collection


def get_distinct_racks() -> list[str]:
    """Retrieve list of distinct rack identifiers currently used."""
    try:
        return list(medicines_collection.distinct("rack"))
    except PyMongoError:
        return []


def get_distinct_shelves() -> list[str]:
    """Retrieve list of distinct shelf identifiers currently used."""
    try:
        return list(medicines_collection.distinct("shelf"))
    except PyMongoError:
        return []


def get_distinct_cabinets() -> list[str]:
    """Retrieve list of distinct cabinet identifiers currently used."""
    try:
        return list(medicines_collection.distinct("cabinet"))
    except PyMongoError:
        return []


def get_location_summary() -> list[dict[str, Any]]:
    """
    Aggregate counts of medicines grouped by rack, shelf, and cabinet.

    Returns:
        List of location summary dictionaries with item count and total quantity.
    """
    pipeline = [
        {
            "$group": {
                "_id": {
                    "rack": "$rack",
                    "shelf": "$shelf",
                    "cabinet": "$cabinet",
                },
                "total_items": {"$sum": 1},
                "total_quantity": {"$sum": "$quantity"},
            }
        },
        {"$sort": {"_id.rack": 1, "_id.shelf": 1, "_id.cabinet": 1}},
    ]

    try:
        return list(medicines_collection.aggregate(pipeline))
    except PyMongoError:
        return []
