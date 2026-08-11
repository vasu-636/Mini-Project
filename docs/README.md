# Medicine Warehouse Inventory Management System (MWIMS) — Documentation Hub

Welcome to the official documentation for **MWIMS** — covering both the backend architecture and the complete Tkinter GUI frontend.

---

## 📄 Documentation Index

| Document | Audience | Description |
| :--- | :--- | :--- |
| 🎨 [**`FRONTEND_ARCHITECTURE_AND_VIEWS_GUIDE.md`**](./FRONTEND_ARCHITECTURE_AND_VIEWS_GUIDE.md) | **Frontend / GUI Developers** | Complete frontend code explanation — design system (theme.py), view-by-view breakdown, widget patterns, treeview & dialog conventions, role-based UI gating, data flow examples. |
| 🔌 [**`FRONTEND_INTEGRATION_GUIDE.md`**](./FRONTEND_INTEGRATION_GUIDE.md) | **Frontend Developers (UI/Tkinter)** | Controller API reference: all function signatures, parameters, response tuple structures, authorisation requirements, and Tkinter integration examples. |
| 🏗️ [**`BACKEND_ARCHITECTURE_AND_MODELS.md`**](./BACKEND_ARCHITECTURE_AND_MODELS.md) | **Backend Developers & Evaluators** | System architecture, MVC flow, MongoDB connection (`database.py`), index setup (`initialize_db.py`), PyMongo data models. |
| 🛡️ [**`CONTROLLERS_AND_MIDDLEWARES_GUIDE.md`**](./CONTROLLERS_AND_MIDDLEWARES_GUIDE.md) | **Backend Developers & Evaluators** | All 5 controller modules and 4 middleware decorators (`@require_auth`, `@require_role`, `@handle_exceptions`, `@validate_required_fields`). |
| ⚙️ [**`SERVICES_AND_UTILS_GUIDE.md`**](./SERVICES_AND_UTILS_GUIDE.md) | **Backend Developers & Evaluators** | Domain services (alerts, inventory, reports, search) and utility helpers (bcrypt hashing, regex validation, BSON serialization). |
| 🎓 [**`VIVA_AND_INTERVIEW_QUESTION_BANK.md`**](./VIVA_AND_INTERVIEW_QUESTION_BANK.md) | **Project Presenters & Students** | 25+ viva/interview questions with detailed, technically accurate answers. |

---

## ⚡ Quick Start — Running the GUI

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Ensure MongoDB is running on localhost:27017

# 3. Launch the GUI application
python gui.py
```

Default Administrator Credentials (auto-seeded on first launch):

| Field | Value |
|-------|-------|
| Username | `admin` |
| Email | `admin@warehouse.com` |
| Password | `AdminPassword123!` |

---

## ⚡ Quick Start — Controller API for Frontend Developers

All backend interactions flow through controllers only:

```python
from controllers.auth_controller import login_user, logout_user
from controllers.medicine_controller import add_medicine, get_all_medicines
from controllers.inventory_controller import adjust_stock, get_inventory_dashboard_metrics
from controllers.warehouse_controller import transfer_medicine_location
from controllers.report_controller import generate_inventory_report
```

Every controller returns: `(success: bool, message: str, data: Any | None)`

---

## 🚀 Database Initialization (manual)

The GUI auto-initializes on launch. To run manually:

```bash
python initialize_db.py
```
