"""
User Management View for MWIMS (Admin Only).

Provides:
  • List all users
  • Create new user
  • Deactivate user account (soft-delete)
  • Search / filter users

All operations go through auth_controller only.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Optional

from controllers import auth_controller
from utils.constants import ROLE_ADMIN, VALID_ROLES
from views.theme import (
    ACCENT, BG_CARD, BG_DARK, BORDER, DANGER,
    FONT_BODY, FONT_CAPTION, FONT_FAMILY, FONT_HEADING,
    INPUT_BG, PAD_LG, PAD_MD, PAD_SM, PAD_XL, PAD_XS,
    SUCCESS, TEXT_DIM, TEXT_PRIMARY, TEXT_SECONDARY, WARNING,
    make_scrolled_tree, populate_tree,
)


# ─────────────────────────────────────────────────────────────────────
#  CREATE USER DIALOG
# ─────────────────────────────────────────────────────────────────────

class _CreateUserDialog(tk.Toplevel):
    """Modal dialog for registering a new user account."""

    def __init__(self, parent: tk.Widget, on_saved) -> None:
        super().__init__(parent)
        self.on_saved = on_saved
        self.title("Create New User")
        self.configure(bg=BG_CARD)
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        self._var_username = tk.StringVar()
        self._var_email    = tk.StringVar()
        self._var_password = tk.StringVar()
        self._var_role     = tk.StringVar(value="staff")
        self._var_status   = tk.StringVar()

        self._build()
        self._centre()

    def _build(self) -> None:
        tk.Frame(self, bg=ACCENT, height=5).pack(fill="x")

        hdr = tk.Frame(self, bg=BG_CARD, padx=PAD_LG, pady=PAD_MD)
        hdr.pack(fill="x")
        tk.Label(hdr, text="👤  Create New User",
                 font=(FONT_FAMILY, 12, "bold"),
                 bg=BG_CARD, fg=TEXT_PRIMARY).pack(anchor="w")

        form = tk.Frame(self, bg=BG_CARD, padx=PAD_LG, pady=PAD_SM)
        form.pack(fill="x")

        fields = [
            ("Username",  self._var_username, "entry",  None),
            ("Email",     self._var_email,    "entry",  None),
            ("Password",  self._var_password, "entry",  None),
            ("Role",      self._var_role,     "combo",  list(VALID_ROLES)),
        ]

        for idx, (label, var, kind, opts) in enumerate(fields):
            lbl_row = tk.Frame(form, bg=BG_CARD)
            lbl_row.pack(fill="x", pady=(PAD_XS, 0))
            tk.Label(lbl_row, text=label, font=FONT_CAPTION,
                     bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w")

            if kind == "combo":
                w = ttk.Combobox(form, textvariable=var,
                                 values=opts, width=28, state="readonly")
            else:
                show = "●" if label == "Password" else ""
                w = tk.Entry(
                    form, textvariable=var, show=show, width=30,
                    font=FONT_BODY,
                    bg=INPUT_BG, fg=TEXT_PRIMARY,
                    insertbackground=TEXT_PRIMARY,
                    relief="flat", bd=0,
                    highlightthickness=1,
                    highlightbackground=BORDER,
                    highlightcolor=ACCENT,
                )
            w.pack(fill="x", pady=(2, PAD_XS))

        tk.Label(form, textvariable=self._var_status,
                 font=FONT_CAPTION, bg=BG_CARD, fg=DANGER,
                 wraplength=340).pack(anchor="w", pady=(0, PAD_XS))

        btn_row = tk.Frame(self, bg=BG_CARD, padx=PAD_LG, pady=PAD_MD)
        btn_row.pack(fill="x")
        tk.Button(btn_row, text="💾  Save",
                  font=(FONT_FAMILY, 10, "bold"),
                  bg=ACCENT, fg=TEXT_PRIMARY,
                  activebackground="#388AFF",
                  relief="flat", bd=0, cursor="hand2",
                  padx=PAD_MD, pady=PAD_XS,
                  command=self._save).pack(side="left", padx=(0, PAD_SM))
        tk.Button(btn_row, text="Cancel",
                  font=FONT_BODY, bg=BG_CARD, fg=TEXT_SECONDARY,
                  relief="flat", bd=0, cursor="hand2",
                  padx=PAD_MD, pady=PAD_XS,
                  command=self.destroy).pack(side="left")

    def _centre(self) -> None:
        self.update_idletasks()
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    def _save(self) -> None:
        username = self._var_username.get().strip()
        email    = self._var_email.get().strip()
        password = self._var_password.get().strip()
        role     = self._var_role.get().strip()

        if not username:
            self._var_status.set("Username is required.")
            return
        if not email:
            self._var_status.set("Email is required.")
            return
        if not password:
            self._var_status.set("Password is required.")
            return
        if not role:
            self._var_status.set("Role is required.")
            return

        ok, msg = auth_controller.register_user(username, email, password, role)
        if ok:
            messagebox.showinfo("Success", f"User '{username}' created successfully.", parent=self)
            self.on_saved()
            self.destroy()
        else:
            self._var_status.set(msg)


# ─────────────────────────────────────────────────────────────────────
#  USER MANAGEMENT VIEW
# ─────────────────────────────────────────────────────────────────────

class UserManagementView(tk.Frame):
    """
    Admin-only User Management screen.

    Displays all users in a Treeview with search, create,
    and deactivate capabilities.
    """

    _COLS   = ("username", "email", "role", "status", "id")
    _HEADS  = ("Username", "Email", "Role", "Status", "User ID")
    _WIDTHS = (130, 210, 80, 80, 200)

    def __init__(self, parent: tk.Widget, user: dict[str, Any]) -> None:
        super().__init__(parent, bg=BG_DARK)
        self.user = user
        self.role = user.get("role", "staff")
        self._all_users: list[dict] = []
        self._build_ui()
        self._load_users()

    # ──────────────────────── BUILD ───────────────────────────────────

    def _build_ui(self) -> None:
        # Title
        title_bar = tk.Frame(self, bg=BG_DARK)
        title_bar.pack(fill="x", padx=PAD_XL, pady=(PAD_LG, PAD_SM))
        tk.Label(title_bar, text="👥  User Management",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg=BG_DARK, fg=TEXT_PRIMARY).pack(side="left")
        tk.Label(title_bar, text="(Admin Only)",
                 font=FONT_CAPTION, bg=BG_DARK, fg=DANGER).pack(side="left", padx=PAD_SM)

        # Toolbar
        toolbar = tk.Frame(self, bg=BG_DARK)
        toolbar.pack(fill="x", padx=PAD_XL, pady=(0, PAD_SM))

        tk.Label(toolbar, text="🔍", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_SECONDARY).pack(side="left")
        self._var_search = tk.StringVar()
        self._var_search.trace_add("write", lambda *_: self._apply_search())
        tk.Entry(toolbar, textvariable=self._var_search, width=26,
                 font=FONT_BODY,
                 bg=INPUT_BG, fg=TEXT_PRIMARY,
                 insertbackground=TEXT_PRIMARY,
                 relief="flat", bd=0,
                 highlightthickness=1,
                 highlightbackground=BORDER,
                 highlightcolor=ACCENT).pack(side="left", padx=(PAD_XS, PAD_MD), ipady=4)

        tk.Button(toolbar, text="🔄 Refresh",
                  font=FONT_BODY, bg=BG_CARD, fg=TEXT_SECONDARY,
                  relief="flat", bd=0, cursor="hand2",
                  padx=PAD_SM, command=self._load_users).pack(side="left", padx=(0, PAD_MD))

        tk.Button(toolbar, text="➕  Create User",
                  font=(FONT_FAMILY, 10, "bold"),
                  bg=ACCENT, fg=TEXT_PRIMARY,
                  activebackground="#388AFF",
                  relief="flat", bd=0, cursor="hand2",
                  padx=PAD_MD, pady=3,
                  command=self._open_create_dialog).pack(side="left", padx=(0, PAD_SM))

        tk.Button(toolbar, text="🚫  Deactivate",
                  font=FONT_BODY, bg=DANGER, fg=TEXT_PRIMARY,
                  activebackground="#ff6b63",
                  relief="flat", bd=0, cursor="hand2",
                  padx=PAD_SM, pady=3,
                  command=self._deactivate_selected).pack(side="left")

        # Status
        self._var_status = tk.StringVar(value="")
        tk.Label(self, textvariable=self._var_status,
                 font=FONT_CAPTION, bg=BG_DARK, fg=TEXT_SECONDARY,
                 anchor="w").pack(fill="x", padx=PAD_XL)

        # Treeview
        tree_container = tk.Frame(self, bg=BG_DARK)
        tree_container.pack(fill="both", expand=True, padx=PAD_XL, pady=(PAD_SM, PAD_LG))

        self._tree, _, _ = make_scrolled_tree(
            tree_container,
            columns=self._COLS,
            headings=self._HEADS,
            col_widths=self._WIDTHS,
            height=16,
        )
        self._tree.tag_configure("inactive", foreground=TEXT_DIM)

    # ──────────────────────── DATA ────────────────────────────────────

    def _load_users(self) -> None:
        ok, msg, users = auth_controller.get_all_users()
        if ok:
            self._all_users = users
            self._apply_search()
            self._var_status.set(f"{len(users)} user(s) registered.")
        else:
            self._var_status.set(f"Error: {msg}")

    def _apply_search(self) -> None:
        keyword = self._var_search.get().strip().lower()
        source  = (
            [u for u in self._all_users
             if keyword in u.get("username", "").lower()
             or keyword in u.get("email", "").lower()
             or keyword in u.get("role", "").lower()]
            if keyword else self._all_users
        )

        self._tree.delete(*self._tree.get_children())
        for u in source:
            is_active = u.get("is_active", True)
            status    = "Active" if is_active else "Deactivated"
            row = (
                u.get("username", ""),
                u.get("email", ""),
                u.get("role", "").upper(),
                status,
                str(u.get("_id", "")),
            )
            tag = ("evenrow" if is_active else "inactive")
            self._tree.insert("", "end", values=row, tags=(tag,))

    # ──────────────────────── ACTIONS ─────────────────────────────────

    def _open_create_dialog(self) -> None:
        _CreateUserDialog(self, on_saved=self._load_users)

    def _get_selected_user(self) -> Optional[dict]:
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a user row.", parent=self)
            return None
        values = self._tree.item(sel[0], "values")
        user_id = values[4] if values else None
        for u in self._all_users:
            if str(u.get("_id", "")) == user_id:
                return u
        return None

    def _deactivate_selected(self) -> None:
        u = self._get_selected_user()
        if not u:
            return
        if not u.get("is_active", True):
            messagebox.showinfo("Already Deactivated",
                                f"'{u['username']}' is already deactivated.", parent=self)
            return
        if u.get("role") == ROLE_ADMIN:
            messagebox.showerror("Not Allowed",
                                 "Administrator accounts cannot be deactivated.", parent=self)
            return
        if not messagebox.askyesno(
            "Confirm Deactivation",
            f"Deactivate user '{u['username']}'?\nThey will no longer be able to log in.",
            parent=self,
        ):
            return

        ok, msg = auth_controller.deactivate_user(str(u["_id"]))
        if ok:
            messagebox.showinfo("Deactivated", msg, parent=self)
            self._load_users()
        else:
            messagebox.showerror("Error", msg, parent=self)
