# MWIMS Controllers & Middlewares Technical Guide

> **Medicine Warehouse Inventory Management System (MWIMS)**  
> **Controllers, Business Rules, Security Middlewares, and Error Trapping Reference**

---

## Part 1: Middlewares (`middlewares/`)

MWIMS uses higher-order Python decorators as middleware functions to intercept controller execution, validate active sessions, enforce Role-Based Access Control (RBAC), check payload parameters, and catch unhandled runtime exceptions.

---

### Module 1: `middlewares/auth_middleware.py`
- **Purpose**: Manages desktop user session state in-memory and provides authentication guards for controller functions.
- **Key Functions**:
  - `set_current_user(user)`: Sets active session user.
  - `get_current_user()`: Retrieves active session user.
  - `clear_current_user()`: Logs out active session.
  - `is_authenticated()`: Returns `True` if active user session exists.
  - `@require_auth`: Decorator restricting controller functions to authenticated sessions.

---

### Module 2: `middlewares/role_middleware.py`
- **Purpose**: Enforces Role-Based Access Control (RBAC). Restricts function execution to users with specific roles (e.g., `"admin"`).
- **Key Function**: `@require_role(*allowed_roles)`: Decorator verifying user role before execution.

---

### Module 3: `middlewares/validation_middleware.py`
- **Purpose**: Ensures required keyword parameters exist and are non-empty before executing controller logic.
- **Key Function**: `@validate_required_fields(required_fields)`: Parameter validation decorator.

---

### Module 4: `middlewares/exception_handler.py`
- **Purpose**: Provides a global safety net that catches unexpected runtime exceptions across controller methods, preventing GUI crashes in Tkinter.
- **Key Function**: `@handle_exceptions(default_message)`: Traps uncaught exceptions and returns standard failure tuple `(False, "Error message")`.

---

## Part 2: Controllers (`controllers/`)

Controllers coordinate application workflows. They validate input parameters using `utils/validator.py`, enforce security using middlewares, call models/services, and log audit events.

---

### Module 5: `controllers/auth_controller.py`
- **Functions**:
  - `register_user(username, email, password, role="staff")`
  - `login_user(username_or_email, password)`
  - `logout_user()`
  - `change_password(user_id, current_password, new_password)`
  - `get_all_users()` (`@require_role("admin")`)
  - `deactivate_user(target_user_id)` (`@require_role("admin")`)

---

### Module 6: `controllers/medicine_controller.py`
- **Functions**:
  - `add_medicine(...)` (`@require_auth`)
  - `get_all_medicines()` (`@require_auth`)
  - `get_medicine_by_id(medicine_id)` (`@require_auth`)
  - `update_medicine(medicine_id, update_fields)` (`@require_auth`)
  - `delete_medicine(medicine_id)` (`@require_role("admin")`)

---

### Module 7: `controllers/inventory_controller.py`
- **Functions**:
  - `adjust_stock(medicine_id, delta)` (`@require_auth`)
  - `get_low_stock_alerts()` (`@require_auth`)
  - `get_expiry_alerts(warning_days)` (`@require_auth`)
  - `get_inventory_dashboard_metrics()` (`@require_auth`)

---

### Module 8: `controllers/report_controller.py`
- **Functions**:
  - `generate_inventory_report()` (`@require_auth`)
  - `get_activity_logs(limit)` (`@require_role("admin")`)

---

### Module 9: `controllers/warehouse_controller.py`
- **Functions**:
  - `get_warehouse_locations()` (`@require_auth`)
  - `get_location_summary()` (`@require_auth`)
  - `transfer_medicine_location(medicine_id, new_rack, new_shelf, new_cabinet)` (`@require_auth`)
