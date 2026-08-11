# 💊 MWIMS — Medicine Warehouse Inventory Management System

> A professional **Tkinter desktop application** backed by **MongoDB** for managing medicine warehouse inventory.  
> Built with a clean MVC architecture: Python 3.13+ · Tkinter · PyMongo · bcrypt.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [Default Credentials](#-default-credentials)
- [Role-Based Access Control](#-role-based-access-control)
- [Available Screens](#-available-screens)
- [Architecture Overview](#-architecture-overview)
- [Data Flow](#-data-flow)
- [Documentation Index](#-documentation-index)
- [Contributing](#-contributing)

---

## 🌟 Overview

MWIMS is a **production-quality desktop application** that provides:

- **Secure login** with bcrypt-hashed passwords and session management
- **Full Medicine CRUD** with batch tracking, category, type, and location metadata
- **Inventory management** — receive stock, reduce stock, transfer warehouse locations
- **Smart alerts** — expiry warnings (configurable window) and low-stock deficits
- **Warehouse management** — distinct rack / shelf / cabinet overview and location finder
- **Reports** — inventory summary, expiry, low-stock, and admin activity-log reports with **CSV export**
- **User management** (Admin only) — create accounts, view all users, deactivate accounts
- **Role-based UI** — menus, buttons, and entire screens are shown or hidden based on the logged-in role

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 Authentication | Login with username or email, bcrypt verification, session middleware |
| 👥 User Management | Admin-only: create, list, search, deactivate users |
| 💊 Medicine CRUD | Add, edit, delete, search medicines via Treeview table |
| 📦 Inventory | Receive/reduce stock (delta), transfer warehouse location |
| 🏭 Warehouse | Location overview, location finder, full medicine map |
| ⏰ Expiry Alerts | Expired / Critical / Warning tabs, configurable warning window |
| ⚠️ Low Stock | Out-of-stock (Critical) and below-minimum (Warning) tabs |
| 📊 Reports | Inventory, Expiry, Low-Stock and Activity Log reports |
| 📥 CSV Export | Export any report to a `.csv` file via file-save dialog |
| ⚙️ Settings | Profile card, change password, logout |
| 🎨 Dark Theme | Professional GitHub-inspired dark UI with consistent design tokens |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.13+ |
| GUI Framework | Tkinter (standard library only) |
| Database | MongoDB 6+ (local) |
| DB Driver | PyMongo 4.x |
| Password Hashing | bcrypt |
| IDE | Visual Studio Code |

---

## 📁 Project Structure

```
MWIMS/
│
├── gui.py                     ← GUI entry point  (run this)
├── app.py                     ← Legacy CLI entry point
├── config.py                  ← MongoDB URI, admin seed config
├── database.py                ← MongoDB connection & collections
├── initialize_db.py           ← Index setup + default admin seed
├── requirements.txt
│
├── controllers/               ← Business logic layer (backend)
│   ├── auth_controller.py
│   ├── medicine_controller.py
│   ├── inventory_controller.py
│   ├── warehouse_controller.py
│   └── report_controller.py
│
├── models/                    ← PyMongo data access layer
│   ├── user_model.py
│   ├── medicine_model.py
│   ├── inventory_model.py
│   ├── warehouse_model.py
│   └── report_model.py
│
├── services/                  ← Domain services
│   ├── alert_service.py
│   ├── inventory_service.py
│   ├── report_service.py
│   └── search_service.py
│
├── middlewares/               ← Decorators & session helpers
│   ├── auth_middleware.py
│   ├── role_middleware.py
│   ├── exception_handler.py
│   └── validation_middleware.py
│
├── utils/                     ← Shared utilities
│   ├── constants.py
│   ├── validator.py
│   ├── helpers.py
│   └── hash.py
│
├── views/                     ← Tkinter GUI (frontend only)
│   ├── __init__.py
│   ├── theme.py               ← Design system: colours, fonts, widget factories
│   ├── login_view.py          ← Login screen
│   ├── main_app.py            ← App shell: sidebar + dashboard
│   ├── medicine_view.py       ← Medicine CRUD screen
│   ├── inventory_view.py      ← Stock adjustment + transfer
│   ├── warehouse_view.py      ← Location overview + finder
│   ├── expiry_view.py         ← Expiry alerts screen
│   ├── low_stock_view.py      ← Low stock alerts screen
│   ├── reports_view.py        ← Reports + CSV export
│   ├── user_management_view.py← User management (Admin only)
│   └── settings_view.py       ← Profile + change password
│
└── docs/                      ← Full documentation
    ├── README.md
    ├── FRONTEND_ARCHITECTURE_AND_VIEWS_GUIDE.md  ← Frontend docs (new)
    ├── FRONTEND_INTEGRATION_GUIDE.md
    ├── BACKEND_ARCHITECTURE_AND_MODELS.md
    ├── CONTROLLERS_AND_MIDDLEWARES_GUIDE.md
    ├── SERVICES_AND_UTILS_GUIDE.md
    └── VIVA_AND_INTERVIEW_QUESTION_BANK.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.13+** — [python.org/downloads](https://www.python.org/downloads/)
- **MongoDB 6+** running locally on `mongodb://localhost:27017`  
  — [mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)
- **pip** package manager

### Installation

```bash
# 1. Clone or download the project
cd path/to/Mini-Project

# 2. (Optional but recommended) Create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

**`requirements.txt` contents:**
```
pymongo
bcrypt
```

### Running the Application

**Start the GUI (recommended):**
```bash
python gui.py
```

**Initialise the database manually (optional — `gui.py` does this automatically):**
```bash
python initialize_db.py
```

**Legacy CLI mode (terminal-based):**
```bash
python app.py
```

> ⚠️ Ensure MongoDB is running **before** starting the application.

---

## 🔑 Default Credentials

After first launch, a default administrator account is automatically seeded:

| Field | Value |
|-------|-------|
| **Username** | `admin` |
| **Email** | `admin@warehouse.com` |
| **Password** | `AdminPassword123!` |
| **Role** | `admin` |

> 🔐 Change the default password immediately after first login via **Settings → Change Password**.

---

## 🛡 Role-Based Access Control

MWIMS implements three user roles with different permission levels:

| Permission | 👑 Admin | 🧑 Staff | 🔍 Auditor |
|-----------|:--------:|:--------:|:----------:|
| Login | ✅ | ✅ | ✅ |
| View Dashboard | ✅ | ✅ | ✅ |
| View Medicines | ✅ | ✅ | ✅ |
| Add Medicine | ✅ | ✅ | ❌ |
| Edit Medicine | ✅ | ✅ | ❌ |
| **Delete Medicine** | ✅ | ❌ | ❌ |
| Adjust Stock | ✅ | ✅ | ❌ |
| Transfer Location | ✅ | ✅ | ❌ |
| View Alerts | ✅ | ✅ | ✅ |
| View Reports | ✅ | ✅ | ✅ |
| Export CSV | ✅ | ✅ | ✅ |
| **User Management** | ✅ | ❌ | ❌ |
| **Activity Logs** | ✅ | ❌ | ❌ |
| Change Own Password | ✅ | ✅ | ✅ |

> Role enforcement is **dual-layered**: the backend decorators (`@require_role`) reject unauthorised calls, and the frontend hides/disables buttons and menus for clarity.

---

## 🖥 Available Screens

| # | Screen | Access | Description |
|---|--------|--------|-------------|
| 1 | **Login** | All | Dark-themed login card with brand banner |
| 2 | **Dashboard** | All | Live metric cards + quick-action buttons |
| 3 | **Medicines** | All (write: Admin/Staff) | Full CRUD with treeview, search, Add/Edit dialog |
| 4 | **Inventory** | All (write: Admin/Staff) | Stock ±δ, transfer location, inventory table |
| 5 | **Warehouse** | All | Location overview, finder, medicine map |
| 6 | **Expiry Alerts** | All | Expired / Critical / Warning tabs |
| 7 | **Low Stock** | All | Out-of-stock / below-minimum tabs |
| 8 | **Reports** | All | Inventory/Expiry/Low-stock + CSV export |
| 9 | **User Management** | **Admin only** | Create, list, search, deactivate users |
| 10 | **Settings** | All | Profile card, change password, logout |

---

## 🏗 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     TKINTER GUI (views/)                │
│  LoginView  MainApp  MedicineView  InventoryView  …     │
└────────────────────┬────────────────────────────────────┘
                     │  calls only controllers
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   CONTROLLERS (controllers/)            │
│  auth_controller  medicine_controller  inventory_…  …  │
└────────────────────┬────────────────────────────────────┘
                     │
           ┌─────────┴──────────┐
           ▼                    ▼
┌──────────────────┐  ┌──────────────────────────────────┐
│  MIDDLEWARES     │  │  SERVICES (services/)            │
│  @require_auth   │  │  alert_service  inventory_svc … │
│  @require_role   │  └──────────────┬───────────────────┘
│  @handle_exc     │                 │
└──────────────────┘                 ▼
                          ┌──────────────────────┐
                          │  MODELS (models/)    │
                          │  user_model          │
                          │  medicine_model  …   │
                          └──────────┬───────────┘
                                     │
                                     ▼
                          ┌──────────────────────┐
                          │  MongoDB (PyMongo)   │
                          │  MWIMS database      │
                          └──────────────────────┘
```

### Key Design Principles

- **Views never touch MongoDB** — zero direct database calls in `views/`
- **Controllers are the only API** — all view→backend communication via controller functions
- **Standard response tuple** — every controller returns `(bool, str, data | None)`
- **Session in middleware** — `auth_middleware._current_user_session` holds login state
- **Role enforcement is dual** — backend decorator + frontend UI gating

---

## 📊 Data Flow

### Example: Adding a Medicine

```
User fills Add Medicine dialog
         │
         ▼
MedicineView._handle_save()          [views/medicine_view.py]
  → frontend validation (required fields, int check)
  → medicine_controller.add_medicine(...)
         │
         ▼
medicine_controller.add_medicine()   [controllers/medicine_controller.py]
  → @require_auth   checks session
  → @handle_exceptions wraps errors
  → validates category, type, date, batch uniqueness
  → medicine_model.create_medicine(payload)
  → report_model.log_activity(...)   (audit trail)
  → returns (True, "Medicine added.", doc)
         │
         ▼
MedicineView receives (True, msg, doc)
  → messagebox.showinfo("Success", msg)
  → _load_medicines()   ← refreshes Treeview table
```

---

## 📚 Documentation Index

All detailed documentation lives in the `docs/` folder:

| Document | Description |
|----------|-------------|
| [`docs/README.md`](docs/README.md) | Documentation hub overview |
| [`docs/FRONTEND_ARCHITECTURE_AND_VIEWS_GUIDE.md`](docs/FRONTEND_ARCHITECTURE_AND_VIEWS_GUIDE.md) | **Complete frontend code explanation** — theme system, view-by-view breakdown, widget patterns, integration details |
| [`docs/FRONTEND_INTEGRATION_GUIDE.md`](docs/FRONTEND_INTEGRATION_GUIDE.md) | Controller API reference for frontend integration |
| [`docs/BACKEND_ARCHITECTURE_AND_MODELS.md`](docs/BACKEND_ARCHITECTURE_AND_MODELS.md) | Backend MVC architecture and data models |
| [`docs/CONTROLLERS_AND_MIDDLEWARES_GUIDE.md`](docs/CONTROLLERS_AND_MIDDLEWARES_GUIDE.md) | All controllers and middleware decorators |
| [`docs/SERVICES_AND_UTILS_GUIDE.md`](docs/SERVICES_AND_UTILS_GUIDE.md) | Domain services and utility helpers |
| [`docs/VIVA_AND_INTERVIEW_QUESTION_BANK.md`](docs/VIVA_AND_INTERVIEW_QUESTION_BANK.md) | 25+ viva/interview Q&A bank |

---

## 🤝 Contributing

1. **Never modify backend files** (`controllers/`, `models/`, `services/`, `middlewares/`, `utils/`)  
   unless a minimal import change is strictly required for integration.
2. All GUI changes must live inside `views/`.
3. New screens must be registered in `views/main_app.py → _load_section()`.
4. All backend calls must go through controllers — no direct PyMongo in views.
5. Follow **PEP 8**, use **type hints**, and add **Google-style docstrings**.

---

*MWIMS — Built with ❤️ using Python & Tkinter*
