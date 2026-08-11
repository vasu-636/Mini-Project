"""
Main Application Shell (Dashboard + Navigation) for MWIMS.

Hosts the sidebar navigation panel and the main content area.
Each screen is loaded as a child Frame that replaces the previous one.
Role-based menu items are hidden / shown according to the logged-in user.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable, Optional

from controllers import auth_controller, inventory_controller
from middlewares import auth_middleware
from utils.constants import ROLE_ADMIN, ROLE_STAFF
from views.theme import (
    ACCENT, BG_CARD, BG_CARD_ALT, BG_DARK, BG_PANEL,
    BORDER, DANGER, FONT_BODY, FONT_CAPTION, FONT_FAMILY,
    FONT_HEADING, FONT_SMALL, FONT_TITLE,
    PAD_LG, PAD_MD, PAD_SM, PAD_XL, PAD_XS,
    SUCCESS, TEXT_DIM, TEXT_PRIMARY, TEXT_SECONDARY,
    WARNING,
)


# ─────────────────────────────────────────────────────────────────────
#  SIDEBAR NAVIGATION BUTTON
# ─────────────────────────────────────────────────────────────────────

class _NavButton(tk.Frame):
    """A single sidebar navigation item with icon + label + hover effect."""

    def __init__(
        self,
        parent: tk.Widget,
        icon: str,
        label: str,
        on_click: Callable[[], None],
        active: bool = False,
    ) -> None:
        super().__init__(parent, bg=BG_PANEL, cursor="hand2")
        self._on_click  = on_click
        self._active    = active
        self._icon      = icon
        self._label_txt = label

        self._build()
        self.set_active(active)

    def _build(self) -> None:
        self._btn = tk.Button(
            self,
            text=f"  {self._icon}  {self._label_txt}",
            font=FONT_BODY,
            bg=BG_PANEL, fg=TEXT_SECONDARY,
            activebackground=BG_CARD, activeforeground=TEXT_PRIMARY,
            relief="flat", bd=0, anchor="w",
            padx=PAD_MD, pady=PAD_SM,
            cursor="hand2",
            command=self._on_click,
        )
        self._btn.pack(fill="x")

        self._indicator = tk.Frame(self, bg=BG_PANEL, width=3)
        self._indicator.place(x=0, y=0, relheight=1)

        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        self._btn.bind("<Enter>", self._on_hover)
        self._btn.bind("<Leave>", self._on_leave)

    def _on_hover(self, _=None) -> None:
        if not self._active:
            self._btn.configure(bg=BG_CARD, fg=TEXT_PRIMARY)

    def _on_leave(self, _=None) -> None:
        if not self._active:
            self._btn.configure(bg=BG_PANEL, fg=TEXT_SECONDARY)

    def set_active(self, active: bool) -> None:
        self._active = active
        if active:
            self._btn.configure(
                bg=BG_CARD, fg=ACCENT,
                font=(FONT_FAMILY, 10, "bold"),
            )
            self._indicator.configure(bg=ACCENT)
        else:
            self._btn.configure(bg=BG_PANEL, fg=TEXT_SECONDARY, font=FONT_BODY)
            self._indicator.configure(bg=BG_PANEL)


# ─────────────────────────────────────────────────────────────────────
#  STAT CARD (Dashboard quick-stat)
# ─────────────────────────────────────────────────────────────────────

class _StatCard(tk.Frame):
    """Compact metric card for the dashboard panel."""

    def __init__(
        self,
        parent: tk.Widget,
        icon: str,
        title: str,
        value: str,
        accent: str = ACCENT,
    ) -> None:
        super().__init__(parent, bg=BG_CARD, padx=PAD_MD, pady=PAD_MD)

        tk.Label(self, text=icon, font=(FONT_FAMILY, 22),
                 bg=BG_CARD, fg=accent).pack(anchor="w")
        tk.Label(self, text=value,
                 font=(FONT_FAMILY, 18, "bold"),
                 bg=BG_CARD, fg=accent).pack(anchor="w")
        tk.Label(self, text=title,
                 font=FONT_SMALL, bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w")


# ─────────────────────────────────────────────────────────────────────
#  MAIN APPLICATION SHELL
# ─────────────────────────────────────────────────────────────────────

class MainApp(tk.Frame):
    """
    Root application shell drawn after successful login.

    Layout
    ------
    ┌────────────┬──────────────────────────────────────────┐
    │  Sidebar   │             Content Area                 │
    │ (200 px)   │          (fills remainder)               │
    └────────────┴──────────────────────────────────────────┘

    Args:
        master:   Root Tk window.
        user:     Sanitised user dict returned by auth_controller.
        on_logout: Callback to destroy shell and show login again.
    """

    def __init__(self, master: tk.Tk, user: dict[str, Any], on_logout: Callable) -> None:
        super().__init__(master, bg=BG_DARK)
        self.master    = master
        self.user      = user
        self.on_logout = on_logout
        self.role      = user.get("role", "staff")

        self._active_key: Optional[str] = None
        self._nav_buttons: dict[str, _NavButton] = {}
        self._content_frame: Optional[tk.Frame] = None

        self.pack(fill="both", expand=True)
        self._build_ui()
        self.show_section("dashboard")

    # ──────────────────────────── BUILD ──────────────────────────────

    def _build_ui(self) -> None:
        """Assemble sidebar + content area."""
        # ── Top header bar ──────────────────────────────────────────
        self._build_header()

        # ── Body row (sidebar + content) ────────────────────────────
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True)

        self._sidebar = tk.Frame(body, bg=BG_PANEL, width=215)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        # Vertical separator
        tk.Frame(body, bg=BORDER, width=1).pack(side="left", fill="y")

        self._content_area = tk.Frame(body, bg=BG_DARK)
        self._content_area.pack(side="left", fill="both", expand=True)

        self._build_sidebar()

    def _build_header(self) -> None:
        """Top header bar with brand + user info."""
        hdr = tk.Frame(self, bg=BG_PANEL, height=48)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        # Brand
        tk.Label(hdr, text="💊 MWIMS",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=BG_PANEL, fg=TEXT_PRIMARY).pack(side="left", padx=PAD_MD)

        # Right side: role badge + username
        right = tk.Frame(hdr, bg=BG_PANEL)
        right.pack(side="right", padx=PAD_MD)

        role_colour = {
            "admin":   ACCENT,
            "staff":   SUCCESS,
            "auditor": WARNING,
        }.get(self.role, TEXT_SECONDARY)

        tk.Label(right,
                 text=f"  {self.role.upper()}  ",
                 font=FONT_CAPTION,
                 bg=role_colour, fg=BG_DARK).pack(side="right", padx=(PAD_SM, 0))
        tk.Label(right,
                 text=f"👤  {self.user.get('username', 'User')}",
                 font=FONT_BODY,
                 bg=BG_PANEL, fg=TEXT_SECONDARY).pack(side="right", padx=PAD_SM)

        # Separator
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

    def _build_sidebar(self) -> None:
        """Populate the sidebar with role-filtered navigation buttons."""
        # Section header
        tk.Label(
            self._sidebar,
            text="NAVIGATION",
            font=(FONT_FAMILY, 8, "bold"),
            bg=BG_PANEL, fg=TEXT_DIM,
        ).pack(anchor="w", padx=PAD_MD, pady=(PAD_MD, PAD_XS))

        # Nav entries: (key, icon, label, min_role) where min_role=None means all roles
        nav_items = [
            ("dashboard",   "🏠", "Dashboard",        None),
            ("medicines",   "💊", "Medicines",         None),
            ("inventory",   "📦", "Inventory",         None),
            ("warehouse",   "🏭", "Warehouse",         None),
            ("expiry",      "⏰", "Expiry Alerts",     None),
            ("low_stock",   "⚠️", "Low Stock",         None),
            ("reports",     "📊", "Reports",           None),
            ("users",       "👥", "User Management",   ROLE_ADMIN),
        ]

        for key, icon, label, required_role in nav_items:
            if required_role and self.role != required_role:
                continue  # hide items the role cannot access

            btn = _NavButton(
                self._sidebar, icon, label,
                on_click=lambda k=key: self.show_section(k),
            )
            btn.pack(fill="x")
            self._nav_buttons[key] = btn

        # Spacer
        tk.Frame(self._sidebar, bg=BG_PANEL).pack(fill="both", expand=True)

        # Divider
        tk.Frame(self._sidebar, bg=BORDER, height=1).pack(fill="x", padx=PAD_SM)

        # Settings
        settings_btn = _NavButton(
            self._sidebar, "⚙️", "Settings",
            on_click=lambda: self.show_section("settings"),
        )
        settings_btn.pack(fill="x")
        self._nav_buttons["settings"] = settings_btn

        # Logout
        logout_btn = tk.Button(
            self._sidebar,
            text="  🚪  Logout",
            font=FONT_BODY,
            bg=BG_PANEL, fg=DANGER,
            activebackground=BG_CARD, activeforeground=DANGER,
            relief="flat", bd=0, anchor="w",
            padx=PAD_MD, pady=PAD_SM,
            cursor="hand2",
            command=self._handle_logout,
        )
        logout_btn.pack(fill="x", pady=(0, PAD_SM))

    # ──────────────────────────── NAVIGATION ─────────────────────────

    def show_section(self, key: str) -> None:
        """
        Destroy current content frame and load the requested screen.

        This is the central navigation dispatcher.
        """
        # Deactivate previous, activate new
        if self._active_key and self._active_key in self._nav_buttons:
            self._nav_buttons[self._active_key].set_active(False)
        if key in self._nav_buttons:
            self._nav_buttons[key].set_active(True)
        self._active_key = key

        # Destroy old content
        if self._content_frame:
            self._content_frame.destroy()
            self._content_frame = None

        # Lazy-import to avoid circular dependencies and keep startup fast
        view_frame = self._load_section(key)
        if view_frame:
            self._content_frame = view_frame
            self._content_frame.pack(fill="both", expand=True)

    def _load_section(self, key: str) -> Optional[tk.Frame]:
        """Import and instantiate the matching screen Frame."""
        role = self.role

        if key == "dashboard":
            return self._build_dashboard()

        if key == "medicines":
            from views.medicine_view import MedicineView
            return MedicineView(self._content_area, self.user)

        if key == "inventory":
            from views.inventory_view import InventoryView
            return InventoryView(self._content_area, self.user)

        if key == "warehouse":
            from views.warehouse_view import WarehouseView
            return WarehouseView(self._content_area, self.user)

        if key == "expiry":
            from views.expiry_view import ExpiryView
            return ExpiryView(self._content_area, self.user)

        if key == "low_stock":
            from views.low_stock_view import LowStockView
            return LowStockView(self._content_area, self.user)

        if key == "reports":
            from views.reports_view import ReportsView
            return ReportsView(self._content_area, self.user)

        if key == "users" and role == ROLE_ADMIN:
            from views.user_management_view import UserManagementView
            return UserManagementView(self._content_area, self.user)

        if key == "settings":
            from views.settings_view import SettingsView
            return SettingsView(self._content_area, self.user, self._handle_logout)

        return self._build_dashboard()

    # ──────────────────────────── DASHBOARD ──────────────────────────

    def _build_dashboard(self) -> tk.Frame:
        """Build the dashboard overview screen inline."""
        frame = tk.Frame(self._content_area, bg=BG_DARK)

        # Title bar
        title_bar = tk.Frame(frame, bg=BG_DARK)
        title_bar.pack(fill="x", padx=PAD_XL, pady=(PAD_LG, PAD_MD))

        tk.Label(title_bar, text="Dashboard",
                 font=(FONT_FAMILY, 18, "bold"),
                 bg=BG_DARK, fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(title_bar,
                 text=f"Welcome back, {self.user.get('username', 'User')} 👋",
                 font=FONT_BODY, bg=BG_DARK, fg=TEXT_SECONDARY).pack(anchor="w")

        # Stat cards row
        cards_row = tk.Frame(frame, bg=BG_DARK)
        cards_row.pack(fill="x", padx=PAD_XL, pady=(0, PAD_LG))

        # Fetch metrics from backend
        metrics: dict = {}
        try:
            ok, _msg, metrics = inventory_controller.get_inventory_dashboard_metrics()
        except Exception:
            pass

        stats_cfg = [
            ("📦", "Total Medicines",   str(metrics.get("total_unique_medicines", 0)),    ACCENT),
            ("🔢", "Total Stock Units", str(metrics.get("total_stock_quantity", 0)),       SUCCESS),
            ("⚠️", "Low Stock Items",   str(metrics.get("low_stock_count", 0)),            WARNING),
            ("⏰", "Expiry Alerts",     str(metrics.get("expiring_soon_count", 0)),        DANGER),
        ]

        for icon, title, value, colour in stats_cfg:
            card = _StatCard(cards_row, icon, title, value, colour)
            card.pack(side="left", padx=(0, PAD_MD), ipadx=PAD_MD, ipady=PAD_SM)

        # Divider
        tk.Frame(frame, bg=BORDER, height=1).pack(fill="x", padx=PAD_XL)

        # Quick-action buttons
        qa_frame = tk.Frame(frame, bg=BG_DARK)
        qa_frame.pack(fill="x", padx=PAD_XL, pady=PAD_LG)

        tk.Label(qa_frame, text="Quick Actions",
                 font=FONT_HEADING, bg=BG_DARK, fg=TEXT_PRIMARY).pack(anchor="w", pady=(0, PAD_SM))

        btn_row = tk.Frame(qa_frame, bg=BG_DARK)
        btn_row.pack(anchor="w")

        qa_actions = [
            ("💊 Medicines",   "medicines",  ACCENT),
            ("📦 Inventory",   "inventory",  SUCCESS),
            ("📊 Reports",     "reports",    WARNING),
            ("⏰ Expiry Check","expiry",      DANGER),
        ]

        for label, section, colour in qa_actions:
            btn = tk.Button(
                btn_row, text=label,
                font=(FONT_FAMILY, 10, "bold"),
                bg=colour, fg=BG_DARK if colour in (SUCCESS, WARNING) else TEXT_PRIMARY,
                activebackground=colour,
                relief="flat", bd=0, cursor="hand2",
                padx=PAD_MD, pady=PAD_SM,
                command=lambda s=section: self.show_section(s),
            )
            btn.pack(side="left", padx=(0, PAD_SM))

        # Summary table (all metrics as key-value)
        if metrics:
            tk.Frame(frame, bg=BORDER, height=1).pack(fill="x", padx=PAD_XL)
            detail_frame = tk.Frame(frame, bg=BG_DARK)
            detail_frame.pack(fill="x", padx=PAD_XL, pady=PAD_LG)
            tk.Label(detail_frame, text="Inventory Summary",
                     font=FONT_HEADING, bg=BG_DARK, fg=TEXT_PRIMARY).pack(anchor="w", pady=(0, PAD_SM))

            for k, v in metrics.items():
                row = tk.Frame(detail_frame, bg=BG_DARK)
                row.pack(anchor="w", pady=1)
                tk.Label(row, text=f"  {k.replace('_', ' ').title()}:",
                         font=FONT_BODY, bg=BG_DARK, fg=TEXT_SECONDARY, width=28, anchor="w").pack(side="left")
                tk.Label(row, text=str(v),
                         font=(FONT_FAMILY, 10, "bold"),
                         bg=BG_DARK, fg=TEXT_PRIMARY).pack(side="left")

        return frame

    # ──────────────────────────── ACTIONS ────────────────────────────

    def _handle_logout(self) -> None:
        """Confirm logout, call backend, trigger on_logout callback."""
        if messagebox.askyesno(
            "Confirm Logout",
            "Are you sure you want to logout?",
            parent=self,
        ):
            auth_controller.logout_user()
            self.destroy()
            self.on_logout()
