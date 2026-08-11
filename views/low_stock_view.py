"""
Low Stock Alert View for MWIMS.

Lists all medicines whose current quantity is below their minimum_stock threshold.
Fetched via inventory_controller.get_low_stock_alerts().
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from controllers import inventory_controller
from views.theme import (
    ACCENT, BG_CARD, BG_DARK, BORDER, DANGER,
    FONT_BODY, FONT_CAPTION, FONT_FAMILY, FONT_HEADING,
    PAD_LG, PAD_MD, PAD_SM, PAD_XL, PAD_XS,
    SUCCESS, TEXT_DIM, TEXT_PRIMARY, TEXT_SECONDARY, WARNING,
    make_scrolled_tree, populate_tree,
)


class LowStockView(tk.Frame):
    """
    Low Stock Alert screen.

    Shows two sections:
      1. CRITICAL – quantity == 0 (out of stock)
      2. WARNING  – quantity > 0 but below minimum_stock
    """

    _COLS   = ("name", "batch", "qty", "min_stock", "deficit", "level", "rack")
    _HEADS  = ("Medicine Name", "Batch #", "Current Qty", "Min Stock", "Deficit", "Alert Level", "Rack")
    _WIDTHS = (175, 105, 90, 85, 75, 100, 70)

    def __init__(self, parent: tk.Widget, user: dict[str, Any]) -> None:
        super().__init__(parent, bg=BG_DARK)
        self.user = user
        self._build_ui()
        self._load_alerts()

    # ─────────────────────────── BUILD ───────────────────────────────

    def _build_ui(self) -> None:
        # Title + refresh
        title_bar = tk.Frame(self, bg=BG_DARK)
        title_bar.pack(fill="x", padx=PAD_XL, pady=(PAD_LG, PAD_SM))
        tk.Label(title_bar, text="⚠️  Low Stock Alerts",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg=BG_DARK, fg=TEXT_PRIMARY).pack(side="left")
        tk.Button(title_bar, text="🔄 Refresh", font=FONT_BODY,
                  bg=BG_CARD, fg=TEXT_SECONDARY,
                  relief="flat", bd=0, cursor="hand2",
                  padx=PAD_SM, command=self._load_alerts).pack(side="right")

        # Badge row
        self._badge_row = tk.Frame(self, bg=BG_DARK)
        self._badge_row.pack(fill="x", padx=PAD_XL, pady=(0, PAD_SM))

        # Tabs
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=PAD_XL, pady=(0, PAD_LG))

        self._tab_critical = tk.Frame(nb, bg=BG_DARK)
        self._tab_warning  = tk.Frame(nb, bg=BG_DARK)
        self._tab_all      = tk.Frame(nb, bg=BG_DARK)

        nb.add(self._tab_critical, text="  🛑  Out of Stock (Critical)  ")
        nb.add(self._tab_warning,  text="  ⚠️  Below Minimum (Warning) ")
        nb.add(self._tab_all,      text="  📋  All Low Stock Items      ")

        self._tree_critical, _, _ = make_scrolled_tree(
            self._tab_critical, self._COLS, self._HEADS, self._WIDTHS, height=14)
        self._tree_warning,  _, _ = make_scrolled_tree(
            self._tab_warning,  self._COLS, self._HEADS, self._WIDTHS, height=14)
        self._tree_all,      _, _ = make_scrolled_tree(
            self._tab_all,      self._COLS, self._HEADS, self._WIDTHS, height=14)

    # ─────────────────────────── DATA ────────────────────────────────

    def _load_alerts(self) -> None:
        ok, _msg, alerts = inventory_controller.get_low_stock_alerts()
        if not ok:
            alerts = []

        critical = [a for a in alerts if a.get("alert_level") == "CRITICAL"]
        warning  = [a for a in alerts if a.get("alert_level") == "WARNING"]

        # Badges
        for w in self._badge_row.winfo_children():
            w.destroy()
        for text, colour in [
            (f"  🛑  Out of Stock: {len(critical)}  ",  DANGER),
            (f"  ⚠️  Below Min: {len(warning)}  ",      WARNING),
            (f"  📋  Total: {len(alerts)}  ",            ACCENT),
        ]:
            tk.Label(self._badge_row, text=text,
                     font=(FONT_FAMILY, 9, "bold"),
                     bg=colour,
                     fg=BG_DARK if colour == WARNING else TEXT_PRIMARY,
                     padx=PAD_SM, pady=2).pack(side="left", padx=(0, PAD_XS))

        # Fill trees
        populate_tree(self._tree_critical, [self._row(a) for a in critical])
        populate_tree(self._tree_warning,  [self._row(a) for a in warning])

        # All tab with coloured tags
        self._tree_all.delete(*self._tree_all.get_children())
        for a in alerts:
            tag = "danger" if a.get("alert_level") == "CRITICAL" else "warning"
            self._tree_all.insert("", "end", values=self._row(a), tags=(tag,))

    @staticmethod
    def _row(a: dict) -> tuple:
        return (
            a.get("medicine_name", ""),
            a.get("batch_number", ""),
            a.get("quantity", 0),
            a.get("minimum_stock", 0),
            a.get("deficit", 0),
            a.get("alert_level", ""),
            a.get("rack", ""),
        )
