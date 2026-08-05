"""
Search service for multi-field filtering and inventory search.

Provides search functionality across medicine names, batch numbers, categories,
types, and warehouse locations.
"""

from __future__ import annotations

import re
from typing import Any

from models import medicine_model
from utils.helpers import stringify_object_id


def search_medicines(
    keyword: str = "",
    category: str = "",
    type_name: str = "",
    rack: str = "",
    shelf: str = "",
    cabinet: str = ""
) -> list[dict[str, Any]]:
    """
    Search medicines using keyword match and filter criteria.

    Args:
        keyword: Search keyword matching medicine name or batch number.
        category: Filter by category.
        type_name: Filter by medicine type.
        rack: Filter by rack.
        shelf: Filter by shelf.
        cabinet: Filter by cabinet.

    Returns:
        List of matching sanitized medicine dictionaries.
    """
    query_filter: dict[str, Any] = {}

    if keyword.strip():
        regex_pattern = {"$regex": re.escape(keyword.strip()), "$options": "i"}
        query_filter["$or"] = [
            {"medicine_name": regex_pattern},
            {"batch_number": regex_pattern},
        ]

    if category.strip():
        query_filter["category"] = category.strip()

    if type_name.strip():
        query_filter["type"] = type_name.strip()

    if rack.strip():
        query_filter["rack"] = rack.strip()

    if shelf.strip():
        query_filter["shelf"] = shelf.strip()

    if cabinet.strip():
        query_filter["cabinet"] = cabinet.strip()

    raw_results = medicine_model.get_all_medicines(query_filter)
    sanitized_results = [stringify_object_id(doc) for doc in raw_results if doc]

    return [doc for doc in sanitized_results if doc is not None]
