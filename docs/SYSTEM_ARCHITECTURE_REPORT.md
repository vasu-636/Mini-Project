# 💊 System Architecture Report: MWIMS (Medicine Warehouse Inventory Management System)

> **Prepared for:** Professor & Project Evaluation  
> **Topic:** End-to-End System Architecture & Technical Design  
> **Language Style:** Simple, Clear, and Concept-Focused (With Real-World Analogies)

---

## 📌 1. Executive Summary & Project Overview

### What is MWIMS?
**MWIMS** stands for **Medicine Warehouse Inventory Management System**. It is a **desktop software application** designed for pharmaceutical warehouses to track medicine stocks, manage warehouse shelf locations, receive/dispatch items, trigger automatic low-stock and expiry warnings, and maintain security logs.

### Key Technology Stack
* **Programming Language:** Python 3.13+
* **User Interface (GUI):** Python `tkinter` (Native Desktop GUI) with a custom GitHub-inspired Dark Theme
* **Database:** MongoDB 6+ (NoSQL Document Database)
* **Database Driver:** `PyMongo` (Official high-performance Python driver)
* **Security & Hashing:** `bcrypt` (Industry-standard password hashing algorithm)

---

## 🏛️ 2. High-Level Architecture: The MVC Pattern

MWIMS is built using the **MVC (Model-View-Controller)** architecture, enhanced with **Middlewares** and **Domain Services**.

### 🍽️ Simple Analogy: The Restaurant Model
To explain this architecture to your professor, think of a **fine-dining restaurant**:

1. **View (The Dining Area / Menu):** What the customer sees. In our app, it's the Tkinter screens, buttons, and tables. It takes user orders (clicks) and displays the final meal (data).
2. **Controller (The Waiter):** Receives the customer's request from the View, checks with the security guard (Middleware), takes it to the chef, and brings back the response.
3. **Service (The Specialty Chef):** Handles complex calculations (e.g., calculating expiry alert warnings or stock deficits).
4. **Model (The Pantry Manager):** Knows exactly where food items are stored and directly accesses the database storage.
5. **MongoDB (The Pantry / Storage):** The raw storage room where all documents and records live.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        1. PRESENTATION LAYER                           │
│                     (views/ & view_components)                         │
│            Tkinter GUI Screens, Forms, Treeview Tables                 │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │  User actions (Clicks / Inputs)
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       2. BUSINESS LOGIC LAYER                          │
│                            (controllers/)                              │
│              Orchestrates workflows & validates rules                  │
└──────────────────┬──────────────────────────────────┬──────────────────┘
                   │                                  │
                   ▼                                  ▼
┌─────────────────────────────────────┐  ┌───────────────────────────────┐
│     3. SECURITY & MIDDLEWARE        │  │      4. DOMAIN SERVICES       │
│           (middlewares/)            │  │          (services/)          │
│ Authentication, RBAC, Error Handling│  │ Expiry logic, Low Stock alerts│
└──────────────────┬──────────────────┘  └──────────────┬────────────────┘
                   │                                    │
                   └──────────────────┬─────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        5. DATA ACCESS LAYER                            │
│                              (models/)                                 │
│                   PyMongo Queries & MongoDB CRUD                       │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │  BSON Document Queries
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                           6. DATABASE LAYER                            │
│                             (MongoDB 6+)                               │
│            Collections: users, medicines, activity_logs, reports       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 3. Layer-by-Layer Architectural Breakdown

### Layer 1: Presentation Layer (Views) — `views/` & `views/theme.py`
* **What it does:** Renders the desktop GUI windows, sidebars, dashboard cards, data tables (`Treeview`), forms, and pop-up dialogs.
* **Key Components:**
  * `gui.py`: Main app entry point that launches the window.
  * `theme.py`: Centralized **Design System** (defines dark colors, fonts, standard buttons, input fields, cards).
  * `main_app.py`: Sidebar navigation shell that switches between screens.
  * Screen Views: `login_view.py`, `medicine_view.py`, `inventory_view.py`, `warehouse_view.py`, `expiry_view.py`, `low_stock_view.py`, `reports_view.py`, `user_management_view.py`, `settings_view.py`.
* **Golden Rule:** **Views NEVER talk directly to MongoDB.** They only talk to Controllers.

