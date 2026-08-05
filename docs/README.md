# Medicine Warehouse Inventory Management System (MWIMS) - Documentation Hub

Welcome to the official backend documentation and frontend integration manual for **MWIMS**.

This `docs/` directory contains complete documentation, API interface contracts, architectural explanations, and technical interview/viva preparation guides.

---

## 📄 Documentation Directory Overview

| Document File | Target Audience | Description |
| :--- | :--- | :--- |
| 🔌 [**`FRONTEND_INTEGRATION_GUIDE.md`**](./FRONTEND_INTEGRATION_GUIDE.md) | **Frontend Developers (UI/Tkinter)** | Complete controller API reference detailing available function calls, arguments, response tuple structures, authorization requirements, and Tkinter code examples. |
| 🏗️ [**`BACKEND_ARCHITECTURE_AND_MODELS.md`**](./BACKEND_ARCHITECTURE_AND_MODELS.md) | **Backend Developers & Evaluators** | High-level system architecture, MVC flow, database connection management (`database.py`), index setup (`initialize_db.py`), and raw PyMongo data models (`user_model.py`, `medicine_model.py`). |
| 🛡️ [**`CONTROLLERS_AND_MIDDLEWARES_GUIDE.md`**](./CONTROLLERS_AND_MIDDLEWARES_GUIDE.md) | **Backend Developers & Evaluators** | Detailed breakdown of all 5 controller modules and 4 middleware decorators (`@require_auth`, `@require_role`, `@validate_required_fields`, `@handle_exceptions`). |
| ⚙️ [**`SERVICES_AND_UTILS_GUIDE.md`**](./SERVICES_AND_UTILS_GUIDE.md) | **Backend Developers & Evaluators** | Domain logic services (alerts, inventory valuation, multi-field search, report formatting) and utility helpers (bcrypt password hashing, regex validation, BSON ObjectId serialization). |
| 🎓 [**`VIVA_AND_INTERVIEW_QUESTION_BANK.md`**](./VIVA_AND_INTERVIEW_QUESTION_BANK.md) | **Project Presenters & Students** | Master defense question bank containing exhaustive, technically accurate sample answers for 25+ viva and interview questions. |

---

## ⚡ Quick Start for Frontend Developers

1. Read [`FRONTEND_INTEGRATION_GUIDE.md`](./FRONTEND_INTEGRATION_GUIDE.md).
2. Import controller functions directly into your Tkinter views:
   ```python
   from controllers.auth_controller import login_user
   from controllers.medicine_controller import add_medicine, get_all_medicines
   from controllers.inventory_controller import adjust_stock, get_inventory_dashboard_metrics
   from services.search_service import search_medicines
   ```
3. All controllers return standard response tuples: `(success: bool, message: str, data: Any | None)`.

---

## 🚀 Quick Start for Database Initialization

Before running the UI, initialize MongoDB indexes and default seed data:

```bash
python initialize_db.py
```

- Default Administrator Credentials:
  - **Username**: `admin`
  - **Email**: `admin@warehouse.com`
  - **Password**: `AdminPassword123!`
