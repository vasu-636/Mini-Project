# MWIMS Services & Utilities Technical Guide

> **Medicine Warehouse Inventory Management System (MWIMS)**  
> **Domain Logic Services, Cryptographic Security, and Shared Helper Utilities**

---

## Part 1: Utilities (`utils/`)

Utilities provide pure, reusable stateless helper functions and constants across all backend modules.

---

### Module 1: `utils/hash.py`
- **Purpose**: Provides cryptographic password hashing and verification using the `bcrypt` adaptive hashing algorithm (`SALT_ROUNDS = 12`).
- **Key Functions**:
  - `hash_password(password: str) -> str`: Hashes plain text password.
  - `verify_password(plain_password: str, hashed_password: str) -> bool`: Verifies password against stored bcrypt hash.

---

### Module 2: `utils/validator.py`
- **Purpose**: Sanitizes user input and enforces business constraints.
- **Key Functions**:
  - `is_non_empty_string(value)`
  - `is_valid_email(email)`
  - `is_valid_username(username)`
  - `is_valid_password(password)`
  - `is_valid_role(role)`
  - `is_non_negative_integer(value)`
  - `is_positive_integer(value)`
  - `parse_iso_date(date_str)`
  - `is_valid_category(category)`
  - `is_valid_type(type_name)`

---

### Module 3: `utils/helpers.py`
- **Purpose**: Provides object transformation, BSON sanitization, and date formatting.
- **Key Functions**:
  - `stringify_object_id(doc)`: Converts `_id` field from BSON `ObjectId` to string for UI serialization.
  - `format_datetime(dt, fmt)`: Formats datetime or date object.
  - `sanitize_user_doc(user_doc)`: Strips password field from user dictionary.

---

### Module 4: `utils/constants.py`
- **Purpose**: Central repository of immutable system constants using `typing.Final`.
- **Exported Values**: Roles (`admin`, `staff`), medicine categories (10 items), dosage types (9 items), stock thresholds, activity log constants, report types.

---

## Part 2: Services (`services/`)

Services encapsulate complex domain rules and analytics across models.

---

### Module 5: `services/inventory_service.py`
- **Key Functions**:
  - `get_inventory_summary()`: Aggregates dashboard metrics.
  - `validate_stock_adjustment(current_quantity, adjustment_delta)`: Validates quantity changes and prevents negative stock balances.

---

### Module 6: `services/alert_service.py`
- **Key Functions**:
  - `check_low_stock_alerts()`: Evaluates items below minimum stock threshold and calculates deficit.
  - `check_expiry_alerts(warning_days)`: Identifies items expiring within warning window or already expired.

---

### Module 7: `services/search_service.py`
- **Key Function**:
  - `search_medicines(keyword, category, type_name, rack, shelf, cabinet)`: Executes regex search across medicine names/batch numbers and applies exact location/type filters.

---

### Module 8: `services/report_service.py`
- **Key Function**:
  - `generate_inventory_report()`: Compiles executive analytical inventory report data payload.
