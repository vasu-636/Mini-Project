"""
Validation middleware for checking required parameter payloads.

Provides wrapper functions to validate function inputs prior to execution.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Sequence


def validate_required_fields(
    required_fields: Sequence[str]
) -> Callable[..., Any]:
    """
    Decorator to verify that a payload dictionary contains all non-empty required fields.

    Args:
        required_fields: Names of key fields required in kwargs payload.

    Returns:
        Decorator wrapper function.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Check kwargs for required fields
            for field in required_fields:
                val = kwargs.get(field)
                if val is None or (isinstance(val, str) and not val.strip()):
                    return False, f"Missing or empty required parameter: '{field}'."
            return func(*args, **kwargs)

        return wrapper

    return decorator
