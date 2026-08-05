"""
Authentication middleware for session context validation and function access control.

Provides decorators and context helpers to verify active user login states.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

# Global session context dictionary for active desktop session
_current_user_session: dict[str, Any] | None = None


def set_current_user(user: dict[str, Any] | None) -> None:
    """Set the globally authenticated session user."""
    global _current_user_session
    _current_user_session = user


def get_current_user() -> dict[str, Any] | None:
    """Retrieve the currently authenticated session user."""
    return _current_user_session


def clear_current_user() -> None:
    """Clear the authenticated session user (Logout)."""
    global _current_user_session
    _current_user_session = None


def is_authenticated() -> bool:
    """Check if a valid session user is currently logged in."""
    return _current_user_session is not None


def require_auth(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to enforce authentication on controller methods.

    Returns error tuple (False, "Authentication required", None) if no active user session.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not is_authenticated():
            return False, "Authentication required. Please log in first.", None
        return func(*args, **kwargs)

    return wrapper