### Layer 2: Business Logic Layer (Controllers) — `controllers/`
* **What it does:** Acts as the traffic controller. It accepts input from Views, runs security checks, calls business logic, triggers database models, and returns clean results back to the View.
* **Key Components:**
  * `auth_controller.py`: Login, self-registration, user creation, session cleanup.
  * `medicine_controller.py`: Medicine creation, updating details, deletion.
  * `inventory_controller.py`: Stock receiving (adding quantity), stock dispatching (reducing quantity), warehouse transfers.
  * `warehouse_controller.py`: Shelf/rack location overview & medicine search by warehouse location.
  * `report_controller.py`: Generating activity logs, stock reports, and CSV file exports.

### Layer 3: Security & Middleware Layer — `middlewares/`
* **What it does:** Acts as the security guard for the application before any sensitive operation runs.
* **Key Components:**
  * `auth_middleware.py` (`@require_auth`): Verifies if the user is currently logged in.
  * `role_middleware.py` (`@require_role`): Enforces **Role-Based Access Control (RBAC)**. Blocks regular `staff` from accessing `admin`-only screens like User Management.
  * `exception_handler.py` (`@handle_exceptions`): Catches any unexpected crashes or database failures, prevents the GUI from freezing, and returns a clean `(False, "Error message")` response to the user interface.

### Layer 4: Domain Services Layer — `services/`
* **What it does:** Houses heavy domain algorithms and logic so controllers remain clean and simple.
* **Key Components:**
  * `alert_service.py`: Computes medicine expiry dates (e.g., items expiring within 30 days) and low-stock deficits (`minimum_stock - current_quantity`).
  * `inventory_service.py`: Validates stock movements (prevents stock from going below 0).
  * `report_service.py`: Formats inventory summary metrics and builds CSV export tables.
  * `search_service.py`: Filters medicines dynamically by name, category, batch number, or rack location.

### Layer 5: Data Access Layer (Models) — `models/`
* **What it does:** Contains pure database queries. Reads and writes BSON documents to MongoDB using `PyMongo`.
* **Key Components:**
  * `user_model.py`: Queries for user lookup, account creation, password updating, deactivation.
  * `medicine_model.py`: CRUD operations for medicine documents.
  * `inventory_model.py`: Atomic stock quantity updates using `$inc` and location updates.
  * `warehouse_model.py`: Rack, shelf, and cabinet location map queries.
  * `report_model.py`: Activity log persistence and audit history.

### Layer 6: Storage Layer (Database) — MongoDB
* **What it does:** Local NoSQL database running on port `27017`.
* **Collections:**
  1. `users` — Account profiles, bcrypt password hashes, roles (`admin` / `staff`).
  2. `medicines` — Medicine details, batch number, expiry date, quantity, rack/shelf/cabinet location.
  3. `activity_logs` — Audit logs of who performed what action and when.
  4. `reports` — System report metadata.

---

## 🔄 4. End-to-End Data Flow Examples

### Scenario 1: User Logging Into the App
```
User enters Username & Password in Tkinter Login Screen
               │
               ▼
LoginView calls auth_controller.login_user(username, password)
               │
               ▼
auth_controller requests User Document from user_model
               │
               ▼
user_model queries MongoDB: users_collection.find_one({"username": ...})
               │
               ▼
auth_controller passes raw password & stored hash to hash.py (bcrypt verification)
               │
               ▼
If matched: Session Middleware stores active user info (_current_user)
               │
               ▼
LoginView is destroyed -> MainApp shell opens with sidebar customized for user's Role!
```

### Scenario 2: Warehouse Staff Receives / Dispatches Stock
```
Staff enters +50 units stock adjustment in InventoryView
               │
               ▼
InventoryView calls inventory_controller.adjust_stock(med_id, 50, reason)
               │
               ▼
Middlewares check: Is user logged in? (@require_auth) Does user have permission? (@require_role)
               │
               ▼
inventory_service validates: new quantity >= 0?
               │
               ▼
inventory_model executes MongoDB update: medicines_collection.update_one({"$inc": {"quantity": 50}})
               │
               ▼
report_model logs action in activity_logs: "Stock increased by 50 by Staff John"
               │
               ▼
Controller returns success tuple (True, "Stock updated successfully")
               │
               ▼
InventoryView updates UI cards & refreshes the table dynamically!
```

---

## 🗄️ 5. Database Schema & Data Models

Because MongoDB is a **NoSQL Document Database**, data is stored as JSON-like **BSON documents** rather than rigid SQL tables.

