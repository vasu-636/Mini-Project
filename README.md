# 💊 Medicine Warehouse Inventory Management System (MWIMS)

A professional desktop application built with **Python**, **MongoDB**, and **Tkinter** for managing medicine inventory in warehouses.

---

# 📌 Project Overview

The Medicine Warehouse Inventory Management System (MWIMS) is designed to automate warehouse operations by replacing manual inventory management with a secure and efficient software solution.

The system helps warehouse administrators to:

- Manage medicine inventory
- Track expiry dates
- Monitor stock levels
- Locate medicines quickly
- Generate reports
- Maintain secure user authentication

This project follows a professional **MVC (Model-View-Controller)** architecture and is being developed in milestones.

---

# 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.13+ | Backend Development |
| MongoDB | Database |
| PyMongo | MongoDB Driver |
| bcrypt | Password Hashing |
| Tkinter | Desktop GUI (Upcoming) |

---

# 📁 Project Structure

```text
MWIMS/
│
├── app.py
├── config.py
├── database.py
├── initialize_db.py
│
├── controllers/
│   ├── auth_controller.py
│   └── medicine_controller.py
│
├── models/
│   ├── user_model.py
│   └── medicine_model.py
│
├── views/
│   ├── auth_view.py
│   ├── menu_view.py
│   └── medicine_view.py
│
├── utils/
│   ├── hash.py
│   ├── validator.py
│   └── helpers.py
│
├── requirements.txt
└── README.md
```

---

# 🏗 Architecture

```text
                User
                  │
                  ▼
             View Layer
                  │
                  ▼
         Controller Layer
                  │
                  ▼
            Model Layer
                  │
                  ▼
           MongoDB Database
```

This project follows the **MVC (Model-View-Controller)** architecture to maintain clean code, scalability, and separation of responsibilities.

---

# ✅ Milestone 1 — Day 1 Progress

## Completed Tasks

### 1. Project Planning

- Defined the overall project architecture.
- Selected MVC design pattern.
- Planned folder structure for scalable development.

---

### 2. Configuration Module (`config.py`)

Implemented:

- MongoDB URI
- Security configurations
- bcrypt Salt Rounds

Example:

```python
MONGO_URI = "mongodb://localhost:27017/MWIMS"

SALT_ROUNDS = 12
```

---

### 3. Database Module (`database.py`)

Implemented:

- MongoDB Client
- Database Connection
- Connection Verification using `ping`
- Connection Timeout
- Collection Initialization

Collections:

- users
- medicines
- categories
- suppliers
- activity_logs

---

### 4. Password Utility (`utils/hash.py`)

Implemented:

- Password Hashing
- Password Verification
- bcrypt Integration
- Input Validation
- Custom Exceptions
- Type Hinting
- Google Style Documentation

---

### 5. Development Standards

Established coding standards for the entire project:

- MVC Architecture
- PEP 8 Naming Conventions
- Type Hinting
- Google Style Docstrings
- Custom Exceptions
- Single Responsibility Principle (SRP)
- Fail Fast Principle
- Clean Folder Organization

---

# 📚 Python Concepts Learned

- Modules
- Packages
- Imports
- Type Hints
- Custom Exceptions
- UTF-8 Encoding
- Password Hashing
- bcrypt
- MongoDB Connection using PyMongo
- Connection Timeout
- Database Ping
- Project Architecture (MVC)

---

# 🔐 Security Features

Implemented:

- bcrypt Password Hashing
- Configurable Salt Rounds
- Password Verification
- Input Validation

---

# 🚧 Upcoming Tasks (Day 2)

- Create `user_model.py`
- Create `medicine_model.py`
- Implement CRUD operations for users
- Database queries using PyMongo
- Create default admin account (`initialize_db.py`)

---

# 🎯 Long-Term Features

- User Authentication
- Role-Based Access Control
- Medicine CRUD
- Inventory Management
- Expiry Alerts
- Low Stock Alerts
- Search by Batch Number
- Search by Warehouse Location
- CSV Report Generation
- Dashboard
- Tkinter GUI
- Barcode/QR Code Integration (Future)

---

# 📈 Development Status

| Milestone | Status |
|-----------|--------|
| Project Planning | ✅ Completed |
| Folder Structure | ✅ Completed |
| Configuration | ✅ Completed |
| MongoDB Connection | ✅ Completed |
| Password Hashing | ✅ Completed |
| Models | ⏳ In Progress |
| Controllers | ⏳ Pending |
| Views | ⏳ Pending |
| Tkinter GUI | ⏳ Pending |

---