# MWIMS Master Viva & Technical Interview Question Bank

> **Medicine Warehouse Inventory Management System (MWIMS)**  
> **Exhaustive Defense Questions & Technically Accurate Sample Answers**

---

### Q1: Why did you create `config.py`?
**Answer:**  
We created `config.py` to centralize all application configuration parameters, database URI endpoints, security salt factors, and default seed credentials in a single file. This adheres to the **Single Responsibility Principle (SRP)** and prevents secret sprawl across business logic files.

---

### Q2: Why is `database.py` separate from `config.py` and models?
**Answer:**  
`database.py` separates connection management from configuration (`config.py`) and data operations (`models`). We implement a **Singleton Connection Pattern** where `pymongo.MongoClient` is instantiated once during module loading and shared across all models, preventing connection pool exhaustion.

---

### Q3: Why did you use `MongoClient` instead of connecting anew in every function?
**Answer:**  
`MongoClient` automatically manages an internal thread-safe **connection pool** to MongoDB. Establishing a new TCP socket on every function call introduces latency (~50-100ms) and quickly exhausts server connection limits. Reusing a single `MongoClient` instance exported from `database.py` maximizes throughput and resource efficiency.

---

### Q4: Why did you choose `bcrypt` for password hashing instead of MD5 or SHA-256?
**Answer:**  
MD5 and SHA-256 are fast hash functions designed for message integrity. Fast hashes are vulnerable to GPU rainbow-table attacks. `bcrypt` is an adaptive, slow hashing algorithm that incorporates a **salt** and a configurable **workload factor (salt rounds = 12)**, making brute-force attacks computationally infeasible.

---

### Q5: Why did you create `utils/hash.py`?
**Answer:**  
`utils/hash.py` abstracts lower-level bcrypt encoding/decoding and error handling behind clean, strongly-typed helper functions (`hash_password` and `verify_password`). It catches raw bcrypt exceptions and raises domain-specific exceptions (`PasswordHashError`, `PasswordVerificationError`).

---

### Q6: Why did you create `initialize_db.py`?
**Answer:**  
`initialize_db.py` acts as an automated database bootstrapping and migration script. It creates essential MongoDB B-tree indexes (unique constraints on `username`, `email`, and `batch_number`) and seeds the initial administrator account.

---

### Q7: Why did you create `models/user_model.py`?
**Answer:**  
`user_model.py` encapsulates all data persistence operations for the `users` collection. It abstracts raw PyMongo queries into clean Python functions, enforcing a strict **Separation of Concerns (SoC)**.

---

### Q8: Why did you use the MVC (Model-View-Controller) Architecture?
**Answer:**  
MVC decouples data management (Model), user interface (View), and business logic (Controller). This provides maintainability, testability without launching the Tkinter GUI, and reusability across different UI views.

---

### Q9: Why did you use PyMongo instead of an ORM/ODM like MongoEngine?
**Answer:**  
PyMongo is the official high-performance native Python driver for MongoDB. Native PyMongo avoids the heavy object-relational mapping overhead of MongoEngine and gives us direct control over raw MongoDB query operators (`$set`, `$inc`, `$expr`, `$or`, aggregation pipelines).

---

### Q10: Why did you choose MongoDB over a Relational Database (SQL)?
**Answer:**  
Medicine inventory items possess dynamic attributes (varying dosage forms, storage conditions, cabinet locations). MongoDB's flexible document format allows storing nested objects without complex SQL `JOIN` overhead, and BSON documents map naturally to Python dictionaries.

---

### Q11: Why are models strictly separated from controllers?
**Answer:**  
Models are responsible exclusively for persistence (CRUD operations). Controllers orchestrate application workflows—they check user session authentication (`@require_auth`), enforce role permissions (`@require_role`), validate business rules, invoke models, and log audit events.

---

### Q12: Why shouldn't password hashing be placed inside models?
**Answer:**  
Password hashing is a security business rule, not a database persistence task. Performing password hashing in `auth_controller.py` using `utils/hash.py` keeps models simple and focused on storing data.

---

