# MWIMS Frontend Architecture & Views Guide

> **Medicine Warehouse Inventory Management System (MWIMS)**  
> Complete frontend code explanation for the Tkinter GUI layer.

---

## 📋 Table of Contents

1. [Frontend Overview](#1-frontend-overview)
2. [Directory Structure](#2-directory-structure)
3. [Design System — `theme.py`](#3-design-system--themepy)
   - [Colour Palette](#colour-palette)
   - [Typography](#typography)
   - [Spacing Tokens](#spacing-tokens)
   - [TTK Style Initializer](#ttk-style-initializer)
   - [Widget Factory Helpers](#widget-factory-helpers)
4. [GUI Entry Point — `gui.py`](#4-gui-entry-point--guipy)
5. [Login Screen — `login_view.py`](#5-login-screen--login_viewpy)
6. [Main Application Shell — `main_app.py`](#6-main-application-shell--main_apppy)
7. [Medicine View — `medicine_view.py`](#7-medicine-view--medicine_viewpy)
8. [Inventory View — `inventory_view.py`](#8-inventory-view--inventory_viewpy)
9. [Warehouse View — `warehouse_view.py`](#9-warehouse-view--warehouse_viewpy)
10. [Expiry Alert View — `expiry_view.py`](#10-expiry-alert-view--expiry_viewpy)
11. [Low Stock View — `low_stock_view.py`](#11-low-stock-view--low_stock_viewpy)
12. [Reports View — `reports_view.py`](#12-reports-view--reports_viewpy)
13. [User Management View — `user_management_view.py`](#13-user-management-view--user_management_viewpy)
14. [Settings View — `settings_view.py`](#14-settings-view--settings_viewpy)
15. [Navigation & Screen Loading Pattern](#15-navigation--screen-loading-pattern)
16. [Role-Based UI Gating](#16-role-based-ui-gating)
17. [Error Handling Conventions](#17-error-handling-conventions)
18. [Treeview Pattern](#18-treeview-pattern)
19. [Dialog Pattern](#19-dialog-pattern)
20. [Key Design Decisions](#20-key-design-decisions)

---

## 1. Frontend Overview

The MWIMS GUI is built **exclusively** with Python's standard `tkinter` library — no third-party GUI frameworks are used. It communicates with the backend **only through the controller layer**:

```
views/  →  controllers/  →  models/  →  MongoDB
```

**Strict rules enforced throughout the frontend:**
- ❌ No `pymongo` imports in any `views/` file
- ❌ No business logic (validation rules, calculations) reimplemented in views
- ❌ No direct access to `models/` or `services/` from views
- ✅ Every database interaction goes through a controller function
- ✅ Every controller returns `(bool, str, data | None)` — views consume this tuple

---

## 2. Directory Structure

```
views/
├── __init__.py                 ← Empty package marker
├── theme.py                    ← Design system (single source of truth)
├── login_view.py               ← Login screen Frame
├── main_app.py                 ← App shell: sidebar + content area + dashboard
├── medicine_view.py            ← Medicine CRUD screen
├── inventory_view.py           ← Stock adjustment + transfer
├── warehouse_view.py           ← Warehouse location management
├── expiry_view.py              ← Expiry alert screen
├── low_stock_view.py           ← Low stock alert screen
├── reports_view.py             ← Reports + CSV export
├── user_management_view.py     ← User management (Admin only)
└── settings_view.py            ← Profile + change password
```

And at the project root:

```
gui.py                          ← Application entry point (run this)
```

---

## 3. Design System — `theme.py`

**File:** `views/theme.py`  
**Purpose:** Single source of truth for all visual design tokens. Every colour, font, padding value, and reusable widget factory is defined here. No view file hardcodes colour strings or font tuples directly.

### Colour Palette

```python
# Background shades (darkest → lightest)
BG_DARK    = "#0D1117"   # root window background (GitHub dark)
BG_PANEL   = "#161B22"   # sidebar and header panels
BG_CARD    = "#1C2333"   # card and dialog interiors
BG_CARD_ALT= "#21262D"   # alternate rows / hover states

# Brand accent
ACCENT       = "#2F81F7"   # primary interactive colour (GitHub blue)
ACCENT_HOVER = "#388AFF"
ACCENT_DARK  = "#1F6FEB"

# Semantic colours
SUCCESS = "#3FB950"        # green  — positive actions
WARNING = "#D29922"        # amber  — caution states
DANGER  = "#F85149"        # red    — errors / destructive actions
INFO    = "#58A6FF"        # light blue — informational

# Text hierarchy
TEXT_PRIMARY   = "#E6EDF3" # main readable text
TEXT_SECONDARY = "#8B949E" # labels, captions, placeholder text
TEXT_DIM       = "#484F58" # muted, disabled, decorative text
TEXT_ACCENT    = "#2F81F7" # clickable / highlighted text

# Treeview row colours
TREE_BG     = "#161B22"
TREE_ODD    = "#1C2333"    # slightly lighter odd rows
TREE_EVEN   = "#161B22"    # standard even rows
TREE_SELECT = "#264F78"    # selected row highlight
TREE_HEADING= "#0D1117"    # column heading row

# Input field colours
INPUT_BG     = "#0D1117"
INPUT_BORDER = "#30363D"
INPUT_FOCUS  = "#2F81F7"   # highlight colour on focus

BORDER = "#30363D"         # separator / divider lines
```

### Typography

```python
FONT_FAMILY   = "Segoe UI"         # system font (Windows native)

FONT_TITLE    = (FONT_FAMILY, 20, "bold")   # screen headings
FONT_SUBTITLE = (FONT_FAMILY, 13, "bold")   # section headings
FONT_HEADING  = (FONT_FAMILY, 11, "bold")   # card headings, button text
FONT_BODY     = (FONT_FAMILY, 10)           # standard body text
FONT_SMALL    = (FONT_FAMILY, 9)            # metadata, secondary labels
FONT_MONO     = ("Consolas", 9)             # IDs, batch numbers
FONT_CAPTION  = (FONT_FAMILY, 8)            # form field labels, hints
```

### Spacing Tokens

```python
PAD_XS = 4    # micro gaps (between icon and text)
PAD_SM = 8    # small padding (button inner padding)
PAD_MD = 14   # medium padding (card inner padding)
PAD_LG = 20   # large padding (screen section spacing)
PAD_XL = 30   # extra-large (page edge margins)
```

### TTK Style Initializer

`apply_theme(root: tk.Tk)` is called **once** in `gui.py` on the root Tk window. It uses `ttk.Style` to configure named styles for:

| Style Name | Applied To | Description |
|-----------|-----------|-------------|
| `TFrame`, `Card.TFrame`, `Panel.TFrame` | `ttk.Frame` | Background variants |
| `TLabel`, `Card.TLabel`, `Dim.TLabel`, `Success.TLabel` | `ttk.Label` | Colour-coded text |
| `Primary.TButton` | `ttk.Button` | Blue accent button |
| `Danger.TButton` | `ttk.Button` | Red destructive button |
| `Ghost.TButton` | `ttk.Button` | Muted secondary button |
| `Success.TButton` | `ttk.Button` | Green confirm button |
| `Sidebar.TButton` / `SidebarActive.TButton` | `ttk.Button` | Navigation items |
| `TEntry` | `ttk.Entry` | Dark input field |
| `TCombobox` | `ttk.Combobox` | Dark dropdown |
| `Treeview` / `Treeview.Heading` | `ttk.Treeview` | Dark table + headers |
| `TNotebook` / `TNotebook.Tab` | `ttk.Notebook` | Dark tabbed panels |
| `TScrollbar` | `ttk.Scrollbar` | Minimal dark scrollbar |

> **Why TTK styles?** They allow a single `style.configure()` call at startup to skin every widget of that type application-wide. This avoids repetitive `bg=`, `fg=`, `font=` arguments on every widget construction.

> **Why plain `tk.Button` for many buttons?** `ttk.Button` does not allow mixing `bg`/`fg` reliably on Windows's default renderer. Plain `tk.Button` is used where pixel-perfect colour control is needed (e.g., the coloured action buttons in the toolbar). `ttk.Button` is used where the ttk style system suffices.

### Widget Factory Helpers

| Helper | Returns | Purpose |
|--------|---------|---------|
| `make_label(parent, text, style)` | `ttk.Label` | Styled label in one call |
| `make_entry(parent, textvariable, show, width)` | `ttk.Entry` | Styled entry field |
| `make_button(parent, text, command, style)` | `ttk.Button` | Styled button |
| `make_combobox(parent, values, textvariable)` | `ttk.Combobox` | Styled dropdown |
| `make_scrolled_tree(parent, columns, headings, col_widths)` | `(Treeview, VScroll, HScroll)` | Full table with both scrollbars |
| `populate_tree(tree, rows)` | `None` | Clear + re-insert rows with alternating tags |
| `separator(parent)` | `ttk.Separator` | Horizontal divider rule |
| `card_frame(parent)` | `ttk.Frame` | BG_CARD styled container frame |

**`make_scrolled_tree` detail:**  
This is the most important factory. It creates a `ttk.Treeview` with a vertical scrollbar on the right and a horizontal scrollbar on the bottom, wired together correctly:

```python
tree, v_scroll, h_scroll = make_scrolled_tree(
    parent,
    columns=("id", "name", "qty"),
    headings=("ID", "Medicine Name", "Qty"),
    col_widths=(80, 200, 60),
    height=14,
)
```

It also pre-configures four row tags used by all views:
- `"oddrow"` → `TREE_ODD` background
- `"evenrow"` → `TREE_EVEN` background
- `"danger"` → dark red background + `DANGER` text
- `"warning"` → dark amber background + `WARNING` text
- `"success"` → dark green background + `SUCCESS` text

---

## 4. GUI Entry Point — `gui.py`

**File:** `gui.py` (project root)  
**Run with:** `python gui.py`

### Responsibilities

1. Create the `tk.Tk()` root window
2. Set window title, geometry, minimum size, and centre on screen
3. Call `apply_theme(root)` — applies global TTK styles
4. Call `initialize_database()` — creates MongoDB indexes and seeds admin user
5. Show `LoginView`
6. On successful login → swap to `MainApp`
7. On logout → swap back to `LoginView`
8. Handle `WM_DELETE_WINDOW` with a confirmation dialog

### Class: `MWIMSApplication`

```python
class MWIMSApplication:
    APP_TITLE = "MWIMS – Medicine Warehouse Inventory Management System"
    WINDOW_W  = 1280
    WINDOW_H  = 780
    MIN_W     = 1100
    MIN_H     = 680
```

**View transition mechanism:**

```python
def _show_login(self) -> None:
    self._clear_view()                          # destroy old Frame
    self._current_view = LoginView(
        master=self._root,
        on_success=self._on_login_success,      # callback
    )

def _on_login_success(self, user: dict) -> None:
    self._clear_view()
    self._current_view = MainApp(
        master=self._root,
        user=user,
        on_logout=self._show_login,             # callback
    )
```

Transitions are achieved by **destroying** the old Frame and **creating** a new one. No frame stacking or `tkraise()` is needed because only one top-level view is alive at a time.

### Integration with Backend

```python
from initialize_db import initialize_database   # backend — DB init
from views.login_view import LoginView          # frontend
from views.main_app import MainApp              # frontend
```

Only `initialize_database()` is called from the backend directly. All subsequent interactions happen through controllers inside the views.

---

## 5. Login Screen — `login_view.py`

**Class:** `LoginView(tk.Frame)`  
**Shown:** Before authentication  
**Backend calls:** `auth_controller.login_user(identifier, password)`

### Layout

```
┌────────────────────────────────────┐
│  ▌▌▌  5px ACCENT top banner       │
│                                    │
│  💊 MWIMS    Medicine Warehouse    │  ← brand row
│  ────────────────────────────────  │
│  Sign in to your account           │
│                                    │
│  Username or Email                 │
│  [____________________________]    │
│                                    │
│  Password                          │
│  [••••••••••••••••••••••••••••]   │
│                                    │
│  [error status message here]       │
│                                    │
│  [      🔐  Sign In          ]     │  ← full-width blue button
│          Exit Application          │  ← ghost text button
└────────────────────────────────────┘
MWIMS · v1.0 · Medicine Warehouse ...   ← footer
```

### Key Implementation Details

**Centred card using `place()`:**
```python
container = tk.Frame(self, bg=BG_DARK)
container.place(relx=0.5, rely=0.5, anchor="center")
```
Using `place` with relative coordinates ensures the card is always visually centred regardless of window size.

**Dark Entry widget (plain `tk.Entry`):**
```python
entry = tk.Entry(
    parent,
    bg=INPUT_BG, fg=TEXT_PRIMARY,
    insertbackground=TEXT_PRIMARY,    # cursor colour
    highlightthickness=1,
    highlightbackground=BORDER,
    highlightcolor=ACCENT,            # blue border on focus
    relief="flat",
)
```
TTK Entry has limited colour control on Windows; plain `tk.Entry` with `highlightcolor` is used for the focus ring effect.

**Enter key binding:**
```python
self.master.bind("<Return>", lambda _: self._handle_login())
```
Bound on the master `Tk` window so it fires regardless of which widget has focus.

**Login flow:**
```python
def _handle_login(self) -> None:
    # 1. Frontend: empty-field guard
    if not identifier: self._set_status("Username or Email is required."); return
    if not password:   self._set_status("Password is required."); return

    # 2. Call controller
    success, msg, user = auth_controller.login_user(identifier, password)

    # 3. Handle response tuple
    if success and user:
        self._set_status("Login successful!", colour=SUCCESS)
        self.after(300, lambda: self.on_success(user))   # brief delay for UX
    else:
        self._set_status(msg or "Login failed.")
        self._entry_password.delete(0, "end")
```

**Status feedback with colour:**
```python
def _set_status(self, msg: str, colour: str = DANGER) -> None:
    self._lbl_status.configure(fg=colour)
    self._var_status.set(msg)
```
The same label is reused for both error (red) and success (green) feedback.

---

## 6. Main Application Shell — `main_app.py`

**Class:** `MainApp(tk.Frame)`  
**Shown:** After login, wraps all authenticated screens  
**Backend calls:** `inventory_controller.get_inventory_dashboard_metrics()`, `auth_controller.logout_user()`

### Layout

```
┌─────────────────────────────────────────────────────────┐
│  💊 MWIMS                        👤 admin  [ADMIN]      │  ← 48px header
├─────────────────────────────────────────────────────────┤
│          │                                              │
│ NAVIGATION│           Content Area                      │
│           │     (current screen Frame packed here)      │
│  🏠 Dashboard                                           │
│  💊 Medicines                                           │
│  📦 Inventory                                          │
│  🏭 Warehouse                                          │
│  ⏰ Expiry Alerts                                       │
│  ⚠️  Low Stock                                          │
│  📊 Reports                                             │
│  👥 User Mgmt  ← Admin only                            │
│                                                         │
│  ─────────────                                         │
│  ⚙️  Settings                                           │
│  🚪 Logout                          215px │            │
└─────────────────────────────────────────────────────────┘
```

### Inner Classes

**`_NavButton(tk.Frame)`**  
A custom sidebar navigation item that wraps a `tk.Button` and a 3px wide left `tk.Frame` indicator strip. On `set_active(True)` the indicator turns `ACCENT` blue and the text turns blue + bold. Hover effects change background on `<Enter>` / `<Leave>` events.

```python
class _NavButton(tk.Frame):
    def set_active(self, active: bool) -> None:
        if active:
            self._btn.configure(bg=BG_CARD, fg=ACCENT,
                                font=(FONT_FAMILY, 10, "bold"))
            self._indicator.configure(bg=ACCENT)   # left blue strip
        else:
            self._btn.configure(bg=BG_PANEL, fg=TEXT_SECONDARY, font=FONT_BODY)
            self._indicator.configure(bg=BG_PANEL)
```

**`_StatCard(tk.Frame)`**  
A compact metric display card for the dashboard:

```python
_StatCard(parent, icon="📦", title="Total Medicines", value="42", accent=ACCENT)
```
Shows icon → value (large, bold, coloured) → title (small, muted).

### Navigation Dispatcher

`show_section(key: str)` is the central routing method:

```python
def show_section(self, key: str) -> None:
    # Deactivate old nav button, activate new one
    if self._active_key in self._nav_buttons:
        self._nav_buttons[self._active_key].set_active(False)
    self._nav_buttons[key].set_active(True)
    self._active_key = key

    # Destroy old content frame
    if self._content_frame:
        self._content_frame.destroy()

    # Load new screen
    self._content_frame = self._load_section(key)
    self._content_frame.pack(fill="both", expand=True)
```

`_load_section(key)` uses **lazy imports** to avoid circular imports and keep startup fast:

```python
def _load_section(self, key: str) -> Optional[tk.Frame]:
    if key == "medicines":
        from views.medicine_view import MedicineView     # imported on demand
        return MedicineView(self._content_area, self.user)
    # ...
```

### Role-Based Menu Filtering

The sidebar nav items table includes a `required_role` column:

```python
nav_items = [
    ("dashboard", "🏠", "Dashboard",       None),         # all roles
    ("medicines", "💊", "Medicines",        None),         # all roles
    ("users",     "👥", "User Management",  ROLE_ADMIN),   # Admin only
]

for key, icon, label, required_role in nav_items:
    if required_role and self.role != required_role:
        continue   # skip — don't create the button at all
```

### Dashboard Screen

The dashboard is built **inline** inside `_build_dashboard()` — it does not have its own file because it is tightly coupled to the shell (navigation to other sections, access to `self.user`).

Dashboard metric cards are populated by:
```python
ok, _msg, metrics = inventory_controller.get_inventory_dashboard_metrics()
```

Metric keys used: `total_unique_medicines`, `total_stock_quantity`, `low_stock_count`, `expiring_soon_count`.

---

## 7. Medicine View — `medicine_view.py`

**Class:** `MedicineView(tk.Frame)`  
**Backend calls:**  
- `medicine_controller.get_all_medicines()`  
- `medicine_controller.get_medicine_by_id(id)`  
- `medicine_controller.add_medicine(...)`  
- `medicine_controller.update_medicine(id, fields)`  
- `medicine_controller.delete_medicine(id)`

### Layout

```
┌─────────────────────────────────────────────────────────┐
│  💊 Medicine Management                                 │
│  🔍 [search box]  🔄 Refresh  ➕ Add  ✏️ Edit  🗑️ Delete│  ← toolbar
│  Showing X of Y medicine(s).                            │  ← status
│                                                         │
│  ┌──────────┬────────────────┬───────┬──────┬──────┐   │
│  │ ID       │ Medicine Name  │ Batch │ Qty  │ ...  │   │  ← Treeview
│  ├──────────┼────────────────┼───────┼──────┼──────┤   │
│  │ abc123…  │ Paracetamol   │ B001  │  50  │ ...  │   │
│  │ def456…  │ Amoxicillin   │ B002  │  12  │ ...  │   │
│  └──────────┴────────────────┴───────┴──────┴──────┘   │
└─────────────────────────────────────────────────────────┘
```

### Treeview Columns

| Column | Key | Width |
|--------|-----|-------|
| ID (short) | `id` | 90 |
| Medicine Name | `name` | 180 |
| Batch # | `batch` | 110 |
| Category | `category` | 130 |
| Type | `type` | 90 |
| Qty | `qty` | 60 |
| Min Stock | `min_stock` | 80 |
| Expiry Date | `expiry` | 100 |
| Rack | `rack` | 60 |
| Shelf | `shelf` | 60 |
| Cabinet | `cabinet` | 70 |

IDs are displayed as `first8chars…` for readability.

### Live Search

`StringVar.trace_add("write", callback)` fires `_apply_search()` on every keystroke:

```python
self._var_search = tk.StringVar()
self._var_search.trace_add("write", lambda *_: self._apply_search())

def _apply_search(self) -> None:
    keyword = self._var_search.get().strip().lower()
    filtered = [
        m for m in self._all_medicines
        if keyword in m.get("medicine_name", "").lower()
        or keyword in m.get("batch_number", "").lower()
        or keyword in m.get("category", "").lower()
        or keyword in m.get("type", "").lower()
    ]
    populate_tree(self._tree, [self._med_to_row(m) for m in filtered])
```

No round-trip to the backend — filtering is done on the locally cached `_all_medicines` list.

### Add/Edit Dialog — `_MedicineDialog(tk.Toplevel)`

A modal `Toplevel` dialog that is reused for both **Add** (medicine=`None`) and **Edit** (medicine=existing dict) modes.

**Field layout (2-column grid):**

```
┌──────────────────────┬──────────────────────┐
│ Medicine Name        │ Batch Number          │
│ [________________]   │ [________________]    │
│ Category             │ Type                  │
│ [Combobox ▾]         │ [Combobox ▾]          │
│ Quantity             │ Minimum Stock         │
│ [____]               │ [____]                │
│ Expiry Date(YYYY-MM) │ Rack                  │
│ [________________]   │ [________________]    │
│ Shelf                │ Cabinet               │
│ [________________]   │ [________________]    │
│ [validation msg]                             │
│ [💾 Save]  [Cancel]                          │
└─────────────────────────────────────────────┘
```

**Populate existing data (edit mode):**
```python
def _populate_existing(self) -> None:
    for key, var in self._vars.items():
        val = self.medicine.get(key, "")
        if hasattr(val, "strftime"):         # datetime → string
            val = val.strftime("%Y-%m-%d")
        var.set(str(val) if val is not None else "")
```

**Save logic:**
- Collect all `StringVar` values
- Run frontend validation (empty fields, integer check)
- If edit mode → call `medicine_controller.update_medicine(id, payload)`
- If add mode → call `medicine_controller.add_medicine(...)`
- On success → `messagebox.showinfo` + call `on_saved(True)` callback → parent refreshes table
- On failure → display backend error message in status label

### Role Gating in Toolbar

```python
if self.role in (ROLE_ADMIN, ROLE_STAFF):
    # show Add + Edit buttons
if self.role == ROLE_ADMIN:
    # show Delete button
```

---

## 8. Inventory View — `inventory_view.py`

**Class:** `InventoryView(tk.Frame)`  
**Backend calls:**  
- `medicine_controller.get_all_medicines()`  
- `inventory_controller.adjust_stock(id, delta)`  
- `warehouse_controller.transfer_medicine_location(id, rack, shelf, cabinet)`

### Three Tabs

#### Tab 1 — Stock Adjustment

Contains a `ttk.Combobox` to select a medicine (displayed as `"Name [Batch]"`) and a delta entry:

- **Receive Stock** button → calls `adjust_stock(id, +abs(delta))`
- **Reduce Stock** button → calls `adjust_stock(id, -abs(delta))`

Both use the same backend function; only the sign of `delta` differs. The view makes the UX explicit with two separate buttons.

```python
def _adjust_stock(self, positive: bool) -> None:
    delta = abs(int(self._var_delta.get()))
    if not positive:
        delta = -delta
    ok, msg, _ = inventory_controller.adjust_stock(str(med["_id"]), delta)
```

Status feedback colour changes dynamically:
```python
if ok:
    self._lbl_stock_status.configure(fg=SUCCESS)
else:
    self._lbl_stock_status.configure(fg=DANGER)
self._var_stock_status.set(msg)
```

#### Tab 2 — Transfer Location

Lets the user select a medicine and enter new Rack / Shelf / Cabinet values, then calls:
```python
warehouse_controller.transfer_medicine_location(id, new_rack, new_shelf, new_cabinet)
```

#### Tab 3 — Inventory Table

A read-only Treeview showing all medicines with key inventory fields. Refreshed alongside the combobox list every time `_load_medicines()` is called.

---

## 9. Warehouse View — `warehouse_view.py`

**Class:** `WarehouseView(tk.Frame)`  
**Backend calls:**  
- `medicine_controller.get_all_medicines()`  
- `warehouse_controller.get_warehouse_locations()`  
- `warehouse_controller.get_location_summary()`

### Three Tabs

#### Tab 1 — Location Overview

Shows three `tk.LabelFrame` columns — **Racks**, **Shelves**, **Cabinets** — populated with coloured labels listing each distinct identifier in use:

```python
for item in locations.get("racks", []):
    tk.Label(lf_racks, text=f"  {item}", fg=ACCENT).pack(anchor="w")
```

Below this, a Treeview shows the location summary aggregate (medicine count + total stock per rack/shelf/cabinet combination).

#### Tab 2 — Location Finder

Three compact entry fields (Rack, Shelf, Cabinet) with a **Find** button that filters `self._medicines` in memory (no backend round-trip):

```python
filtered = [
    m for m in self._medicines
    if (not rack    or m.get("rack","").upper()    == rack)
    and (not shelf  or m.get("shelf","").upper()   == shelf)
    and (not cabinet or m.get("cabinet","").upper() == cabinet)
]
```

Empty fields act as wildcards — entering only `rack="R1"` finds all medicines in R1 regardless of shelf or cabinet.

#### Tab 3 — Medicine Map

Full Treeview listing all medicines with location columns: Name, Batch, Rack, Shelf, Cabinet, Qty, Category.

---

## 10. Expiry Alert View — `expiry_view.py`

**Class:** `ExpiryView(tk.Frame)`  
**Backend calls:** `inventory_controller.get_expiry_alerts(warning_days)`

### Configurable Warning Window

A `ttk.Spinbox` lets the user change the warning window (default 30 days, range 7–180). An **Apply** button re-fetches from the backend with the new value:

```python
ok, _msg, alerts = inventory_controller.get_expiry_alerts(warning_days=days)
```

### Four Tabs

| Tab | Filter | Row Count Source |
|-----|--------|-----------------|
| 💀 Expired | `expiry_status == "EXPIRED"` | `expired` list |
| 🔴 Critical | `expiry_status == "CRITICAL"` | `critical` list |
| 🟡 Warning | `expiry_status == "WARNING"` | `warning` list |
| 📋 All Alerts | All | full `alerts` list |

### Badge Row

Coloured summary pills are rebuilt on every load:

```python
for label, count, colour in [
    (f"💀  Expired: {len(expired)}",   DANGER),
    (f"🔴  Critical: {len(critical)}", "#FF6B35"),
    (f"🟡  Warning: {len(warning)}",   WARNING),
    (f"📋  Total: {len(alerts)}",      ACCENT),
]:
    tk.Label(..., bg=colour, text=label).pack(side="left")
```

### Coloured All-Tab Rows

The All-tab tree manually inserts rows with semantic tags instead of using `populate_tree`:

```python
for a in alerts:
    tag = "danger" if status == "EXPIRED" else "warning" if status == "CRITICAL" else "oddrow"
    self._tree_all.insert("", "end", values=self._row(a), tags=(tag,))
```

---

## 11. Low Stock View — `low_stock_view.py`

**Class:** `LowStockView(tk.Frame)`  
**Backend calls:** `inventory_controller.get_low_stock_alerts()`

Very similar structure to `ExpiryView`. Splits the alert list into:

- **CRITICAL** — `quantity == 0` (completely out of stock)
- **WARNING** — `quantity > 0` but below `minimum_stock`

Additional computed column `deficit` = `minimum_stock - quantity` shows how many units need to be ordered.

---

## 12. Reports View — `reports_view.py`

**Class:** `ReportsView(tk.Frame)`  
**Backend calls:**  
- `report_controller.generate_inventory_report()`  
- `inventory_controller.get_expiry_alerts(warning_days=90)`  
- `inventory_controller.get_low_stock_alerts()`  
- `report_controller.get_activity_logs(limit=200)` ← Admin only

### Summary Cards (Inventory Tab)

The inventory tab shows four stat cards above the table, populated from `report_data["summary"]`:

```
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│    45    │ │  3200    │ │    3     │ │    5     │
│  Total   │ │  Total   │ │  Low     │ │ Expiring │
│Medicines │ │  Stock   │ │  Stock   │ │  Soon    │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
```

### CSV Export

```python
def _export_csv(self, report_key: str) -> None:
    rows = self._report_data.get(report_key, [])

    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        initialfile=f"MWIMS_{report_key}_report.csv",
        filetypes=[("CSV files", "*.csv")],
    )
    if not path: return   # user cancelled

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers_map[report_key])   # column headers
        writer.writerows(rows)
```

Each report type has pre-defined column headers and stores its data in `self._report_data[key]` as a list of tuples, making export trivial.

### Activity Logs (Admin Conditional)

```python
if self.role == ROLE_ADMIN:
    self._tab_logs = tk.Frame(nb, bg=BG_DARK)
    nb.add(self._tab_logs, text="  📝  Activity Logs  ")
    self._build_logs_tab()
```

The tab is **not created at all** for non-admin roles. The backend also enforces this via `@require_role(ROLE_ADMIN)` on `get_activity_logs()`.

---

## 13. User Management View — `user_management_view.py`

**Class:** `UserManagementView(tk.Frame)` — Admin only  
**Backend calls:**  
- `auth_controller.get_all_users()`  
- `auth_controller.register_user(username, email, password, role)`  
- `auth_controller.deactivate_user(user_id)`

### `_CreateUserDialog(tk.Toplevel)`

A modal dialog for creating new user accounts. Fields: Username, Email, Password (masked), Role (combobox with `VALID_ROLES`).

Calls `auth_controller.register_user(...)` which performs full backend validation (username ≥3 chars, valid email format, password ≥6 chars, role membership check, uniqueness checks).

### User Table

The treeview displays: Username · Email · Role · Status (the database `_id` is hidden from the UI for security and stored internally in item `iid` for deactivation reference).

Inactive users are displayed with the `"inactive"` tag (dimmed text):
```python
tag = "evenrow" if is_active else "inactive"
self._tree.insert("", "end", iid=user_id, values=row, tags=(tag,))
```

### Deactivation Guard

Before calling `deactivate_user()`, three guards run:

```python
if not u.get("is_active", True):       # already deactivated
    messagebox.showinfo(...)
    return

if u.get("role") == ROLE_ADMIN:        # protect admin accounts
    messagebox.showerror(...)
    return

if not messagebox.askyesno("Confirm"):  # confirmation
    return
```

---

## 14. Settings View — `settings_view.py`

**Class:** `SettingsView(tk.Frame)`  
**Backend calls:** `auth_controller.change_password(user_id, current_pw, new_pw)`

### Profile Card

Dynamically coloured based on role:

```python
role_colour = {
    "admin":   ACCENT,   # blue
    "staff":   SUCCESS,  # green
    "auditor": WARNING,  # amber
}.get(role, TEXT_SECONDARY)
```

Shows the avatar icon, username, email, and role badge pill.

### Change Password Form

Frontend pre-validation before calling the backend:

| Check | Error Message |
|-------|--------------|
| Current password empty | "Current password is required." |
| New password empty | "New password is required." |
| New password < 6 chars | "New password must be at least 6 characters." |
| New ≠ Confirm | "New password and confirmation do not match." |

Then calls:
```python
ok, msg = auth_controller.change_password(
    self.user.get("_id", ""), current, new_pw
)
```

The backend performs final validation (verifies current password against database hash, enforces minimum 6 chars, prevents reuse of same password).

---

## 15. Navigation & Screen Loading Pattern

The screen loading pattern in `main_app.py` is a **single-active-frame** model:

```
show_section("medicines")
    │
    ├── deactivate old _NavButton
    ├── activate new _NavButton
    ├── self._content_frame.destroy()     ← previous screen garbage collected
    └── self._content_frame = MedicineView(self._content_area, self.user)
                                          ← new screen packed into content area
```

**Why destroy instead of hide/show?**  
Hiding frames with `.pack_forget()` keeps them in memory and does not trigger a data refresh. Destroying and recreating ensures each screen loads fresh data when navigated to.

**Why lazy imports in `_load_section()`?**
```python
if key == "medicines":
    from views.medicine_view import MedicineView   # imported on first access
    return MedicineView(...)
```
This avoids a circular import chain at startup (`gui.py → main_app.py → all views → controllers`) and keeps the initial launch fast since only `theme.py` and `login_view.py` are imported at startup.

---

## 16. Role-Based UI Gating

Role-based access control is enforced at **three levels**:

### Level 1 — Sidebar Menu (structural)
The nav item is **never created** for roles that cannot access it:
```python
if required_role and self.role != required_role:
    continue   # button not created, not visible
```

### Level 2 — Toolbar Buttons
Within a screen, destructive or write buttons are only created for permitted roles:
```python
if self.role in (ROLE_ADMIN, ROLE_STAFF):
    # Add and Edit buttons
if self.role == ROLE_ADMIN:
    # Delete button
```

### Level 3 — Backend Enforcement
Even if the frontend were bypassed, the backend decorators reject the call:
```python
@require_role(ROLE_ADMIN)
def delete_medicine(medicine_id: str) -> tuple[bool, str]:
    ...
```
Returns `(False, "Permission denied.", None)` without touching the database.

---

## 17. Error Handling Conventions

All views follow the same error-display pattern:

| Situation | UI Response |
|-----------|------------|
| Form validation failure | Inline `tk.Label` with `DANGER` text (no dialog) |
| Controller returns `(False, msg, _)` | `messagebox.showerror("Error", msg)` or inline label |
| Controller returns `(True, msg, _)` | `messagebox.showinfo("Success", msg)` |
| Destructive action | `messagebox.askyesno(...)` confirmation first |
| Exception in data load | Status bar label shows error text |

**Important:** After a successful write operation (add/edit/delete), the view **always calls the load method** to refresh the Treeview:
```python
if success:
    messagebox.showinfo("Success", msg)
    self._load_medicines()   # ← refresh table
```

---

## 18. Treeview Pattern

Every table in MWIMS follows the same pattern using `make_scrolled_tree()`:

```python
# 1. Create the tree
self._tree, _, _ = make_scrolled_tree(
    parent_frame,
    columns=("name", "qty", "rack"),
    headings=("Medicine", "Qty", "Rack"),
    col_widths=(200, 60, 80),
    height=14,
)

# 2. Populate on data load
def _load_data(self) -> None:
    ok, _, items = some_controller.get_all_items()
    rows = [(m["medicine_name"], m["quantity"], m["rack"]) for m in items]
    populate_tree(self._tree, rows)

# 3. Read selection
def _get_selected(self) -> Optional[dict]:
    sel = self._tree.selection()
    if not sel:
        messagebox.showwarning("No Selection", "Please select a row first.")
        return None
    idx = self._tree.index(sel[0])
    return self._items[idx]
```

**`populate_tree()` internals:**
```python
def populate_tree(tree: ttk.Treeview, rows: list[tuple]) -> None:
    tree.delete(*tree.get_children())   # clear all rows
    for idx, row in enumerate(rows):
        tag = "oddrow" if idx % 2 else "evenrow"
        tree.insert("", "end", values=row, tags=(tag,))
```

---

## 19. Dialog Pattern

All add/edit dialogs are `tk.Toplevel` subclasses:

```python
class _SomeDialog(tk.Toplevel):
    def __init__(self, parent, ..., on_saved):
        super().__init__(parent)
        self.grab_set()      # modal: blocks parent window interaction
        self.focus_set()     # keyboard focus goes to dialog
        self._build()
        self._centre()       # geometry centred on screen

    def _centre(self) -> None:
        self.update_idletasks()
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    def _save(self) -> None:
        # validate → call controller → on success: callback + destroy
        ok, msg = some_controller.do_action(...)
        if ok:
            self.on_saved()    # notify parent to refresh
            self.destroy()
        else:
            self._var_status.set(msg)   # show error inline
```

Key points:
- `grab_set()` makes the dialog truly modal
- Validation errors appear inline (no nested dialogs)
- `on_saved` callback lets the parent refresh its data without coupling

---

## 20. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Plain `tk` widgets for coloured buttons** | `ttk.Button` on Windows's `clam` theme does not respect `background` reliably; `tk.Button` gives pixel-perfect colour control |
| **`place()` for the login card** | `pack()` and `grid()` don't trivially centre a fixed-size card; `place(relx=0.5, rely=0.5, anchor="center")` does |
| **Destroy-and-recreate screens** | Ensures fresh data on every navigation; simpler than maintaining hidden frames |
| **Lazy screen imports** | Prevents circular imports at startup and reduces initial load time |
| **`StringVar.trace_add` for live search** | Fires on every keystroke without polling; standard Tkinter pattern |
| **`after(300, callback)` on login success** | 300ms delay lets the user see the "Login successful!" green message before the screen transitions |
| **`_report_data` dict in ReportsView** | Stores each report's row tuples at load time so CSV export doesn't need to re-fetch or re-parse data |
| **Dual role enforcement** | Frontend gating for UX clarity; backend decorators for security. Neither alone is sufficient |
| **Alternating row tags via `populate_tree`** | Provides subtle visual row separation without borders, improving readability in dense tables |

---

*This guide covers the complete frontend codebase as of MWIMS v1.0.*  
*For the backend API reference, see [`FRONTEND_INTEGRATION_GUIDE.md`](./FRONTEND_INTEGRATION_GUIDE.md).*
