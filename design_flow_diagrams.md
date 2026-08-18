# 💊 MWIMS — Design Flow Diagrams & Gemini Prompt

This document provides complete, high-definition **Design Flow Diagrams** for the **Medicine Warehouse Inventory Management System (MWIMS)** using Mermaid.js syntax, as well as a ready-to-use **Gemini Prompt** for generating custom diagrams, visual representations, or documentation.

---

## 📐 1. System Architecture & Layered Flow

This flowchart illustrates the end-to-end multi-tier architecture, showing how user interactions flow down through Tkinter Views, Controller APIS, Middlewares, Domain Services, Data Models, and finally to MongoDB.

```mermaid
flowchart TD
    %% Styling
    classDef view fill:#161B22,stroke:#2F81F7,stroke-width:2px,color:#FFFFFF
    classDef ctrl fill:#1F2937,stroke:#3B82F6,stroke-width:2px,color:#FFFFFF
    classDef mid fill:#374151,stroke:#F59E0B,stroke-width:2px,color:#FFFFFF
    classDef svc fill:#111827,stroke:#10B981,stroke-width:2px,color:#FFFFFF
    classDef model fill:#1F2937,stroke:#EC4899,stroke-width:2px,color:#FFFFFF
    classDef db fill:#064E3B,stroke:#34D399,stroke-width:2px,color:#FFFFFF

    subgraph Presentation ["1. Presentation Layer (views/ & theme.py)"]
        UI_Login["Login & Register View"]:::view
        UI_Dash["Dashboard View"]:::view
        UI_Med["Medicine CRUD View"]:::view
        UI_Inv["Inventory & Stock View"]:::view
        UI_Wh["Warehouse Location View"]:::view
        UI_Alerts["Expiry & Low Stock Views"]:::view
        UI_Rep["Reports & Export View"]:::view
        UI_Users["User Management View (Admin)"]:::view
        UI_Set["Settings View"]:::view
    end

    subgraph Controllers ["2. Business Logic Layer (controllers/)"]
        AuthCtrl["auth_controller.py"]:::ctrl
        MedCtrl["medicine_controller.py"]:::ctrl
        InvCtrl["inventory_controller.py"]:::ctrl
        WhCtrl["warehouse_controller.py"]:::ctrl
        RepCtrl["report_controller.py"]:::ctrl
    end

    subgraph Middlewares ["3. Middleware & Security (middlewares/)"]
        ReqAuth["@require_auth Decorator"]:::mid
        ReqRole["@require_role Decorator"]:::mid
        ExcHand["@handle_exceptions Decorator"]:::mid
        SessMgr["Session Manager (_current_user)"]:::mid
    end

    subgraph Services ["4. Domain Services (services/)"]
        AlertSvc["alert_service.py"]:::svc
        InvSvc["inventory_service.py"]:::svc
        RepSvc["report_service.py"]:::svc
        SearchSvc["search_service.py"]:::svc
    end

    subgraph Models ["5. Data Access Layer (models/)"]
        UserModel["user_model.py"]:::model
        MedModel["medicine_model.py"]:::model
        InvModel["inventory_model.py"]:::model
        WhModel["warehouse_model.py"]:::model
        RepModel["report_model.py"]:::model
    end

    subgraph Database ["6. Storage Layer"]
        MongoDB[("MongoDB 6+\n(MWIMS Database)")]:::db
    end

    %% Connections
    Presentation -->|Calls Controller APIs| Controllers
    Controllers --> Middlewares
    Middlewares --> Services
    Services --> Models
    Controllers --> Models
    Models -->|PyMongo Drivers| MongoDB
```

---

## 🗺️ 2. UI Navigation & Screen Flow

This diagram outlines how users navigate between screens in MWIMS, starting from launch, through authentication, sidebar section switching, role-restricted views, and logout.

