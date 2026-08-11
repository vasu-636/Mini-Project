"""
Expiry Alert View for MWIMS.

Shows medicines that are:
  • EXPIRED   – expiry_date <= today
  • CRITICAL  – 1-7 days remaining
  • WARNING   – 8-30 days remaining

Data is fetched via inventory_controller.get_expiry_alerts().
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


class ExpiryView(tk.Frame):
    """
    Expiry Alerts screen.

    Displays three Treeview sections:
      1. Expired medicines (red)
      2. Critical – expiring <= 7 days (orange)
      3. Warning  – expiring <= 30 days (yellow)
    """

    _COLS   = ("name", "batch", "qty", "expiry", "days_left", "status", "rack")
    _HEADS  = ("Medicine Name", "Batch #", "Qty", "Expiry Date", "Days Left", "Status", "Rack")
    _WIDTHS = (175, 105, 60, 100, 80, 80, 70)

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
        tk.Label(title_bar, text="⏰  Expiry Alerts",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg=BG_DARK, fg=TEXT_PRIMARY).pack(side="left")
        tk.Button(title_bar, text="🔄 Refresh", font=FONT_BODY,
                  bg=BG_CARD, fg=TEXT_SECONDARY,
                  relief="flat", bd=0, cursor="hand2",
                  padx=PAD_SM, command=self._load_alerts).pack(side="right")

        # Warning days selector
        ctrl = tk.Frame(self, bg=BG_DARK)
        ctrl.pack(fill="x", padx=PAD_XL, pady=(0, PAD_SM))
        tk.Label(ctrl, text="Warning window (days):", font=FONT_CAPTION,
                 bg=BG_DARK, fg=TEXT_SECONDARY).pack(side="left")
        self._var_days = tk.StringVar(value="30")
        ttk.Spinbox(ctrl, from_=7, to=180, width=6,
                    textvariable=self._var_days,
                    command=self._load_alerts).pack(side="left", padx=PAD_XS)
        tk.Button(ctrl, text="Apply", font=FONT_CAPTION,
                  bg=ACCENT, fg=TEXT_PRIMARY,
                  relief="flat", bd=0, cursor="hand2",
                  padx=PAD_SM,
                  command=self._load_alerts).pack(side="left", padx=PAD_XS)

        # Summary badges
        self._badge_row = tk.Frame(self, bg=BG_DARK)
        self._badge_row.pack(fill="x", padx=PAD_XL, pady=(0, PAD_SM))

        # Notebook for grouped views
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=PAD_XL, pady=(0, PAD_LG))

        self._tab_expired  = tk.Frame(nb, bg=BG_DARK)
        self._tab_critical = tk.Frame(nb, bg=BG_DARK)
        self._tab_warning  = tk.Frame(nb, bg=BG_DARK)
        self._tab_all      = tk.Frame(nb, bg=BG_DARK)

        nb.add(self._tab_expired,  text="  💀  Expired       ")
        nb.add(self._tab_critical, text="  🔴  Critical (≤7d)")
        nb.add(self._tab_warning,  text="  🟡  Warning (≤30d)")
        nb.add(self._tab_all,      text="  📋  All Alerts     ")

        # Build trees inside each tab
        self._tree_expired,  _, _ = make_scrolled_tree(self._tab_expired,  self._COLS, self._HEADS, self._WIDTHS, height=14)
        self._tree_critical, _, _ = make_scrolled_tree(self._tab_critical, self._COLS, self._HEADS, self._WIDTHS, height=14)
        self._tree_warning,  _, _ = make_scrolled_tree(self._tab_warning,  self._COLS, self._HEADS, self._WIDTHS, height=14)
        self._tree_all,      _, _ = make_scrolled_tree(self._tab_all,      self._COLS, self._HEADS, self._WIDTHS, height=14)

    # ─────────────────────────── DATA ────────────────────────────────

    def _load_alerts(self) -> None:
        try:
            days = int(self._var_days.get())
        except ValueError:
            days = 30

        ok, _msg, alerts = inventory_controller.get_expiry_alerts(warning_days=days)
        if not ok:
            alerts = []

        expired  = [a for a in alerts if a.get("expiry_status") == "EXPIRED"]
        critical = [a for a in alerts if a.get("expiry_status") == "CRITICAL"]
        warning  = [a for a in alerts if a.get("expiry_status") == "WARNING"]

        # Update badges
        for w in self._badge_row.winfo_children():
            w.destroy()

        for label, count, colour in [
            (f"💀  Expired: {len(expired)}",       len(expired),  DANGER),
            (f"🔴  Critical: {len(critical)}",     len(critical), "#FF6B35"),
            (f"🟡  Warning: {len(warning)}",       len(warning),  WARNING),
            (f"📋  Total: {len(alerts)}",          len(alerts),   ACCENT),
        ]:
            tk.Label(self._badge_row, text=f"  {label}  ",
                     font=(FONT_FAMILY, 9, "bold"),
                     bg=colour, fg=BG_DARK if colour in (WARNING, "#FF6B35") else TEXT_PRIMARY,
                     padx=PAD_SM, pady=2).pack(side="left", padx=(0, PAD_XS))

        # Populate trees
        populate_tree(self._tree_expired,  [self._row(a) for a in expired],  )
        populate_tree(self._tree_critical, [self._row(a) for a in critical], )
        populate_tree(self._tree_warning,  [self._row(a) for a in warning],  )
        populate_tree(self._tree_all,      [self._row(a) for a in alerts],   )

        # Apply row colours for all-tab
        self._tree_all.delete(*self._tree_all.get_children())
        for a in alerts:
            status = a.get("expiry_status", "")
            tag = "danger" if status == "EXPIRED" else "warning" if status == "CRITICAL" else "oddrow"
            self._tree_all.insert("", "end", values=self._row(a), tags=(tag,))

    @staticmethod
    def _row(a: dict) -> tuple:
        expiry = a.get("expiry_date", "")
        if hasattr(expiry, "strftime"):
            expiry = expiry.strftime("%Y-%m-%d")
        return (
            a.get("medicine_name", ""),
            a.get("batch_number", ""),
            a.get("quantity", 0),
            str(expiry),
            a.get("days_remaining", 0),
            a.get("expiry_status", ""),
            a.get("rack", ""),
        )
