"""
Centralized exception handling middleware.

Provides a decorator to catch uncaught runtime exceptions and return
standard failure response tuples.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable


def handle_exceptions(
    default_message: str = "An unexpected server error occurred."
) -> Callable[..., Any]:
    """
    Decorator to wrap controller methods in a try-except block.

    Args:
        default_message: Fallback error message returned when an exception occurs.

    Returns:
        Decorator wrapper function.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                print(f"[ERROR] Unhandled exception in {func.__name__}: {exc}")
                return False, f"{default_message} Error: {str(exc)}"

        return wrapper

    return decorator
