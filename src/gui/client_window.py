import tkinter as tk
from tkinter import ttk, messagebox
import re
import sys
import os

# Connect storage file
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from storage import load_records, save_records


class ClientWindow(tk.Toplevel):
    """
    Client Management Window
    Provides Create, Search, Update, Delete functionality for client records.
    """
    def __init__(self, master):
        super().__init__(master)

        # ----------------------------------------------------------
        # Window configuration
        self.title("Client Record System")
        self.geometry("1100x800")
        self.resizable(False, False) # Prevent resizing to maintain layout
        self.configure(bg="#f4f6f7")

        # Focus behaviour
        self.transient(master)
        self.grab_set()
        self.focus()

        # ----------------------------------------------------------
        # Load client records 
        self.records = load_records() or []  
        print("DEBUG: Loaded client records:", self.records) 

        # ----------------------------------------------------------
        # Required fields for validation
        self.required_fields = ["ID", "Name", "Phone Number"]

        # ----------------------------------------------------------
        # Style Setup
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.map("Treeview", background=[("selected", "#3498db")])
        self.style.configure("Treeview", font=("Arial", 12))
        self.style.configure("Treeview.Heading", font=("Arial", 13, "bold"))
 
        # ----------------------------------------------------------
        # Load Client Icon
        assets = os.path.join(os.path.dirname(__file__), "assets")
        try:
            self.client_icon = tk.PhotoImage(
                file=os.path.join(assets, "client.png")
            ).subsample(3,3)  # reduce icon size
        except Exception:
            self.client_icon = None

        # ----------------------------------------------------------
        # Build the GUI
        self.create_widgets()
        self.populate_treeview()

        # ----------------------------------------------------------
        # Event bindings
        
        self.protocol("WM_DELETE_WINDOW", self.on_close) # Save records when window closes
        self.bind("<Return>", lambda event: self.create_client()) # Press enter to create a client
        self.entries["ID"].focus_set() # Set focus to ID entry initially

    # ----------------------------------------------------------
    # GUI Components
    def create_widgets(self): 
        """Create and place all GUI widgets"""

        # Header
        header = tk.Frame(self,bg="#2c3e50", pady=15)
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
        # Main container frame
        main = tk.Frame(self, bg="#f4f6f7", padx=20, pady=10)
        main.pack(fill="both", expand=True)

        # ----------------------------------------------------------
        # Form Frame for client input
        form = tk.LabelFrame(
            main,
            text="Client Information",
            font=("Arial", 11, "bold"),
            bg="white",
            padx=20,
            pady=20
        )
        form.pack(fill="x", pady=10)

        # List of fields to display in the form
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

        # Form Grid
        for i, field in enumerate(self.fields):
            row = i // 2
            col = (i % 2) * 2
            # Add '*' for required fields
            label_text = field + " *" if field in self.required_fields else field
            tk.Label(
                form,
                text=label_text,
                bg="white",
                font=("Arial", 12)
            ).grid(row=row, column=col, sticky="w", pady=10)

            entry = tk.Entry(form, font=("Arial", 12), bd=2, relief="solid")
            entry.grid(row=row, column=col+1, pady=10, padx=10, sticky="ew")
            self.entries[field] = entry

        # Make form columns expand properly
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        # Required fields note
        tk.Label(
            main,
            text="* Required fields",
            bg="#f4f6f7",
            fg="#c0392b",
            font=("Arial", 10, "italic")
        ).pack(anchor="w", padx=5)

        # ----------------------------------------------------------
        # Buttons frame
        btn_frame = tk.Frame(main, bg="#f4f6f7")
        btn_frame.pack(fill="x", pady=12)

        # Define buttons with colours and linked commands
        buttons = [
            ("Create", "#27ae60", self.create_client),
            ("Update", "#2980b9", self.update_client),
            ("Delete", "#c0392b", self.delete_client),
            ("Search", "#8e44ad", self.search_client),
            ("Clear", "#7f8c8d", self.clear_form)
        ]
        
        # Button hover effect
        def on_enter(e):
            e.widget['bg'] = '#34495e'
        def on_leave(e, color):
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
        # Treeview Table
        table_frame = tk.Frame(main, bg="white")
        table_frame.pack(fill="both", expand=True, pady=12)

        # Only showing main info
        columns = ("ID", "Name", "City", "Country", "Phone Number")
        # Treeview columns
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12
        )
        # colors rows differently
        self.tree.tag_configure('oddrow', background='white')
        self.tree.tag_configure('evenrow', background='#f2f2f2')

        for col in columns:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, anchor="center", width=190)

        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbar for Treeview
        scroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        # ----------------------------------------------------------
        # Empty record message
        self.empty_label = tk.Label(
            table_frame,
            text="No clients registered yet",
            font=("Arial", 15, "italic"),
            bg="white",
            fg="#777777"
        )
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

         # Bind table selection
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # ----------------------------------------------------------
        # Total clients counter
        self.counter = tk.Label(
            main,
            text="",
            font=("Arial", 12, "bold"),
            bg="#f4f6f7"
        )
        self.counter.pack(anchor="e", padx=5)

        # ----------------------------------------------------------
        # Status bar at bottom
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
    # Populate Treeview
    def populate_treeview(self):
        """
        Populate the Treeview table with client records.
        Implements Empty State and updates total counter.
        """
         # Clear the table first
        for item in self.tree.get_children():
            self.tree.delete(item)

        count = 0
        for idx, r in enumerate(self.records):
            if r.get("Type") == "Client":
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.tree.insert("", "end", values=(
                    r.get("ID"), r.get("Name"), r.get("City"),
                    r.get("Country"), r.get("Phone Number")
                ), tags=(tag,))
                count += 1

        # Show or hide the empty label
        if count == 0:
            self.empty_label.lift()   # make it visible
        else:
            self.empty_label.lower()  # hide it

        # Update total clients counter
        self.counter.config(text=f"Total Clients: {count}")

    # ----------------------------------------------------------
    # Basic functions
    def get_client_id(self):
        """Return client ID as integer, with validation"""
        try:
            return int(self.entries["ID"].get())
        except ValueError:
            messagebox.showwarning("Input Error", "ID must be a number.")
            return None

    def clear_form(self):
        """Clear the entry fields"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
            entry.config(highlightthickness=0)
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        self.entries["ID"].focus_set()
        self.status.config(text="✔ Form cleared. Ready")

    def get_entry_values(self):
        return {f: self.entries[f].get().strip() for f in self.fields}

    def validate_field(self, field, value):
        """Validate input for each field based on type rules. Optional fields can be empty."""
        value = value.strip()
        # If field is empty, skip validation
        if not value:
            return True
        if field in ["ID", "Zip Code", "Phone Number"]:
            return value.isdigit()  # must be numbers
        elif field in ["Name", "City", "State", "Country"]:
            return bool(re.match(r"^[A-Za-z\s'-]+$", value))  # Letters + spaces only
        return True  # fallback for any other field

    def validate_entries(self, values):
        """
        Validate all entry values.
        Returns (is_valid, invalid_field_name) tuple.
        """
        # Check required fields
        for field in self.required_fields:
            if not values[field]:
                return False, field
        # Validate all fields
        for field, value in values.items():
            if not self.validate_field(field, value):
                return False, field
        return True, None

    # ----------------------------------------------------------
    # Create, Search, Update, Delete
    def create_client(self):
        """Create a new client record after validating required fields"""
        missing = []
        for field in self.required_fields:
            if not self.entries[field].get().strip():
                missing.append(field)
                # highlight required fields if missing
                self.entries[field].config(highlightbackground="red", highlightthickness=1)
            else:
                self.entries[field].config(highlightthickness=0)

        if missing: 
            messagebox.showwarning("Validation", "Please fill all required fields.")
            self.status.config(text="Validation failed: required fields missing.")
            return
        
        # Validate entries
        values = self.get_entry_values()
        is_valid, invalid_field = self.validate_entries(values)
        if not is_valid:
                messagebox.showwarning("Validation Error", f"Invalid or missing value for '{invalid_field}'.")
                self.entries[invalid_field].focus()
                self.status.config(text=f"Validation failed: '{invalid_field}' invalid/missing.")
                return

        # Check if ID is valid
        cid = self.get_client_id()
        if cid is None:
            self.status.config(text="Invalid ID. Client not created.")
            return

        # Check if ID already exists
        if any(r.get("Type") == "Client" and str(r.get("ID")) == str(cid) for r in self.records):
            messagebox.showerror("Error", "Client ID already exists.")
            self.status.config(text="Duplicate ID. Client not created.")
            return

        # Create and save new record
        values["ID"] = cid
        values["Type"] = "Client"
        self.records.append(values)
        save_records(self.records)
        self.populate_treeview()
        self.clear_form()
        self.status.config(text="✔ Client added successfully.")
        messagebox.showinfo("Success", "✔ Client record added successfully.")

    # -----------------------------
    def search_client(self):
        """Search client by ID and optionally verify other fields"""
        cid = self.get_client_id()
        if cid is None:
            return

        values = self.get_entry_values()

        # Find record with this ID
        record = next(
            (r for r in self.records if r.get("Type") == "Client" and str(r.get("ID")) == str(cid)), None)
        if not record:
            messagebox.showinfo("Search", "Client not found.")
            self.status.config(text="✖ Client not found.")
            return

        # If other fields are filled, check if they match
        mismatch = False
        for field, value in values.items():
            if field == "ID":
                continue
            if value:  # only check fields the user entered
                if str(record.get(field, "")).lower() != value.lower():
                    mismatch = True
                    break

        if mismatch:
            messagebox.showwarning(
                "Search",
                "Client ID exists but some entered information does not match."
           )
            self.status.config(text="✖ ID found but information mismatch.")
            return

        # If everything matches OR ID only search → show record
        for field in self.fields:
            self.entries[field].delete(0, tk.END)
            self.entries[field].insert(0, record.get(field, ""))

        # Highlight in table
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if str(values[0]) == str(cid):
                self.tree.selection_set(item)
                self.tree.focus(item)
                self.tree.see(item)
                break

        self.status.config(text=f"✔ Client '{record['Name']}' found.")
        messagebox.showinfo("Search Result", f"✔ Client '{record['Name']}' found.")

    # -----------------------------
    def update_client(self):
        """Update an existing client record"""
        cid = self.get_client_id()
        if cid is None:
            return
        
        # Find record
        record = next(
        (r for r in self.records if r.get("Type") == "Client" and str(r.get("ID")) == str(cid)), None)
        if not record:
            messagebox.showinfo("Update", "Client not found.")
            return

        # Save old ID for cascading update
        old_id = record["ID"]

        # Get values
        values = self.get_entry_values()

        # Validate
        is_valid, invalid_field = self.validate_entries(values)
        if not is_valid:
            messagebox.showwarning("Validation Error", f"Invalid or missing value for '{invalid_field}'.")
            self.entries[invalid_field].focus()
            self.status.config(text=f"Validation failed: '{invalid_field}' invalid/missing.")
            return

        # Update client record
        for field in self.fields:
            record[field] = values[field]

        new_id = record["ID"]

        # Cascading update for flights
        if old_id != new_id:
            for r in self.records:
                if r.get("Type") == "Flight" and r.get("Client_ID") == old_id:
                    r["Client_ID"] = new_id

        save_records(self.records)
        self.populate_treeview()
        self.clear_form()
        self.status.config(text="✔ Client record updated successfully.")
        messagebox.showinfo("Success", "✔ Client record updated successfully.")

    # -----------------------------
    def delete_client(self):
        """Delete a client record after confirmation"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Delete", "Select a client first")
            return

        item = selected[0]
        values = self.tree.item(item, "values")
        client_id = str(values[0]) # Treat as string to match JSONL

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete Client {client_id} and ALL their flights?"
        )
        if not confirm:
            return

        # Remove client and related flights
        self.records = [
            r for r in self.records
            if not ((r.get("Type") == "Client" and str(r.get("ID")) == client_id) or
                    (r.get("Type") == "Flight" and str(r.get("Client_ID")) == client_id))
        ]
        save_records(self.records)
        self.populate_treeview()
        self.tree.selection_remove(self.tree.selection())  # clear selection
        self.status.config(text=f"✔ Client {client_id} and related flights deleted.")
        messagebox.showinfo("Deleted", "Client and associated flights removed.")

    # ----------------------------------------------------------
    # Treeview Event
    def on_tree_select(self, event):
        """Populate form when a client is selected in the Treeview"""
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        cid = values[0]
        for r in self.records:
             if r.get("Type") == "Client" and str(r.get("ID")) == str(cid):
                for field in self.fields:
                    self.entries[field].delete(0, tk.END)
                    self.entries[field].insert(0, r.get(field, ""))
                self.status.config(text="Client loaded from table.")
                break
    
    # ----------------------------------------------------------
    # Close event
    def on_close(self):
        """Save all records and update main window status before closing"""
        save_records(self.records)
        self.destroy()

    