```mermaid
flowchart TD
    Start([Launch application: python gui.py]):::startStyle --> DBInit[Initialize DB & Seed Admin]
    DBInit --> LoginScreen[Login Screen / Self-Registration]

    classDef startStyle fill:#0F766E,stroke:#14B8A6,stroke-width:2px,color:#FFF
    classDef screen fill:#1E293B,stroke:#38BDF8,stroke-width:2px,color:#FFF
    classDef adminScreen fill:#701A75,stroke:#F472B6,stroke-width:2px,color:#FFF
    classDef decision fill:#854D0E,stroke:#FACC15,stroke-width:2px,color:#FFF

    LoginScreen --> SubmitCredentials{Authenticate Credentials?}:::decision
    SubmitCredentials -->|Failure| ShowError[Display Error Toast/Messagebox] --> LoginScreen
    SubmitCredentials -->|Success| MainShell[Main Application Shell]

    MainShell --> SideBar{Select Sidebar Tab}:::decision

    SideBar -->|Dashboard| DashView[Dashboard - Key Metrics & Quick Actions]:::screen
    SideBar -->|Medicines| MedView[Medicines - Treeview, Search, CRUD Dialogs]:::screen
    SideBar -->|Inventory| InvView[Inventory - Receive/Reduce Stock, Transfer]:::screen
    SideBar -->|Warehouse| WhView[Warehouse - Rack/Shelf Overview, Finder]:::screen
    SideBar -->|Expiry Alerts| ExpView[Expiry Alerts - Critical / Warning / Expired]:::screen
    SideBar -->|Low Stock| StockView[Low Stock Alerts - Deficit & Minimum Stock]:::screen
    SideBar -->|Reports| RepView[Reports - Summary Tables & CSV Export]:::screen
    SideBar -->|Settings| SetView[Settings - Profile Info & Password Change]:::screen
    
    SideBar -->|Admin Only| RoleCheck{Is Admin Role?}:::decision
    RoleCheck -->|Yes| UserMgmtView[User Management - List, Create, Deactivate]:::adminScreen
    RoleCheck -->|No| Hidden[Tab Hidden / Access Denied]

    SetView --> Logout([Click Logout]):::startStyle
    Logout --> ResetSession[Clear Session Token] --> LoginScreen
```

---

## 🔐 3. Authentication & Session Sequence Flow

Sequence diagram demonstrating user authentication, password hashing validation with bcrypt, session middleware binding, and role-based UI gating.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant View as LoginView (Tkinter)
    participant Ctrl as auth_controller
    participant Hash as hash.py (bcrypt)
    participant Mid as auth_middleware
    participant Model as user_model
    participant DB as MongoDB

    User->>View: Enters username & password
    User->>View: Clicks "Login"
    View->>Ctrl: login_user(username, password)
    Ctrl->>Model: get_user_by_username(username)
    Model->>DB: find_one({"username": username})
    DB-->>Model: User Document (contains hashed_password, role)
    Model-->>Ctrl: User dict

    Ctrl->>Hash: verify_password(raw_password, hashed_password)
    Hash-->>Ctrl: Password Match (True)

    Ctrl->>Mid: set_current_user(user_doc)
    Mid-->>Mid: Store active user in session memory

    Ctrl-->>View: (True, "Login successful", user_doc)
    View->>View: Destroy Login Window
    View->>User: Render MainApp Shell (Apply RBAC Gating)
```

---

## 📦 4. Medicine Inventory & Stock Movement Data Flow

Sequence diagram illustrating the end-to-end data flow when a warehouse operator receives or reduces medicine stock.

```mermaid
sequenceDiagram
    autonumber
    actor Staff as Staff / Admin
    participant UI as InventoryView
    participant Ctrl as inventory_controller
    participant Mid as @require_auth & @require_role
    participant Svc as inventory_service
    participant MedModel as medicine_model
    participant RepModel as report_model
    participant DB as MongoDB

    Staff->>UI: Selects Medicine & enters Stock Delta (+/-)
    Staff->>UI: Clicks "Adjust Stock"
    UI->>Ctrl: adjust_stock(medicine_id, quantity_delta, reason)
    
    Ctrl->>Mid: Execute Middleware Checks
    Mid->>Mid: Check active session & role permission
    Mid-->>Ctrl: Authorized

    Ctrl->>Svc: process_stock_adjustment(medicine_id, delta)
    Svc->>MedModel: get_medicine_by_id(medicine_id)
    MedModel->>DB: find_one({"_id": ObjectId})
    DB-->>MedModel: Medicine document
    MedModel-->>Svc: Current stock level

    Svc->>Svc: Validate target stock (Ensure quantity >= 0)
    Svc->>MedModel: update_stock_quantity(medicine_id, new_quantity)
    MedModel->>DB: update_one({"_id": ObjectId}, {"$set": {"quantity": new_val}})
    DB-->>MedModel: Success Acknowledgment

    Svc->>RepModel: log_activity(user_id, "STOCK_ADJUSTMENT", details)
    RepModel->>DB: insert_one(activity_log_doc)

    Svc-->>Ctrl: Updated Medicine Document
    Ctrl-->>UI: (True, "Stock updated successfully.", data)
    UI->>UI: Refresh Treeview Table & Update Summary Cards
    UI-->>Staff: Show Success Dialog
