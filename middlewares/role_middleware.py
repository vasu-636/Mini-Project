"""
Role-based access control (RBAC) middleware.

Provides decorators to restrict execution of controller methods based on user roles.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from middlewares.auth_middleware import get_current_user, is_authenticated


def require_role(*allowed_roles: str) -> Callable[..., Any]:
    """
    Decorator to restrict access to users possessing specified roles.

    Args:
        allowed_roles: Role strings allowed to execute the function.

    Returns:
        Decorator wrapper function.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not is_authenticated():
                return False, "Authentication required. Access denied."

            current_user = get_current_user()
            user_role = current_user.get("role", "") if current_user else ""

            normalized_allowed = [r.strip().lower() for r in allowed_roles]
            if user_role.strip().lower() not in normalized_allowed:
                return (
                    False,
                    f"Permission denied. Required role: {', '.join(allowed_roles)}.",
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator
