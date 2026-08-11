"""
Login & Registration Screen View for MWIMS.

Displays a professional dark-themed authentication screen.
Integrates with auth_controller.login_user() and auth_controller.register_user().
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from controllers import auth_controller
from initialize_db import initialize_database
from utils.constants import VALID_ROLES
from views.theme import (
    ACCENT, BG_CARD, BG_DARK, BORDER, DANGER, FONT_BODY,
    FONT_CAPTION, FONT_FAMILY, FONT_HEADING, FONT_TITLE,
    INPUT_BG, PAD_LG, PAD_MD, PAD_SM, PAD_XL, PAD_XS,
    SUCCESS, TEXT_DIM, TEXT_PRIMARY, TEXT_SECONDARY,
    apply_theme, make_button, make_entry, make_label,
)


class LoginView(tk.Frame):
    """
    Full-screen login & registration page rendered inside the root Tk window.

    Args:
        master: The root Tk application window.
        on_success: Callback invoked with the authenticated user dict on success.
    """

    def __init__(self, master: tk.Tk, on_success) -> None:
        super().__init__(master, background=BG_DARK)
        self.master = master
        self.on_success = on_success

        # Login state variables
        self._var_identifier = tk.StringVar()
        self._var_password    = tk.StringVar()
        self._var_status      = tk.StringVar()

        # Registration state variables
        self._var_reg_username         = tk.StringVar()
        self._var_reg_email            = tk.StringVar()
        self._var_reg_password         = tk.StringVar()
        self._var_reg_confirm_password = tk.StringVar()
        self._var_reg_role             = tk.StringVar(value="staff")
        self._var_reg_status           = tk.StringVar()

        self._build_ui()

    # ─────────────────────────── UI BUILD ────────────────────────────

    def _build_ui(self) -> None:
        """Lay out all login & registration screen widgets."""
        self.pack(fill="both", expand=True)
        self.configure(background=BG_DARK)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # ── Outer centering container ────────────────────────────────
        container = tk.Frame(self, bg=BG_DARK)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # ── Logo / branding banner ───────────────────────────────────
        banner = tk.Frame(container, bg=ACCENT, width=400, height=6)
        banner.pack(fill="x")

        # ── Card ─────────────────────────────────────────────────────
        card = tk.Frame(
            container, bg=BG_CARD,
            padx=PAD_XL, pady=PAD_XL,
            width=400,
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

        # ── Frames for Login and Register ────────────────────────────
        self._login_frame = tk.Frame(card, bg=BG_CARD)
        self._register_frame = tk.Frame(card, bg=BG_CARD)

        self._build_login_form(self._login_frame)
        self._build_register_form(self._register_frame)

        # ── Footer ───────────────────────────────────────────────────
        tk.Label(
            container,
            text="MWIMS  ·  v1.0  ·  Medicine Warehouse Inventory Management System",
            font=FONT_CAPTION, bg=BG_DARK, fg=TEXT_DIM,
        ).pack(pady=(PAD_SM, 0))

        # Default to login mode
        self._show_login_mode()

    # ──────────────────────── FORM BUILDERS ─────────────────────────

    def _build_login_form(self, parent: tk.Frame) -> None:
        """Build the Sign In form layout."""
        # Sign-in heading
        tk.Label(parent, text="Sign in to your account",
                 font=FONT_HEADING, bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w", pady=(0, PAD_SM))

        # Username / Email
        self._field_label(parent, "Username or Email")
        self._entry_identifier = self._make_dark_entry(parent, self._var_identifier)
        self._entry_identifier.pack(fill="x", pady=(0, PAD_MD))

        # Password
        self._field_label(parent, "Password")
        self._entry_password = self._make_dark_entry(
            parent, self._var_password, show="●"
        )
        self._entry_password.pack(fill="x", pady=(0, PAD_SM))

        # Status message
        self._lbl_status = tk.Label(
            parent, textvariable=self._var_status,
            font=FONT_CAPTION, bg=BG_CARD, fg=DANGER,
            wraplength=340, justify="left",
        )
        self._lbl_status.pack(anchor="w", pady=(0, PAD_MD))

        # Login button
        btn_login = tk.Button(
            parent, text="  🔐  Sign In",
            font=(FONT_FAMILY, 11, "bold"),
            bg=ACCENT, fg=TEXT_PRIMARY,
            activebackground="#388AFF", activeforeground=TEXT_PRIMARY,
            relief="flat", bd=0, cursor="hand2",
            command=self._handle_login, pady=PAD_SM,
        )
        btn_login.pack(fill="x", pady=(0, PAD_SM))

        # Register switch link
        btn_switch_reg = tk.Button(
            parent, text="Don't have an account? Register here",
            font=FONT_CAPTION,
            bg=BG_CARD, fg=ACCENT,
            activebackground=BG_CARD, activeforeground="#388AFF",
            relief="flat", bd=0, cursor="hand2",
            command=self._show_register_mode,
        )
        btn_switch_reg.pack(pady=(0, PAD_SM))

        # Exit button
        btn_exit = tk.Button(
            parent, text="Exit Application",
            font=FONT_CAPTION,
            bg=BG_CARD, fg=TEXT_DIM,
            activebackground=BG_CARD, activeforeground=TEXT_SECONDARY,
            relief="flat", bd=0, cursor="hand2",
            command=self.master.destroy,
        )
        btn_exit.pack()

    def _build_register_form(self, parent: tk.Frame) -> None:
        """Build the Registration form layout."""
        # Registration heading
        tk.Label(parent, text="Create a new account",
                 font=FONT_HEADING, bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w", pady=(0, PAD_SM))

        # Username
        self._field_label(parent, "Username")
        self._entry_reg_username = self._make_dark_entry(parent, self._var_reg_username)
        self._entry_reg_username.pack(fill="x", pady=(0, PAD_XS))

        # Email
        self._field_label(parent, "Email Address")
        self._entry_reg_email = self._make_dark_entry(parent, self._var_reg_email)
        self._entry_reg_email.pack(fill="x", pady=(0, PAD_XS))

        # Password
        self._field_label(parent, "Password")
        self._entry_reg_password = self._make_dark_entry(
            parent, self._var_reg_password, show="●"
        )
        self._entry_reg_password.pack(fill="x", pady=(0, PAD_XS))

        # Confirm Password
        self._field_label(parent, "Confirm Password")
        self._entry_reg_confirm_password = self._make_dark_entry(
            parent, self._var_reg_confirm_password, show="●"
        )
        self._entry_reg_confirm_password.pack(fill="x", pady=(0, PAD_XS))

        # Role Selection
        self._field_label(parent, "Account Role")
        cmb_role = ttk.Combobox(
            parent, textvariable=self._var_reg_role,
            values=list(VALID_ROLES), state="readonly",
        )
        cmb_role.pack(fill="x", pady=(0, PAD_SM))

        # Status message
        self._lbl_reg_status = tk.Label(
            parent, textvariable=self._var_reg_status,
            font=FONT_CAPTION, bg=BG_CARD, fg=DANGER,
            wraplength=340, justify="left",
        )
        self._lbl_reg_status.pack(anchor="w", pady=(0, PAD_SM))

        # Register button
        btn_register = tk.Button(
            parent, text="  📝  Register Account",
            font=(FONT_FAMILY, 11, "bold"),
            bg=ACCENT, fg=TEXT_PRIMARY,
            activebackground="#388AFF", activeforeground=TEXT_PRIMARY,
            relief="flat", bd=0, cursor="hand2",
            command=self._handle_register, pady=PAD_SM,
        )
        btn_register.pack(fill="x", pady=(0, PAD_SM))

        # Login switch link
        btn_switch_login = tk.Button(
            parent, text="Already have an account? Sign In",
            font=FONT_CAPTION,
            bg=BG_CARD, fg=ACCENT,
            activebackground=BG_CARD, activeforeground="#388AFF",
            relief="flat", bd=0, cursor="hand2",
            command=self._show_login_mode,
        )
        btn_switch_login.pack()

    # ──────────────────────── MODE SWITCHING ────────────────────────

    def _show_login_mode(self) -> None:
        """Switch view card to Login mode."""
        self._register_frame.pack_forget()
        self._login_frame.pack(fill="x", expand=True)
        self.master.bind("<Return>", lambda _: self._handle_login())
        if hasattr(self, "_entry_identifier"):
            self._entry_identifier.focus_set()

    def _show_register_mode(self) -> None:
        """Switch view card to Register mode."""
        self._login_frame.pack_forget()
        self._register_frame.pack(fill="x", expand=True)
        self.master.bind("<Return>", lambda _: self._handle_register())
        if hasattr(self, "_entry_reg_username"):
            self._entry_reg_username.focus_set()

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
        """Validate inputs then call the auth controller for login."""
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

    def _handle_register(self) -> None:
        """Validate registration inputs and call auth_controller.register_user."""
        username = self._var_reg_username.get().strip()
        email    = self._var_reg_email.get().strip()
        password = self._var_reg_password.get().strip()
        confirm  = self._var_reg_confirm_password.get().strip()
        role     = self._var_reg_role.get().strip()

        if not username:
            self._set_reg_status("Username is required.")
            return
        if not email:
            self._set_reg_status("Email address is required.")
            return
        if not password:
            self._set_reg_status("Password is required.")
            return
        if password != confirm:
            self._set_reg_status("Passwords do not match.")
            return

        self._set_reg_status("Registering account…", colour=TEXT_SECONDARY)
        self.update_idletasks()

        success, msg = auth_controller.register_user(username, email, password, role)

        if success:
            self._var_identifier.set(username)
            self._var_password.set("")
            self._var_reg_username.set("")
            self._var_reg_email.set("")
            self._var_reg_password.set("")
            self._var_reg_confirm_password.set("")
            self._var_reg_role.set("staff")

            self._show_login_mode()
            self._set_status(f"User '{username}' registered! Please sign in.", colour=SUCCESS)
            self._entry_password.focus_set()
        else:
            self._set_reg_status(msg or "Registration failed.")

    def _set_status(self, msg: str, colour: str = DANGER) -> None:
        self._lbl_status.configure(fg=colour)
        self._var_status.set(msg)

    def _set_reg_status(self, msg: str, colour: str = DANGER) -> None:
        self._lbl_reg_status.configure(fg=colour)
        self._var_reg_status.set(msg)

