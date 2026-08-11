"""
Inventory Management View for MWIMS.

Supports:
  • Receive Stock   (positive delta)
  • Reduce Stock    (negative delta)
  • Transfer Location
  • Stock History via audit activity logs (Admin)

All operations go through inventory_controller / warehouse_controller.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Optional

from controllers import inventory_controller, medicine_controller, warehouse_controller
from utils.constants import ROLE_ADMIN
from views.theme import (
    ACCENT, BG_CARD, BG_DARK, BG_PANEL, BORDER, DANGER,
    FONT_BODY, FONT_CAPTION, FONT_FAMILY, FONT_HEADING,
    INPUT_BG, PAD_LG, PAD_MD, PAD_SM, PAD_XL, PAD_XS,
    SUCCESS, TEXT_DIM, TEXT_PRIMARY, TEXT_SECONDARY, WARNING,
    make_scrolled_tree, populate_tree,
)


class InventoryView(tk.Frame):
    """
    Inventory Management screen.

    Tabs:
      1. Stock Adjustment  (receive / reduce)
      2. Transfer Location
      3. Inventory Table
    """

    _COLS    = ("id", "name", "batch", "qty", "min_stock", "rack", "shelf", "cabinet", "category")
    _HEADS   = ("ID", "Medicine Name", "Batch #", "Qty", "Min Stock", "Rack", "Shelf", "Cabinet", "Category")
    _WIDTHS  = (88, 175, 105, 60, 75, 55, 55, 65, 120)

    def __init__(self, parent: tk.Widget, user: dict[str, Any]) -> None:
        super().__init__(parent, bg=BG_DARK)
        self.user  = user
        self.role  = user.get("role", "staff")
        self._medicines: list[dict] = []
        self._build_ui()
        self._load_medicines()

    # ─────────────────────────── BUILD ───────────────────────────────

    def _build_ui(self) -> None:
        # Title
        title_bar = tk.Frame(self, bg=BG_DARK)
        title_bar.pack(fill="x", padx=PAD_XL, pady=(PAD_LG, PAD_SM))
        tk.Label(title_bar, text="📦  Inventory Management",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg=BG_DARK, fg=TEXT_PRIMARY).pack(side="left")

        # Tabs
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=PAD_XL, pady=(0, PAD_LG))

        self._tab_stock    = tk.Frame(nb, bg=BG_DARK)
        self._tab_transfer = tk.Frame(nb, bg=BG_DARK)
        self._tab_table    = tk.Frame(nb, bg=BG_DARK)

        nb.add(self._tab_stock,    text="  📥  Stock Adjustment  ")
        nb.add(self._tab_transfer, text="  🔄  Transfer Location  ")
        nb.add(self._tab_table,    text="  📋  Inventory Table    ")

        self._build_stock_tab()
        self._build_transfer_tab()
        self._build_table_tab()

    # ── Tab 1: Stock Adjustment ───────────────────────────────────────

    def _build_stock_tab(self) -> None:
        p = self._tab_stock
        card = tk.Frame(p, bg=BG_CARD, padx=PAD_XL, pady=PAD_XL)
        card.pack(padx=PAD_XL, pady=PAD_XL, anchor="nw")

        tk.Label(card, text="Stock Adjustment",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=BG_CARD, fg=TEXT_PRIMARY).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, PAD_MD))

        # Medicine picker
        self._field_label(card, "Select Medicine", 1)
        self._var_stock_med = tk.StringVar()
        self._combo_stock = ttk.Combobox(card, textvariable=self._var_stock_med,
                                         width=36, state="readonly")
        self._combo_stock.grid(row=1, column=1, sticky="ew", padx=(PAD_SM, 0), pady=PAD_XS)

        # Delta
        self._field_label(card, "Quantity Δ (positive = receive, negative = reduce)", 2)
        self._var_delta = tk.StringVar()
        self._entry_delta = self._make_entry(card, self._var_delta, width=12)
        self._entry_delta.grid(row=2, column=1, sticky="w", padx=(PAD_SM, 0), pady=PAD_XS)

        # Status
        self._var_stock_status = tk.StringVar()
        self._lbl_stock_status = tk.Label(card, textvariable=self._var_stock_status,
                                          font=FONT_CAPTION, bg=BG_CARD, fg=DANGER,
                                          wraplength=360)
        self._lbl_stock_status.grid(row=3, column=0, columnspan=2, sticky="w", pady=PAD_XS)

        # Buttons
        btn_row = tk.Frame(card, bg=BG_CARD)
        btn_row.grid(row=4, column=0, columnspan=2, sticky="w", pady=(PAD_SM, 0))

        if self.role != "auditor":
            tk.Button(btn_row, text="📥  Receive Stock",
                      font=(FONT_FAMILY, 10, "bold"),
                      bg=SUCCESS, fg=BG_DARK,
                      activebackground="#52c562",
                      relief="flat", bd=0, cursor="hand2",
                      padx=PAD_MD, pady=4,
                      command=lambda: self._adjust_stock(positive=True)).pack(side="left", padx=(0, PAD_SM))

            tk.Button(btn_row, text="📤  Reduce Stock",
                      font=(FONT_FAMILY, 10, "bold"),
                      bg=DANGER, fg=TEXT_PRIMARY,
                      activebackground="#ff6b63",
                      relief="flat", bd=0, cursor="hand2",
                      padx=PAD_MD, pady=4,
                      command=lambda: self._adjust_stock(positive=False)).pack(side="left")
        else:
            tk.Label(card, text="🔒  Read-only: Auditor cannot adjust stock.",
                     font=FONT_BODY, bg=BG_CARD, fg=WARNING).grid(
                row=4, column=0, columnspan=2, sticky="w")

    # ── Tab 2: Transfer Location ──────────────────────────────────────

    def _build_transfer_tab(self) -> None:
        p = self._tab_transfer
        card = tk.Frame(p, bg=BG_CARD, padx=PAD_XL, pady=PAD_XL)
        card.pack(padx=PAD_XL, pady=PAD_XL, anchor="nw")

        tk.Label(card, text="Transfer Medicine Location",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=BG_CARD, fg=TEXT_PRIMARY).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, PAD_MD))

        self._field_label(card, "Select Medicine", 1)
        self._var_transfer_med = tk.StringVar()
        self._combo_transfer = ttk.Combobox(card, textvariable=self._var_transfer_med,
                                            width=36, state="readonly")
        self._combo_transfer.grid(row=1, column=1, sticky="ew", padx=(PAD_SM, 0), pady=PAD_XS)

        for i, (label, attr) in enumerate([
            ("New Rack",    "_var_new_rack"),
            ("New Shelf",   "_var_new_shelf"),
            ("New Cabinet", "_var_new_cabinet"),
        ], start=2):
            self._field_label(card, label, i)
            var = tk.StringVar()
            setattr(self, attr, var)
            self._make_entry(card, var, width=18).grid(
                row=i, column=1, sticky="w", padx=(PAD_SM, 0), pady=PAD_XS)

        self._var_transfer_status = tk.StringVar()
        tk.Label(card, textvariable=self._var_transfer_status,
                 font=FONT_CAPTION, bg=BG_CARD, fg=DANGER, wraplength=360).grid(
            row=5, column=0, columnspan=2, sticky="w", pady=PAD_XS)

        if self.role != "auditor":
            tk.Button(card, text="🔄  Transfer",
                      font=(FONT_FAMILY, 10, "bold"),
                      bg=ACCENT, fg=TEXT_PRIMARY,
                      activebackground="#388AFF",
                      relief="flat", bd=0, cursor="hand2",
                      padx=PAD_MD, pady=4,
                      command=self._handle_transfer).grid(
                row=6, column=0, columnspan=2, sticky="w", pady=(PAD_SM, 0))

    # ── Tab 3: Inventory Table ────────────────────────────────────────

    def _build_table_tab(self) -> None:
        p = self._tab_table
        toolbar = tk.Frame(p, bg=BG_DARK)
        toolbar.pack(fill="x", pady=(PAD_SM, 0))
        tk.Button(toolbar, text="🔄 Refresh", font=FONT_BODY,
                  bg=BG_CARD, fg=TEXT_SECONDARY,
                  relief="flat", bd=0, cursor="hand2",
                  padx=PAD_SM, command=self._load_medicines).pack(side="left", padx=PAD_SM)

        tree_frame = tk.Frame(p, bg=BG_DARK)
        tree_frame.pack(fill="both", expand=True)
        self._inv_tree, _, _ = make_scrolled_tree(
            tree_frame, self._COLS, self._HEADS, self._WIDTHS, height=16
        )

    # ─────────────────────────── DATA ────────────────────────────────

    def _load_medicines(self) -> None:
        ok, _msg, meds = medicine_controller.get_all_medicines()
        if ok:
            self._medicines = meds
            names = [f"{m.get('medicine_name', '')} [{m.get('batch_number', '')}]"
                     for m in meds]
            self._combo_stock["values"]    = names
            self._combo_transfer["values"] = names

            rows = []
            for m in meds:
                expiry = m.get("expiry_date", "")
                if hasattr(expiry, "strftime"):
                    expiry = expiry.strftime("%Y-%m-%d")
                rows.append((
                    str(m.get("_id", ""))[:8],
                    m.get("medicine_name", ""),
                    m.get("batch_number", ""),
                    m.get("quantity", 0),
                    m.get("minimum_stock", 0),
                    m.get("rack", ""),
                    m.get("shelf", ""),
                    m.get("cabinet", ""),
                    m.get("category", ""),
                ))
            populate_tree(self._inv_tree, rows)

    # ─────────────────────────── ACTIONS ─────────────────────────────

    def _get_selected_med_idx(self, combo: ttk.Combobox) -> Optional[int]:
        sel = combo.current()
        if sel < 0:
            messagebox.showwarning("No Medicine", "Please select a medicine first.", parent=self)
            return None
        return sel

    def _adjust_stock(self, positive: bool) -> None:
        idx = self._get_selected_med_idx(self._combo_stock)
        if idx is None:
            return

        delta_str = self._var_delta.get().strip()
        if not delta_str or not delta_str.lstrip("-").isdigit():
            self._var_stock_status.set("Please enter a valid integer quantity delta.")
            return

        delta = abs(int(delta_str))
        if delta == 0:
            self._var_stock_status.set("Delta cannot be zero.")
            return

        if not positive:
            delta = -delta

        med = self._medicines[idx]
        ok, msg, _ = inventory_controller.adjust_stock(str(med["_id"]), delta)
        if ok:
            self._lbl_stock_status.configure(fg=SUCCESS)
            self._var_stock_status.set(msg)
            self._load_medicines()
        else:
            self._lbl_stock_status.configure(fg=DANGER)
            self._var_stock_status.set(msg)

    def _handle_transfer(self) -> None:
        idx = self._get_selected_med_idx(self._combo_transfer)
        if idx is None:
            return

        rack    = self._var_new_rack.get().strip()
        shelf   = self._var_new_shelf.get().strip()
        cabinet = self._var_new_cabinet.get().strip()

        if not rack or not shelf or not cabinet:
            self._var_transfer_status.set("Rack, Shelf, and Cabinet are all required.")
            return

        med = self._medicines[idx]
        ok, msg = warehouse_controller.transfer_medicine_location(
            str(med["_id"]), rack, shelf, cabinet
        )
        if ok:
            messagebox.showinfo("Transfer Complete", msg, parent=self)
            self._var_transfer_status.set("")
            self._load_medicines()
        else:
            self._var_transfer_status.set(msg)

    # ─────────────────────────── HELPERS ─────────────────────────────

    @staticmethod
    def _field_label(parent: tk.Frame, text: str, row: int) -> None:
        tk.Label(parent, text=text, font=FONT_CAPTION, bg=BG_CARD,
                 fg=TEXT_SECONDARY, width=22, anchor="w").grid(
            row=row, column=0, sticky="w", pady=PAD_XS)

    @staticmethod
    def _make_entry(parent: tk.Frame, var: tk.StringVar, width: int = 26) -> tk.Entry:
        return tk.Entry(
            parent, textvariable=var, width=width,
            font=FONT_BODY,
            bg=INPUT_BG, fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
