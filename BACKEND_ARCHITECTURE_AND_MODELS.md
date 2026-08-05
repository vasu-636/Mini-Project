# MWIMS Backend Architecture & Core Modules Documentation

> **Medicine Warehouse Inventory Management System (MWIMS)**  
> **Backend Architecture, Data Models, and Core Infrastructure Manual**

---

## 1. System Architecture Overview & MVC Flow

MWIMS follows a clean, decoupled **Model-View-Controller (MVC)** architectural pattern enhanced with an explicit **Service Layer** and functional **Middleware Infrastructure**:

```
+-------------------------------------------------------------+
|                  Tkinter Desktop UI Views                   |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                      Controllers Layer                      |
| (auth, medicine, inventory, report, warehouse controllers)  |
+-------------------------------------------------------------+
     |                         |                         |
     v                         v                         v
+------------------+  +------------------+  +------------------+
| Middleware Layer |  |  Service Layer   |  |   Model Layer    |
| (Auth, Role,     |  | (Alert, Search,  |  | (PyMongo CRUD    |
|  Exception)      |  |  Inventory, Rep) |  |  Operations)     |
+------------------+  +------------------+  +------------------+
                                                         |
                                                         v
                                            +--------------------------+
                                            | MongoDB Database (MWIMS) |
                                            +--------------------------+
```

- **Models (`models/`)**: Handle pure PyMongo database operations (CRUD, indexing, query execution). Models do not contain business logic or authentication rules.
- **Controllers (`controllers/`)**: Receive requests from Tkinter views, validate rules, check permissions via middlewares, invoke models/services, and log audit events.
- **Services (`services/`)**: Encapsulate domain logic (e.g., alert calculations, inventory valuation, fuzzy search, report aggregation).
- **Middlewares (`middlewares/`)**: Provide cross-cutting concerns: active session validation, Role-Based Access Control (RBAC), parameter validation, and global exception trapping.
- **Utils (`utils/`)**: Provide pure helper utilities (bcrypt hashing, regex validations, string formatting, constants).

---

## Module 1: `config.py`

### 1. Purpose & Responsibilities
Centralized configuration hub of the MWIMS backend application. Defines global system constants, environment connection strings, cryptographic parameters, and seed account credentials.

### 2. Exported Constants
- `MONGO_URI = "mongodb://localhost:27017/MWIMS"`
- `DB_NAME = "MWIMS"`
- `SALT_ROUNDS = 12`
- `DEFAULT_ADMIN_USERNAME = "admin"`
- `DEFAULT_ADMIN_EMAIL = "admin@warehouse.com"`
- `DEFAULT_ADMIN_PASSWORD = "AdminPassword123!"`

---

## Module 2: `database.py`

### 1. Purpose & Responsibilities
Manages the PyMongo client connection pool and exposes thread-safe references to all primary MongoDB collections (`users`, `medicines`, `activity_logs`, `reports`).

### 2. Exported Collections
- `users_collection = db["users"]`
- `medicines_collection = db["medicines"]`
- `activity_logs_collection = db["activity_logs"]`
- `reports_collection = db["reports"]`

---

## Module 3: `initialize_db.py`

### 1. Purpose & Responsibilities
Database bootstrapping and seed script. Builds required MongoDB unique/secondary B-tree indexes and seeds the default administrator user if no admin account exists.

### 2. Key Functions
- `setup_indexes()`: Builds unique indexes on `username`, `email`, `batch_number`, and secondary indexes on `medicine_name`, `expiry_date`, `category`, `timestamp`.
- `seed_admin_user()`: Idempotently creates default admin user if none exists.
- `initialize_database()`: Orchestrates setup sequence.

---

## Module 4: `models/user_model.py`

### 1. Purpose & Responsibilities
Data access layer for the `users` collection handling CRUD operations, ObjectId conversions, and existence checks.

### 2. Key Functions
- `create_user(user_data)`: Inserts user document with UTC `created_at` / `updated_at`.
- `get_user_by_username(username)`: Exact match lookup.
- `get_user_by_email(email)`: Case-insensitive email lookup.
- `get_user_by_id(user_id)`: Primary key ObjectId lookup.
- `get_all_users()`: Returns all user documents.
- `update_user(user_id, update_data)`: Atomic `$set` update.
- `delete_user(user_id)`: Atomic `delete_one`.
- `username_exists(username)` / `email_exists(email)`: Boolean existence checks.

---

## Module 5: `models/medicine_model.py`

### 1. Purpose & Responsibilities
Data access layer for managing medicine inventory records in the `medicines` collection.

### 2. Key Functions
- `create_medicine(medicine_data)`: Inserts medicine record with timestamps.
- `get_medicine_by_id(medicine_id)`: Fetches medicine by ObjectId.
- `get_medicine_by_batch(batch_number)`: Unique batch lookup.
- `get_all_medicines(query_filter)`: Fetches filtered list of medicine documents.
- `update_medicine(medicine_id, update_data)`: Updates medicine fields.
- `delete_medicine(medicine_id)`: Deletes medicine record.
- `batch_number_exists(batch_number)`: Checks batch number uniqueness.
- `get_medicines_by_location(rack, shelf, cabinet)`: Retrieves items matching exact location.
