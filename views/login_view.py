"""
Login Screen View for MWIMS.

Displays a professional dark-themed login dialog.
Integrates with auth_controller.login_user() only.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from controllers import auth_controller
from initialize_db import initialize_database
from views.theme import (
    ACCENT, BG_CARD, BG_DARK, BORDER, DANGER, FONT_BODY,
    FONT_CAPTION, FONT_FAMILY, FONT_HEADING, FONT_TITLE,
    INPUT_BG, PAD_LG, PAD_MD, PAD_SM, PAD_XL, PAD_XS,
    SUCCESS, TEXT_DIM, TEXT_PRIMARY, TEXT_SECONDARY,
    apply_theme, make_button, make_entry, make_label,
)


class LoginView(tk.Frame):
    """
    Full-screen login page rendered inside the root Tk window.

    Args:
        master: The root Tk application window.
        on_success: Callback invoked with the authenticated user dict on success.
    """

    def __init__(self, master: tk.Tk, on_success) -> None:
        super().__init__(master, background=BG_DARK)
        self.master = master
        self.on_success = on_success

        self._var_identifier = tk.StringVar()
        self._var_password    = tk.StringVar()
        self._var_status      = tk.StringVar()

        self._build_ui()

    # ─────────────────────────── UI BUILD ────────────────────────────

    def _build_ui(self) -> None:
        """Lay out all login screen widgets."""
        self.pack(fill="both", expand=True)
        self.configure(background=BG_DARK)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # ── Outer centering container ────────────────────────────────
        container = tk.Frame(self, bg=BG_DARK)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # ── Logo / branding banner ───────────────────────────────────
        banner = tk.Frame(container, bg=ACCENT, width=380, height=6)
        banner.pack(fill="x")

        # ── Card ─────────────────────────────────────────────────────
        card = tk.Frame(
            container, bg=BG_CARD,
            padx=PAD_XL, pady=PAD_XL,
            width=380,
        )
        card.pack()

        # Logo icon row
        icon_row = tk.Frame(card, bg=BG_CARD)
        icon_row.pack(pady=(0, PAD_MD))

        tk.Label(
            icon_row, text="💊", font=(FONT_FAMILY, 36),
            bg=BG_CARD, fg=ACCENT,
        ).pack(side="left", padx=(0, PAD_SM))

        brand_col = tk.Frame(icon_row, bg=BG_CARD)
        brand_col.pack(side="left", anchor="w")
        tk.Label(brand_col, text="MWIMS", font=(FONT_FAMILY, 22, "bold"),
                 bg=BG_CARD, fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(brand_col, text="Medicine Warehouse Inventory", font=FONT_CAPTION,
                 bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w")

        # Divider
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", pady=(0, PAD_MD))

        # Sign-in heading
        tk.Label(card, text="Sign in to your account",
                 font=FONT_HEADING, bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w")

        # ── Username / Email ──────────────────────────────────────────
        self._field_label(card, "Username or Email")
        self._var_identifier = tk.StringVar()
        self._entry_identifier = self._make_dark_entry(card, self._var_identifier)
        self._entry_identifier.pack(fill="x", pady=(0, PAD_MD))

        # ── Password ─────────────────────────────────────────────────
        self._field_label(card, "Password")
        self._var_password = tk.StringVar()
        self._entry_password = self._make_dark_entry(
            card, self._var_password, show="●"
        )
        self._entry_password.pack(fill="x", pady=(0, PAD_SM))

        # ── Status message ───────────────────────────────────────────
        self._lbl_status = tk.Label(
            card, textvariable=self._var_status,
            font=FONT_CAPTION, bg=BG_CARD, fg=DANGER,
            wraplength=340, justify="left",
        )
        self._lbl_status.pack(anchor="w", pady=(0, PAD_MD))

        # ── Login button ─────────────────────────────────────────────
        btn_login = tk.Button(
            card, text="  🔐  Sign In",
            font=(FONT_FAMILY, 11, "bold"),
            bg=ACCENT, fg=TEXT_PRIMARY,
            activebackground="#388AFF", activeforeground=TEXT_PRIMARY,
            relief="flat", bd=0, cursor="hand2",
            command=self._handle_login, pady=PAD_SM,
        )
        btn_login.pack(fill="x", pady=(0, PAD_SM))

        # ── Exit button ──────────────────────────────────────────────
        btn_exit = tk.Button(
            card, text="Exit Application",
            font=FONT_CAPTION,
            bg=BG_CARD, fg=TEXT_DIM,
            activebackground=BG_CARD, activeforeground=TEXT_SECONDARY,
            relief="flat", bd=0, cursor="hand2",
            command=self.master.destroy,
        )
        btn_exit.pack()

        # ── Footer ───────────────────────────────────────────────────
        tk.Label(
            container,
            text="MWIMS  ·  v1.0  ·  Medicine Warehouse Inventory Management System",
            font=FONT_CAPTION, bg=BG_DARK, fg=TEXT_DIM,
        ).pack(pady=(PAD_SM, 0))

        # Bind Enter key
        self.master.bind("<Return>", lambda _: self._handle_login())
        self._entry_identifier.focus_set()

    # ─────────────────────────── HELPERS ─────────────────────────────

    @staticmethod
    def _field_label(parent: tk.Frame, text: str) -> None:
        tk.Label(parent, text=text, font=FONT_CAPTION,
                 bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))

    @staticmethod
    def _make_dark_entry(parent: tk.Frame,
                         var: tk.StringVar,
                         show: str = "") -> tk.Entry:
        entry = tk.Entry(
            parent, textvariable=var, show=show,
            font=FONT_BODY,
            bg=INPUT_BG, fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        entry.configure({"disabledforeground": TEXT_SECONDARY})
        return entry

    # ─────────────────────────── ACTIONS ─────────────────────────────

    def _handle_login(self) -> None:
        """Validate inputs then call the auth controller."""
        identifier = self._var_identifier.get().strip()
        password   = self._var_password.get().strip()

        if not identifier:
            self._set_status("Username or Email is required.")
            return
        if not password:
            self._set_status("Password is required.")
            return

        self._set_status("Authenticating…", colour=TEXT_SECONDARY)
        self.update_idletasks()

        success, msg, user = auth_controller.login_user(identifier, password)

        if success and user:
            self._set_status("Login successful!", colour=SUCCESS)
            self.master.unbind("<Return>")
            self.after(300, lambda: self.on_success(user))
        else:
            self._set_status(msg or "Login failed.")
            self._entry_password.delete(0, "end")
            self._entry_identifier.focus_set()

    def _set_status(self, msg: str, colour: str = DANGER) -> None:
        self._lbl_status.configure(fg=colour)
        self._var_status.set(msg)
