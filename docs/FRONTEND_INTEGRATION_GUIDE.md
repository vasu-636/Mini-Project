# MWIMS Frontend Developer Integration Guide

> **Medicine Warehouse Inventory Management System (MWIMS)**  
> **Interface Contract & Controller API Reference for Frontend UI Developers**

---

## 🎯 Overview for Frontend Developers

As a Frontend Developer working on the **MWIMS UI (Tkinter / Desktop / Web)**, you do **NOT** communicate directly with MongoDB or write PyMongo queries. 

Instead, you call clean, strongly-typed **Controller Functions** from the `controllers/` directory.

### Standard Response Format
Every controller function returns a standard Python **Tuple**:

```python
(success: bool, message: str, data: Any | None)
```

- **`success` (`bool`)**: `True` if the operation succeeded; `False` if it failed (e.g., validation error, permission denied).
- **`message` (`str`)**: Human-readable notification suitable for showing directly in UI alert dialogs (`messagebox.showinfo` or `messagebox.showerror`).
- **`data` (`Any | None`)**: Returned payload dictionary/list on success, or `None` on failure.

---

## 🔐 Session Management & Authentication Workflow

### Active User Session
The backend automatically manages user session state in `middlewares/auth_middleware.py`.

```python
from controllers.auth_controller import login_user, logout_user
from middlewares.auth_middleware import get_current_user, is_authenticated

# 1. Login User
success, msg, user_data = login_user("admin", "AdminPassword123!")
if success:
    print(f"Logged in as: {user_data['username']} (Role: {user_data['role']})")

# 2. Check Session in View
if is_authenticated():
    current_user = get_current_user()

# 3. Logout User
logout_user()
```

---

## 📋 Available Controller Functions for UI Views

---

### 1. Auth & User Management (`controllers/auth_controller.py`)

#### `login_user(username_or_email: str, password: str)`
- **Purpose**: Authenticate user and initialize active desktop session.
- **Parameters**:
  - `username_or_email` (`str`): Username or registered email address.
  - `password` (`str`): Plain-text password.
- **Returns**: `tuple[bool, str, dict[str, Any] | None]`
- **User Document Format**:
  ```json
  {
    "_id": "64f8a123bc4567890def1234",
    "username": "admin",
    "email": "admin@warehouse.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2026-08-05T12:00:00Z"
  }
  ```
  *(Note: Password hashes are automatically stripped for security)*

#### `register_user(username: str, email: str, password: str, role: str = "staff")`
- **Purpose**: Create a new user account (Staff or Admin).
- **Validation Rules**: Username $\ge 3$ alnum, valid email format, password $\ge 6$ chars.
- **Returns**: `tuple[bool, str]`

#### `logout_user()`
- **Purpose**: Clear active session and log `LOGOUT` audit event.
- **Returns**: `tuple[bool, str]`

#### `change_password(user_id: str, current_password: str, new_password: str)`
- **Requires**: Logged-in session (`@require_auth`).
- **Returns**: `tuple[bool, str]`

#### `get_all_users()`
- **Requires**: Admin Role (`@require_role("admin")`).
- **Returns**: `tuple[bool, str, list[dict[str, Any]]]`

#### `deactivate_user(target_user_id: str)`
- **Requires**: Admin Role (`@require_role("admin")`).
- **Returns**: `tuple[bool, str]`

---

### 2. Medicine Management (`controllers/medicine_controller.py`)

#### `add_medicine(medicine_name, batch_number, category, type_name, quantity, minimum_stock, expiry_date, rack, shelf, cabinet)`
- **Requires**: Logged-in session (`@require_auth`).
- **Parameters**:
  - `medicine_name` (`str`): e.g., `"Amoxicillin 500mg"`
  - `batch_number` (`str`): e.g., `"BAT-2026-001"` (Must be unique)
  - `category` (`str`): Must be one of: `"Antibiotic"`, `"Analgesic"`, `"Antipyretic"`, `"Antiseptic"`, `"Cardiovascular"`, `"Dermatological"`, `"Gastrointestinal"`, `"Respiratory"`, `"Vitamins & Supplements"`, `"Other"`
  - `type_name` (`str`): Must be one of: `"Tablet"`, `"Capsule"`, `"Syrup"`, `"Injection"`, `"Ointment"`, `"Drops"`, `"Inhaler"`, `"Powder"`, `"Other"`
  - `quantity` (`int`): $\ge 0$
  - `minimum_stock` (`int`): $\ge 0$
  - `expiry_date` (`str`): `"YYYY-MM-DD"` format (e.g., `"2026-12-31"`)
  - `rack`, `shelf`, `cabinet` (`str`): Storage location identifiers.
- **Returns**: `tuple[bool, str, dict[str, Any] | None]`

#### `get_all_medicines()`
- **Requires**: Logged-in session (`@require_auth`).
- **Returns**: `tuple[bool, str, list[dict[str, Any]]]`

