"""
Client record management window for the Travel Record Management System.

Implements ``ClientWindow``, a modal ``tk.Toplevel`` that provides a
full CRUD interface (Create, Search, Update, Delete) for Client records
stored in the shared JSONL data file.  Includes per-field validation and
cascade ID propagation to associated Flight records.
"""

import os
import re
import tkinter as tk
from tkinter import ttk, messagebox

from src.storage import load_records, save_records  # PEP 8 fix


class ClientWindow(tk.Toplevel):
    """
    Client Record Management Window.

    Provides a full CRUD interface (Create, Search, Update, Delete)
    for client records stored in the shared JSONL data file.
    """

    def __init__(self, master: tk.Misc) -> None:  # PEP 8 fix: add type annotations
        super().__init__(master)

        # ----------------------------------------------------------
        # Window title and background colour
        # ----------------------------------------------------------
        self.title("Client Record System")
        self.configure(bg="#f4f6f7")

        # ----------------------------------------------------------
        # HiDPI / scaling-aware window sizing
        #
        # On HiDPI displays (e.g. Wayland fractional scaling) tkinter
        # reports a scaling factor greater than the standard baseline of
        # 96 DPI / 72 pt = 1.333. The compositor then scales the window
        # back down, making it appear smaller than intended.
        #
        # To compensate, the target dimensions are multiplied by the
        # ratio between the actual scaling and the baseline, so that
        # the compositor scales the window back to the intended visual size.
        #
        # The window is then centred on whichever monitor the mouse
        # cursor currently resides on, calculated from the pointer
        # x-coordinate and the estimated per-monitor width.
        # ----------------------------------------------------------
        BASE_SCALING = 96.0 / 72.0  # Standard tkinter baseline scaling factor
        actual_scaling = float(self.tk.call("tk", "scaling"))  # PEP 8 fix: use double quotes consistently
        ratio = actual_scaling / BASE_SCALING  # HiDPI multiplier (1.0 on normal displays)

        # Total virtual desktop dimensions (spanning all connected monitors)
        phys_w = self.winfo_screenwidth()
        phys_h = self.winfo_screenheight()

        # Estimate the number of monitors from the virtual desktop aspect ratio
        # (e.g. 6912 / 2160 ≈ 3 monitors arranged side by side)
        monitors = max(1, round(phys_w / phys_h))
        mon_w = phys_w // monitors  # Approximate width of a single monitor in pixels

        # Target visual size in device-independent pixels
        TARGET_W, TARGET_H = 1300, 820

        # Scale up to compensate for HiDPI; clamp to monitor bounds
        WIN_W = min(int(TARGET_W * ratio), mon_w - 40)
        WIN_H = min(int(TARGET_H * ratio), phys_h - 80)

        self.resizable(True, True)
        self.minsize(WIN_W, WIN_H)

        # Force tkinter to calculate widget sizes before reading pointer position
        self.update_idletasks()

        # Centre on the monitor where the mouse cursor currently resides
        ptr_x = self.winfo_pointerx()
        mon_index = min(ptr_x // mon_w, monitors - 1)  # Zero-based monitor index
        mon_origin_x = mon_index * mon_w                # Left edge of the active monitor
        x = mon_origin_x + (mon_w - WIN_W) // 2        # Horizontal centre
        y = (phys_h - WIN_H) // 2                      # Vertical centre
        self.geometry(f"{WIN_W}x{WIN_H}+{x}+{y}")

        # ----------------------------------------------------------
        # Focus and modality
        # transient() keeps this window above the master at all times;
        # grab_set() makes it modal (blocks interaction with the master).
        # ----------------------------------------------------------
        self.transient(master)
        self.lift()
        self.focus_force()
        self.grab_set()
        self.focus()

        # ----------------------------------------------------------
        # Load client records from the shared JSONL storage file
        # ----------------------------------------------------------
        self.records = load_records() or []

        # ----------------------------------------------------------
        # Fields that must not be empty when creating or updating a record.
        # "ID" is intentionally excluded: it is auto-assigned on creation
        # and only entered manually when searching or updating by ID.
        # ----------------------------------------------------------
        self.required_fields = ["Name", "Phone Number"]

        # ----------------------------------------------------------
        # ttk Style configuration
        # Applied to the Treeview table and its scrollbars
        # ----------------------------------------------------------
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.map("Treeview", background=[("selected", "#3498db")])
        self.style.configure("Treeview", font=("Arial", 12))
        self.style.configure("Treeview.Heading", font=("Arial", 13, "bold"))
        self.style.configure(
            "Vertical.TScrollbar",
            gripcount=0,
            background="#5d6d7e",
            troughcolor="#ecf0f1",
            bordercolor="#ecf0f1",
            arrowcolor="white",
            width=22  # Wider than the default for easier grabbing
        )
        self.style.configure(
            "Horizontal.TScrollbar",
            gripcount=0,
            background="#5d6d7e",
            troughcolor="#ecf0f1",
            bordercolor="#ecf0f1",
            arrowcolor="white",
            width=18
        )

        # ----------------------------------------------------------
        # Load the client icon for the header.
        # Falls back gracefully if the asset file is not found.
        # ----------------------------------------------------------
        assets = os.path.join(os.path.dirname(__file__), "assets")
        try:
            self.client_icon = tk.PhotoImage(
                file=os.path.join(assets, "client.png")
            ).subsample(3, 3)  # Reduce icon to one-third of its original size
        except Exception:
            self.client_icon = None

        # ----------------------------------------------------------
        # Build all GUI widgets and populate the Treeview with existing records
        # ----------------------------------------------------------
        self.create_widgets()
        self.populate_treeview()

        # ----------------------------------------------------------
        # Event bindings
        # ----------------------------------------------------------
        self.protocol("WM_DELETE_WINDOW", self.on_close)           # Save on close
        self.bind("<Return>", lambda event: self.create_client())  # Enter key creates a record
        self.entries["Name"].focus_set()                          # Initial focus on Name for Create

    # ----------------------------------------------------------
    # GUI construction
    # ----------------------------------------------------------

    def create_widgets(self) -> None:  # PEP 8 fix: add type annotations
        """Create and lay out all GUI widgets within the window."""

        # Header bar — dark background with centred title and icon
        header = tk.Frame(self, bg="#2c3e50", pady=15)
        header.pack(fill="x")
        tk.Label(
            header,
            text="CLIENT RECORD MANAGEMENT",
            font=("Arial", 18, "bold"),
            image=self.client_icon,
            compound="left",
            fg="white",
            bg="#2c3e50"
        ).pack()

        # ----------------------------------------------------------
        # Main container — holds the form, buttons, and table
        # ----------------------------------------------------------
        main = tk.Frame(self, bg="#f4f6f7", padx=20, pady=10)
        main.pack(fill="both", expand=True)

        # ----------------------------------------------------------
        # Input form — labelled frame containing all record fields
        # ----------------------------------------------------------
        form = tk.LabelFrame(
            main,
            text="Client Information",
            font=("Arial", 11, "bold"),
            bg="white",
            padx=20,
            pady=20
        )
        form.pack(fill="x", pady=10)

        # Field names in display order
        self.fields = [
            "ID",
            "Name",
            "Address Line 1",
            "Address Line 2",
            "Address Line 3",
            "City",
            "State",
            "Zip Code",
            "Country",
            "Phone Number"
        ]
        self.entries = {}

        # Lay out fields in a two-column grid
        for i, field in enumerate(self.fields):
            row = i // 2
            col = (i % 2) * 2
            # Append an asterisk to required field labels; the ID field
            # gets a note because it is auto-assigned during Create and
            # only entered manually for Search and Update.
            if field == "ID":
                label_text = "ID (auto-assigned; enter for Search/Update)"
            elif field in self.required_fields:
                label_text = field + " *"
            else:
                label_text = field
            tk.Label(
                form,
                text=label_text,
                bg="white",
                font=("Arial", 12)
            ).grid(row=row, column=col, sticky="w", pady=10)

            entry = tk.Entry(form, font=("Arial", 12), bd=2, relief="solid")
            entry.grid(row=row, column=col + 1, pady=10, padx=10, sticky="ew")
            self.entries[field] = entry

        # Allow both entry columns to expand when the window is resized
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        # Required fields note below the form
        tk.Label(
            main,
            text="* Required fields",
            bg="#f4f6f7",
            fg="#c0392b",
            font=("Arial", 10, "italic")
        ).pack(anchor="w", padx=5)

        # ----------------------------------------------------------
        # CRUD action buttons
        # ----------------------------------------------------------
        btn_frame = tk.Frame(main, bg="#f4f6f7")
        btn_frame.pack(fill="x", pady=12)

        buttons = [
            ("Create", "#27ae60", self.create_client),
            ("Update", "#2980b9", self.update_client),
            ("Delete", "#c0392b", self.delete_client),
            ("Search", "#8e44ad", self.search_client),
            ("Clear",  "#7f8c8d", self.clear_form),
        ]

        def on_enter(e: tk.Event) -> None:  # PEP 8 fix: add type annotations
            """Darken button on mouse-over."""
            e.widget['bg'] = '#34495e'

        def on_leave(e: tk.Event, color: str) -> None:  # PEP 8 fix: add type annotations
            """Restore original button colour when cursor leaves."""
            e.widget['bg'] = color

        for i, (text, color, cmd) in enumerate(buttons):
            btn = tk.Button(
                btn_frame,
                text=text,
                bg=color,
                fg="white",
                width=14,
                font=("Arial", 12, "bold"),
                command=cmd
            )
            btn.grid(row=0, column=i, padx=5, sticky="ew")
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", lambda e, c=color: on_leave(e, c))
            btn_frame.columnconfigure(i, weight=1)

        # ----------------------------------------------------------
        # Treeview record table with vertical and horizontal scrollbars
        # ----------------------------------------------------------
        table_frame = tk.Frame(main, bg="white")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = (
            "ID", "NAME", "ADDRESS 1", "ADDRESS 2", "ADDRESS 3",
            "CITY", "STATE", "ZIP CODE", "COUNTRY", "PHONE NUMBER"
        )

        # All 10 columns share the same width; stretch=True ensures they
        # expand proportionally when the window is resized
        col_width = 130
        col_widths = {col: col_width for col in columns}

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",  # Hide the default empty first column
            height=12
        )

        # Alternating row colours for readability
        self.tree.tag_configure('oddrow',  background='white')
        self.tree.tag_configure('evenrow', background='#f2f2f2')

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(
                col,
                anchor="center",
                width=col_widths[col],
                minwidth=col_widths[col],
                stretch=True  # All columns expand equally when the window is resized
            )

        # Horizontal scrollbar — packed before the tree so it appears below
        xscroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=xscroll.set)
        xscroll.pack(side="bottom", fill="x")

        # Vertical scrollbar — packed before the tree so it appears to the right
        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        yscroll.pack(side="right", fill="y")

        self.tree.pack(fill="both", expand=True)

        # Placeholder label shown when no records exist
        self.empty_label = tk.Label(
            table_frame,
            text="No clients registered yet",
            font=("Arial", 15, "italic"),
            bg="white",
            fg="#777777"
        )
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

        # Populate the form when the user clicks a row in the table
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # ----------------------------------------------------------
        # Total record counter displayed below the table
        # ----------------------------------------------------------
        self.counter = tk.Label(
            main,
            text="",
            font=("Arial", 12, "bold"),
            bg="#f4f6f7"
        )
        self.counter.pack(anchor="e", padx=5)

        # ----------------------------------------------------------
        # Status bar at the bottom of the window
        # ----------------------------------------------------------
        self.status = tk.Label(
            self,
            text="System Ready",
            bd=1,
            relief="sunken",
            anchor="w",
            bg="#ecf0f1",
            font=("Arial", 12)
        )
        self.status.pack(fill="x", side="bottom")

    # ----------------------------------------------------------
    # Treeview population
    # ----------------------------------------------------------

    def populate_treeview(self) -> None:  # PEP 8 fix: add type annotations
        """
        Clear and repopulate the Treeview with all client records.
        Shows an empty-state label when no records are present and
        updates the total client counter.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)

        count = 0
        for idx, r in enumerate(self.records):
            if r.get("Type") == "Client":
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.tree.insert("", "end", values=(
                    r.get("ID"),
                    r.get("Name"),
                    r.get("Address Line 1"),
                    r.get("Address Line 2"),
                    r.get("Address Line 3"),
                    r.get("City"),
                    r.get("State"),
                    r.get("Zip Code"),
                    r.get("Country"),
                    r.get("Phone Number")
                ), tags=(tag,))
                count += 1

        # Toggle empty-state label visibility
        if count == 0:
            self.empty_label.lift()   # Bring the label to the front
        else:
            self.empty_label.lower()  # Send the label behind the Treeview

        self.counter.config(text=f"Total Clients: {count}")

    # ----------------------------------------------------------
    # Input helpers
    # ----------------------------------------------------------

    def get_client_id(self) -> int | None:  # PEP 8 fix: add type annotations
        """
        Read and return the ID field as an integer.
        Displays a warning dialogue and returns None if the value is not numeric.
        """
        try:
            return int(self.entries["ID"].get())
        except ValueError:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Input Error", "ID must be a number.", parent=self)
            return None

    def clear_form(self) -> None:  # PEP 8 fix: add type annotations
        """Clear all entry fields and remove any validation highlights."""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
            entry.config(highlightthickness=0)
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        # Focus Name since ID is auto-assigned on Create (entered only for Search/Update)
        self.entries["Name"].focus_set()
        self.status.config(text="✔ Form cleared. Ready")

    def get_entry_values(self) -> dict[str, str]:  # PEP 8 fix: add type annotations
        """Return a dictionary of all field values, stripped of leading/trailing whitespace."""
        return {f: self.entries[f].get().strip() for f in self.fields}

    def validate_field(self, field: str, value: str) -> bool:  # PEP 8 fix: add type annotations
        """
        Validate a single field value according to its expected data type.
        Optional fields that are empty are considered valid.
        """
        value = value.strip()
        if not value:
            return True  # Empty optional fields are acceptable
        if field in ["ID", "Zip Code", "Phone Number"]:
            return value.isdigit()  # Numeric fields must contain digits only
        elif field in ["Name", "City", "State", "Country"]:
            return bool(re.match(r"^[A-Za-z\s'-]+$", value))  # Letters and spaces only
        return True  # All other fields accept any non-empty string

    def validate_entries(self, values: dict[str, str]) -> tuple[bool, str | None]:  # PEP 8 fix
        """
        Validate all entry values.

        Returns a tuple of (is_valid: bool, invalid_field: str | None).
        Checks required fields first, then applies per-field type validation.
        """
        for field in self.required_fields:
            if not values[field]:
                return False, field
        for field, value in values.items():
            if not self.validate_field(field, value):
                return False, field
        return True, None

    # ----------------------------------------------------------
    # CRUD operations
    # ----------------------------------------------------------

    def create_client(self) -> None:  # PEP 8 fix: add type annotations
        """
        Validate the form and create a new client record.

        The ID is auto-assigned to the next available integer — the user
        does not enter an ID manually during creation.  The ID field in the
        form is reserved for Search and Update operations only.
        Highlights any missing required fields in red before saving.
        """
        missing = []
        for field in self.required_fields:
            if not self.entries[field].get().strip():
                missing.append(field)
                self.entries[field].config(highlightbackground="red", highlightthickness=1)
            else:
                self.entries[field].config(highlightthickness=0)

        if missing:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Validation", "Please fill all required fields.", parent=self)
            self.status.config(text="Validation failed: required fields missing.")
            return

        values = self.get_entry_values()
        is_valid, invalid_field = self.validate_entries(values)
        if not is_valid:
            self.lift()
            self.focus_force()
            messagebox.showwarning(
                "Validation Error",
                f"Invalid or missing value for '{invalid_field}'.",
                parent=self
            )
            self.entries[invalid_field].focus()
            self.status.config(text=f"Validation failed: '{invalid_field}' invalid/missing.")
            return

        # Auto-assign the next available Client ID; the user never enters one manually.
        # max(..., default=0) returns 0 when no Client records exist yet, so the
        # first ID assigned will be 1.
        existing_ids = [
            r["ID"] for r in self.records
            if r.get("Type") == "Client" and isinstance(r.get("ID"), int)
        ]
        cid = max(existing_ids, default=0) + 1

        # PEP 8 fix: remove extra alignment spaces before `=`
        values["ID"] = cid
        values["Type"] = "Client"
        self.records.append(values)
        save_records(self.records)
        self.populate_treeview()
        self.clear_form()
        self.status.config(text=f"✔ Client added successfully (assigned ID: {cid}).")
        self.lift()
        self.focus_force()
        messagebox.showinfo(
            "Success",
            f"✔ Client record added successfully.\nAssigned ID: {cid}",
            parent=self
        )

    def search_client(self) -> None:  # PEP 8 fix: add type annotations
        """
        Search for a client by ID.
        If additional fields are filled in, verifies that they match the stored record.
        Populates the form and highlights the matching row in the table on success.
        """
        cid = self.get_client_id()
        if cid is None:
            return

        values = self.get_entry_values()

        record = next(
            (r for r in self.records
             if r.get("Type") == "Client" and str(r.get("ID")) == str(cid)),
            None
        )
        if not record:
            self.lift()
            self.focus_force()
            messagebox.showinfo("Search", "Client not found.", parent=self)
            self.status.config(text="✖ Client not found.")
            return

        # Check that any additionally entered fields match the stored record
        mismatch = any(
            value and str(record.get(field, "")).lower() != value.lower()
            for field, value in values.items()
            if field != "ID"
        )
        if mismatch:
            self.lift()
            self.focus_force()
            messagebox.showwarning(
                "Search",
                "Client ID exists but some entered information does not match.",
                parent=self
            )
            self.status.config(text="✖ ID found but information mismatch.")
            return

        # Populate the form with the found record
        for field in self.fields:
            self.entries[field].delete(0, tk.END)
            self.entries[field].insert(0, record.get(field, ""))

        # Highlight the matching row in the Treeview
        for item in self.tree.get_children():
            if str(self.tree.item(item, "values")[0]) == str(cid):
                self.tree.selection_set(item)
                self.tree.focus(item)
                self.tree.see(item)
                break

        self.status.config(text=f"✔ Client '{record['Name']}' found.")
        self.lift()
        self.focus_force()
        messagebox.showinfo("Search Result", f"✔ Client '{record['Name']}' found.", parent=self)

    def update_client(self) -> None:  # PEP 8 fix: add type annotations
        """
        Update an existing client record identified by the ID field.
        Cascades any ID change to associated flight records.
        """
        cid = self.get_client_id()
        if cid is None:
            return

        record = next(
            (r for r in self.records
             if r.get("Type") == "Client" and str(r.get("ID")) == str(cid)),
            None
        )
        if not record:
            self.lift()
            self.focus_force()
            messagebox.showinfo("Update", "Client not found.", parent=self)
            return

        old_id = record["ID"]
        values = self.get_entry_values()

        is_valid, invalid_field = self.validate_entries(values)
        if not is_valid:
            self.lift()
            self.focus_force()
            messagebox.showwarning(
                "Validation Error",
                f"Invalid or missing value for '{invalid_field}'.",
                parent=self
            )
            self.entries[invalid_field].focus()
            self.status.config(text=f"Validation failed: '{invalid_field}' invalid/missing.")
            return

        for field in self.fields:
            record[field] = values[field]

        new_id = record["ID"]

        # Cascade ID change to any linked flight records
        if old_id != new_id:
            for r in self.records:
                if r.get("Type") == "Flight" and r.get("Client_ID") == old_id:
                    r["Client_ID"] = new_id

        save_records(self.records)
        self.populate_treeview()
        self.clear_form()
        self.status.config(text="✔ Client record updated successfully.")
        self.lift()
        self.focus_force()
        messagebox.showinfo("Success", "✔ Client record updated successfully.", parent=self)

    def delete_client(self) -> None:  # PEP 8 fix: add type annotations
        """
        Delete the selected client record and all associated flight records
        after asking the user for confirmation.
        """
        selected = self.tree.selection()
        if not selected:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Delete", "Select a client first.", parent=self)
            return

        client_id = str(self.tree.item(selected[0], "values")[0])

        self.lift()
        self.focus_force()
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete Client {client_id} and ALL their flights?",
            parent=self
        ):
            return

        # Remove the client and all of their associated flight records
        self.records = [
            r for r in self.records
            if not (
                # PEP 8 fix: remove extra alignment spaces
                (r.get("Type") == "Client" and str(r.get("ID")) == client_id) or
                (r.get("Type") == "Flight" and str(r.get("Client_ID")) == client_id)
            )
        ]
        save_records(self.records)
        self.populate_treeview()
        self.tree.selection_remove(self.tree.selection())
        self.status.config(text=f"✔ Client {client_id} and related flights deleted.")
        self.lift()
        self.focus_force()
        messagebox.showinfo("Deleted", "Client and associated flights removed.", parent=self)

    # ----------------------------------------------------------
    # Treeview selection event
    # ----------------------------------------------------------

    def on_tree_select(self, event: tk.Event) -> None:  # PEP 8 fix: add type annotations
        """Populate the form fields when the user selects a row in the Treeview."""
        selected = self.tree.selection()
        if not selected:
            return
        cid = self.tree.item(selected[0], "values")[0]
        for r in self.records:
            if r.get("Type") == "Client" and str(r.get("ID")) == str(cid):
                for field in self.fields:
                    self.entries[field].delete(0, tk.END)
                    self.entries[field].insert(0, r.get(field, ""))
                self.status.config(text="Client loaded from table.")
                break

    # ----------------------------------------------------------
    # Window close event
    # ----------------------------------------------------------

    def on_close(self) -> None:  # PEP 8 fix: add type annotations
        """Persist all records to the JSONL file before destroying the window."""
        save_records(self.records)
        self.destroy()
