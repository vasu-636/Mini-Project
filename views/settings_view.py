"""
Settings View for MWIMS.

Provides:
  • Profile summary card
  • Change Password form
  • Logout button

Integrates with auth_controller.change_password() only.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Any, Callable

from controllers import auth_controller
from views.theme import (
    ACCENT, BG_CARD, BG_DARK, BORDER, DANGER,
    FONT_BODY, FONT_CAPTION, FONT_FAMILY, FONT_HEADING,
    INPUT_BG, PAD_LG, PAD_MD, PAD_SM, PAD_XL, PAD_XS,
    SUCCESS, TEXT_DIM, TEXT_PRIMARY, TEXT_SECONDARY, WARNING,
)


class SettingsView(tk.Frame):
    """
    Settings screen with profile info and password change form.

    Args:
        parent:     Content area widget.
        user:       Current user dict.
        on_logout:  Callback invoked to perform logout flow.
    """

    def __init__(
        self,
        parent: tk.Widget,
        user: dict[str, Any],
        on_logout: Callable,
    ) -> None:
        super().__init__(parent, bg=BG_DARK)
        self.user      = user
        self.on_logout = on_logout
        self._build_ui()

    # ─────────────────────────── BUILD ───────────────────────────────

    def _build_ui(self) -> None:
        # Title
        title_bar = tk.Frame(self, bg=BG_DARK)
        title_bar.pack(fill="x", padx=PAD_XL, pady=(PAD_LG, PAD_SM))
        tk.Label(title_bar, text="⚙️  Settings",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg=BG_DARK, fg=TEXT_PRIMARY).pack(side="left")

        content = tk.Frame(self, bg=BG_DARK)
        content.pack(fill="both", expand=True, padx=PAD_XL)

        # ── Profile Card ──────────────────────────────────────────────
        profile_card = tk.Frame(content, bg=BG_CARD, padx=PAD_XL, pady=PAD_LG)
        profile_card.pack(fill="x", pady=(0, PAD_LG))

        role = self.user.get("role", "staff")
        role_colour = {"admin": ACCENT, "staff": SUCCESS, "auditor": WARNING}.get(role, TEXT_SECONDARY)

        tk.Label(profile_card, text="👤", font=(FONT_FAMILY, 36),
                 bg=BG_CARD, fg=role_colour).pack(side="left", padx=(0, PAD_LG))

        info = tk.Frame(profile_card, bg=BG_CARD)
        info.pack(side="left", anchor="w")

        tk.Label(info, text=self.user.get("username", "Unknown"),
                 font=(FONT_FAMILY, 15, "bold"),
                 bg=BG_CARD, fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(info, text=self.user.get("email", ""),
                 font=FONT_BODY, bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w")
        tk.Label(info,
                 text=f"  {role.upper()}  ",
                 font=(FONT_FAMILY, 9, "bold"),
                 bg=role_colour,
                 fg=BG_DARK if role in ("staff", "auditor") else TEXT_PRIMARY,
                 padx=PAD_SM, pady=2).pack(anchor="w", pady=(PAD_XS, 0))

        # ── Change Password ───────────────────────────────────────────
        pw_card = tk.Frame(content, bg=BG_CARD, padx=PAD_XL, pady=PAD_LG)
        pw_card.pack(fill="x", pady=(0, PAD_LG))

        tk.Label(pw_card, text="🔒  Change Password",
                 font=(FONT_FAMILY, 12, "bold"),
                 bg=BG_CARD, fg=TEXT_PRIMARY).pack(anchor="w", pady=(0, PAD_MD))

        # Separator
        tk.Frame(pw_card, bg=BORDER, height=1).pack(fill="x", pady=(0, PAD_MD))

        # Current Password
        self._var_current_pw  = tk.StringVar()
        self._var_new_pw      = tk.StringVar()
        self._var_confirm_pw  = tk.StringVar()
        self._var_pw_status   = tk.StringVar()

        for label, var in [
            ("Current Password",      self._var_current_pw),
            ("New Password",          self._var_new_pw),
            ("Confirm New Password",  self._var_confirm_pw),
        ]:
            tk.Label(pw_card, text=label, font=FONT_CAPTION,
                     bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w", pady=(PAD_XS, 0))
            tk.Entry(
                pw_card, textvariable=var, show="●", width=30,
                font=FONT_BODY,
                bg=INPUT_BG, fg=TEXT_PRIMARY,
                insertbackground=TEXT_PRIMARY,
                relief="flat", bd=0,
                highlightthickness=1,
                highlightbackground=BORDER,
                highlightcolor=ACCENT,
            ).pack(anchor="w", fill="x", pady=(2, PAD_XS), ipady=4)

        # Status label
        self._lbl_pw_status = tk.Label(
            pw_card, textvariable=self._var_pw_status,
            font=FONT_CAPTION, bg=BG_CARD, fg=DANGER, wraplength=360,
        )
        self._lbl_pw_status.pack(anchor="w", pady=(0, PAD_SM))

        # Save button
        tk.Button(
            pw_card, text="💾  Update Password",
            font=(FONT_FAMILY, 10, "bold"),
            bg=ACCENT, fg=TEXT_PRIMARY,
            activebackground="#388AFF",
            relief="flat", bd=0, cursor="hand2",
            padx=PAD_MD, pady=PAD_XS,
            command=self._change_password,
        ).pack(anchor="w")

        # ── Danger Zone ───────────────────────────────────────────────
        danger_card = tk.Frame(content, bg=BG_CARD, padx=PAD_XL, pady=PAD_LG)
        danger_card.pack(fill="x", pady=(0, PAD_LG))

        tk.Label(danger_card, text="⚠️  Session",
                 font=(FONT_FAMILY, 12, "bold"),
                 bg=BG_CARD, fg=TEXT_PRIMARY).pack(anchor="w", pady=(0, PAD_SM))
        tk.Frame(danger_card, bg=BORDER, height=1).pack(fill="x", pady=(0, PAD_MD))

        tk.Button(
            danger_card, text="🚪  Logout",
            font=(FONT_FAMILY, 10, "bold"),
            bg=DANGER, fg=TEXT_PRIMARY,
            activebackground="#ff6b63",
            relief="flat", bd=0, cursor="hand2",
            padx=PAD_MD, pady=PAD_XS,
            command=self.on_logout,
        ).pack(anchor="w")

    # ─────────────────────────── ACTIONS ─────────────────────────────

    def _change_password(self) -> None:
        current = self._var_current_pw.get().strip()
        new_pw  = self._var_new_pw.get().strip()
        confirm = self._var_confirm_pw.get().strip()

        # Frontend validation
        if not current:
            self._set_pw_status("Current password is required.")
            return
        if not new_pw:
            self._set_pw_status("New password is required.")
            return
        if len(new_pw) < 6:
            self._set_pw_status("New password must be at least 6 characters.")
            return
        if new_pw != confirm:
            self._set_pw_status("New password and confirmation do not match.")
            return

        ok, msg = auth_controller.change_password(
            self.user.get("_id", ""), current, new_pw
        )
        if ok:
            self._set_pw_status(msg, colour=SUCCESS)
            self._var_current_pw.set("")
            self._var_new_pw.set("")
            self._var_confirm_pw.set("")
            messagebox.showinfo("Password Changed", msg, parent=self)
        else:
            self._set_pw_status(msg)

    def _set_pw_status(self, msg: str, colour: str = DANGER) -> None:
        self._lbl_pw_status.configure(fg=colour)
        self._var_pw_status.set(msg)