### Q13: Why do controllers call models instead of views calling models directly?
**Answer:**  
Routing all data access through controllers guarantees that security middlewares validate every user operation, enforcing authentication, RBAC permissions, input validation, and audit logging.

---

### Q14: Why shouldn't Tkinter views communicate directly with MongoDB?
**Answer:**  
Direct database access from views tightly couples UI widgets to database schemas. A change in collection structure would break GUI event handlers, and it exposes raw database connection objects to front-end components.

---

### Q15: Why did you create reusable helper functions in `utils/helpers.py`?
**Answer:**  
Functions like `stringify_object_id()` and `sanitize_user_doc()` prevent code duplication. BSON `ObjectId` objects cannot be natively serialized or displayed in Tkinter widgets without string conversion, and `sanitize_user_doc()` guarantees password hashes are stripped before reaching the UI.

---

### Q16: Why did you use Python Type Hints (`str | ObjectId`, `dict[str, Any]`)?
**Answer:**  
Type hints enhance code clarity, enable static code analysis (e.g., `mypy`), prevent runtime type mismatches, and improve IDE autocompletion.

---

### Q17: Why did you use Google Style Docstrings across all functions?
**Answer:**  
Google Style docstrings provide standardized documentation detailing function purpose, argument types, return values, and raised exceptions.

---

### Q18: Why did you use central exception handling decorators (`@handle_exceptions`)?
**Answer:**  
Uncaught runtime exceptions in desktop Tkinter applications cause the GUI event loop to freeze. `@handle_exceptions` traps uncaught exceptions, logs the stack trace to the terminal, and returns a standardized error tuple `(False, "User friendly error message")` to display gracefully in UI message boxes.

---

### Q19: Why did you handle BSON `ObjectId` explicitly in models?
**Answer:**  
MongoDB uses 12-byte BSON `ObjectId` values for primary keys (`_id`), whereas front-end forms pass 24-character hexadecimal strings. Our helper `_to_object_id()` safely validates and converts string inputs into `ObjectId` instances, trapping `InvalidId` errors.

---

### Q20: Why did you create `username_exists()` and `email_exists()` helper functions?
**Answer:**  
These functions provide clean boolean wrappers around `get_user_by_username()` and `get_user_by_email()`, allowing `auth_controller.py` to perform explicit pre-validation checks before attempting database insertions.

---

### Q21: Why do you store `created_at` and `updated_at` timestamps in UTC?
**Answer:**  
Storing timestamps in Coordinated Universal Time (UTC) using `datetime.now(timezone.utc)` prevents time zone ambiguity and daylight saving issues across different server environments.

---

### Q22: Why do you seed a default administrator user in `initialize_db.py`?
**Answer:**  
On a fresh installation, the database contains zero user documents. Without a default administrator account, no user could ever log in to create subsequent staff accounts.

---

### Q23: How did you prevent duplicate admin creation during database seeding?
**Answer:**  
`seed_admin_user()` executes `users_collection.find_one({"role": "admin"})` before attempting an insertion. If an admin account already exists, it skips seeding and returns `True`.

---

### Q24: What is the purpose of `@require_auth` vs `@require_role(ROLE_ADMIN)`?
**Answer:**  
- `@require_auth` ensures that a user has an active logged-in session.
- `@require_role(ROLE_ADMIN)` verifies that the active session user possesses the `"admin"` role, blocking regular `"staff"` users from administrative actions.

---

### Q25: How does the alert service calculate stock shortages and expiry risk?
**Answer:**  
- **Low Stock**: Queries items where `$expr: {$lte: ["$quantity", "$minimum_stock"]}`. Computes `deficit = minimum_stock - quantity`. Assigns `"CRITICAL"` if quantity is 0, otherwise `"WARNING"`.
- **Expiry Risk**: Computes `cutoff_date = UTC_NOW + timedelta(days=30)` and queries `expiry_date <= cutoff_date`. Calculates `days_remaining`. Assigns `"EXPIRED"` if $\le 0$ days, `"CRITICAL"` if $\le 7$ days, and `"WARNING"` otherwise.
