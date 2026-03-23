"""
Airline record management window for the Travel Record Management System.

Implements ``AirlineWindow``, a modal ``tk.Toplevel`` that provides a
full CRUD interface (Create, Search, Update, Delete) for Airline records
stored in the shared JSONL data file.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox

from src.exceptions import DuplicateRecordError, RecordNotFoundError
from src.record.airline_record import (
    create_airline as _create_airline,
    delete_airline as _delete_airline,
    update_airline as _update_airline,
)
from src.repository import RecordRepository


class AirlineWindow(tk.Toplevel):
    """
    Airline Record Management Window.

    Handles Airline Company records, each containing an ID and a Company Name.
    Provides a full CRUD interface: Create, Search, Update, and Delete.
    """

    def __init__(self, master: tk.Misc | None = None) -> None:
        super().__init__(master)

        # ----------------------------------------------------------
        # Window title and background colour
        # ----------------------------------------------------------
        self.title("Airline Management System")
        self.configure(bg="#f4f6f7")

        # ----------------------------------------------------------
        # HiDPI / scaling-aware window sizing
        # ----------------------------------------------------------
        BASE_SCALING = 96.0 / 72.0  # Standard tkinter baseline scaling factor
        actual_scaling = float(self.tk.call("tk", "scaling"))
        ratio = actual_scaling / BASE_SCALING  # HiDPI multiplier (1.0 on normal displays)

        phys_w = self.winfo_screenwidth()
        phys_h = self.winfo_screenheight()

        monitors = max(1, round(phys_w / phys_h))
        mon_w = phys_w // monitors

        TARGET_W, TARGET_H = 1300, 820

        WIN_W = min(int(TARGET_W * ratio), mon_w - 40)
        WIN_H = min(int(TARGET_H * ratio), phys_h - 80)

        self.resizable(True, True)
        self.minsize(WIN_W, WIN_H)

        self.update_idletasks()

        ptr_x = self.winfo_pointerx()
        mon_index = min(ptr_x // mon_w, monitors - 1)
        mon_origin_x = mon_index * mon_w
        x = mon_origin_x + (mon_w - WIN_W) // 2
        y = (phys_h - WIN_H) // 2
        self.geometry(f"{WIN_W}x{WIN_H}+{x}+{y}")

        # ----------------------------------------------------------
        # Focus and modality
        # ----------------------------------------------------------
        self.transient(master)
        self.lift()
        self.focus_force()
        self.grab_set()
        self.focus()

        # ----------------------------------------------------------
        # Load all records via the Repository layer
        # ----------------------------------------------------------
        self.repo = RecordRepository()
        self.repo.load()
        self.records = self.repo.records

        self._sort_reverse: dict[str, bool] = {}
        self._sort_col: str | None = None
        self._col_headings: dict[str, str] = {}

        # ----------------------------------------------------------
        # ttk Style configuration
        # ----------------------------------------------------------
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.map(
            "Treeview",
            background=[("selected", "#1f618d")],
        )
        self.style.configure("Treeview", font=("Arial", 12))
        self.style.configure("Treeview.Heading", font=("Arial", 13, "bold"))
        self.style.configure(
            "Vertical.TScrollbar",
            gripcount=0,
            background="#5d6d7e",
            troughcolor="#ecf0f1",
            bordercolor="#ecf0f1",
            arrowcolor="white",
            width=22,
        )
        self.style.configure(
            "Horizontal.TScrollbar",
            gripcount=0,
            background="#5d6d7e",
            troughcolor="#ecf0f1",
            bordercolor="#ecf0f1",
            arrowcolor="white",
            width=18,
        )

        # ----------------------------------------------------------
        # Airline icon — graceful fallback if asset is missing
        # ----------------------------------------------------------
        assets = os.path.join(os.path.dirname(__file__), "assets")
        try:
            self.airline_icon = tk.PhotoImage(
                file=os.path.join(assets, "airline.png")
            ).subsample(3, 4)
        except Exception:
            self.airline_icon = None

        # ----------------------------------------------------------
        # Build all GUI widgets and populate the Treeview
        # ----------------------------------------------------------
        self.create_widgets()
        self.populate_treeview()

        # ----------------------------------------------------------
        # Event bindings
        # ----------------------------------------------------------
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Return>", lambda e: self.create_airline())
        self.name_entry.focus_set()

    # ----------------------------------------------------------
    # GUI construction
    # ----------------------------------------------------------

    def create_widgets(self) -> None:
        """Create and lay out all GUI widgets within the window."""

        header = tk.Frame(self, bg="#2c3e50", pady=15)
        header.pack(fill="x")
        tk.Label(
            header,
            text=" AIRLINE COMPANY RECORDS",
            font=("Arial", 18, "bold"),
            image=self.airline_icon,
            compound="left",
            fg="white",
            bg="#2c3e50",
        ).pack()

        main = tk.Frame(self, bg="#f4f6f7", padx=20, pady=10)
        main.pack(fill="both", expand=True)

        form = tk.LabelFrame(
            main,
            text=" Airline Information ",
            bg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=20,
        )
        form.pack(fill="x", pady=10)

        tk.Label(
            form,
            text="Airline ID (auto-assigned; enter for Search/Update)",
            bg="white",
            font=("Arial", 12),
        ).grid(row=0, column=0, sticky="w", pady=8)
        self.id_entry = tk.Entry(form, bd=2, relief="solid", font=("Arial", 12))
        self.id_entry.grid(row=0, column=1, sticky="ew", padx=10)

        tk.Label(
            form, text="Company Name *", bg="white", font=("Arial", 12)
        ).grid(row=1, column=0, sticky="w", pady=8)
        self.name_entry = tk.Entry(form, bd=2, relief="solid", font=("Arial", 12))
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=10)

        form.columnconfigure(1, weight=1)

        tk.Label(
            form,
            text="* Required fields",
            font=("Arial", 10, "italic"),
            fg="#e74c3c",
            bg="white",
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 5))

        # ----------------------------------------------------------
        # CRUD action buttons
        # ----------------------------------------------------------
        btn_frame = tk.Frame(main, bg="#f4f6f7")
        btn_frame.pack(fill="x", pady=12)

        buttons = [
            ("Create", "#1a7a40", self.create_airline),
            ("Update", "#2980b9", self.update_airline),
            ("Delete", "#c0392b", self.delete_airline),
            ("Search", "#8e44ad", self.search_airline),
            ("Clear",  "#7f8c8d", self.clear_form),
        ]

        def on_enter(e: tk.Event) -> None:
            e.widget["bg"] = "#34495e"

        def on_leave(e: tk.Event, color: str) -> None:
            e.widget["bg"] = color

        for i, (text, color, cmd) in enumerate(buttons):
            btn = tk.Button(
                btn_frame,
                text=text,
                bg=color,
                fg="white",
                width=14,
                font=("Arial", 12, "bold"),
                command=cmd,
            )
            btn.grid(row=0, column=i, padx=5, sticky="ew")
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", lambda e, c=color: on_leave(e, c))
            btn_frame.columnconfigure(i, weight=1)

        # ----------------------------------------------------------
        # Treeview with vertical scrollbar
        # ----------------------------------------------------------
        table_frame = tk.Frame(main, bg="white")
        table_frame.pack(fill="both", expand=True, pady=12)

        cols = ("ID", "Company Name")
        self.tree = ttk.Treeview(
            table_frame, columns=cols, show="headings", height=12
        )

        self.tree.tag_configure("oddrow",  background="white")
        self.tree.tag_configure("evenrow", background="#f2f2f2")

        for col in cols:
            self._col_headings[col] = col.upper()
            self.tree.heading(
                col, text=col.upper(),
                command=lambda c=col: self._sort_column(c),
            )
            self.tree.column(col, anchor="center", width=250)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.empty_label = tk.Label(
            table_frame,
            text="No airlines registered yet",
            font=("Arial", 15, "italic"),
            bg="white",
            fg="#555555",
        )
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

        self.counter = tk.Label(
            main, text="", bg="#f4f6f7", font=("Arial", 12, "bold")
        )
        self.counter.pack(anchor="e", padx=5)

        self.status = tk.Label(
            self,
            text="System Ready",
            bd=1,
            relief="sunken",
            anchor="w",
            bg="#ecf0f1",
            font=("Arial", 12),
        )
        self.status.pack(fill="x", side="bottom")

    # ----------------------------------------------------------
    # Column sort
    # ----------------------------------------------------------

    def _sort_column(self, col: str) -> None:
        """Sort the Treeview by *col*, toggling direction on repeated clicks."""
        reverse = self._sort_reverse.get(col, False)
        self._sort_reverse[col] = not reverse

        if self._sort_col and self._sort_col != col:
            self.tree.heading(self._sort_col, text=self._col_headings[self._sort_col])

        indicator = "▲" if not reverse else "▼"
        self.tree.heading(col, text=f"{self._col_headings[col]} {indicator}")
        self._sort_col = col

        items = self.tree.get_children("")
        col_index = self.tree["columns"].index(col)
        NUMERIC_COLUMNS = {"ID"}

        data = []
        for item in items:
            raw = self.tree.item(item, "values")[col_index]
            if col in NUMERIC_COLUMNS:
                try:
                    key: int | str = int(raw)
                except (ValueError, TypeError):
                    key = 0
            else:
                key = str(raw).lower()
            data.append((key, item))

        data.sort(key=lambda t: t[0], reverse=reverse)

        for index, (_, item) in enumerate(data):
            self.tree.move(item, "", index)
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree.item(item, tags=(tag,))

    # ----------------------------------------------------------
    # Treeview population
    # ----------------------------------------------------------

    def populate_treeview(self) -> None:
        """Clear and repopulate the Treeview with all airline records."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        count = 0
        for index, r in enumerate(self.records):
            if r.get("Type") == "Airline":
                tag = "evenrow" if index % 2 == 0 else "oddrow"
                self.tree.insert(
                    "", "end",
                    values=(r.get("ID"), r.get("Company Name")),
                    tags=(tag,),
                )
                count += 1

        if count == 0:
            self.empty_label.lift()
        else:
            self.empty_label.lower()

        self.counter.config(text=f"Total Airlines: {count}")

    # ----------------------------------------------------------
    # Input helpers
    # ----------------------------------------------------------

    def clear_form(self) -> None:
        """Clear both entry fields and deselect any highlighted table row."""
        self.id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        self.name_entry.focus_set()
        self.status.config(text="✔ Form cleared. Ready")

    # ----------------------------------------------------------
    # CRUD operations
    # ----------------------------------------------------------

    def create_airline(self) -> None:
        """Validate the form and create a new airline record.

        The ID is auto-assigned to the next available integer.
        Blocks creation if a record with the same Company Name already
        exists (case-insensitive comparison).
        """
        name = self.name_entry.get().strip()
        if not name:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Validation", "Company Name is required.", parent=self)
            return

        # Block duplicate company names (case-insensitive) before delegating
        # to the Record layer, which only checks for duplicate IDs.
        duplicate = next(
            (r for r in self.records
             if r.get("Type") == "Airline"
             and r.get("Company Name", "").lower() == name.lower()),
            None,
        )
        if duplicate:
            self.lift()
            self.focus_force()
            messagebox.showerror(
                "Duplicate Record",
                f"An airline named '{duplicate['Company Name']}' already exists "
                f"(ID: {duplicate['ID']}).\n\nPlease use a different company name.",
                parent=self,
            )
            return

        # Delegate creation to the Record layer; ID is auto-assigned
        try:
            record = _create_airline(self.records, name)
            aid = record["ID"]
            self.repo.save()
        except DuplicateRecordError as exc:
            self.lift()
            self.focus_force()
            messagebox.showerror("Duplicate Record", str(exc), parent=self)
            return

        self.populate_treeview()
        self.clear_form()
        self.status.config(text=f"✔ Airline created successfully (assigned ID: {aid}).")
        self.lift()
        self.focus_force()
        messagebox.showinfo(
            "Success",
            f"✔ Airline added successfully.\nAssigned ID: {aid}",
            parent=self,
        )

    def search_airline(self) -> None:
        """Search for an airline by ID, optionally verifying the Company Name."""
        aid = self.id_entry.get().strip()
        name = self.name_entry.get().strip()

        if not aid:
            self.lift()
            self.focus_force()
            messagebox.showwarning(
                "Search",
                "Please enter an Airline ID to search. "
                "Company Name alone is not sufficient.",
                parent=self,
            )
            return

        record = next(
            (r for r in self.records
             if str(r.get("ID")) == str(aid) and r.get("Type") == "Airline"),
            None,
        )
        if not record:
            self.lift()
            self.focus_force()
            messagebox.showinfo("Search", f"Airline ID {aid} not found.", parent=self)
            return

        if name and record["Company Name"].lower() != name.lower():
            self.lift()
            self.focus_force()
            messagebox.showwarning(
                "Search",
                f"Airline ID {aid} exists but Company Name does not match.",
                parent=self,
            )
            self.status.config(text="✖ ID found but Name mismatch.")
            return

        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, record["ID"])
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, record["Company Name"])

        for item in self.tree.get_children():
            if str(self.tree.item(item, "values")[0]) == str(record["ID"]):
                self.tree.selection_set(item)
                self.tree.focus(item)
                self.tree.see(item)
                break

        self.status.config(text=f"✔ Airline '{record['Company Name']}' found.")
        self.lift()
        self.focus_force()
        messagebox.showinfo("Search Result", f"✔ Airline {aid} found.", parent=self)

    def update_airline(self) -> None:
        """Update the Company Name of an existing airline by its ID.

        Also blocks the update if the new name is already used by a
        different airline record (case-insensitive comparison).
        """
        aid = self.id_entry.get().strip()
        name = self.name_entry.get().strip()

        if not aid:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Update", "Enter Airline ID.", parent=self)
            return
        if not name:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Update", "Enter Company Name.", parent=self)
            return

        # Block if another airline (different ID) already uses this name
        duplicate = next(
            (r for r in self.records
             if r.get("Type") == "Airline"
             and r.get("Company Name", "").lower() == name.lower()
             and str(r.get("ID")) != str(aid)),
            None,
        )
        if duplicate:
            self.lift()
            self.focus_force()
            messagebox.showerror(
                "Duplicate Record",
                f"An airline named '{duplicate['Company Name']}' already exists "
                f"(ID: {duplicate['ID']}).\n\nPlease use a different company name.",
                parent=self,
            )
            return

        try:
            _update_airline(self.records, int(aid), **{"Company Name": name})
            self.repo.save()
        except RecordNotFoundError as exc:
            self.lift()
            self.focus_force()
            messagebox.showerror("Not Found", str(exc), parent=self)
            return

        self.populate_treeview()
        self.clear_form()
        self.status.config(text=f"✔ Airline {aid} updated successfully.")
        self.lift()
        self.focus_force()
        messagebox.showinfo("Update Successful", f"✔ Airline {aid} updated.", parent=self)

    def delete_airline(self) -> None:
        """Delete the selected airline and all associated flight records."""
        selected = self.tree.selection()
        if not selected:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Delete", "Select an airline first.", parent=self)
            return

        airline_id = int(self.tree.item(selected[0], "values")[0])

        self.lift()
        self.focus_force()
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete Airline {airline_id} and ALL related flights?",
            parent=self,
        ):
            return

        try:
            _delete_airline(self.records, airline_id)
            self.repo.save()
        except RecordNotFoundError as exc:
            self.lift()
            self.focus_force()
            messagebox.showerror("Not Found", str(exc), parent=self)
            return

        self.populate_treeview()
        self.clear_form()
        self.status.config(text=f"✔ Airline {airline_id} and related flights deleted.")
        self.lift()
        self.focus_force()
        messagebox.showinfo("Deleted", "Airline and associated flights removed.", parent=self)

    # ----------------------------------------------------------
    # Treeview selection event
    # ----------------------------------------------------------

    def on_tree_select(self, event: tk.Event) -> None:
        """Populate the form fields when the user selects a row in the Treeview."""
        selected = self.tree.selection()
        if not selected:
            return
        val = self.tree.item(selected[0], "values")
        if val[1] == "No Airlines Registered Yet.":
            return
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, val[0])
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, val[1])

    # ----------------------------------------------------------
    # Window close event
    # ----------------------------------------------------------

    def on_close(self) -> None:
        """Persist all records to the JSONL file before destroying the window."""
        self.repo.save()
        self.destroy()
