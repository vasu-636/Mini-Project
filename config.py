"""
Application Configuration
"""

# ===========================
# MongoDB Configuration
# ===========================

MONGO_URI = "mongodb://localhost:27017/MWIMS"
DB_NAME = "MWIMS"

# ===========================
# Security Configuration
# ===========================

SALT_ROUNDS = 12

# ===========================
# Default Admin Seed Config
# ===========================

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_EMAIL = "admin@warehouse.com"
DEFAULT_ADMIN_PASSWORD = "AdminPassword123!"