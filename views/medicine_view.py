"""
Medicine Management View for MWIMS.

Provides full CRUD: Add, Update, Delete, Search, and List medicines.
All database interactions are performed via medicine_controller only.
Role-based: Delete is Admin-only; Auditor has read-only access.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Optional

from controllers import medicine_controller
from utils.constants import (
    MEDICINE_CATEGORIES, MEDICINE_TYPES,
    ROLE_ADMIN, ROLE_STAFF,
)
from views.theme import (
    ACCENT, BG_CARD, BG_DARK, BG_PANEL, BORDER, DANGER,
    FONT_BODY, FONT_CAPTION, FONT_FAMILY, FONT_HEADING,
    INPUT_BG, PAD_LG, PAD_MD, PAD_SM, PAD_XL, PAD_XS,
    SUCCESS, TEXT_DIM, TEXT_PRIMARY, TEXT_SECONDARY, WARNING,
    apply_theme, make_scrolled_tree, populate_tree, separator,
)


# ─────────────────────────────────────────────────────────────────────
#  ADD / EDIT MEDICINE DIALOG
# ─────────────────────────────────────────────────────────────────────

class _MedicineDialog(tk.Toplevel):
    """
    Modal dialog for creating or editing a medicine record.

    Args:
        parent:     Parent widget.
        user:       Current user dict.
        medicine:   Existing medicine dict for edit mode; None for add mode.
        on_saved:   Callback invoked with (success: bool) after save.
    """

    _FIELDS = [
        ("Medicine Name",    "medicine_name",  "entry",   None),
        ("Batch Number",     "batch_number",   "entry",   None),
        ("Category",         "category",       "combo",   list(MEDICINE_CATEGORIES)),
        ("Type",             "type",           "combo",   list(MEDICINE_TYPES)),
        ("Quantity",         "quantity",       "entry",   None),
        ("Minimum Stock",    "minimum_stock",  "entry",   None),
        ("Expiry Date",      "expiry_date",    "entry",   None),  # YYYY-MM-DD hint
        ("Rack",             "rack",           "entry",   None),
        ("Shelf",            "shelf",          "entry",   None),
        ("Cabinet",          "cabinet",        "entry",   None),
    ]

    def __init__(
        self,
        parent: tk.Widget,
        user: dict[str, Any],
        medicine: Optional[dict[str, Any]],
        on_saved,
    ) -> None:
        super().__init__(parent)
        self.user       = user
        self.medicine   = medicine
        self.on_saved   = on_saved
        self._edit_mode = medicine is not None

        self.title("Edit Medicine" if self._edit_mode else "Add New Medicine")
        self.configure(bg=BG_CARD)
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        self._vars: dict[str, tk.StringVar] = {}
        self._widgets: dict[str, tk.Widget] = {}
        self._var_status = tk.StringVar()

        self._build()
        self._centre()

        if self._edit_mode:
            self._populate_existing()

    # ──────────────────────── BUILD ───────────────────────────────────

    def _build(self) -> None:
        # Header
        hdr = tk.Frame(self, bg=ACCENT, height=5)
        hdr.pack(fill="x")

        title_bar = tk.Frame(self, bg=BG_CARD, padx=PAD_LG, pady=PAD_MD)
        title_bar.pack(fill="x")
        tk.Label(
            title_bar,
            text=("✏️  Edit Medicine" if self._edit_mode else "➕  Add New Medicine"),
            font=(FONT_FAMILY, 12, "bold"), bg=BG_CARD, fg=TEXT_PRIMARY,
        ).pack(anchor="w")

        # Form body
        form = tk.Frame(self, bg=BG_CARD, padx=PAD_LG, pady=PAD_SM)
        form.pack(fill="both", expand=True)

        for idx, (label, key, widget_type, options) in enumerate(self._FIELDS):
            row = idx // 2
            col = idx % 2
            cell = tk.Frame(form, bg=BG_CARD, padx=PAD_SM, pady=PAD_XS)
            cell.grid(row=row, column=col, sticky="ew", padx=PAD_XS)

            tk.Label(cell, text=label + ("  (YYYY-MM-DD)" if key == "expiry_date" else ""),
                     font=FONT_CAPTION, bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w")

            var = tk.StringVar()
            self._vars[key] = var

            if widget_type == "combo":
                widget = ttk.Combobox(cell, textvariable=var,
                                      values=options, width=24, state="readonly")
            else:
                widget = tk.Entry(
                    cell, textvariable=var, width=26,
                    font=FONT_BODY,
                    bg=INPUT_BG, fg=TEXT_PRIMARY,
                    insertbackground=TEXT_PRIMARY,
                    relief="flat", bd=0,
                    highlightthickness=1,
                    highlightbackground=BORDER,
                    highlightcolor=ACCENT,
                )
            widget.pack(fill="x", pady=(2, 0))
            self._widgets[key] = widget

        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        # Status message
        tk.Label(form, textvariable=self._var_status,
                 font=FONT_CAPTION, bg=BG_CARD, fg=DANGER,
                 wraplength=420, justify="left").grid(
            row=len(self._FIELDS)//2 + 1, column=0, columnspan=2, sticky="w", padx=PAD_SM
        )

        # Buttons
        btn_row = tk.Frame(self, bg=BG_CARD, padx=PAD_LG, pady=PAD_MD)
        btn_row.pack(fill="x")

        tk.Button(
            btn_row, text="💾  Save",
            font=(FONT_FAMILY, 10, "bold"),
            bg=ACCENT, fg=TEXT_PRIMARY,
            activebackground="#388AFF",
            relief="flat", bd=0, cursor="hand2",
            padx=PAD_MD, pady=PAD_XS,
            command=self._handle_save,
        ).pack(side="left", padx=(0, PAD_SM))

        tk.Button(
            btn_row, text="Cancel",
            font=FONT_BODY,
            bg=BG_CARD, fg=TEXT_SECONDARY,
            activebackground=BG_DARK,
            relief="flat", bd=0, cursor="hand2",
            padx=PAD_MD, pady=PAD_XS,
            command=self.destroy,
        ).pack(side="left")

    def _centre(self) -> None:
        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    def _populate_existing(self) -> None:
        """Pre-fill fields with existing medicine data."""
        if not self.medicine:
            return
        for key, var in self._vars.items():
            val = self.medicine.get(key, "")
            if hasattr(val, "strftime"):
                val = val.strftime("%Y-%m-%d")
            var.set(str(val) if val is not None else "")

    # ──────────────────────── ACTIONS ─────────────────────────────────

    def _handle_save(self) -> None:
        # ── Collect & validate ────────────────────────────────────────
        data: dict[str, Any] = {k: v.get().strip() for k, v in self._vars.items()}

        required = ["medicine_name", "batch_number", "category", "type",
                    "quantity", "minimum_stock", "expiry_date",
                    "rack", "shelf", "cabinet"]
        for field in required:
            if not data.get(field):
                self._var_status.set(
                    f"'{field.replace('_', ' ').title()}' is required."
                )
                return

        # Numeric validation
        for num_field in ("quantity", "minimum_stock"):
            if not data[num_field].isdigit():
                self._var_status.set(
                    f"'{num_field.replace('_', ' ').title()}' must be a non-negative integer."
                )
                return

        self._var_status.set("")

        if self._edit_mode and self.medicine:
            # ── UPDATE ────────────────────────────────────────────────
            payload = {
                "medicine_name": data["medicine_name"],
                "category":      data["category"],
                "type":          data["type"],
                "quantity":      int(data["quantity"]),
                "minimum_stock": int(data["minimum_stock"]),
                "expiry_date":   data["expiry_date"],
                "rack":          data["rack"],
                "shelf":         data["shelf"],
                "cabinet":       data["cabinet"],
            }

            success, msg = medicine_controller.update_medicine(
                self.medicine["_id"], payload
            )
            if success:
                messagebox.showinfo(
                    "Success", "Medicine updated successfully.", parent=self
                )
                self.on_saved(True)
                self.destroy()
            else:
                self._var_status.set(msg)
        else:
            # ── CREATE ────────────────────────────────────────────────
            success, msg, _med = medicine_controller.add_medicine(
                medicine_name=data["medicine_name"],
                batch_number=data["batch_number"],
                category=data["category"],
                type_name=data["type"],
                quantity=int(data["quantity"]),
                minimum_stock=int(data["minimum_stock"]),
                expiry_date=data["expiry_date"],
                rack=data["rack"],
                shelf=data["shelf"],
                cabinet=data["cabinet"],
            )
            if success:
                messagebox.showinfo(
                    "Success", "Medicine added successfully.", parent=self
                )
                self.on_saved(True)
                self.destroy()
            else:
                self._var_status.set(msg)


# ─────────────────────────────────────────────────────────────────────
#  MAIN MEDICINE VIEW
# ─────────────────────────────────────────────────────────────────────

class MedicineView(tk.Frame):
    """
    Medicine Management screen with Treeview table and CRUD toolbar.

    Roles:
        admin  → full CRUD
        staff  → add + edit (no delete)
        auditor→ read-only
    """

    _COLUMNS = (
        "id", "name", "batch", "category", "type",
        "qty", "min_stock", "expiry", "rack", "shelf", "cabinet",
    )
    _HEADINGS = (
        "ID (short)", "Medicine Name", "Batch #", "Category", "Type",
        "Qty", "Min Stock", "Expiry Date", "Rack", "Shelf", "Cabinet",
    )
    _WIDTHS = (90, 180, 110, 130, 90, 60, 80, 100, 60, 60, 70)

    def __init__(self, parent: tk.Widget, user: dict[str, Any]) -> None:
        super().__init__(parent, bg=BG_DARK)
        self.user = user
        self.role = user.get("role", "staff")
        self._all_medicines: list[dict] = []
        self._selected_id: Optional[str] = None

        self._build_ui()
        self._load_medicines()

    # ──────────────────────── BUILD ───────────────────────────────────

    def _build_ui(self) -> None:
        # ── Title bar ──────────────────────────────────────────────
        title_bar = tk.Frame(self, bg=BG_DARK)
        title_bar.pack(fill="x", padx=PAD_XL, pady=(PAD_LG, PAD_SM))
        tk.Label(title_bar, text="💊  Medicine Management",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg=BG_DARK, fg=TEXT_PRIMARY).pack(side="left")

        # ── Toolbar ────────────────────────────────────────────────
        toolbar = tk.Frame(self, bg=BG_DARK)
        toolbar.pack(fill="x", padx=PAD_XL, pady=(0, PAD_SM))

        # Search
        tk.Label(toolbar, text="🔍 Search:", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_SECONDARY).pack(side="left")
        self._var_search = tk.StringVar()
        self._var_search.trace_add("write", lambda *_: self._apply_search())
        self._entry_search = tk.Entry(
            toolbar, textvariable=self._var_search, width=28,
            font=FONT_BODY,
            bg=INPUT_BG, fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        self._entry_search.pack(side="left", padx=(PAD_XS, PAD_MD), ipady=4)

        tk.Button(toolbar, text="🔄 Refresh",
                  font=FONT_BODY, bg=BG_CARD, fg=TEXT_SECONDARY,
                  activebackground=BG_CARD, relief="flat", bd=0, cursor="hand2",
                  padx=PAD_SM, command=self._load_medicines).pack(side="left", padx=(0, PAD_MD))

        # Action buttons (role-gated)
        if self.role in (ROLE_ADMIN, ROLE_STAFF):
            tk.Button(toolbar, text="➕  Add Medicine",
                      font=(FONT_FAMILY, 10, "bold"),
                      bg=ACCENT, fg=TEXT_PRIMARY,
                      activebackground="#388AFF",
                      relief="flat", bd=0, cursor="hand2",
                      padx=PAD_MD, pady=3,
                      command=self._open_add_dialog).pack(side="left", padx=(0, PAD_SM))

            tk.Button(toolbar, text="✏️  Edit",
                      font=FONT_BODY,
                      bg=BG_CARD, fg=TEXT_SECONDARY,
                      activebackground=BG_CARD, relief="flat", bd=0, cursor="hand2",
                      padx=PAD_SM, pady=3,
                      command=self._open_edit_dialog).pack(side="left", padx=(0, PAD_SM))

        if self.role == ROLE_ADMIN:
            tk.Button(toolbar, text="🗑️  Delete",
                      font=FONT_BODY,
                      bg=DANGER, fg=TEXT_PRIMARY,
                      activebackground="#ff6b63",
                      relief="flat", bd=0, cursor="hand2",
                      padx=PAD_SM, pady=3,
                      command=self._delete_selected).pack(side="left")

        # ── Status bar ─────────────────────────────────────────────
        self._var_status = tk.StringVar(value="Loading medicines…")
        tk.Label(self, textvariable=self._var_status,
                 font=FONT_CAPTION, bg=BG_DARK, fg=TEXT_SECONDARY,
                 anchor="w").pack(fill="x", padx=PAD_XL)

        # ── Treeview ───────────────────────────────────────────────
        tree_container = tk.Frame(self, bg=BG_DARK)
        tree_container.pack(fill="both", expand=True, padx=PAD_XL, pady=(PAD_SM, PAD_LG))

        self._tree, _, _ = make_scrolled_tree(
            tree_container,
            columns=self._COLUMNS,
            headings=self._HEADINGS,
            col_widths=self._WIDTHS,
            height=18,
        )
        self._tree.bind("<<TreeviewSelect>>", self._on_row_select)
        self._tree.bind("<Double-1>", lambda _: self._open_edit_dialog())

    # ──────────────────────── DATA ────────────────────────────────────

    def _load_medicines(self) -> None:
        """Fetch all medicines from the backend and populate the table."""
        ok, msg, meds = medicine_controller.get_all_medicines()
        if ok:
            self._all_medicines = meds
            self._apply_search()
            self._var_status.set(
                f"{len(meds)} medicine(s) loaded. "
                f"{'Double-click to edit.' if self.role != 'auditor' else 'Read-only mode.'}"
            )
        else:
            self._var_status.set(f"Error: {msg}")

    def _apply_search(self) -> None:
        """Filter the loaded medicines list by the search keyword."""
        keyword = self._var_search.get().strip().lower()
        if keyword:
            filtered = [
                m for m in self._all_medicines
                if keyword in m.get("medicine_name", "").lower()
                or keyword in m.get("batch_number", "").lower()
                or keyword in m.get("category", "").lower()
                or keyword in m.get("type", "").lower()
            ]
        else:
            filtered = self._all_medicines

        rows = [self._med_to_row(m) for m in filtered]
        populate_tree(self._tree, rows)
        self._var_status.set(f"Showing {len(filtered)} of {len(self._all_medicines)} medicine(s).")

    @staticmethod
    def _med_to_row(m: dict) -> tuple:
        eid = str(m.get("_id", ""))[:8] + "…"
        expiry = m.get("expiry_date", "")
        if hasattr(expiry, "strftime"):
            expiry = expiry.strftime("%Y-%m-%d")
        return (
            eid,
            m.get("medicine_name", ""),
            m.get("batch_number", ""),
            m.get("category", ""),
            m.get("type", ""),
            m.get("quantity", 0),
            m.get("minimum_stock", 0),
            str(expiry),
            m.get("rack", ""),
            m.get("shelf", ""),
            m.get("cabinet", ""),
        )

    # ──────────────────────── SELECTION ───────────────────────────────

    def _on_row_select(self, _=None) -> None:
        sel = self._tree.selection()
        if sel:
            idx = self._tree.index(sel[0])
            keyword = self._var_search.get().strip().lower()
            source = (
                [m for m in self._all_medicines
                 if keyword in m.get("medicine_name", "").lower()
                 or keyword in m.get("batch_number", "").lower()]
                if keyword else self._all_medicines
            )
            if 0 <= idx < len(source):
                self._selected_id = str(source[idx].get("_id", ""))

    def _get_selected_medicine(self) -> Optional[dict]:
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a medicine row first.", parent=self)
            return None
        idx = self._tree.index(sel[0])
        keyword = self._var_search.get().strip().lower()
        source = (
            [m for m in self._all_medicines
             if keyword in m.get("medicine_name", "").lower()
             or keyword in m.get("batch_number", "").lower()]
            if keyword else self._all_medicines
        )
        if 0 <= idx < len(source):
            return source[idx]
        return None

    # ──────────────────────── DIALOGS ─────────────────────────────────

    def _open_add_dialog(self) -> None:
        _MedicineDialog(self, self.user, medicine=None,
                        on_saved=lambda _: self._load_medicines())

    def _open_edit_dialog(self) -> None:
        if self.role == "auditor":
            messagebox.showinfo("Read-only", "Auditor role cannot edit medicines.", parent=self)
            return
        med = self._get_selected_medicine()
        if med:
            _MedicineDialog(self, self.user, medicine=med,
                            on_saved=lambda _: self._load_medicines())

    def _delete_selected(self) -> None:
        med = self._get_selected_medicine()
        if not med:
            return
        name = med.get("medicine_name", "Unknown")
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Permanently delete '{name}'?\nThis action cannot be undone.",
            parent=self,
        ):
            return

        ok, msg = medicine_controller.delete_medicine(str(med["_id"]))
        if ok:
            messagebox.showinfo("Deleted", f"'{name}' has been deleted.", parent=self)
            self._load_medicines()
        else:
            messagebox.showerror("Delete Failed", msg, parent=self)
