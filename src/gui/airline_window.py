import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Adjust the Python path to allow imports from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from storage import load_records, save_records


class AirlineWindow(tk.Toplevel):
    """
    Airline Record Management Window.

    Handles Airline Company records, each containing an ID and a Company Name.
    Provides a full CRUD interface: Create, Search, Update, and Delete.
    """

    def __init__(self, master=None):
        super().__init__(master)

        # ----------------------------------------------------------
        # Window title and background colour
        # ----------------------------------------------------------
        self.title("Airline Management System")
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
        actual_scaling = float(self.tk.call('tk', 'scaling'))  # Current system scaling
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
        # Load all records from the shared JSONL storage file
        # ----------------------------------------------------------
        self.records = load_records() or []
        print("DEBUG: Loaded records:", self.records)

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
        # Load the airline icon for the header.
        # Falls back gracefully if the asset file is not found.
        # ----------------------------------------------------------
        assets = os.path.join(os.path.dirname(__file__), "assets")
        try:
            self.airline_icon = tk.PhotoImage(
                file=os.path.join(assets, "airline.png")
            ).subsample(3, 4)  # Reduce icon to roughly one-quarter of its original size
        except Exception:
            self.airline_icon = None

        # ----------------------------------------------------------
        # Build all GUI widgets and populate the Treeview with existing records
        # ----------------------------------------------------------
        self.create_widgets()
        self.populate_treeview()

        # ----------------------------------------------------------
        # Event bindings
        # ----------------------------------------------------------
        self.protocol("WM_DELETE_WINDOW", self.on_close)           # Persist records on close
        self.bind("<Return>", lambda e: self.create_airline())      # Enter key creates a record
        self.id_entry.focus_set()                                   # Initial focus on the ID field

    # ----------------------------------------------------------
    # GUI construction
    # ----------------------------------------------------------

    def create_widgets(self):
        """Create and lay out all GUI widgets within the window."""

        # Header bar — dark background with centred title and icon
        header = tk.Frame(self, bg="#2c3e50", pady=15)
        header.pack(fill="x")
        tk.Label(
            header,
            text=" AIRLINE COMPANY RECORDS",
            font=("Arial", 18, "bold"),
            image=self.airline_icon,
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
        # Input form — labelled frame containing the two airline fields
        # ----------------------------------------------------------
        form = tk.LabelFrame(
            main,
            text=" Airline Information ",
            bg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=20
        )
        form.pack(fill="x", pady=10)

        # Airline ID field
        tk.Label(
            form, text="Airline ID *", bg="white", font=("Arial", 12)
        ).grid(row=0, column=0, sticky="w", pady=8)
        self.id_entry = tk.Entry(form, bd=2, relief="solid", font=("Arial", 12))
        self.id_entry.grid(row=0, column=1, sticky="ew", padx=10)

        # Company Name field
        tk.Label(
            form, text="Company Name *", bg="white", font=("Arial", 12)
        ).grid(row=1, column=0, sticky="w", pady=8)
        self.name_entry = tk.Entry(form, bd=2, relief="solid", font=("Arial", 12))
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=10)

        # Allow the entry column to expand when the window is resized
        form.columnconfigure(1, weight=1)

        # Required fields note below the form entries
        tk.Label(
            form,
            text="* Required fields",
            font=("Arial", 10, "italic"),
            fg="#e74c3c",  # Red to indicate mandatory fields
            bg="white"
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 5))

        # ----------------------------------------------------------
        # CRUD action buttons
        # ----------------------------------------------------------
        btn_frame = tk.Frame(main, bg="#f4f6f7")
        btn_frame.pack(fill="x", pady=12)

        buttons = [
            ("Create", "#27ae60", self.create_airline),
            ("Update", "#2980b9", self.update_airline),
            ("Delete", "#c0392b", self.delete_airline),
            ("Search", "#8e44ad", self.search_airline),
            ("Clear",  "#7f8c8d", self.clear_form),
        ]

        def on_enter(e):
            """Darken button on mouse-over."""
            e.widget['bg'] = '#34495e'

        def on_leave(e, color):
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
        # Treeview record table with vertical scrollbar
        # ----------------------------------------------------------
        table_frame = tk.Frame(main, bg="white")
        table_frame.pack(fill="both", expand=True, pady=12)

        cols = ("ID", "Company Name")
        self.tree = ttk.Treeview(
            table_frame,
            columns=cols,
            show="headings",  # Hide the default empty first column
            height=12
        )

        # Alternating row colours for readability
        self.tree.tag_configure('oddrow',  background='white')
        self.tree.tag_configure('evenrow', background='#f2f2f2')

        for col in cols:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, anchor="center", width=250)

        # Vertical scrollbar — packed before the tree so it appears to the right
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # Populate the form when the user clicks a row in the table
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Placeholder label shown when no records exist
        self.empty_label = tk.Label(
            table_frame,
            text="No airlines registered yet",
            font=("Arial", 15, "italic"),
            bg="white",
            fg="#555555"
        )
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

        # ----------------------------------------------------------
        # Total record counter displayed below the table
        # ----------------------------------------------------------
        self.counter = tk.Label(
            main,
            text="",
            bg="#f4f6f7",
            font=("Arial", 12, "bold")
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

    def populate_treeview(self):
        """
        Clear and repopulate the Treeview with all airline records.
        Shows an empty-state label when no records are present and
        updates the total airline counter.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)

        count = 0
        for index, r in enumerate(self.records):
            if r.get("Type") == "Airline":
                tag = "evenrow" if index % 2 == 0 else "oddrow"
                self.tree.insert(
                    "", "end",
                    values=(r.get("ID"), r.get("Company Name")),
                    tags=(tag,)
                )
                count += 1

        # Toggle empty-state label visibility
        if count == 0:
            self.empty_label.lift()   # Bring the label to the front
        else:
            self.empty_label.lower()  # Send the label behind the Treeview

        self.counter.config(text=f"Total Airlines: {count}")

    # ----------------------------------------------------------
    # Input helpers
    # ----------------------------------------------------------

    def clear_form(self):
        """Clear both entry fields and deselect any highlighted table row."""
        self.id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        self.id_entry.focus_set()
        self.status.config(text="✔ Form cleared. Ready")

    # ----------------------------------------------------------
    # CRUD operations
    # ----------------------------------------------------------

    def create_airline(self):
        """
        Validate the form and create a new airline record.
        Rejects non-numeric IDs and duplicate airline IDs.
        """
        try:
            aid = int(self.id_entry.get().strip())
        except ValueError:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Input Error", "ID must be a number.", parent=self)
            return

        name = self.name_entry.get().strip()
        if not name:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Validation", "Company Name is required.", parent=self)
            return

        # Reject duplicate airline IDs
        if any(r.get("ID") == aid and r.get("Type") == "Airline" for r in self.records):
            self.lift()
            self.focus_force()
            messagebox.showerror("Error", "Airline ID already exists.", parent=self)
            return

        self.records.append({"ID": aid, "Company Name": name, "Type": "Airline"})
        save_records(self.records)
        self.populate_treeview()
        self.clear_form()
        self.status.config(text="✔ Airline created successfully.")
        self.lift()
        self.focus_force()
        messagebox.showinfo("Success", "✔ Airline added successfully.", parent=self)

    def search_airline(self):
        """
        Search for an airline by ID.
        If a Company Name is also provided, verifies that it matches the stored record.
        Populates the form and highlights the matching row in the table on success.
        """
        aid  = self.id_entry.get().strip()
        name = self.name_entry.get().strip()

        if not aid:
            self.lift()
            self.focus_force()
            messagebox.showwarning(
                "Search",
                "Please enter an Airline ID to search. Company Name alone is not sufficient.",
                parent=self
            )
            return

        record = next(
            (r for r in self.records
             if str(r.get("ID")) == str(aid) and r.get("Type") == "Airline"),
            None
        )
        if not record:
            self.lift()
            self.focus_force()
            messagebox.showinfo("Search", f"Airline ID {aid} not found.", parent=self)
            return

        # If a name was entered, verify it matches the stored record
        if name and record["Company Name"].lower() != name.lower():
            self.lift()
            self.focus_force()
            messagebox.showwarning(
                "Search",
                f"Airline ID {aid} exists but Company Name does not match.",
                parent=self
            )
            self.status.config(text="✖ ID found but Name mismatch.")
            return

        # Populate the form with the found record
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, record["ID"])
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, record["Company Name"])

        # Highlight the matching row in the Treeview
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

    def update_airline(self):
        """Update the Company Name of an existing airline identified by its ID."""
        aid  = self.id_entry.get().strip()
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

        for r in self.records:
            if str(r.get("ID")) == str(aid) and r.get("Type") == "Airline":
                r["Company Name"] = name
                save_records(self.records)
                self.populate_treeview()
                self.clear_form()
                self.status.config(text=f"✔ Airline {aid} updated successfully.")
                self.lift()
                self.focus_force()
                messagebox.showinfo("Update Successful", f"✔ Airline {aid} updated.", parent=self)
                return

        self.lift()
        self.focus_force()
        messagebox.showinfo("Update", "Airline not found.", parent=self)

    def delete_airline(self):
        """
        Delete the selected airline record and all associated flight records
        after asking the user for confirmation.
        """
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
            parent=self
        ):
            return

        # Remove the airline record
        self.records = [
            r for r in self.records
            if not (r.get("Type") == "Airline" and r.get("ID") == airline_id)
        ]

        # Cascade delete all flight records linked to this airline
        self.records = [
            r for r in self.records
            if not (r.get("Type") == "Flight" and r.get("Airline_ID") == airline_id)
        ]

        save_records(self.records)
        self.populate_treeview()
        self.clear_form()
        self.status.config(text=f"✔ Airline {airline_id} and related flights deleted.")
        self.lift()
        self.focus_force()
        messagebox.showinfo("Deleted", "Airline and associated flights removed.", parent=self)

    # ----------------------------------------------------------
    # Treeview selection event
    # ----------------------------------------------------------

    def on_tree_select(self, event):
        """Populate the form fields when the user selects a row in the Treeview."""
        selected = self.tree.selection()
        if not selected:
            return
        val = self.tree.item(selected[0], "values")
        # Guard against the empty-state placeholder row
        if val[1] == "No Airlines Registered Yet.":
            return
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, val[0])
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, val[1])

    # ----------------------------------------------------------
    # Window close event
    # ----------------------------------------------------------

    def on_close(self):
        """Persist all records to the JSONL file before destroying the window."""
        save_records(self.records)
        self.destroy()
