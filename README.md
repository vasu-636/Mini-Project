# 💊 Medicine Warehouse Inventory Management System (MWIMS)

A professional backend architecture built with **Python 3.13+**, **MongoDB**, **PyMongo**, and **bcrypt** for managing medicine warehouse inventory, stock alerts, locations, user RBAC, and report generation.

---

## 📌 Project Overview

The Medicine Warehouse Inventory Management System (MWIMS) automates warehouse operations with a secure, modular, and scalable software solution following the **MVC (Model-View-Controller)** architecture.

Key features provided by the backend:
- **Secure Authentication & RBAC**: Password hashing using `bcrypt`, session state context, and Role-Based Access Control (`admin` vs `staff`).
- **User Management**: User creation, email/username validation, account activation/deactivation, and security logging.
- **Medicine Management**: Full CRUD for medicine records, unique batch tracking, category & type constraints.
- **Warehouse Location Allocation**: Tracking physical stock allocation across Racks, Shelves, and Cabinets.
- **Inventory Tracking & Stock Movements**: Atomic stock adjustments, shortage calculations, and stock audits.
- **Real-Time Alert Engine**: Low stock alerts and expiry warning calculations ($N$ days before expiration).
- **Multi-Field Search**: Case-insensitive regex search across medicine names, batch numbers, categories, and locations.
- **Reporting & CSV Export**: Analytical summary reports, audit activity logs, and CSV data export.

---

## 🛠 Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.13+** | Primary Backend Language |
| **MongoDB** | NoSQL Database |
| **PyMongo (4.13.2)** | MongoDB Python Driver |
| **bcrypt (4.3.0)** | Password Hashing |

---

## 📁 Project Structure

```text
MWIMS/
│
├── app.py                    # Main terminal application entry point
├── config.py                 # MongoDB URI & application settings
├── database.py               # PyMongo connection & collection handles
├── initialize_db.py          # Database index creation & admin seeder
├── initialize_database.py    # Database setup wrapper
│
├── controllers/              # Business Orchestration Controllers
│   ├── auth_controller.py
│   ├── medicine_controller.py
│   ├── inventory_controller.py
│   ├── warehouse_controller.py
│   └── report_controller.py
│
├── models/                   # Pure Database Query Models (PyMongo)
│   ├── user_model.py
│   ├── medicine_model.py
│   ├── inventory_model.py
│   ├── warehouse_model.py
│   └── report_model.py
│
├── middlewares/              # Access Control & Exception Wrappers
│   ├── auth_middleware.py
│   ├── role_middleware.py
│   ├── validation_middleware.py
│   └── exception_handler.py
│
├── services/                 # Domain Services & Analytics
│   ├── alert_service.py
│   ├── inventory_service.py
│   ├── report_service.py
│   └── search_service.py
│
├── utils/                    # Reusable Utilities & Helpers
│   ├── constants.py
│   ├── logger.py
│   ├── validator.py
│   ├── helpers.py
│   ├── hash.py
│   └── csv_export.py
│
├── requirements.txt          # Python Package Dependencies
└── README.md                 # System Documentation
```

---

## 🚀 How to Run the Application in Terminal

### 1. Prerequisites
- Python 3.13+ installed
- MongoDB Community Server running locally at `mongodb://localhost:27017`

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Application via Terminal

To start the interactive terminal interface:

```bash
py -3 app.py
```

Or initialize the database directly:

```bash
py -3 initialize_db.py
```
