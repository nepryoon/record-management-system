import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from src.storage import load_records, save_records  # PEP 8 fix


class FlightWindow(tk.Toplevel):
    """
    Flight Record Management Window.

    Handles Flight records containing Client ID, Airline ID, Date,
    Start City, and End City. Provides a full CRUD interface:
    Create, Search, Update, and Delete.
    """

    def __init__(self, master=None):
        super().__init__(master)

        # ----------------------------------------------------------
        # Window title and background colour
        # ----------------------------------------------------------
        self.title("Flight Record System")
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
        # Load the flight icon for the header.
        # Falls back gracefully if the asset file is not found.
        # ----------------------------------------------------------
        assets = os.path.join(os.path.dirname(__file__), "assets")
        try:
            self.flight_icon = tk.PhotoImage(
                file=os.path.join(assets, "flight.png")
            ).subsample(3, 4)  # Reduce icon to roughly one-quarter of its original size
        except Exception:
            self.flight_icon = None

        # ----------------------------------------------------------
        # Build all GUI widgets and populate the Treeview with existing records
        # ----------------------------------------------------------
        self.create_widgets()
        self.populate_treeview()

        # ----------------------------------------------------------
        # Event bindings
        # ----------------------------------------------------------
        self.protocol("WM_DELETE_WINDOW", self.on_close)              # Persist records on close
        self.bind("<Return>", lambda e: self.create_flight())          # Enter key creates a record
        self.entries["Client ID *"].focus_set()                        # Initial focus on Client ID

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
            text="FLIGHT RECORD MANAGEMENT",
            font=("Arial", 18, "bold"),
            image=self.flight_icon,
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
        # Input form — labelled frame containing all flight fields
        # ----------------------------------------------------------
        form = tk.LabelFrame(
            main,
            text="Flight Information",
            font=("Arial", 11, "bold"),
            bg="white",
            padx=20,
            pady=20
        )
        form.pack(fill="x", pady=10)

        # Field labels displayed in the form; all are mandatory for a flight record
        labels = [
            "Client ID *",
            "Airline ID *",
            "Date (YYYY-MM-DD HH:MM) *",
            "Start City *",
            "End City *"
        ]
        self.entries = {}

        # Lay out each field on its own row
        for i, text in enumerate(labels):
            tk.Label(
                form,
                text=text,
                bg="white",
                font=("Arial", 12)
            ).grid(row=i, column=0, sticky="w", pady=10)
            entry = tk.Entry(form, font=("Arial", 12), bd=2, relief="solid")
            entry.grid(row=i, column=1, padx=10, sticky="ew")
            self.entries[text] = entry

        # Allow the entry column to expand when the window is resized
        form.columnconfigure(1, weight=1)

        # Required fields note below the last form entry
        tk.Label(
            form,
            text="* Required fields",
            font=("Arial", 11, "italic"),
            fg="#e74c3c",  # Red to indicate mandatory fields
            bg="white"
        ).grid(row=len(labels), column=0, columnspan=2, sticky="w", pady=(0, 5))

        # ----------------------------------------------------------
        # CRUD action buttons
        # ----------------------------------------------------------
        btn_frame = tk.Frame(main, bg="#f4f6f7")
        btn_frame.pack(fill="x", pady=12)

        buttons = [
            ("Create", "#27ae60", self.create_flight),
            ("Update", "#2980b9", self.update_flight),
            ("Delete", "#c0392b", self.delete_flight),
            ("Search", "#8e44ad", self.search_flight),
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
        # Treeview record table with vertical and horizontal scrollbars
        # ----------------------------------------------------------
        table_frame = tk.Frame(main, bg="white")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("CLIENT ID", "AIRLINE ID", "DATE", "START CITY", "END CITY")
        col_widths = {
            "CLIENT ID": 100, "AIRLINE ID": 100, "DATE": 200,
            "START CITY": 180, "END CITY": 180
        }

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
                minwidth=col_widths[col]
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

        # Populate the form when the user clicks a row in the table
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Placeholder label shown when no records exist
        self.empty_label = tk.Label(
            table_frame,
            text="No flights registered yet",
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
        Clear and repopulate the Treeview with all flight records.
        Shows an empty-state label when no records are present and
        updates the total flight counter.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)

        count = 0
        for index, r in enumerate(self.records):
            if r.get("Type") == "Flight":
                tag = "evenrow" if index % 2 == 0 else "oddrow"
                self.tree.insert(
                    "", "end",
                    values=(
                        r.get("Client_ID"),
                        r.get("Airline_ID"),
                        r.get("Date"),
                        r.get("Start City"),
                        r.get("End City")
                    ),
                    tags=(tag,)
                )
                count += 1

        # Toggle empty-state label visibility
        if count == 0:
            self.empty_label.lift()   # Bring the label to the front
        else:
            self.empty_label.lower()  # Send the label behind the Treeview

        self.counter.config(text=f"Total Flights: {count}")

    # ----------------------------------------------------------
    # Input helpers
    # ----------------------------------------------------------

    def clear_form(self):
        """Clear all entry fields and deselect any highlighted table row."""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        self.entries["Client ID *"].focus_set()
        self.status.config(text="✔ Form cleared. Ready")

    # ----------------------------------------------------------
    # CRUD operations
    # ----------------------------------------------------------

    def create_flight(self):
        """
        Validate the form and create a new flight record.
        Verifies that the referenced Client ID and Airline ID already
        exist in the data store before saving.
        """
        # Reload records to ensure no stale data is used
        self.records = load_records() or []

        client_id  = self.entries["Client ID *"].get().strip()
        airline_id = self.entries["Airline ID *"].get().strip()
        date       = self.entries["Date (YYYY-MM-DD HH:MM) *"].get().strip()
        start      = self.entries["Start City *"].get().strip()
        end        = self.entries["End City *"].get().strip()

        # All fields are mandatory for a flight record
        if not all([client_id, airline_id, date, start, end]):
            self.lift()
            self.focus_force()
            messagebox.showwarning("Validation", "All fields must be filled.", parent=self)
            return

        # Validate the date string against the expected format
        try:
            datetime.strptime(date, "%Y-%m-%d %H:%M")
        except ValueError:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Date Error", "Use format: YYYY-MM-DD HH:MM", parent=self)
            return

        # Verify that the referenced client exists
        if not any(
            r.get("Type") == "Client" and str(r.get("ID")) == str(client_id)
            for r in self.records
        ):
            self.lift()
            self.focus_force()
            messagebox.showerror("Error", f"Client ID {client_id} does not exist.", parent=self)
            return

        # Verify that the referenced airline exists
        if not any(
            r.get("Type") == "Airline" and str(r.get("ID")) == str(airline_id)
            for r in self.records
        ):
            self.lift()
            self.focus_force()
            messagebox.showerror("Error", f"Airline ID {airline_id} does not exist.", parent=self)
            return

        self.records.append({
            "Client_ID":  int(client_id),
            "Airline_ID": int(airline_id),
            "Date":       date,
            "Start City": start,
            "End City":   end,
            "Type":       "Flight"
        })
        save_records(self.records)
        self.populate_treeview()
        self.clear_form()
        self.status.config(text="✔ Flight created successfully.")
        self.lift()
        self.focus_force()
        messagebox.showinfo("Success", "✔ Flight record added successfully.", parent=self)

    def search_flight(self):
        """
        Search for all flights belonging to a given Client ID.
        Highlights every matching row in the Treeview on success.
        """
        cid   = self.entries["Client ID *"].get().strip()
        found = False

        for r in self.records:
            if r.get("Type") == "Flight" and str(r.get("Client_ID")) == cid:
                found = True
                # Highlight the corresponding row in the Treeview
                for item in self.tree.get_children():
                    vals = self.tree.item(item, "values")
                    if (str(vals[0]) == str(r.get("Client_ID")) and
                            str(vals[1]) == str(r.get("Airline_ID")) and
                            str(vals[2]) == str(r.get("Date"))):
                        self.tree.selection_set(item)
                        self.tree.focus(item)
                        self.tree.see(item)
                        break

        if found:
            self.status.config(text=f"✔ Flights for Client ID {cid} found.")
            self.lift()
            self.focus_force()
            messagebox.showinfo(
                "Search Result", f"✔ Flight for Client ID {cid} found.", parent=self
            )
        else:
            self.lift()
            self.focus_force()
            messagebox.showinfo("Search", "✖ Flight not found.", parent=self)

    def update_flight(self):
        """
        Update the currently selected flight record with values from the form.
        The record is matched by the original Client ID, Airline ID, and Date
        read from the selected Treeview row.
        """
        selected = self.tree.selection()
        if not selected:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Update", "Select a flight first.", parent=self)
            return

        values = self.tree.item(selected[0], "values")
        orig_client_id  = int(values[0])
        orig_airline_id = int(values[1])
        orig_date       = str(values[2])

        # Locate the matching record in the in-memory list
        record_to_update = next(
            (r for r in self.records
             if r.get("Type") == "Flight"
             and r.get("Client_ID")  == orig_client_id
             and r.get("Airline_ID") == orig_airline_id
             and str(r.get("Date"))  == orig_date),
            None
        )
        if not record_to_update:
            self.lift()
            self.focus_force()
            messagebox.showerror("Error", "Could not find the record to update.", parent=self)
            return

        # Overwrite each field with the current entry values
        record_to_update["Client_ID"]  = int(self.entries["Client ID *"].get())
        record_to_update["Airline_ID"] = int(self.entries["Airline ID *"].get())
        record_to_update["Date"]       = self.entries["Date (YYYY-MM-DD HH:MM) *"].get()
        record_to_update["Start City"] = self.entries["Start City *"].get()
        record_to_update["End City"]   = self.entries["End City *"].get()

        save_records(self.records)
        self.populate_treeview()
        self.status.config(text="✔ Flight record updated successfully.")
        self.lift()
        self.focus_force()
        messagebox.showinfo("Success", "✔ Flight record updated successfully.", parent=self)

    def delete_flight(self):
        """
        Delete the selected flight record after asking the user for confirmation.
        Matches the record by Client ID, Airline ID, and Date.
        """
        selected = self.tree.selection()
        if not selected:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Delete", "Select a flight first.", parent=self)
            return

        self.lift()
        self.focus_force()
        if not messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete the selected flight?",
            parent=self
        ):
            return

        values = self.tree.item(selected[0], "values")
        deleted = False

        for r in self.records:
            if (r.get("Type") == "Flight"
                    and str(r.get("Client_ID"))  == str(values[0])
                    and str(r.get("Airline_ID")) == str(values[1])
                    and str(r.get("Date"))        == str(values[2])):
                self.records.remove(r)
                deleted = True
                break

        if deleted:
            save_records(self.records)
            self.populate_treeview()
            self.clear_form()
            self.status.config(text="✔ Flight deleted successfully.")
            self.lift()
            self.focus_force()
            messagebox.showinfo(
                "Delete Successful", "✔ Flight was deleted successfully.", parent=self
            )
        else:
            self.lift()
            self.focus_force()
            messagebox.showinfo("Delete", "Flight not found.", parent=self)

    # ----------------------------------------------------------
    # Treeview selection event
    # ----------------------------------------------------------

    def on_tree_select(self, event):
        """Populate the form fields when the user selects a row in the Treeview."""
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        keys   = list(self.entries.keys())
        # Map each Treeview column value to its corresponding entry widget
        for i, key in enumerate(keys):
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, values[i])

    # ----------------------------------------------------------
    # Window close event
    # ----------------------------------------------------------

    def on_close(self):
        """Persist all records to the JSONL file before destroying the window."""
        save_records(self.records)
        self.grab_release()  # Release the modal grab before destroying
        self.destroy()