```

---

## 🚨 5. Alert System & CSV Export Flow

Flowchart showing how real-time expiry and low-stock alerts are generated and exported.

```mermaid
flowchart LR
    subgraph Trigger ["1. Trigger / Request"]
        A[User opens Expiry/Low-Stock Tab or Report Screen]
    end

    subgraph ServiceLayer ["2. Domain Processing (services/)"]
        B1[alert_service.get_expiry_alerts]
        B2[alert_service.get_low_stock_alerts]
        B3[report_service.generate_report]
    end

    subgraph DataFetch ["3. Database Queries"]
        C1["Query Expiry Date <= Threshold"]
        C2["Query Stock Quantity <= Minimum Reorder Level"]
        C3["Aggregate Inventory & Audit Logs"]
    end

    subgraph UI_Render ["4. Presentation"]
        D1[Categorize Into Expired / Critical / Warning Tabs]
        D2[Render Data in Tkinter Treeview]
    end

    subgraph Export ["5. CSV Export"]
        E1[User Clicks 'Export CSV']
        E2[Open file-save dialog asksaveasfilename]
        E3[Write formatted CSV file to disk]
    end

    A --> B1 & B2 & B3
    B1 --> C1
    B2 --> C2
    B3 --> C3
    C1 & C2 & C3 --> D1 --> D2
    D2 --> E1 --> E2 --> E3
```

---

## 🤖 6. Gemini Prompt (Ready to Copy-Paste)

If you need Gemini to generate **visual architecture diagrams**, **presentation slide outlines**, **UI design mockups**, or **technical documentation**, copy and paste the prompt below into Gemini:

```text
You are an expert Software Architect and UI/UX Designer specializing in Python desktop applications and MongoDB database architectures.

I need you to analyze and generate comprehensive design flows and architectural diagrams for MWIMS (Medicine Warehouse Inventory Management System), a desktop application built with Python 3.13+, Tkinter, PyMongo, and MongoDB.

### Project Context & Specifications:
1. Architecture Pattern: Clean MVC Architecture (Views -> Controllers -> Services/Middlewares -> Data Models -> MongoDB).
2. Key User Roles: Admin (Full Access + User Mgmt), Staff (Inventory CRUD & Adjustments), Auditor (Read-Only & CSV Export).
3. Primary Modules:
   - Presentation Layer: Tkinter Views (`login_view.py`, `main_app.py`, `medicine_view.py`, `inventory_view.py`, `warehouse_view.py`, `expiry_view.py`, `low_stock_view.py`, `reports_view.py`, `user_management_view.py`, `settings_view.py`) with a centralized design system in `theme.py`.
   - Business Controllers: `auth_controller`, `medicine_controller`, `inventory_controller`, `warehouse_controller`, `report_controller`.
   - Security & Decorators: `@require_auth`, `@require_role`, `@handle_exceptions`, bcrypt password hashing, session management in memory.
   - Domain Services: `alert_service` (Expiry & Low stock thresholds), `inventory_service` (Stock deltas & transfers), `report_service` (Data aggregation), `search_service` (Filtering & indexing).
   - Data Models: PyMongo wrappers over MongoDB collections (`users`, `medicines`, `inventory_logs`, `warehouses`, `activity_logs`).

### What I need you to generate:
1. Detailed Technical Breakdown: Explain the exact data flow for a multi-step inventory operation (e.g., Medicine Transfer between warehouse locations).
2. Mermaid Diagrams:
   - Component & Layer Architecture Diagram.
   - User Role Access Control Matrix Flowchart.
   - Sequence Diagram for Report Generation and CSV Export.
3. Recommendations for Improvement: Suggest 3-5 architectural enhancements (e.g., adding caching, asynchronous database calls, or audit log encryption) tailored specifically to Python Tkinter + MongoDB setups.

Please format the response cleanly with Markdown formatting, headings, code blocks, and Mermaid diagrams.
```