### 1. `users` Collection Schema
```json
{
  "_id": "ObjectId('65f1a2b3c4d5e6f7a8b9c0d1')",
  "username": "admin",
  "email": "admin@mwims.com",
  "password": "$2b$12$eImiTXuWVxfM37uY4JANjO5E.5R2G...",  // bcrypt hash
  "role": "admin",                                       // 'admin' or 'staff'
  "is_active": true,
  "created_at": "2026-08-18T10:00:00Z",
  "updated_at": "2026-08-18T10:00:00Z"
}
```

### 2. `medicines` Collection Schema
```json
{
  "_id": "ObjectId('65f1a2b3c4d5e6f7a8b9c0d2')",
  "medicine_name": "Paracetamol 500mg",
  "generic_name": "Acetaminophen",
  "category": "Analgesic",
  "type": "Tablet",
  "batch_number": "BATCH-2026-001",
  "manufacturer": "PharmaCorp",
  "quantity": 250,
  "minimum_stock": 50,
  "purchase_price": 12.50,
  "selling_price": 20.00,
  "expiry_date": "2027-12-31T00:00:00Z",
  "location": {
    "rack": "Rack-A",
    "shelf": "Shelf-02",
    "cabinet": "Cab-1"
  },
  "created_at": "2026-08-18T10:00:00Z"
}
```

---

## 💡 6. Key Design Justifications (Why We Chose This)

When your professor asks **"Why did you build it this way?"**, use these bullet points:

1. **Why MVC Architecture?**
   * **Separation of Concerns:** UI design, business logic, and database operations are completely independent.
   * **Maintainability:** If we change MongoDB to SQL in the future, we only rewrite the `models/` layer — the UI and controllers remain untouched.
   * **Testability:** Controllers and Services can be tested without opening the Tkinter window.

2. **Why MongoDB instead of MySQL/SQL?**
   * Medicines have dynamic metadata (varying batch details, storage conditions, rack/shelf/cabinet location objects).
   * Document format maps 1-to-1 with Python dictionaries.
   * Super fast read/write performance for inventory lookups.

3. **Why Native PyMongo over MongoEngine ORM?**
   * Avoids heavy ORM memory overhead.
   * Gives us direct control over raw atomic MongoDB operators like `$inc` (for race-condition-safe stock adjustments) and aggregation pipelines.

4. **Why `bcrypt` for Password Security?**
   * Simple MD5 or SHA-256 hashes are vulnerable to brute-force GPU rainbow table attacks.
   * `bcrypt` uses an adaptive **salt factor (12 rounds)**, making brute-force decryption computationally impossible.

5. **Why Custom Dark Theme in Tkinter?**
   * Default Tkinter looks dated. We created a modern design system (`views/theme.py`) with Github dark colors, custom rounded cards, and responsive widgets to give a professional enterprise desktop feel.

---

## 🎓 7. Professor Viva & Defense Cheat Sheet

| Question Expected from Professor | Simple & Exact Answer to Give |
| :--- | :--- |
| **"What is the architecture of your system?"** | *"Our project uses a multi-tier MVC architecture. Tkinter handles the View layer, Controllers process business logic, Middlewares enforce authentication and RBAC security, Services compute alerts/reports, and PyMongo Models manage database operations with MongoDB."* |
| **"How do you handle security & permissions?"** | *"Passwords are hashed with `bcrypt` (12 rounds). Session permissions are managed via custom Python decorators (`@require_auth` and `@require_role`). Non-admin users are blocked from administrative functions at both the UI tab level and controller level."* |
| **"What happens if two users update stock at the exact same time?"** | *"We use MongoDB's atomic operator `$inc` in `inventory_model.py`. This performs atomic addition/subtraction directly at the database level, preventing race conditions."* |
| **"How do expiry and low-stock alerts work?"** | *"The `alert_service.py` queries medicines where `expiry_date <= CURRENT_DATE + 30 days` or where `quantity <= minimum_stock`. It dynamically categorizes them into 'EXPIRED', 'CRITICAL', or 'WARNING' states."* |
| **"What prevents the GUI from crashing if MongoDB drops?"** | *"We use a global `@handle_exceptions` decorator wrapping controller functions. If a database error occurs, it catches the exception, logs it, and returns a friendly error message to the Tkinter interface."* |
| **"Where is the database connection established?"** | *"In `database.py`, using the Singleton Pattern. A single `pymongo.MongoClient` instance manages a thread-safe connection pool shared across all models."* |

---
*Report generated for MWIMS Project Presentation.*
