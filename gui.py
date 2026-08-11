"""
Medicine Warehouse Inventory Management System (MWIMS)
GUI Entry Point.

Launches the Tkinter desktop application, initialises the database,
shows the Login screen, and transitions to the main application shell
after successful authentication.

Usage:
    python gui.py
"""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import messagebox

# ── Attempt DB initialisation (backend) ────────────────────────────
try:
    from initialize_db import initialize_database
    from views.theme import apply_theme, BG_DARK, TEXT_PRIMARY, FONT_FAMILY
    from views.login_view import LoginView
    from views.main_app import MainApp
except ImportError as exc:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Import Error",
        f"Failed to import required modules:\n{exc}\n\n"
        "Ensure all dependencies are installed:\n"
        "  pip install pymongo bcrypt",
    )
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────
#  MWIMS APPLICATION
# ─────────────────────────────────────────────────────────────────

class MWIMSApplication:
    """
    Top-level application controller.

    Manages the root Tk window lifecycle and transitions between
    the Login screen and the authenticated Main application shell.
    """

    APP_TITLE  = "MWIMS – Medicine Warehouse Inventory Management System"
    WINDOW_W   = 1280
    WINDOW_H   = 780
    MIN_W      = 1100
    MIN_H      = 680

    def __init__(self) -> None:
        self._root = tk.Tk()
        self._root.title(self.APP_TITLE)
        self._root.configure(bg=BG_DARK)
        self._root.geometry(f"{self.WINDOW_W}x{self.WINDOW_H}")
        self._root.minsize(self.MIN_W, self.MIN_H)

        # Centre on screen
        self._root.update_idletasks()
        x = (self._root.winfo_screenwidth()  - self.WINDOW_W) // 2
        y = (self._root.winfo_screenheight() - self.WINDOW_H) // 2
        self._root.geometry(f"+{x}+{y}")

        # Apply global ttk theme
        apply_theme(self._root)

        # Handle window close
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._current_view = None

    # ─────────────────────────── LIFECYCLE ───────────────────────────

    def run(self) -> None:
        """Initialise database and show the login screen."""
        try:
            initialize_database()
        except Exception as exc:
            messagebox.showerror(
                "Database Error",
                f"Failed to connect to MongoDB:\n{exc}\n\n"
                "Please ensure MongoDB is running on localhost:27017.",
                parent=self._root,
            )
            self._root.destroy()
            sys.exit(1)

        self._show_login()
        self._root.mainloop()

    def _show_login(self) -> None:
        """Destroy current view and show the Login screen."""
        self._clear_view()
        self._current_view = LoginView(
            master=self._root,
            on_success=self._on_login_success,
        )

    def _on_login_success(self, user: dict) -> None:
        """Transition from Login to the Main application shell."""
        self._clear_view()
        self._current_view = MainApp(
            master=self._root,
            user=user,
            on_logout=self._show_login,
        )

    def _clear_view(self) -> None:
        """Destroy the currently visible top-level Frame."""
        if self._current_view and self._current_view.winfo_exists():
            self._current_view.destroy()
        self._current_view = None

    def _on_close(self) -> None:
        """Prompt before closing the application."""
        if messagebox.askyesno(
            "Exit MWIMS",
            "Are you sure you want to exit the application?",
            parent=self._root,
        ):
            self._root.destroy()


# ─────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = MWIMSApplication()
    app.run()