#### `get_medicine_by_id(medicine_id: str)`
- **Returns**: `tuple[bool, str, dict[str, Any] | None]`

#### `update_medicine(medicine_id: str, update_fields: dict[str, Any])`
- **Requires**: Logged-in session (`@require_auth`).
- **Example Usage**:
  ```python
  update_medicine("64f8a123bc4567890def1234", {
      "quantity": 150,
      "minimum_stock": 20
  })
  ```
- **Returns**: `tuple[bool, str]`

#### `delete_medicine(medicine_id: str)`
- **Requires**: Admin Role (`@require_role("admin")`).
- **Returns**: `tuple[bool, str]`

---

### 3. Inventory & Alerts (`controllers/inventory_controller.py`)

#### `adjust_stock(medicine_id: str, delta: int)`
- **Purpose**: Atomically add or subtract stock quantity.
- **Parameters**:
  - `delta` (`int`): Positive to add stock (e.g., `+50`), negative to subtract (e.g., `-10`).
- **Returns**: `tuple[bool, str, dict[str, Any] | None]`

#### `get_low_stock_alerts()`
- **Purpose**: Fetch items with stock quantity $\le$ minimum stock.
- **Returns**: `tuple[bool, str, list[dict[str, Any]]]`
- **Alert Item Fields**: Contains original medicine fields plus:
  - `"deficit"` (`int`): Quantity needed to reach minimum stock threshold.
  - `"alert_level"` (`str`): `"CRITICAL"` (quantity = 0) or `"WARNING"`.

#### `get_expiry_alerts(warning_days: int = 30)`
- **Purpose**: Fetch items expiring within `warning_days` or already expired.
- **Returns**: `tuple[bool, str, list[dict[str, Any]]]`
- **Alert Item Fields**: Contains original medicine fields plus:
  - `"days_remaining"` (`int`): Days until expiration (negative if already expired).
  - `"expiry_status"` (`str`): `"EXPIRED"`, `"CRITICAL"` ($\le 7$ days), or `"WARNING"`.

#### `get_inventory_dashboard_metrics()`
- **Purpose**: Fetch aggregated overview metrics for the main UI dashboard.
- **Returns**: `tuple[bool, str, dict[str, Any]]`
- **Payload Schema**:
  ```json
  {
    "total_unique_medicines": 45,
    "total_stock_quantity": 3200,
    "low_stock_alert_count": 3,
    "expiring_alert_count": 5,
    "expired_item_count": 1
  }
  ```

---

### 4. Search Service (`services/search_service.py`)

#### `search_medicines(keyword="", category="", type_name="", rack="", shelf="", cabinet="")`
- **Purpose**: Multi-criteria fuzzy search across medicine name, batch number, category, type, and location.
- **Example Usage**:
  ```python
  from services.search_service import search_medicines

  results = search_medicines(keyword="Amox", category="Antibiotic")
  ```
- **Returns**: `list[dict[str, Any]]`

---

### 5. Warehouse & Location Control (`controllers/warehouse_controller.py`)

#### `get_warehouse_locations()`
- **Returns**: `tuple[bool, str, dict[str, list[str]]]` (`{"racks": [...], "shelves": [...], "cabinets": [...]}`)

#### `get_location_summary()`
- **Returns**: `tuple[bool, str, list[dict[str, Any]]]` (Medicine item counts grouped by Rack/Shelf/Cabinet).

#### `transfer_medicine_location(medicine_id: str, new_rack: str, new_shelf: str, new_cabinet: str)`
- **Returns**: `tuple[bool, str]`

---

### 6. Analytics & Reports (`controllers/report_controller.py`)

#### `generate_inventory_report()`
- **Returns**: `tuple[bool, str, dict[str, Any]]` (Complete analytical report document).

#### `get_activity_logs(limit: int = 100)`
- **Requires**: Admin Role (`@require_role("admin")`).
- **Returns**: `tuple[bool, str, list[dict[str, Any]]]` (Audit trail records).

---

## 🎨 Sample Integration Code for Tkinter Views

Here is a standard pattern for calling controllers from your Tkinter UI widgets:

```python
import tkinter as tk
from tkinter import messagebox
from controllers.medicine_controller import add_medicine

def on_save_medicine():
    name = entry_name.get()
    batch = entry_batch.get()
    category = combo_category.get()
    type_name = combo_type.get()
    qty = int(entry_qty.get() or 0)
    min_stock = int(entry_min_stock.get() or 0)
    expiry = entry_expiry.get() # YYYY-MM-DD
    rack = entry_rack.get()
    shelf = entry_shelf.get()
    cabinet = entry_cabinet.get()

    # Call Controller
    success, message, new_data = add_medicine(
        name, batch, category, type_name, qty, min_stock, expiry, rack, shelf, cabinet
    )

    if success:
        messagebox.showinfo("Success", message)
        clear_form()
        refresh_medicine_table()
    else:
        messagebox.showerror("Validation Error", message)
```
