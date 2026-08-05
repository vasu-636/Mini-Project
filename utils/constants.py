"""
Application constants for MWIMS.

This module defines system-wide constant values used across models,
controllers, services, and utilities.
"""

from typing import Final

# User Roles
ROLE_ADMIN: Final[str] = "admin"
ROLE_STAFF: Final[str] = "staff"
VALID_ROLES: Final[tuple[str, ...]] = (ROLE_ADMIN, ROLE_STAFF)

# Medicine Categories & Types
MEDICINE_CATEGORIES: Final[tuple[str, ...]] = (
    "Antibiotic",
    "Analgesic",
    "Antipyretic",
    "Antiseptic",
    "Cardiovascular",
    "Dermatological",
    "Gastrointestinal",
    "Respiratory",
    "Vitamins & Supplements",
    "Other",
)

MEDICINE_TYPES: Final[tuple[str, ...]] = (
    "Tablet",
    "Capsule",
    "Syrup",
    "Injection",
    "Ointment",
    "Drops",
    "Inhaler",
    "Powder",
    "Other",
)

# Stock & Alert Thresholds
DEFAULT_MINIMUM_STOCK: Final[int] = 10
DEFAULT_EXPIRY_WARNING_DAYS: Final[int] = 30

# Activity Log Action Types
ACTION_LOGIN: Final[str] = "LOGIN"
ACTION_LOGOUT: Final[str] = "LOGOUT"
ACTION_CREATE_USER: Final[str] = "CREATE_USER"
ACTION_UPDATE_USER: Final[str] = "UPDATE_USER"
ACTION_DELETE_USER: Final[str] = "DELETE_USER"
ACTION_ADD_MEDICINE: Final[str] = "ADD_MEDICINE"
ACTION_UPDATE_MEDICINE: Final[str] = "UPDATE_MEDICINE"
ACTION_DELETE_MEDICINE: Final[str] = "DELETE_MEDICINE"
ACTION_ADJUST_STOCK: Final[str] = "ADJUST_STOCK"
ACTION_GENERATE_REPORT: Final[str] = "GENERATE_REPORT"

# Report Types
REPORT_TYPE_INVENTORY: Final[str] = "INVENTORY_SUMMARY"
REPORT_TYPE_LOW_STOCK: Final[str] = "LOW_STOCK_ALERT"
REPORT_TYPE_EXPIRY: Final[str] = "EXPIRY_ALERT"
REPORT_TYPE_ACTIVITY: Final[str] = "ACTIVITY_LOG"
