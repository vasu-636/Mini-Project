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

The project follows the **MVC (Model-View-Controller)** architecture and is being developed milestone by milestone using professional software development practices.

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

The project follows the **MVC (Model-View-Controller)** architecture to maintain clean code, modularity, and separation of responsibilities.

---

# ✅ Milestone 1 Progress

## ✔ Day 1 - Backend Foundation

### Completed

#### Configuration (`config.py`)

- MongoDB URI
- bcrypt Salt Rounds
- Project Configuration

---

#### Database (`database.py`)

Implemented:

- MongoDB Client
- Database Connection
- Connection Verification using `ping`
- Connection Timeout
- Database Initialization
- Collection Initialization

Collections:

- users
- medicines

---

#### Password Utility (`utils/hash.py`)

Implemented:

- Password Hashing
- Password Verification
- Input Validation
- bcrypt Integration
- Type Hints
- Google Style Docstrings

---

## ✔ Day 2 - User Management Foundation

### User Model (`models/user_model.py`)

Implemented:

- Create User
- Get User by Username
- Get User by Email
- Get User by ID
- Update User
- Delete User
- Username Exists
- Email Exists

Features:

- CRUD Operations
- MongoDB Queries using PyMongo
- ObjectId Handling
- Timestamp Management
- Exception Handling
- Type Hints
- Google Style Docstrings

---

### Database Initialization (`initialize_db.py`)

Implemented:

- Default Admin Creation
- Duplicate Admin Check
- Password Hashing
- MongoDB Insertion
- Safe Initialization

---

# 📚 Python Concepts Learned

- Project Structure
- MVC Architecture
- Modules & Packages
- Imports
- Type Hints
- Google Style Docstrings
- Exception Handling
- PyMongo CRUD Operations
- MongoDB ObjectId
- MongoDB Collections
- bcrypt Password Hashing
- Timestamp Management

---

# 🔐 Security Features

Implemented:

- bcrypt Password Hashing
- Password Verification
- Configurable Salt Rounds
- Default Admin Initialization
- Duplicate Username Prevention
- Duplicate Email Prevention

---

# 🚧 Upcoming Tasks (Day 3)

- Authentication Controller (`auth_controller.py`)
- Login Business Logic
- User Authentication
- Password Verification
- Login Validation

---

# 🎯 Long-Term Features

- User Authentication
- Role-Based Access Control
- Medicine CRUD
- Inventory Management
- Expiry Alerts
- Low Stock Alerts
- Search System
- Warehouse Location Management
- Report Generation
- Tkinter GUI
- Barcode/QR Code Support (Future)

---

# 📈 Development Status

| Module | Status |
|---------|--------|
| Project Planning | ✅ Completed |
| Folder Structure | ✅ Completed |
| Configuration | ✅ Completed |
| Database Connection | ✅ Completed |
| Password Hashing | ✅ Completed |
| User Model | ✅ Completed |
| Database Initialization | ✅ Completed |
| Authentication Controller | ⏳ Pending |
| Authentication View | ⏳ Pending |
| Medicine Model | ⏳ Pending |
| Medicine CRUD | ⏳ Pending |
| Inventory Management | ⏳ Pending |
| Tkinter GUI | ⏳ Pending |

---

# 👥 Team Workflow

### Branch Strategy

- `main` → Production branch
- `vasu-dev` → Vasu
- `hassan-dev` → Hassan
- `yash-dev` → Yash

### Git Workflow

1. Pull the latest changes from your branch.
2. Develop new features on your personal branch.
3. Commit with meaningful messages.
4. Push only to your personal branch.
5. Only the repository owner merges changes into `main`.

---

# 📅 Current Progress

**Current Milestone:** Milestone 1

**Completed:**

- ✅ Day 1
- ✅ Day 2

**Next Milestone:**

- Authentication Controller (Day 3)

---
