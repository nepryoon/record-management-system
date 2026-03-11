import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime

# connect storage module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from storage import load_records, save_records


class FlightWindow(tk.Toplevel):
    """
    Flight Management Window
    Handles Flight records (Client_ID, Airline_ID, Date, Start City, End City).
    Includes Create, Search, Update, Delete functionality
    """

    def __init__(self, master=None):
        super().__init__(master)

        # ----------------------------------------------------------
        # Window configuration
        self.title("Flight Record System")
        self.geometry("1000x700")
        self.configure(bg="#f4f6f7")
        self.resizable(False, False) # Fixed size

        # Focus Management
        self.transient(master)
        self.grab_set()
        self.focus()

        # ----------------------------------------------------------
        # load records
        self.records = load_records() or []

        # ----------------------------------------------------------
        # Style Setup
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.map("Treeview", background=[("selected", "#3498db")])
        self.style.configure("Treeview", font=("Arial", 12))
        self.style.configure("Treeview.Heading", font=("Arial", 13, "bold"))

        # ----------------------------------------------------------
        # Load Flight Icon
        assets = os.path.join(os.path.dirname(__file__), "assets")
        try:
            self.flight_icon = tk.PhotoImage(
                file=os.path.join(assets, "flight.png")
            ).subsample(3,4)  # reduces size (128 -> 32)
        except:
            self.flight_icon = None
        
        # ----------------------------------------------------------
        # Build the GUI
        self.create_widgets()
        self.populate_treeview()
        
        # ----------------------------------------------------------
        # Event bindings
        self.protocol("WM_DELETE_WINDOW", self.on_close) # Save records when window closes
        self.bind("<Return>", lambda e: self.create_flight()) # Enter to create airline
        self.entries["Client ID *"].focus_set() # Set focus to ID entry initially

    # -----------------------------
    # GUI
    def create_widgets(self):
        """Create and place all GUI widgets"""

        # Header
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
        # Main container frame
        main = tk.Frame(self, bg="#f4f6f7", padx=20, pady=10)
        main.pack(fill="both", expand=True)

        # ----------------------------------------------------------
        # Form Frame
        form = tk.LabelFrame(
            main,
            text="Flight Information",
            font=("Arial", 11, "bold"),
            bg="white",
            padx=20,
            pady=20
        )
        form.pack(fill="x", pady=10)

        # ----------------------------------------------------------
        # List of fields to display in the form
        labels = [
            "Client ID *",
            "Airline ID *",
            "Date (YYYY-MM-DD HH:MM) *",
            "Start City *",
            "End City *"
        ]
        self.entries = {}

        for i, text in enumerate(labels):
            tk.Label(
                form,
                text=text,
                bg="white",
                font=("Arial", 12)
            ).grid(row=i, column=0, sticky="w", pady=10)
            entry = tk.Entry(
                form,
                font=("Arial", 12),
                bd=2,
                relief="solid"
            )
            entry.grid(row=i, column=1, padx=10, sticky="ew")
            self.entries[text] = entry
        form.columnconfigure(1, weight=1)

        # ----------------------------------------------------------
        # Required fields note
        note = tk.Label(
            form,
            text="* Required fields",
            font=("Arial", 11, "italic"),
            fg="#e74c3c",  # red color to indicate importance
            bg="white"
        )
        note.grid(row=len(labels), column=0, columnspan=2, sticky="w", pady=(0,5)) 

        # ----------------------------------------------------------
        # Buttons frame
        btn_frame = tk.Frame(main, bg="#f4f6f7")
        btn_frame.pack(fill="x", pady=12)

        # Define buttons with colours and linked commands
        buttons = [
            ("Create", "#27ae60", self.create_flight),
            ("Update", "#2980b9", self.update_flight),
            ("Delete", "#c0392b", self.delete_flight),
            ("Search", "#8e44ad", self.search_flight),
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
        # Treeview Tabl
        table_frame = tk.Frame(main, bg="white")
        table_frame.pack(fill="both", expand=True, pady=12)

        columns = ("Client ID", "Airline ID", "Date", "Start City", "End City")
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
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=190)

        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind table selection
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Empty record message
        self.empty_label = tk.Label(
            table_frame,
            text="No flights registered yet",
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

    # -----------------------------
    # Table treeview
    def populate_treeview(self):
        """
        Populate the Treeview table with flight records.
        Implements Empty State and updates total counter.
        """
        # clear the table first
        for item in self.tree.get_children():
            self.tree.delete(item)

        count = 0
        for index, r in enumerate(self.records):
            if r.get("Type") == "Flight":
                tag = "evenrow" if index % 2 == 0 else "oddrow"
                self.tree.insert(
                    "",
                    "end",
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

        # Show or hide the empty label
        if count == 0:
            self.empty_label.lift() # make it visible
        else:
            self.empty_label.lower() # hide it

        # Update counter label
        self.counter.config(text=f"Total Flights: {count}")

    # ----------------------------------------------------------
    # Basic Functions
    def clear_form(self):
        """Clear the entry fields"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        self.entries["Client ID *"].focus_set()
        self.status.config(text="✔ Form cleared. Ready")

    # ----------------------------------------------------------
    # Create, Search, Update, Delete
    def create_flight(self):
        """Create a new flight record after validating required fields"""
        # Reload records from file
        self.records = load_records() or []

        try:
            client_id = self.entries["Client ID *"].get().strip()
            airline_id = self.entries["Airline ID *"].get().strip()
        except ValueError:
            messagebox.showwarning("Input Error", "Client ID and Airline ID must be entered")
            return

        date = self.entries["Date (YYYY-MM-DD HH:MM) *"].get().strip()
        start = self.entries["Start City *"].get().strip()
        end = self.entries["End City *"].get().strip()

        if not all([client_id, airline_id, date, start, end]):
            messagebox.showwarning("Validation", "All fields must be filled")
            return

        # validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showwarning("Date Error", "Use format: YYYY-MM-DD HH:MM")
            return

        # check client exists
        client_exists = any(
            r.get("Type") == "Client" and str(r.get("ID")) == str(client_id)
            for r in self.records
        )
        if not client_exists:
            messagebox.showerror("Error", f"Client ID {client_id} does not exist")
            return

        # check airline exists
        airline_exists = any(
            r.get("Type") == "Airline" and str(r.get("ID")) == str(airline_id)
            for r in self.records
        )
        if not airline_exists:
            messagebox.showerror("Error", f"Airline ID {airline_id} does not exist")
            return

        record = {
            "Client_ID": int(client_id),
            "Airline_ID": int(airline_id),
            "Date": date,
            "Start City": start,
            "End City": end,
            "Type": "Flight"
        }

        self.records.append(record)
        save_records(self.records)
        self.populate_treeview()
        self.clear_form()
        self.status.config(text="✔ Flight created successfully")
        messagebox.showinfo("Success", "✔ Flight record added successfully")

    # -----------------------------
    def search_flight(self):
        """Search flight by Client ID in self.records"""
        cid = self.entries["Client ID *"].get().strip()
        found = False

        # Search all flight records
        for index, r in enumerate(self.records):
            if r.get("Type") == "Flight" and str(r.get("Client_ID")) == cid:
                found = True
                # Find corresponding Treeview item
                for item in self.tree.get_children():
                    values = self.tree.item(item, "values")
                    if (str(values[0]) == str(r.get("Client_ID")) and
                        str(values[1]) == str(r.get("Airline_ID")) and
                        str(values[2]) == str(r.get("Date"))):
                        self.tree.selection_set(item)
                        self.tree.focus(item)
                        self.tree.see(item)
                        break
        if found:
            self.status.config(text=f"✔ Flights for Client ID {cid} found")
            messagebox.showinfo("Search Result", f"✔ Flight for Client ID {cid} found")
        else:
           messagebox.showinfo("Search", "✖ Flight not found")

    # -----------------------------
    def update_flight(self):
        """Update an existing flight record"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Update", "Select a flight first")
            return

        item = selected[0]  # the selected row in the Treeview
        values = self.tree.item(item, "values")

        # Extract original Client ID and Airline ID from selection
        orig_client_id = int(values[0])
        orig_airline_id = int(values[1])

        # Find the corresponding record in self.records
        record_to_update = None
        for r in self.records:
            if r.get("Type") == "Flight" and r.get("Client_ID") == orig_client_id and r.get("Airline_ID") == orig_airline_id:
                record_to_update = r
                break
        if not record_to_update:
            messagebox.showerror("Error", "Could not find the record to update")
            return

        # Update fields from Entry widgets
        record_to_update["Client_ID"] = int(self.entries["Client ID *"].get())
        record_to_update["Airline_ID"] = int(self.entries["Airline ID *"].get())
        record_to_update["Date"] = self.entries["Date (YYYY-MM-DD HH:MM) *"].get()
        record_to_update["Start City"] = self.entries["Start City *"].get()
        record_to_update["End City"] = self.entries["End City *"].get()

        save_records(self.records)
        self.populate_treeview()
        self.status.config(text="✔ Flight record updated successfully.")
        messagebox.showinfo("Success", "✔ Flight record updated successfully.")

    # -----------------------------
    def delete_flight(self):
        """Delete a flight record after confirmation"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Delete", "Select a flight first")
            return
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete selected flight?"
        )
        if not confirm:
            return
        item = selected[0]
        values = self.tree.item(item, "values")

        deleted = False
        for r in self.records:
            if (
                r.get("Type") == "Flight"
                and str(r.get("Client_ID")) == str(values[0])
                and str(r.get("Airline_ID")) == str(values[1])
                and str(r.get("Date")) == str(values[2])
            ):
                self.records.remove(r)
                deleted = True
                break
        if deleted:
            save_records(self.records)
            self.populate_treeview()
            self.clear_form()
            self.status.config(text=f"✔ Flight deleted successfully.")
            messagebox.showinfo("Delete Successful", f"✔ Flight was deleted successfully.")
        else: 
            messagebox.showinfo("Delete", "Flight not found.")

    # ----------------------------------------------------------
    # Treeview Event
    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        keys = list(self.entries.keys())
        for i in range(len(keys)):
            self.entries[keys[i]].delete(0, tk.END)
            self.entries[keys[i]].insert(0, values[i])

    # ----------------------------------------------------------
    # Close event
    def on_close(self):
        """Save all records and update main window status before closing"""
        save_records(self.records)
        self.grab_release()
        self.destroy()