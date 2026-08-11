"""
Reports View for MWIMS.

Generates and displays:
  1. Inventory Summary Report  (via report_controller)
  2. Expiry Alert Report
  3. Low Stock Report
  4. Activity Logs             (Admin only)
  5. CSV Export for each report

All data fetched via report_controller / inventory_controller.
"""

from __future__ import annotations

import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any

from controllers import inventory_controller, report_controller
from utils.constants import ROLE_ADMIN
from views.theme import (
    ACCENT, BG_CARD, BG_DARK, BORDER, DANGER,
    FONT_BODY, FONT_CAPTION, FONT_FAMILY, FONT_HEADING,
    PAD_LG, PAD_MD, PAD_SM, PAD_XL, PAD_XS,
    SUCCESS, TEXT_DIM, TEXT_PRIMARY, TEXT_SECONDARY, WARNING,
    make_scrolled_tree, populate_tree,
)


class ReportsView(tk.Frame):
    """
    Reports screen with tabs for each report type + CSV export.
    """

    def __init__(self, parent: tk.Widget, user: dict[str, Any]) -> None:
        super().__init__(parent, bg=BG_DARK)
        self.user  = user
        self.role  = user.get("role", "staff")
        self._report_data: dict[str, list] = {}
        self._build_ui()

    # ─────────────────────────── BUILD ───────────────────────────────

    def _build_ui(self) -> None:
        # Title bar
        title_bar = tk.Frame(self, bg=BG_DARK)
        title_bar.pack(fill="x", padx=PAD_XL, pady=(PAD_LG, PAD_SM))
        tk.Label(title_bar, text="📊  Reports",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg=BG_DARK, fg=TEXT_PRIMARY).pack(side="left")

        tk.Button(title_bar, text="🔄 Refresh All", font=FONT_BODY,
                  bg=BG_CARD, fg=TEXT_SECONDARY,
                  relief="flat", bd=0, cursor="hand2",
                  padx=PAD_SM, command=self._load_all).pack(side="right")

        # Tabs
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=PAD_XL, pady=(0, PAD_LG))

        self._tab_inv     = tk.Frame(nb, bg=BG_DARK)
        self._tab_expiry  = tk.Frame(nb, bg=BG_DARK)
        self._tab_low     = tk.Frame(nb, bg=BG_DARK)

        nb.add(self._tab_inv,    text="  📋  Inventory Report  ")
        nb.add(self._tab_expiry, text="  ⏰  Expiry Report     ")
        nb.add(self._tab_low,    text="  ⚠️   Low Stock Report  ")

        if self.role == ROLE_ADMIN:
            self._tab_logs = tk.Frame(nb, bg=BG_DARK)
            nb.add(self._tab_logs, text="  📝  Activity Logs     ")
            self._build_logs_tab()

        self._build_inv_tab()
        self._build_expiry_tab()
        self._build_low_tab()

        self._load_all()

    # ── Inventory Report Tab ─────────────────────────────────────────

    def _build_inv_tab(self) -> None:
        p = self._tab_inv
        # Summary cards row
        self._inv_summary_row = tk.Frame(p, bg=BG_DARK)
        self._inv_summary_row.pack(fill="x", padx=PAD_LG, pady=PAD_SM)

        # Export button
        tk.Button(p, text="📥  Export CSV",
                  font=(FONT_FAMILY, 10, "bold"),
                  bg=SUCCESS, fg=BG_DARK,
                  activebackground="#52c562",
                  relief="flat", bd=0, cursor="hand2",
                  padx=PAD_MD, pady=3,
                  command=lambda: self._export_csv("inventory")).pack(
            anchor="e", padx=PAD_LG, pady=(0, PAD_XS))

        tree_frame = tk.Frame(p, bg=BG_DARK)
        tree_frame.pack(fill="both", expand=True, padx=PAD_LG, pady=(0, PAD_LG))

        self._inv_tree, _, _ = make_scrolled_tree(
            tree_frame,
            columns=("name", "batch", "qty", "min_stock", "expiry", "rack", "category", "type"),
            headings=("Medicine Name", "Batch #", "Qty", "Min Stock", "Expiry", "Rack", "Category", "Type"),
            col_widths=(175, 105, 60, 80, 100, 65, 120, 90),
            height=14,
        )

    # ── Expiry Report Tab ─────────────────────────────────────────────

    def _build_expiry_tab(self) -> None:
        p = self._tab_expiry
        tk.Button(p, text="📥  Export CSV",
                  font=(FONT_FAMILY, 10, "bold"),
                  bg=SUCCESS, fg=BG_DARK,
                  activebackground="#52c562",
                  relief="flat", bd=0, cursor="hand2",
                  padx=PAD_MD, pady=3,
                  command=lambda: self._export_csv("expiry")).pack(
            anchor="e", padx=PAD_LG, pady=(PAD_SM, PAD_XS))

        tree_frame = tk.Frame(p, bg=BG_DARK)
        tree_frame.pack(fill="both", expand=True, padx=PAD_LG, pady=(0, PAD_LG))

        self._expiry_tree, _, _ = make_scrolled_tree(
            tree_frame,
            columns=("name", "batch", "qty", "expiry", "days_left", "status"),
            headings=("Medicine Name", "Batch #", "Qty", "Expiry Date", "Days Left", "Status"),
            col_widths=(175, 105, 60, 100, 80, 90),
            height=14,
        )

    # ── Low Stock Report Tab ──────────────────────────────────────────

    def _build_low_tab(self) -> None:
        p = self._tab_low
        tk.Button(p, text="📥  Export CSV",
                  font=(FONT_FAMILY, 10, "bold"),
                  bg=SUCCESS, fg=BG_DARK,
                  activebackground="#52c562",
                  relief="flat", bd=0, cursor="hand2",
                  padx=PAD_MD, pady=3,
                  command=lambda: self._export_csv("low_stock")).pack(
            anchor="e", padx=PAD_LG, pady=(PAD_SM, PAD_XS))

        tree_frame = tk.Frame(p, bg=BG_DARK)
        tree_frame.pack(fill="both", expand=True, padx=PAD_LG, pady=(0, PAD_LG))

        self._low_tree, _, _ = make_scrolled_tree(
            tree_frame,
            columns=("name", "batch", "qty", "min_stock", "deficit", "level"),
            headings=("Medicine Name", "Batch #", "Qty", "Min Stock", "Deficit", "Alert Level"),
            col_widths=(175, 105, 60, 85, 70, 100),
            height=14,
        )

    # ── Activity Logs Tab (Admin) ─────────────────────────────────────

    def _build_logs_tab(self) -> None:
        p = self._tab_logs
        tk.Button(p, text="📥  Export CSV",
                  font=(FONT_FAMILY, 10, "bold"),
                  bg=SUCCESS, fg=BG_DARK,
                  activebackground="#52c562",
                  relief="flat", bd=0, cursor="hand2",
                  padx=PAD_MD, pady=3,
                  command=lambda: self._export_csv("activity_logs")).pack(
            anchor="e", padx=PAD_LG, pady=(PAD_SM, PAD_XS))

        tree_frame = tk.Frame(p, bg=BG_DARK)
        tree_frame.pack(fill="both", expand=True, padx=PAD_LG, pady=(0, PAD_LG))

        self._logs_tree, _, _ = make_scrolled_tree(
            tree_frame,
            columns=("timestamp", "username", "action", "details"),
            headings=("Timestamp", "Username", "Action", "Details"),
            col_widths=(155, 100, 130, 380),
            height=14,
        )

    # ─────────────────────────── DATA ────────────────────────────────

    def _load_all(self) -> None:
        self._load_inventory_report()
        self._load_expiry_report()
        self._load_low_stock_report()
        if self.role == ROLE_ADMIN:
            self._load_activity_logs()

    def _load_inventory_report(self) -> None:
        ok, _msg, data = report_controller.generate_inventory_report()
        items = data.get("items", []) if ok else []
        summary = data.get("summary", {}) if ok else {}

        # Update summary cards
        for w in self._inv_summary_row.winfo_children():
            w.destroy()
        for label, val, colour in [
            ("Total Medicines", summary.get("total_unique_medicines", 0), ACCENT),
            ("Total Stock",     summary.get("total_stock_quantity", 0),   SUCCESS),
            ("Low Stock",       summary.get("low_stock_count", 0),        WARNING),
            ("Expiring Soon",   summary.get("expiring_soon_count", 0),    DANGER),
        ]:
            card = tk.Frame(self._inv_summary_row, bg=BG_CARD, padx=PAD_MD, pady=PAD_XS)
            card.pack(side="left", padx=(0, PAD_SM))
            tk.Label(card, text=str(val), font=(FONT_FAMILY, 16, "bold"),
                     bg=BG_CARD, fg=colour).pack()
            tk.Label(card, text=label, font=FONT_CAPTION,
                     bg=BG_CARD, fg=TEXT_SECONDARY).pack()

        rows = []
        for m in items:
            expiry = m.get("expiry_date", "")
            if hasattr(expiry, "strftime"):
                expiry = expiry.strftime("%Y-%m-%d")
            rows.append((
                m.get("medicine_name", ""),
                m.get("batch_number", ""),
                m.get("quantity", 0),
                m.get("minimum_stock", 0),
                str(expiry),
                m.get("rack", ""),
                m.get("category", ""),
                m.get("type", ""),
            ))
        populate_tree(self._inv_tree, rows)
        self._report_data["inventory"] = rows

    def _load_expiry_report(self) -> None:
        ok, _msg, alerts = inventory_controller.get_expiry_alerts(warning_days=90)
        if not ok:
            alerts = []

        rows = []
        for a in alerts:
            expiry = a.get("expiry_date", "")
            if hasattr(expiry, "strftime"):
                expiry = expiry.strftime("%Y-%m-%d")
            rows.append((
                a.get("medicine_name", ""),
                a.get("batch_number", ""),
                a.get("quantity", 0),
                str(expiry),
                a.get("days_remaining", 0),
                a.get("expiry_status", ""),
            ))

        self._expiry_tree.delete(*self._expiry_tree.get_children())
        for row in rows:
            status = row[5]
            tag = "danger" if status == "EXPIRED" else "warning" if status == "CRITICAL" else "oddrow"
            self._expiry_tree.insert("", "end", values=row, tags=(tag,))
        self._report_data["expiry"] = rows

    def _load_low_stock_report(self) -> None:
        ok, _msg, alerts = inventory_controller.get_low_stock_alerts()
        if not ok:
            alerts = []

        rows = [
            (
                a.get("medicine_name", ""),
                a.get("batch_number", ""),
                a.get("quantity", 0),
                a.get("minimum_stock", 0),
                a.get("deficit", 0),
                a.get("alert_level", ""),
            )
            for a in alerts
        ]
        self._low_tree.delete(*self._low_tree.get_children())
        for row in rows:
            tag = "danger" if row[5] == "CRITICAL" else "warning"
            self._low_tree.insert("", "end", values=row, tags=(tag,))
        self._report_data["low_stock"] = rows

    def _load_activity_logs(self) -> None:
        ok, _msg, logs = report_controller.get_activity_logs(limit=200)
        if not ok:
            logs = []

        rows = []
        for log in logs:
            ts = log.get("timestamp", "")
            if hasattr(ts, "strftime"):
                ts = ts.strftime("%Y-%m-%d %H:%M:%S")
            rows.append((
                str(ts),
                log.get("username", ""),
                log.get("action", ""),
                log.get("details", ""),
            ))
        populate_tree(self._logs_tree, rows)
        self._report_data["activity_logs"] = rows

    # ─────────────────────────── CSV EXPORT ──────────────────────────

    def _export_csv(self, report_key: str) -> None:
        rows = self._report_data.get(report_key, [])
        if not rows:
            messagebox.showinfo("No Data", "No data available to export.", parent=self)
            return

        headers_map = {
            "inventory":     ["Medicine Name","Batch","Qty","Min Stock","Expiry","Rack","Category","Type"],
            "expiry":        ["Medicine Name","Batch","Qty","Expiry Date","Days Left","Status"],
            "low_stock":     ["Medicine Name","Batch","Qty","Min Stock","Deficit","Alert Level"],
            "activity_logs": ["Timestamp","Username","Action","Details"],
        }
        headers = headers_map.get(report_key, [])

        default_name = f"MWIMS_{report_key}_report.csv"
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Report As",
            parent=self,
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if headers:
                    writer.writerow(headers)
                writer.writerows(rows)
            messagebox.showinfo(
                "Export Successful",
                f"Report exported to:\n{path}",
                parent=self,
            )
        except OSError as exc:
            messagebox.showerror("Export Error", str(exc), parent=self)
