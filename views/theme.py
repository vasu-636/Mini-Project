"""
MWIMS GUI Theme & Style Constants.

Single source of truth for all visual design tokens used across every view.
All colours, typography, spacing, and reusable widget-factory helpers live here.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional

# ─────────────────────────────────────────────
#  COLOUR PALETTE
# ─────────────────────────────────────────────

# Background shades
BG_DARK        = "#0D1117"   # app root background
BG_PANEL       = "#161B22"   # sidebar / panel
BG_CARD        = "#1C2333"   # card / frame interior
BG_CARD_ALT    = "#21262D"   # alternate row / hover

# Accent brand colour
ACCENT         = "#2F81F7"   # primary blue
ACCENT_HOVER   = "#388AFF"
ACCENT_DARK    = "#1F6FEB"

# Semantic colours
SUCCESS        = "#3FB950"
WARNING        = "#D29922"
DANGER         = "#F85149"
INFO           = "#58A6FF"

# Text
TEXT_PRIMARY   = "#E6EDF3"
TEXT_SECONDARY = "#8B949E"
TEXT_DIM       = "#484F58"
TEXT_ACCENT    = "#2F81F7"

# Treeview / table
TREE_BG        = "#161B22"
TREE_ODD       = "#1C2333"
TREE_EVEN      = "#161B22"
TREE_SELECT    = "#264F78"
TREE_HEADING   = "#0D1117"

# Input
INPUT_BG       = "#0D1117"
INPUT_BORDER   = "#30363D"
INPUT_FOCUS    = "#2F81F7"

# Border
BORDER         = "#30363D"

# ─────────────────────────────────────────────
#  TYPOGRAPHY
# ─────────────────────────────────────────────
FONT_FAMILY    = "Segoe UI"

FONT_TITLE     = (FONT_FAMILY, 20, "bold")
FONT_SUBTITLE  = (FONT_FAMILY, 13, "bold")
FONT_HEADING   = (FONT_FAMILY, 11, "bold")
FONT_BODY      = (FONT_FAMILY, 10)
FONT_SMALL     = (FONT_FAMILY, 9)
FONT_MONO      = ("Consolas", 9)
FONT_CAPTION   = (FONT_FAMILY, 8)

# ─────────────────────────────────────────────
#  SPACING
# ─────────────────────────────────────────────
PAD_XS  = 4
PAD_SM  = 8
PAD_MD  = 14
PAD_LG  = 20
PAD_XL  = 30

# ─────────────────────────────────────────────
#  TTK STYLE INITIALIZER
# ─────────────────────────────────────────────

def apply_theme(root: tk.Tk) -> None:
    """Configure global ttk styles to match the MWIMS dark theme."""
    style = ttk.Style(root)
    style.theme_use("clam")

    # ── General frame / label ───────────────────
    style.configure("TFrame",       background=BG_DARK)
    style.configure("Card.TFrame",  background=BG_CARD)
    style.configure("Panel.TFrame", background=BG_PANEL)
    style.configure("TLabel",       background=BG_DARK, foreground=TEXT_PRIMARY, font=FONT_BODY)
    style.configure("Card.TLabel",  background=BG_CARD, foreground=TEXT_PRIMARY, font=FONT_BODY)
    style.configure("Panel.TLabel", background=BG_PANEL, foreground=TEXT_PRIMARY, font=FONT_BODY)
    style.configure("Dim.TLabel",   background=BG_DARK, foreground=TEXT_SECONDARY, font=FONT_SMALL)
    style.configure("Heading.TLabel",background=BG_DARK, foreground=TEXT_PRIMARY, font=FONT_HEADING)
    style.configure("Title.TLabel", background=BG_DARK, foreground=TEXT_PRIMARY, font=FONT_TITLE)
    style.configure("Subtitle.TLabel",background=BG_DARK, foreground=TEXT_SECONDARY, font=FONT_SUBTITLE)
    style.configure("Success.TLabel",background=BG_DARK, foreground=SUCCESS, font=FONT_BODY)
    style.configure("Warning.TLabel",background=BG_DARK, foreground=WARNING, font=FONT_BODY)
    style.configure("Danger.TLabel", background=BG_DARK, foreground=DANGER,  font=FONT_BODY)

    # ── Separator ───────────────────────────────
    style.configure("TSeparator", background=BORDER)

    # ── Buttons ─────────────────────────────────
    style.configure(
        "Primary.TButton",
        background=ACCENT, foreground=TEXT_PRIMARY,
        font=FONT_HEADING, borderwidth=0, relief="flat",
        padding=(PAD_SM, PAD_XS),
    )
    style.map(
        "Primary.TButton",
        background=[("active", ACCENT_HOVER), ("pressed", ACCENT_DARK)],
        relief=[("pressed", "flat")],
    )
    style.configure(
        "Danger.TButton",
        background=DANGER, foreground=TEXT_PRIMARY,
        font=FONT_HEADING, borderwidth=0, relief="flat",
        padding=(PAD_SM, PAD_XS),
    )
    style.map("Danger.TButton",
              background=[("active", "#ff6b63"), ("pressed", "#c93d37")])

    style.configure(
        "Ghost.TButton",
        background=BG_CARD, foreground=TEXT_SECONDARY,
        font=FONT_BODY, borderwidth=1, relief="flat",
        padding=(PAD_SM, PAD_XS),
    )
    style.map("Ghost.TButton",
              background=[("active", BG_CARD_ALT)],
              foreground=[("active", TEXT_PRIMARY)])

    style.configure(
        "Success.TButton",
        background=SUCCESS, foreground="#0D1117",
        font=FONT_HEADING, borderwidth=0, relief="flat",
        padding=(PAD_SM, PAD_XS),
    )
    style.map("Success.TButton",
              background=[("active", "#52c562")])

    style.configure(
        "Warning.TButton",
        background=WARNING, foreground="#0D1117",
        font=FONT_HEADING, borderwidth=0, relief="flat",
        padding=(PAD_SM, PAD_XS),
    )
    style.map("Warning.TButton",
              background=[("active", "#e8ad2b")])

    style.configure(
        "Sidebar.TButton",
        background=BG_PANEL, foreground=TEXT_SECONDARY,
        font=FONT_BODY, borderwidth=0, relief="flat",
        padding=(PAD_MD, PAD_SM), anchor="w",
    )
    style.map(
        "Sidebar.TButton",
        background=[("active", BG_CARD)],
        foreground=[("active", TEXT_PRIMARY)],
    )
    style.configure(
        "SidebarActive.TButton",
        background=BG_CARD, foreground=ACCENT,
        font=(FONT_FAMILY, 10, "bold"), borderwidth=0, relief="flat",
        padding=(PAD_MD, PAD_SM), anchor="w",
    )

    # ── Entry ────────────────────────────────────
    style.configure(
        "TEntry",
        fieldbackground=INPUT_BG, foreground=TEXT_PRIMARY,
        insertcolor=TEXT_PRIMARY, bordercolor=INPUT_BORDER,
        font=FONT_BODY, padding=PAD_XS,
    )
    style.map("TEntry", bordercolor=[("focus", INPUT_FOCUS)])

    # ── Combobox ─────────────────────────────────
    style.configure(
        "TCombobox",
        fieldbackground=INPUT_BG, foreground=TEXT_PRIMARY,
        selectbackground=ACCENT, selectforeground=TEXT_PRIMARY,
        background=INPUT_BG, arrowcolor=TEXT_SECONDARY,
    )
    style.map("TCombobox",
              fieldbackground=[("readonly", INPUT_BG)],
              foreground=[("readonly", TEXT_PRIMARY)])

    # ── Scrollbar ────────────────────────────────
    style.configure(
        "TScrollbar",
        background=BG_PANEL, troughcolor=BG_DARK,
        arrowcolor=TEXT_DIM, borderwidth=0,
    )
    style.map("TScrollbar", background=[("active", TEXT_DIM)])

    # ── Treeview ─────────────────────────────────
    style.configure(
        "Treeview",
        background=TREE_BG, foreground=TEXT_PRIMARY,
        fieldbackground=TREE_BG, font=FONT_BODY,
        rowheight=28, borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=TREE_HEADING, foreground=TEXT_SECONDARY,
        font=FONT_HEADING, relief="flat", borderwidth=0,
    )
    style.map(
        "Treeview",
        background=[("selected", TREE_SELECT)],
        foreground=[("selected", TEXT_PRIMARY)],
    )
    style.map("Treeview.Heading",
              background=[("active", BG_CARD_ALT)])

    # ── Notebook tabs ─────────────────────────────
    style.configure(
        "TNotebook",
        background=BG_DARK, borderwidth=0, tabmargins=[2, 4, 2, 0],
    )
    style.configure(
        "TNotebook.Tab",
        background=BG_PANEL, foreground=TEXT_SECONDARY,
        font=FONT_BODY, padding=(PAD_MD, PAD_XS),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", BG_CARD), ("active", BG_CARD_ALT)],
        foreground=[("selected", TEXT_PRIMARY), ("active", TEXT_PRIMARY)],
    )

    # ── LabelFrame ───────────────────────────────
    style.configure(
        "TLabelframe",
        background=BG_CARD, bordercolor=BORDER, relief="flat",
    )
    style.configure(
        "TLabelframe.Label",
        background=BG_CARD, foreground=TEXT_SECONDARY, font=FONT_SMALL,
    )

    # ── Progressbar ──────────────────────────────
    style.configure(
        "TProgressbar",
        troughcolor=BG_PANEL, background=ACCENT, borderwidth=0,
    )


# ─────────────────────────────────────────────
#  REUSABLE WIDGET FACTORY HELPERS
# ─────────────────────────────────────────────

def make_label(parent: tk.Widget, text: str, style: str = "TLabel", **kw) -> ttk.Label:
    """Return a styled ttk.Label."""
    return ttk.Label(parent, text=text, style=style, **kw)


def make_entry(parent: tk.Widget, textvariable: Optional[tk.StringVar] = None,
               show: str = "", width: int = 30, **kw) -> ttk.Entry:
    """Return a styled ttk.Entry."""
    kw_entry: dict = dict(style="TEntry", width=width)
    if textvariable:
        kw_entry["textvariable"] = textvariable
    if show:
        kw_entry["show"] = show
    kw_entry.update(kw)
    return ttk.Entry(parent, **kw_entry)


def make_button(parent: tk.Widget, text: str, command=None,
                style: str = "Primary.TButton", **kw) -> ttk.Button:
    """Return a styled ttk.Button."""
    return ttk.Button(parent, text=text, command=command, style=style, **kw)


def make_combobox(parent: tk.Widget, values: list[str],
                  textvariable: Optional[tk.StringVar] = None,
                  width: int = 28, state: str = "readonly", **kw) -> ttk.Combobox:
    """Return a styled ttk.Combobox."""
    cb = ttk.Combobox(parent, values=values, width=width, state=state, style="TCombobox", **kw)
    if textvariable:
        cb.configure(textvariable=textvariable)
    return cb


def make_scrolled_tree(
    parent: tk.Widget,
    columns: tuple[str, ...],
    headings: tuple[str, ...],
    col_widths: Optional[tuple[int, ...]] = None,
    show: str = "headings",
    height: int = 14,
) -> tuple[ttk.Treeview, ttk.Scrollbar, ttk.Scrollbar]:
    """
    Create a Treeview with vertical + horizontal scrollbars packed into *parent*.

    Returns:
        (tree, v_scroll, h_scroll)
    """
    frame = ttk.Frame(parent)
    frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(frame, columns=columns, show=show, height=height, style="Treeview")

    v_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    h_scroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

    v_scroll.pack(side="right", fill="y")
    h_scroll.pack(side="bottom", fill="x")
    tree.pack(side="left", fill="both", expand=True)

    # Configure headings & columns
    for i, col in enumerate(columns):
        tree.heading(col, text=headings[i] if headings else col,
                     anchor="w")
        width = (col_widths[i] if col_widths else 120)
        tree.column(col, width=width, minwidth=60, anchor="w")

    # Alternate row tags
    tree.tag_configure("oddrow",  background=TREE_ODD)
    tree.tag_configure("evenrow", background=TREE_EVEN)
    tree.tag_configure("danger",  background="#2c1616", foreground=DANGER)
    tree.tag_configure("warning", background="#2a2210", foreground=WARNING)
    tree.tag_configure("success", background="#122515", foreground=SUCCESS)

    return tree, v_scroll, h_scroll


def populate_tree(tree: ttk.Treeview, rows: list[tuple]) -> None:
    """Clear existing rows and insert new rows with alternating colour tags."""
    tree.delete(*tree.get_children())
    for idx, row in enumerate(rows):
        tag = "oddrow" if idx % 2 else "evenrow"
        tree.insert("", "end", values=row, tags=(tag,))


def separator(parent: tk.Widget, **kw) -> ttk.Separator:
    """Return a horizontal separator."""
    return ttk.Separator(parent, orient="horizontal", **kw)


def card_frame(parent: tk.Widget, **kw) -> ttk.Frame:
    """Return a BG_CARD styled frame."""
    return ttk.Frame(parent, style="Card.TFrame", **kw)
