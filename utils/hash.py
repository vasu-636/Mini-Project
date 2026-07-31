"""
Password hashing utilities.

This module provides helper functions for securely hashing and
verifying user passwords using the bcrypt algorithm.
"""

from __future__ import annotations

import bcrypt

from config import SALT_ROUNDS


class PasswordHashError(Exception):
    """Raised when password hashing fails."""


class PasswordVerificationError(Exception):
    """Raised when password verification fails."""


def hash_password(password: str) -> str:
    """
    Generate a bcrypt hash for a plain-text password.

    Args:
        password: Plain-text password.

    Returns:
        Bcrypt hash as a UTF-8 string.

    Raises:
        TypeError:
            If password is not a string.

        ValueError:
            If password is empty.

        PasswordHashError:
            If bcrypt fails to generate the hash.
    """

    if not isinstance(password, str):
        raise TypeError("Password must be of type 'str'.")

    password = password.strip()

    if not password:
        raise ValueError("Password cannot be empty.")

    try:
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=SALT_ROUNDS)
        )

        return hashed_password.decode("utf-8")

    except Exception as exc:
        raise PasswordHashError(
            "Failed to hash password."
        ) from exc


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.

    Args:
        plain_password:
            Password entered by the user.

        hashed_password:
            Password stored in the database.

    Returns:
        True if passwords match, otherwise False.

    Raises:
        TypeError:
            If arguments are not strings.

        ValueError:
            If either argument is empty.

        PasswordVerificationError:
            If bcrypt verification fails.
    """

    if not isinstance(plain_password, str):
        raise TypeError("plain_password must be of type 'str'.")

    if not isinstance(hashed_password, str):
        raise TypeError("hashed_password must be of type 'str'.")

    plain_password = plain_password.strip()
    hashed_password = hashed_password.strip()

    if not plain_password:
        raise ValueError("Password cannot be empty.")

    if not hashed_password:
        raise ValueError("Hashed password cannot be empty.")

    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    except Exception as exc:
        raise PasswordVerificationError(
            "Password verification failed."
        ) from exc