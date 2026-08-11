"""
Warehouse Management View for MWIMS.

Displays:
  • All distinct rack / shelf / cabinet identifiers in use.
  • Location summary: medicine count & total stock per rack.
  • Location Finder: search medicine by rack/shelf/cabinet.

Uses warehouse_controller and medicine_controller only.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from controllers import medicine_controller, warehouse_controller
from views.theme import (
    ACCENT, BG_CARD, BG_DARK, BG_PANEL, BORDER,
    FONT_BODY, FONT_CAPTION, FONT_FAMILY, FONT_HEADING,
    INPUT_BG, PAD_LG, PAD_MD, PAD_SM, PAD_XL, PAD_XS,
    SUCCESS, TEXT_DIM, TEXT_PRIMARY, TEXT_SECONDARY, WARNING,
    make_scrolled_tree, populate_tree,
)


class WarehouseView(tk.Frame):
    """
    Warehouse Management screen with three tabs:
      1.  Location Overview  – distinct racks, shelves, cabinets + summary grid
      2.  Location Finder    – search medicines by rack / shelf / cabinet
      3.  Medicine Map       – full medicine list with location columns
    """

    def __init__(self, parent: tk.Widget, user: dict[str, Any]) -> None:
        super().__init__(parent, bg=BG_DARK)
        self.user = user
        self._medicines: list[dict] = []
        self._build_ui()
        self._load_data()

    # ─────────────────────────── BUILD ───────────────────────────────

    def _build_ui(self) -> None:
        # Title
        title_bar = tk.Frame(self, bg=BG_DARK)
        title_bar.pack(fill="x", padx=PAD_XL, pady=(PAD_LG, PAD_SM))
        tk.Label(title_bar, text="🏭  Warehouse Management",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg=BG_DARK, fg=TEXT_PRIMARY).pack(side="left")
        tk.Button(title_bar, text="🔄 Refresh", font=FONT_BODY,
                  bg=BG_CARD, fg=TEXT_SECONDARY,
                  relief="flat", bd=0, cursor="hand2",
                  padx=PAD_SM, command=self._load_data).pack(side="right")

        # Notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=PAD_XL, pady=(0, PAD_LG))

        self._tab_overview = tk.Frame(nb, bg=BG_DARK)
        self._tab_finder   = tk.Frame(nb, bg=BG_DARK)
        self._tab_map      = tk.Frame(nb, bg=BG_DARK)

        nb.add(self._tab_overview, text="  🗂️  Location Overview  ")
        nb.add(self._tab_finder,   text="  🔍  Location Finder   ")
        nb.add(self._tab_map,      text="  🗺️  Medicine Map       ")

        self._build_overview_tab()
        self._build_finder_tab()
        self._build_map_tab()

    # ── Tab 1: Location Overview ─────────────────────────────────────

    def _build_overview_tab(self) -> None:
        p = self._tab_overview

        # Three column info panels
        info_row = tk.Frame(p, bg=BG_DARK)
        info_row.pack(fill="x", padx=PAD_LG, pady=PAD_LG)

        for title, attr in [("Racks", "_lf_racks"), ("Shelves", "_lf_shelves"), ("Cabinets", "_lf_cabinets")]:
            lf = tk.LabelFrame(info_row, text=f"  {title}  ",
                               font=FONT_CAPTION,
                               bg=BG_CARD, fg=TEXT_SECONDARY,
                               labelanchor="nw", bd=1,
                               highlightthickness=0,
                               relief="flat",
                               padx=PAD_MD, pady=PAD_SM)
            lf.pack(side="left", expand=True, fill="both", padx=(0, PAD_SM))
            setattr(self, attr, lf)

        # Location summary treeview
        tk.Label(p, text="Location Summary (Medicine Count + Total Stock per Rack)",
                 font=FONT_HEADING, bg=BG_DARK, fg=TEXT_PRIMARY).pack(
            anchor="w", padx=PAD_LG, pady=(PAD_SM, PAD_XS))

        tree_frame = tk.Frame(p, bg=BG_DARK)
        tree_frame.pack(fill="both", expand=True, padx=PAD_LG, pady=(0, PAD_LG))

        self._summary_tree, _, _ = make_scrolled_tree(
            tree_frame,
            columns=("rack", "shelf", "cabinet", "count", "total_stock"),
            headings=("Rack", "Shelf", "Cabinet", "Medicine Count", "Total Stock"),
            col_widths=(90, 80, 90, 130, 120),
            height=10,
        )

    def _populate_overview(self, locations: dict, summary: list) -> None:
        """Fill the location panels and summary tree."""
        # Clear location label frames
        for attr, key, colour in [
            ("_lf_racks",     "racks",    ACCENT),
            ("_lf_shelves",   "shelves",  SUCCESS),
            ("_lf_cabinets",  "cabinets", WARNING),
        ]:
            lf: tk.LabelFrame = getattr(self, attr)
            for w in lf.winfo_children():
                w.destroy()
            items = locations.get(key, [])
            if items:
                for item in items:
                    tk.Label(lf, text=f"  {item}",
                             font=(FONT_FAMILY, 10, "bold"),
                             bg=BG_CARD, fg=colour).pack(anchor="w")
            else:
                tk.Label(lf, text="(none)", font=FONT_CAPTION,
                         bg=BG_CARD, fg=TEXT_DIM).pack(anchor="w")

        # Summary tree
        rows = [
            (
                r.get("rack", ""),
                r.get("shelf", ""),
                r.get("cabinet", ""),
                r.get("count", 0),
                r.get("total_stock", 0),
            )
            for r in summary
        ]
        populate_tree(self._summary_tree, rows)

    # ── Tab 2: Location Finder ────────────────────────────────────────

    def _build_finder_tab(self) -> None:
        p = self._tab_finder
        card = tk.Frame(p, bg=BG_CARD, padx=PAD_XL, pady=PAD_LG)
        card.pack(padx=PAD_XL, pady=PAD_LG, anchor="nw")

        tk.Label(card, text="Search Medicine by Location",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=BG_CARD, fg=TEXT_PRIMARY).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, PAD_MD))

        labels = ["Rack", "Shelf", "Cabinet"]
        self._var_find_rack    = tk.StringVar()
        self._var_find_shelf   = tk.StringVar()
        self._var_find_cabinet = tk.StringVar()
        vars_ = [self._var_find_rack, self._var_find_shelf, self._var_find_cabinet]

        for col, (label, var) in enumerate(zip(labels, vars_)):
            tk.Label(card, text=label, font=FONT_CAPTION,
                     bg=BG_CARD, fg=TEXT_SECONDARY).grid(
                row=1, column=col * 2, sticky="w", padx=(0, PAD_XS))
            entry = tk.Entry(card, textvariable=var, width=10,
                             font=FONT_BODY,
                             bg=INPUT_BG, fg=TEXT_PRIMARY,
                             insertbackground=TEXT_PRIMARY,
                             relief="flat", bd=0,
                             highlightthickness=1,
                             highlightbackground=BORDER,
                             highlightcolor=ACCENT)
            entry.grid(row=1, column=col * 2 + 1, sticky="ew", padx=(0, PAD_MD), pady=PAD_XS)

        tk.Button(card, text="🔍  Find",
                  font=(FONT_FAMILY, 10, "bold"),
                  bg=ACCENT, fg=TEXT_PRIMARY,
                  activebackground="#388AFF",
                  relief="flat", bd=0, cursor="hand2",
                  padx=PAD_MD, pady=4,
                  command=self._find_by_location).grid(
            row=2, column=0, columnspan=6, sticky="w", pady=(PAD_SM, 0))

        # Results table
        result_frame = tk.Frame(p, bg=BG_DARK)
        result_frame.pack(fill="both", expand=True, padx=PAD_XL, pady=(PAD_SM, PAD_LG))

        self._finder_tree, _, _ = make_scrolled_tree(
            result_frame,
            columns=("name", "batch", "qty", "rack", "shelf", "cabinet"),
            headings=("Medicine Name", "Batch #", "Qty", "Rack", "Shelf", "Cabinet"),
            col_widths=(180, 110, 80, 80, 80, 80),
            height=10,
        )

    def _find_by_location(self) -> None:
        rack    = self._var_find_rack.get().strip().upper()
        shelf   = self._var_find_shelf.get().strip().upper()
        cabinet = self._var_find_cabinet.get().strip().upper()

        filtered = [
            m for m in self._medicines
            if (not rack    or m.get("rack", "").upper()    == rack)
            and (not shelf   or m.get("shelf", "").upper()   == shelf)
            and (not cabinet or m.get("cabinet", "").upper() == cabinet)
        ]

        rows = [
            (
                m.get("medicine_name", ""),
                m.get("batch_number", ""),
                m.get("quantity", 0),
                m.get("rack", ""),
                m.get("shelf", ""),
                m.get("cabinet", ""),
            )
            for m in filtered
        ]
        populate_tree(self._finder_tree, rows)

    # ── Tab 3: Medicine Map ───────────────────────────────────────────

    def _build_map_tab(self) -> None:
        p = self._tab_map
        tree_frame = tk.Frame(p, bg=BG_DARK)
        tree_frame.pack(fill="both", expand=True, padx=PAD_LG, pady=PAD_LG)

        self._map_tree, _, _ = make_scrolled_tree(
            tree_frame,
            columns=("name", "batch", "rack", "shelf", "cabinet", "qty", "category"),
            headings=("Medicine Name", "Batch #", "Rack", "Shelf", "Cabinet", "Qty", "Category"),
            col_widths=(180, 110, 70, 70, 80, 60, 120),
            height=18,
        )

    # ─────────────────────────── DATA ────────────────────────────────

    def _load_data(self) -> None:
        # Medicines
        ok, _, meds = medicine_controller.get_all_medicines()
        if ok:
            self._medicines = meds

        # Warehouse locations
        ok_loc, _, locations = warehouse_controller.get_warehouse_locations()
        ok_sum, _, summary   = warehouse_controller.get_location_summary()

        if ok_loc:
            self._populate_overview(
                locations if ok_loc else {},
                summary   if ok_sum else [],
            )

        # Map table
        map_rows = [
            (
                m.get("medicine_name", ""),
                m.get("batch_number", ""),
                m.get("rack", ""),
                m.get("shelf", ""),
                m.get("cabinet", ""),
                m.get("quantity", 0),
                m.get("category", ""),
            )
            for m in self._medicines
        ]
        populate_tree(self._map_tree, map_rows)
