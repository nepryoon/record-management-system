import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Link to the storage logic
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from storage import load_records, save_records

class AirlineWindow(tk.Toplevel):
    """
    Airline Management Window
    Handles Airline Company records (ID and Company Name).
    Includes Create, Search, Update, Delete functionality
    """
    def __init__(self, master=None):
        super().__init__(master)
        
        # ----------------------------------------------------------
        # Window configuration
        self.title("Airline Management System")
        self.geometry("1000x700")
        self.resizable(False, False) # Fixed size
        self.configure(bg="#f4f6f7") # Light background for readability

        # Focus Management
        self.transient(master)
        self.grab_set()
        self.focus()

        # ----------------------------------------------------------
        # Load records
        self.records = load_records() or []
        print("DEBUG: Loaded client records:", self.records) 

        # ----------------------------------------------------------
        # Style Setup
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.map("Treeview", background=[("selected", "#3498db")])
        self.style.configure("Treeview", font=("Arial", 12))
        self.style.configure("Treeview.Heading", font=("Arial", 13, "bold"))

        # ----------------------------------------------------------
        # Load Airline Icon
        assets = os.path.join(os.path.dirname(__file__), "assets")
        try:
            self.airline_icon = tk.PhotoImage(
                file=os.path.join(assets, "airline.png")
            ).subsample(3,4)  # reduces size (128 -> 32)
        except:
            self.airline_icon = None
        
        # ----------------------------------------------------------
        # Build GUI
        self.create_widgets()
        self.populate_treeview()

        # ----------------------------------------------------------
        # Event bindings
        self.protocol("WM_DELETE_WINDOW", self.on_close) # Save records when window closes
        self.bind("<Return>", lambda e: self.create_airline()) # Enter to create airline
        self.id_entry.focus_set() # Set focus to ID entry initially
       
    # ----------------------------------------------------------
    # GUI components
    def create_widgets(self):
        """Create and place all GUI widgets"""

        # Header
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
        # Main container frame
        main = tk.Frame(self, bg="#f4f6f7", padx=20, pady=10)
        main.pack(fill="both", expand=True)

        # ----------------------------------------------------------
        # Form Frame
        form = tk.LabelFrame(
            main,
            text=" Airline Information ",
            bg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=20
        )
        form.pack(fill="x", pady=10)


        # Airline ID
        tk.Label(form, text="Airline ID *", bg="white", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=8)
        self.id_entry = tk.Entry(form, bd=2, relief="solid", font=("Arial", 12))
        self.id_entry.grid(row=0, column=1, sticky="ew", padx=10)

        # Company Name
        tk.Label(form, text="Company Name *", bg="white", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=8)
        self.name_entry = tk.Entry(form, bd=2, relief="solid", font=("Arial", 12))
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=10)
        form.columnconfigure(1, weight=1)

        # Required fields note
        note = tk.Label(
            form,
            text="* Required fields",
            font=("Arial", 10, "italic"),
            fg="#e74c3c",  # red color to indicate importance
            bg="white"
        )
        note.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0,5)) 

        # ----------------------------------------------------------
        # Buttons frame
        btn_frame = tk.Frame(main, bg="#f4f6f7")
        btn_frame.pack(fill="x", pady=12)

        buttons = [
            ("Create", "#27ae60", self.create_airline),
            ("Update", "#2980b9", self.update_airline),
            ("Delete", "#c0392b", self.delete_airline),
            ("Search", "#8e44ad", self.search_airline),
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

        # Treeview columns
        cols = ("ID", "Company Name")
        self.tree = ttk.Treeview(
            table_frame,
            columns=cols,
            show="headings",
            height=12
        )
        # colors rows differently
        self.tree.tag_configure('oddrow', background='white')
        self.tree.tag_configure('evenrow', background='#f2f2f2')

        for col in cols:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, anchor="center", width=250)
        
        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Empty record message
        self.empty_label = tk.Label(
            table_frame,
            text="No airlines registered yet",
            font=("Arial", 15, "italic"),
            bg="white",
            fg="#555555"
        )
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

        # ----------------------------------------------------------
        # Counter Label
        self.counter = tk.Label(
            main,
            text="",
            bg="#f4f6f7",
            font=("Arial",12, "bold")
        )
        self.counter.pack(anchor="e", padx=5)

        # ----------------------------------------------------------
        # Status Bar at bottom
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
    # Logic Methods
    def clear_form(self):
        """Clear the entry fields and deselect any row"""
        self.id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        # remove table selection
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        self.id_entry.focus_set()
        self.status.config(text="✔ Form cleared. Ready")

    def populate_treeview(self):
        """
        Populate the Treeview table with airline records.
        Implements Empty State and updates total counter.
        """
        # Clear the table first
        for item in self.tree.get_children():
            self.tree.delete(item)

        count = 0
        for index, r in enumerate(self.records):
            if r.get("Type") == "Airline":
                tag = "evenrow" if index % 2 == 0 else "oddrow"
                self.tree.insert(
                    "",
                    "end",
                    values=(r.get("ID"), r.get("Company Name")),
                    tags=(tag,)
                )
                count += 1

        # Show or hide the empty label
        if count == 0:
            self.empty_label.lift() # make it visible
        else:
            self.empty_label.lower() # hide it

        # Update counter label
        self.counter.config(text=f"Total Airlines: {count}")

    # ----------------------------------------------------------
    # Create, Search, Update, Delete
    def create_airline(self):
        """Create a new airline record after validating required fields"""
        try:
            aid = int(self.id_entry.get().strip())
        except ValueError:
            messagebox.showwarning("Input Error", "ID must be a number.")
            return

        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Company Name is required.")
            return
        
        # Check duplicate
        for r in self.records:
            if r.get("ID") == aid and r.get("Type") == "Airline":
                messagebox.showerror("Error", "Airline ID already exists.")
                return

        new_airline = {
            "ID": aid,
            "Company Name": name,
            "Type": "Airline"
        }
        self.records.append(new_airline)
        save_records(self.records)
        self.populate_treeview()
        self.clear_form()
        self.status.config(text="✔ Airline created successfully")
        messagebox.showinfo("Success", "✔ Airline added successfully.")

    # -----------------------------
    def search_airline(self):
        """Search airline by ID and optional name"""
        aid = self.id_entry.get().strip()
        name = self.name_entry.get().strip()
        # ID must be provided
        if not aid:
            messagebox.showwarning(
                "Search",
                "Please enter Airline ID to search. Company Name alone is not enough."
            )
            return
        # Search for record with this ID
        record = next((r for r in self.records if str(r.get("ID")) == str(aid) and r.get("Type") == "Airline"), None)
        if not record:
            messagebox.showinfo("Search", f"Airline ID {aid} not found.")
            return
        # ID exists
        if not name:
            # Name not provided, show the record
            self.id_entry.delete(0, tk.END)
            self.id_entry.insert(0, record["ID"])
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, record["Company Name"])
            # Highlight the selected airline in the Treeview after search
            for item in self.tree.get_children():
                values = self.tree.item(item, "values")
                if str(values[0]) == str(record["ID"]):
                    self.tree.selection_set(item)
                    self.tree.focus(item)
                    self.tree.see(item)
                    break
            self.status.config(text=f"✔ Airline '{record['Company Name']}' found")
            messagebox.showinfo("Search Result", f"✔ Airline {aid} found.")
            return
        # Both ID and Name provided: verify match
        if record["Company Name"].lower() == name.lower():
            # Match
            self.id_entry.delete(0, tk.END)
            self.id_entry.insert(0, record["ID"])
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, record["Company Name"])
            # Select in Treeview
            for item in self.tree.get_children():
                values = self.tree.item(item, "values")
                if str(values[0]) == str(record["ID"]):
                    self.tree.selection_set(item)
                    self.tree.focus(item)
                    self.tree.see(item)
                    break
            self.status.config(text=f"✔ Airline '{record['Company Name']}' found")
            messagebox.showinfo("Search Result", f"✔ Airline {aid} found.")
        else:
            # ID exists but Name does not match
            messagebox.showwarning(
                "Search",
                f"Airline ID {aid} exists but Company Name does not match."
            )
            self.status.config(text=f"✖ ID exists but Name mismatch")

    # -----------------------------
    def update_airline(self):
        """Update the company name of an existing airline"""
        aid = self.id_entry.get().strip()
        name = self.name_entry.get().strip()
        if not aid:
            messagebox.showwarning("Update", "Enter Airline ID.")
            return
        if not name:
            messagebox.showwarning("Update", "Enter Company Name.")
            return
        for r in self.records:
            if str(r.get("ID")) == str(aid) and r.get("Type") == "Airline":
                r["Company Name"] = name

                save_records(self.records)
                self.populate_treeview()
                self.clear_form()
                self.status.config(text=f"✔ Airline {aid} updated successfully")
                messagebox.showinfo("Update Successful", f"✔ Airline {aid} updated.")
                return
        messagebox.showinfo("Update", "Airline not found.")

    # -----------------------------
    def delete_airline(self):
        "Delete an airline record after confirmation"
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Delete", "Select an airline first")
            return
        item = selected[0]
        values = self.tree.item(item, "values")
        airline_id = int(values[0])

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete Airline {airline_id} and ALL related flights?"
        )
        if not confirm:
            return

        # Remove airline
        self.records = [
            r for r in self.records
            if not (r.get("Type") == "Airline" and r.get("ID") == airline_id)
        ]

        # Cascading delete flights
        self.records = [
            r for r in self.records
            if not (r.get("Type") == "Flight" and r.get("Airline_ID") == airline_id)
        ]
        save_records(self.records)
        self.populate_treeview()
        self.clear_form()
        self.status.config(text=f"✔ Airline {airline_id} and related flights deleted.")
        messagebox.showinfo("Deleted", "Airline and associated flights removed.")

    # ----------------------------------------------------------
    # Treeview Event
    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            val = self.tree.item(selected[0], "values")
            if val[1] == "No Airlines Registered Yet.": return
            self.id_entry.delete(0, tk.END)
            self.id_entry.insert(0, val[0])
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, val[1])

    # ----------------------------------------------------------
    # Close event
    def on_close(self):
        """Save all records and update main window status before closing"""
        save_records(self.records)
        self.destroy()