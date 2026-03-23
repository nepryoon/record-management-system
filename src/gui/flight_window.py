"""
Flight record management window for the Travel Record Management System.

Implements ``FlightWindow``, a modal ``tk.Toplevel`` that provides a
full CRUD interface (Create, Search, Update, Delete) for Flight records
stored in the shared JSONL data file.  Flight records are identified by
the composite key ``(Client_ID, Airline_ID, Date)`` rather than a
surrogate primary key.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from src.exceptions import DuplicateRecordError, RecordNotFoundError
from src.record.flight_record import (
    create_flight as _create_flight,
    delete_flight as _delete_flight,
    update_flight as _update_flight,
)
from src.repository import RecordRepository


# ---------------------------------------------------------------------------
# Date formatting helpers
# ---------------------------------------------------------------------------

def _fmt_date(raw: str) -> str:
    """Convert a stored ISO-8601 date string to the display format YYYY-MM-DD HH:MM.

    Handles the variants that may be present in the JSONL file:
    ``2026-02-22T13:33:00``, ``2026-02-22T13:33``,
    ``2026-02-22 13:33:00``, ``2026-02-22 13:33``.
    Falls back to the raw value if none of the patterns match.
    """
    for fmt in (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
    ):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d %H:%M")
        except ValueError:
            continue
    return raw  # fallback: return the raw string unchanged


def _display_to_iso(display: str) -> str:
    """Convert a display-format date string (``YYYY-MM-DD HH:MM``) to ISO-8601.

    Returns the original string unchanged if parsing fails, so that values
    already stored in ISO-8601 format pass through without error.
    """
    try:
        return datetime.strptime(display, "%Y-%m-%d %H:%M").isoformat()
    except ValueError:
        return display  # already ISO or unparseable — pass through


class FlightWindow(tk.Toplevel):
    """
    Flight Record Management Window.

    Handles Flight records containing Client ID, Airline ID, Date,
    Start City, and End City. Provides a full CRUD interface:
    Create, Search, Update, and Delete.
    """

    def __init__(self, master: tk.Misc | None = None) -> None:
        super().__init__(master)

        # ----------------------------------------------------------
        # Window title and background colour
        # ----------------------------------------------------------
        self.title("Flight Record System")
        self.configure(bg="#f4f6f7")

        # ----------------------------------------------------------
        # HiDPI / scaling-aware window sizing
        # ----------------------------------------------------------
        BASE_SCALING = 96.0 / 72.0
        actual_scaling = float(self.tk.call("tk", "scaling"))
        ratio = actual_scaling / BASE_SCALING

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
        # Flight icon — graceful fallback if asset is missing
        # ----------------------------------------------------------
        assets = os.path.join(os.path.dirname(__file__), "assets")
        try:
            self.flight_icon = tk.PhotoImage(
                file=os.path.join(assets, "flight.png")
            ).subsample(3, 4)
        except Exception:
            self.flight_icon = None

        # ----------------------------------------------------------
        # Build GUI and populate the Treeview
        # ----------------------------------------------------------
        self.create_widgets()
        self.populate_treeview()

        # ----------------------------------------------------------
        # Event bindings
        # ----------------------------------------------------------
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Return>", lambda e: self.create_flight())
        self.entries["Client ID *"].focus_set()

    # ----------------------------------------------------------
    # GUI construction
    # ----------------------------------------------------------

    def create_widgets(self) -> None:
        """Create and lay out all GUI widgets within the window."""

        header = tk.Frame(self, bg="#2c3e50", pady=15)
        header.pack(fill="x")
        tk.Label(
            header,
            text="FLIGHT RECORD MANAGEMENT",
            font=("Arial", 18, "bold"),
            image=self.flight_icon,
            compound="left",
            fg="white",
            bg="#2c3e50",
        ).pack()

        main = tk.Frame(self, bg="#f4f6f7", padx=20, pady=10)
        main.pack(fill="both", expand=True)

        form = tk.LabelFrame(
            main,
            text="Flight Information",
            font=("Arial", 11, "bold"),
            bg="white",
            padx=20,
            pady=20,
        )
        form.pack(fill="x", pady=10)

        labels = [
            "Client ID *",
            "Airline ID *",
            "Date (YYYY-MM-DD HH:MM) *",
            "Start City *",
            "End City *",
        ]
        self.entries = {}

        for i, text in enumerate(labels):
            tk.Label(form, text=text, bg="white", font=("Arial", 12)).grid(
                row=i, column=0, sticky="w", pady=10
            )
            entry = tk.Entry(form, font=("Arial", 12), bd=2, relief="solid")
            entry.grid(row=i, column=1, padx=10, sticky="ew")
            self.entries[text] = entry

        form.columnconfigure(1, weight=1)

        tk.Label(
            form,
            text="* Required fields",
            font=("Arial", 11, "italic"),
            fg="#e74c3c",
            bg="white",
        ).grid(row=len(labels), column=0, columnspan=2, sticky="w", pady=(0, 5))

        # ----------------------------------------------------------
        # CRUD action buttons
        # ----------------------------------------------------------
        btn_frame = tk.Frame(main, bg="#f4f6f7")
        btn_frame.pack(fill="x", pady=12)

        buttons = [
            ("Create", "#1a7a40", self.create_flight),
            ("Update", "#2980b9", self.update_flight),
            ("Delete", "#c0392b", self.delete_flight),
            ("Search", "#8e44ad", self.search_flight),
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
        # Treeview with scrollbars
        # ----------------------------------------------------------
        table_frame = tk.Frame(main, bg="white")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("CLIENT ID", "AIRLINE ID", "DATE", "START CITY", "END CITY")
        col_widths = {
            "CLIENT ID": 100, "AIRLINE ID": 100, "DATE": 200,
            "START CITY": 180, "END CITY": 180,
        }

        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=12
        )

        self.tree.tag_configure("oddrow",  background="white")
        self.tree.tag_configure("evenrow", background="#f2f2f2")

        for col in columns:
            self._col_headings[col] = col
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_column(c))
            self.tree.column(
                col, anchor="center", width=col_widths[col], minwidth=col_widths[col]
            )

        xscroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=xscroll.set)
        xscroll.pack(side="bottom", fill="x")

        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        yscroll.pack(side="right", fill="y")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.empty_label = tk.Label(
            table_frame,
            text="No flights registered yet",
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
        NUMERIC_COLUMNS = {"CLIENT ID", "AIRLINE ID"}

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
        """Clear and repopulate the Treeview with all flight records.

        Dates stored in ISO-8601 format are converted to the human-readable
        ``YYYY-MM-DD HH:MM`` format for display via :func:`_fmt_date`.
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
                        _fmt_date(r.get("Date", "")),  # human-readable display
                        r.get("Start City"),
                        r.get("End City"),
                    ),
                    tags=(tag,),
                )
                count += 1

        if count == 0:
            self.empty_label.lift()
        else:
            self.empty_label.lower()

        self.counter.config(text=f"Total Flights: {count}")

    # ----------------------------------------------------------
    # Input helpers
    # ----------------------------------------------------------

    def clear_form(self) -> None:
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

    def create_flight(self) -> None:
        """Validate the form and create a new flight record.

        The Date field is parsed from ``YYYY-MM-DD HH:MM`` and stored as
        ISO-8601 (``2025-06-15T10:30:00``) for consistent deserialisation.
        """
        # Reload and re-sync self.records to avoid stale-reference bugs
        self.repo.load()
        self.records = self.repo.records

        client_id  = self.entries["Client ID *"].get().strip()
        airline_id = self.entries["Airline ID *"].get().strip()
        date       = self.entries["Date (YYYY-MM-DD HH:MM) *"].get().strip()
        start      = self.entries["Start City *"].get().strip()
        end        = self.entries["End City *"].get().strip()

        if not all([client_id, airline_id, date, start, end]):
            self.lift(); self.focus_force()
            messagebox.showwarning("Validation", "All fields must be filled.", parent=self)
            return

        # Validate integer IDs before any other processing
        try:
            client_id_int  = int(client_id)
            airline_id_int = int(airline_id)
        except ValueError:
            self.lift(); self.focus_force()
            messagebox.showerror(
                "Input Error",
                "Client ID and Airline ID must be integer numbers.",
                parent=self,
            )
            return

        # Parse and convert the date to ISO-8601 for storage
        try:
            date_iso = datetime.strptime(date, "%Y-%m-%d %H:%M").isoformat()
        except ValueError:
            self.lift(); self.focus_force()
            messagebox.showwarning("Date Error", "Use format: YYYY-MM-DD HH:MM", parent=self)
            return

        try:
            _create_flight(
                self.records,
                client_id=client_id_int,
                airline_id=airline_id_int,
                date=date_iso,
                start_city=start,
                end_city=end,
            )
            self.repo.save()
        except RecordNotFoundError as exc:
            self.lift(); self.focus_force()
            messagebox.showerror("Referential Integrity Error", str(exc), parent=self)
            return
        except DuplicateRecordError as exc:
            self.lift(); self.focus_force()
            messagebox.showerror("Duplicate Record", str(exc), parent=self)
            return
        except (ValueError, TypeError) as exc:
            self.lift(); self.focus_force()
            messagebox.showerror("Input Error", str(exc), parent=self)
            return

        self.populate_treeview()
        self.clear_form()
        self.status.config(text="✔ Flight created successfully.")
        self.lift(); self.focus_force()
        messagebox.showinfo("Success", "✔ Flight record added successfully.", parent=self)

    def search_flight(self) -> None:
        """Search for all flights belonging to a given Client ID and highlight them."""
        cid = self.entries["Client ID *"].get().strip()
        found = False

        for r in self.records:
            if r.get("Type") == "Flight" and str(r.get("Client_ID")) == cid:
                found = True
                # The DATE column stores the display-formatted string
                display_date = _fmt_date(r.get("Date", ""))
                for item in self.tree.get_children():
                    vals = self.tree.item(item, "values")
                    if (
                        str(vals[0]) == str(r.get("Client_ID"))
                        and str(vals[1]) == str(r.get("Airline_ID"))
                        and str(vals[2]) == display_date
                    ):
                        self.tree.selection_set(item)
                        self.tree.focus(item)
                        self.tree.see(item)
                        break

        if found:
            self.status.config(text=f"✔ Flights for Client ID {cid} found.")
            self.lift(); self.focus_force()
            messagebox.showinfo(
                "Search Result", f"✔ Flight for Client ID {cid} found.", parent=self
            )
        else:
            self.lift(); self.focus_force()
            messagebox.showinfo("Search", "✖ Flight not found.", parent=self)

    def update_flight(self) -> None:
        """Update the selected flight record with values from the form.

        The DATE column in the Treeview stores the display format
        ``YYYY-MM-DD HH:MM``; this is converted back to ISO-8601 before
        being passed to the Record layer for the composite-key lookup.
        """
        selected = self.tree.selection()
        if not selected:
            self.lift(); self.focus_force()
            messagebox.showwarning("Update", "Select a flight first.", parent=self)
            return

        values = self.tree.item(selected[0], "values")
        orig_client_id  = int(values[0])
        orig_airline_id = int(values[1])

        # Convert the display-format date back to ISO-8601 for the lookup
        orig_date = _display_to_iso(str(values[2]))

        # Validate new integer IDs from the form
        try:
            new_client_id_int  = int(self.entries["Client ID *"].get().strip())
            new_airline_id_int = int(self.entries["Airline ID *"].get().strip())
        except ValueError:
            self.lift(); self.focus_force()
            messagebox.showerror(
                "Input Error",
                "Client ID and Airline ID must be integer numbers.",
                parent=self,
            )
            return

        # Parse and convert the new date to ISO-8601
        new_date_str = self.entries["Date (YYYY-MM-DD HH:MM) *"].get().strip()
        try:
            new_date_iso = datetime.strptime(new_date_str, "%Y-%m-%d %H:%M").isoformat()
        except ValueError:
            self.lift(); self.focus_force()
            messagebox.showwarning("Date Error", "Use format: YYYY-MM-DD HH:MM", parent=self)
            return

        updates = {
            "Client_ID":  new_client_id_int,
            "Airline_ID": new_airline_id_int,
            "Date":       new_date_iso,
            "Start City": self.entries["Start City *"].get().strip(),
            "End City":   self.entries["End City *"].get().strip(),
        }
        try:
            _update_flight(
                self.records,
                client_id=orig_client_id,
                airline_id=orig_airline_id,
                date=orig_date,
                **updates,
            )
            self.repo.save()
        except RecordNotFoundError as exc:
            self.lift(); self.focus_force()
            messagebox.showerror("Not Found", str(exc), parent=self)
            return
        except (ValueError, TypeError) as exc:
            self.lift(); self.focus_force()
            messagebox.showerror("Input Error", str(exc), parent=self)
            return

        self.populate_treeview()
        self.status.config(text="✔ Flight record updated successfully.")
        self.lift(); self.focus_force()
        messagebox.showinfo("Success", "✔ Flight record updated successfully.", parent=self)

    def delete_flight(self) -> None:
        """Delete the selected flight after confirmation.

        The DATE column stores the display format; it is converted back to
        ISO-8601 before being passed to the Record layer.
        """
        selected = self.tree.selection()
        if not selected:
            self.lift(); self.focus_force()
            messagebox.showwarning("Delete", "Select a flight first.", parent=self)
            return

        self.lift(); self.focus_force()
        if not messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete the selected flight?",
            parent=self,
        ):
            return

        values = self.tree.item(selected[0], "values")

        # Convert display-format date back to ISO-8601 for the composite-key lookup
        stored_date = _display_to_iso(str(values[2]))

        try:
            _delete_flight(
                self.records,
                client_id=int(values[0]),
                airline_id=int(values[1]),
                date=stored_date,
            )
            self.repo.save()
        except RecordNotFoundError as exc:
            self.lift(); self.focus_force()
            messagebox.showerror("Not Found", str(exc), parent=self)
            return
        except (ValueError, TypeError) as exc:
            self.lift(); self.focus_force()
            messagebox.showerror("Input Error", str(exc), parent=self)
            return

        self.populate_treeview()
        self.clear_form()
        self.status.config(text="✔ Flight deleted successfully.")
        self.lift(); self.focus_force()
        messagebox.showinfo(
            "Delete Successful", "✔ Flight was deleted successfully.", parent=self
        )

    # ----------------------------------------------------------
    # Treeview selection event
    # ----------------------------------------------------------

    def on_tree_select(self, event: tk.Event) -> None:
        """Populate the form fields when the user selects a Treeview row.

        The DATE value in the Treeview is already in ``YYYY-MM-DD HH:MM``
        display format, so it can be inserted into the entry widget directly.
        """
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        keys = list(self.entries.keys())
        for i, key in enumerate(keys):
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, values[i])

    # ----------------------------------------------------------
    # Window close event
    # ----------------------------------------------------------

    def on_close(self) -> None:
        """Persist all records to the JSONL file before destroying the window."""
        self.repo.save()
        self.grab_release()
        self.destroy()
