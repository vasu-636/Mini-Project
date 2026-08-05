"""
Authentication controller for managing user registration, login, session, and role security.

Acts as the backend business logic controller for user credentials and RBAC.
"""

from __future__ import annotations

from typing import Any

from middlewares import auth_middleware
from middlewares.exception_handler import handle_exceptions
from middlewares.role_middleware import require_role
from models import report_model, user_model
from utils.constants import ACTION_CREATE_USER, ACTION_LOGIN, ACTION_LOGOUT, ROLE_ADMIN
from utils.hash import (
    PasswordHashError,
    PasswordVerificationError,
    hash_password,
    verify_password,
)
from utils.helpers import sanitize_user_doc, stringify_object_id
from utils.validator import (
    is_valid_email,
    is_valid_password,
    is_valid_role,
    is_valid_username,
)


@handle_exceptions("Failed to register user.")
def register_user(
    username: str,
    email: str,
    password: str,
    role: str = "staff"
) -> tuple[bool, str]:
    """Register a new user account."""
    username = username.strip()
    email = email.strip().lower()
    password = password.strip()
    role = role.strip().lower()

    if not is_valid_username(username):
        return False, "Username must be at least 3 alphanumeric characters."

    if not is_valid_email(email):
        return False, "Invalid email address format."

    if not is_valid_password(password):
        return False, "Password must be at least 6 characters long."

    if not is_valid_role(role):
        return False, "Invalid role specified."

    if user_model.username_exists(username):
        return False, "Username is already taken."

    if user_model.email_exists(email):
        return False, "Email address is already registered."

    hashed_pw = hash_password(password)

    user_payload: dict[str, Any] = {
        "username": username,
        "email": email,
        "password": hashed_pw,
        "role": role,
        "is_active": True,
    }

    inserted_id = user_model.create_user(user_payload)
    if inserted_id is None:
        return False, "Database insertion failed."

    # Audit log if an admin is logged in
    current_user = auth_middleware.get_current_user()
    if current_user:
        report_model.log_activity(
            current_user["_id"],
            current_user["username"],
            ACTION_CREATE_USER,
            f"Registered new user '{username}' with role '{role}'.",
        )

    return True, "User registered successfully."


@handle_exceptions("Authentication failed.")
def login_user(
    username_or_email: str,
    password: str
) -> tuple[bool, str, dict[str, Any] | None]:
    """Authenticate a user session."""
    identifier = username_or_email.strip()
    password = password.strip()

    if not identifier or not password:
        return False, "Username/Email and Password are required.", None

    user = user_model.get_user_by_username(identifier)
    if not user:
        user = user_model.get_user_by_email(identifier.lower())

    invalid_msg = "Invalid username/email or password."

    if not user:
        return False, invalid_msg, None

    if not user.get("is_active", True):
        return False, "Account is deactivated. Please contact an administrator.", None

    if not verify_password(password, user["password"]):
        return False, invalid_msg, None

    sanitized = sanitize_user_doc(user)
    auth_middleware.set_current_user(sanitized)

    if sanitized:
        report_model.log_activity(
            sanitized["_id"],
            sanitized["username"],
            ACTION_LOGIN,
            "User logged in successfully.",
        )

    return True, "Login successful.", sanitized


def logout_user() -> tuple[bool, str]:
    """Terminate current user session."""
    current_user = auth_middleware.get_current_user()
    if current_user:
        report_model.log_activity(
            current_user["_id"],
            current_user["username"],
            ACTION_LOGOUT,
            "User logged out.",
        )

    auth_middleware.clear_current_user()
    return True, "Logged out successfully."


@handle_exceptions("Failed to change password.")
def change_password(
    user_id: str,
    current_password: str,
    new_password: str
) -> tuple[bool, str]:
    """Change password for an authenticated user."""
    user_id = user_id.strip()
    current_password = current_password.strip()
    new_password = new_password.strip()

    if not is_valid_password(new_password):
        return False, "New password must be at least 6 characters long."

    if current_password == new_password:
        return False, "New password cannot be the same as the current password."

    user = user_model.get_user_by_id(user_id)
    if not user:
        return False, "User account not found."

    if not verify_password(current_password, user["password"]):
        return False, "Current password is incorrect."

    new_hashed = hash_password(new_password)
    updated = user_model.update_user(user_id, {"password": new_hashed})

    if not updated:
        return False, "Failed to update password."

    return True, "Password updated successfully."


@require_role(ROLE_ADMIN)
def get_all_users() -> tuple[bool, str, list[dict[str, Any]]]:
    """Retrieve all user accounts (Admin only)."""
    raw_users = user_model.get_all_users()
    sanitized = [sanitize_user_doc(u) for u in raw_users if u]
    return True, "User list retrieved.", [u for u in sanitized if u is not None]


@require_role(ROLE_ADMIN)
def deactivate_user(target_user_id: str) -> tuple[bool, str]:
    """Deactivate a user account (Admin only)."""
    user = user_model.get_user_by_id(target_user_id)
    if not user:
        return False, "User account not found."

    if user.get("role") == ROLE_ADMIN:
        return False, "Administrator accounts cannot be deactivated."

    updated = user_model.update_user(target_user_id, {"is_active": False})
    if not updated:
        return False, "Failed to deactivate user account."

    return True, "User account deactivated successfully."
