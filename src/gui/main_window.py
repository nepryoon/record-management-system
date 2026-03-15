"""
Dashboard window for the Travel Record Management System.

Provides ``open_main_window()``, which builds and runs the primary
tkinter dashboard from which the Client, Airline, and Flight
record-management modules are launched.
"""

import os
import tkinter as tk
from tkinter import messagebox
from tkinter.font import Font

from .client_window import ClientWindow
from .airline_window import AirlineWindow
from .flight_window import FlightWindow


def open_main_window() -> None:
    """
    Initialises the primary dashboard for the Travel Record Management System.

    This function builds and launches the main tkinter window, which serves
    as the entry point for navigating to the three record management modules:
    Clients, Airlines, and Flights.
    """

    # ----------------------------------------------------------
    # Root window initialisation
    # ----------------------------------------------------------
    root = tk.Tk()
    root.title("Travel Record Management System")
    root.configure(bg="#f4f6f7")  # Light grey background for the main canvas

    # ----------------------------------------------------------
    # Physical screen metrics — used for window centring only.
    # No HiDPI scaling is applied to the window size; dimensions
    # are derived from content and a physical millimetre unit instead.
    # ----------------------------------------------------------
    phys_w = root.winfo_screenwidth()
    phys_h = root.winfo_screenheight()

    # Estimate the number of monitors from the virtual desktop aspect ratio
    # (e.g. 5760 x 1080 ≈ 5760/1080 ≈ 5, clamped to at least 1)
    monitors = max(1, round(phys_w / phys_h))
    mon_w = phys_w // monitors  # Approximate width of a single monitor in pixels

    # ----------------------------------------------------------
    # Universal spacing unit: 5 mm converted to pixels.
    # winfo_fpixels('1m') returns the number of screen pixels in
    # 1 mm for this display, accounting for display DPI automatically.
    # All gaps — between buttons, between buttons and window borders,
    # and inside buttons on either side of their labels — use this
    # single value so spacing is perceptually identical on every screen.
    # ----------------------------------------------------------
    SP = round(root.winfo_fpixels('1m') * 5)

    # ----------------------------------------------------------
    # Header frame
    # Displays the application title and subtitle at the top of the window
    # ----------------------------------------------------------
    header_frame = tk.Frame(root, bg="#2c3e50")
    header_frame.pack(fill="x")

    title_label = tk.Label(
        header_frame,
        text="TRAVEL RECORD MANAGEMENT SYSTEM",
        font=("Arial", 13, "bold"),   # Reduced from 16 to 13 for tighter fit
        fg="white",
        bg="#2c3e50",
        wraplength=0,   # wraplength=0 disables wrapping; window width is fixed to content size
        justify="center"
    )
    title_label.pack(pady=(12, 4), fill="x", expand=True)

    tk.Label(
        header_frame,
        text="Select a module to manage system records",
        font=("Arial", 11),
        fg="#d6eaf8",     # Light blue to contrast against the dark header
        bg="#2c3e50"
    ).pack(pady=(0, 12))

    # ----------------------------------------------------------
    # Footer frame
    # Contains a status bar on the left and action buttons on the right
    # ----------------------------------------------------------
    footer_frame = tk.Frame(root, bg="#ecf0f1", height=50)
    footer_frame.pack(side="bottom", fill="x")

    # Status label — updated dynamically to reflect the current application state
    status = tk.Label(
        footer_frame,
        text="Status: System Ready",
        bd=1,
        relief="sunken",
        anchor="w",
        font=("Arial", 11)
    )
    status.pack(side="left", padx=10, fill="x", expand=True)

    def update_status(msg: str) -> None:  # PEP 8 fix: add type annotations
        """Update the footer status label with a real-time message."""
        status.config(text=f"Status: {msg}")
        root.update_idletasks()  # Flush pending UI events immediately

    def confirm_exit() -> None:  # PEP 8 fix: add type annotations
        """
        Prompt the user for confirmation before closing the application.
        Brings the window to the foreground first to ensure the dialogue
        is visible above other applications.
        """
        root.lift()
        root.focus_force()
        if messagebox.askyesno("Exit", "Are you sure you want to exit?", parent=root):
            root.destroy()

    # ----------------------------------------------------------
    # Icon loading
    # Attempts to load PNG icons from the assets subfolder.
    # Falls back to text-only buttons if the files are not found.
    # ----------------------------------------------------------
    assets_path = os.path.join(os.path.dirname(__file__), 'assets')
    try:
        # PEP 8 fix: remove extra alignment spaces before `=`
        client_icon = tk.PhotoImage(file=os.path.join(assets_path, 'client.png'))
        airline_icon = tk.PhotoImage(file=os.path.join(assets_path, 'airline.png'))
        flight_icon = tk.PhotoImage(file=os.path.join(assets_path, 'flight.png'))
    except Exception as e:
        print(f"Icon loading error: {e}")
        client_icon = airline_icon = flight_icon = None  # Graceful degradation

    # ----------------------------------------------------------
    # Module navigation buttons frame
    # Uses a 2-column grid so that Clients and Airlines sit side by side,
    # whilst Flights spans the full width on the second row.
    # ----------------------------------------------------------
    actions_frame = tk.Frame(root, bg="#f4f6f7")
    # No frame-level padding — all spacing is handled precisely in the
    # grid padx/pady below so that every gap equals exactly SP (5 mm).
    actions_frame.pack(expand=False, fill="x")

    # Both columns expand equally when the window is resized
    actions_frame.grid_columnconfigure(0, weight=1)
    actions_frame.grid_columnconfigure(1, weight=1)

    # Rows use natural (content-driven) height; no expansion needed
    # because the window size is fixed to match the content exactly.
    actions_frame.grid_rowconfigure(0, weight=0)
    actions_frame.grid_rowconfigure(1, weight=0)

    # ----------------------------------------------------------
    # Button hover effect callbacks
    # ----------------------------------------------------------
    def on_enter(e: tk.Event) -> None:  # PEP 8 fix: add type annotations
        """Highlight the button when the mouse cursor moves over it."""
        e.widget.config(bg="#465d75", relief="solid", bd=4)

    def on_leave(e: tk.Event) -> None:  # PEP 8 fix: add type annotations
        """Restore the default button style when the cursor leaves."""
        e.widget.config(bg="#34495e", relief="raised", bd=3)

    # ----------------------------------------------------------
    # Shared button style dictionary
    # Applied to all three module buttons for visual consistency.
    # Font and padding are scaled down to suit the 600x600 window.
    # ----------------------------------------------------------
    # PEP 8 fix: remove extra alignment spaces in dict literal
    btn_style = {
        "font": ("Arial", 13, "bold"),
        "fg": "white",
        "bg": "#34495e",   # Dark blue-grey background
        "relief": "raised",
        "bd": 3,
        "compound": "top",       # Icon rendered above the button label
        "padx": SP,   # 5 mm internal horizontal padding (text to button border)
        "pady": SP,   # 5 mm internal vertical padding (label to button border)
        "cursor": "hand2"      # Pointer cursor to indicate interactivity
    }

    # ----------------------------------------------------------
    # Module window opener functions
    # Each function opens the corresponding Toplevel window and
    # registers a close handler to reset the status bar on exit.
    # ----------------------------------------------------------

    def open_clients() -> None:  # PEP 8 fix: add type annotations
        """Open the Client Record Management window."""
        update_status("Opening Clients Module...")
        client_window = ClientWindow(root)

        def on_close() -> None:  # PEP 8 fix: add type annotations
            # Call the window's own on_close() to save records before destroying,
            # satisfying the spec's requirement to save on application close.
            update_status("System Ready")
            client_window.on_close()

        client_window.protocol("WM_DELETE_WINDOW", on_close)

    def open_airlines() -> None:  # PEP 8 fix: add type annotations
        """Open the Airline Record Management window."""
        update_status("Opening Airlines Module...")
        airline_window = AirlineWindow(root)

        def on_close() -> None:  # PEP 8 fix: add type annotations
            # Call the window's own on_close() to save records before destroying,
            # satisfying the spec's requirement to save on application close.
            update_status("System Ready")
            airline_window.on_close()

        airline_window.protocol("WM_DELETE_WINDOW", on_close)

    def open_flights() -> None:  # PEP 8 fix: add type annotations
        """Open the Flight Record Management window."""
        update_status("Opening Flights Module...")
        flight_window = FlightWindow(root)

        def on_close() -> None:  # PEP 8 fix: add type annotations
            # Call the window's own on_close() to save records before destroying,
            # satisfying the spec's requirement to save on application close.
            update_status("System Ready")
            flight_window.on_close()

        flight_window.protocol("WM_DELETE_WINDOW", on_close)

    def show_help() -> None:  # PEP 8 fix: add type annotations
        """Display a brief help dialogue describing each module."""
        root.lift()
        root.focus_force()
        messagebox.showinfo(
            "Help",
            "Select a module to manage records.\n\n"
            "Clients  - Manage customer records\n"
            "Airlines - Manage airline companies\n"
            "Flights  - Manage flight information",
            parent=root
        )

    # ----------------------------------------------------------
    # Clients button — row 0, column 0
    # ----------------------------------------------------------
    client_btn = tk.Button(
        actions_frame, text="Manage Clients",
        command=open_clients, **btn_style
    )
    if client_icon:
        client_btn.config(image=client_icon)
        client_btn.image = client_icon  # Retain reference to prevent garbage collection
    # Left outer gap = SP, right inner gap = SP//2 (combined with airline's
    # left inner gap of SP//2, total gap between the two buttons = SP = 5 mm).
    # Top outer gap = SP, bottom inner gap = SP//2 (combined with flight's
    # top inner gap of SP//2, total gap between the two rows = SP = 5 mm).
    client_btn.grid(
        row=0, column=0,
        padx=(SP, SP // 2),
        pady=(SP, SP // 2),
        sticky="nsew",
    )
    client_btn.bind("<Enter>", on_enter)
    client_btn.bind("<Leave>", on_leave)

    # ----------------------------------------------------------
    # Airlines button — row 0, column 1
    # ----------------------------------------------------------
    airline_btn = tk.Button(
        actions_frame, text="Manage Airlines",
        command=open_airlines, **btn_style
    )
    if airline_icon:
        airline_btn.config(image=airline_icon)
        airline_btn.image = airline_icon
    # Left inner gap = SP//2 (see Clients comment above for the combined gap).
    # Right outer gap = SP. Vertical padding mirrors the Clients button.
    airline_btn.grid(
        row=0, column=1,
        padx=(SP // 2, SP),
        pady=(SP, SP // 2),
        sticky="nsew",
    )
    airline_btn.bind("<Enter>", on_enter)
    airline_btn.bind("<Leave>", on_leave)

    # ----------------------------------------------------------
    # Flights button — row 1, spans both columns
    # ----------------------------------------------------------
    flight_btn = tk.Button(
        actions_frame, text="Manage Flights",
        command=open_flights, **btn_style
    )
    if flight_icon:
        flight_btn.config(image=flight_icon)
        flight_btn.image = flight_icon
    # Horizontal outer gaps = SP on both sides.
    # Top inner gap = SP//2 (combined with the row above = SP = 5 mm).
    # Bottom outer gap = SP (gap to footer).
    flight_btn.grid(
        row=1, column=0, columnspan=2,
        padx=SP,
        pady=(SP // 2, SP),
        sticky="nsew",
    )
    flight_btn.bind("<Enter>", on_enter)
    flight_btn.bind("<Leave>", on_leave)

    # ----------------------------------------------------------
    # Footer action buttons
    # Packed right-to-left: Help appears outermost, Exit next to it
    # ----------------------------------------------------------
    help_btn = tk.Button(
        footer_frame, text="Help", width=12,
        bg="#5d6d7e", fg="white",  # WCAG AA fix: contrast 5.31:1 with white (was 3.48:1)
        font=("Arial", 10, "bold"),
        command=show_help
    )
    help_btn.pack(side="right", padx=8, pady=6)

    exit_btn = tk.Button(
        footer_frame, text="Exit", width=12,
        bg="#a93226", fg="white",   # WCAG AA fix: contrast 6.62:1 with white (was 3.82:1)
        font=("Arial", 10, "bold"),
        command=confirm_exit
    )
    exit_btn.pack(side="right", padx=8, pady=6)

    # ----------------------------------------------------------
    # Fixed window size and centring
    #
    # All widgets have now been packed with SP-based spacing.
    # update_idletasks() forces tkinter to calculate the geometry of every
    # widget so that winfo_reqwidth() and winfo_reqheight() return the exact
    # pixel dimensions needed to display all content without clipping.
    # These become the fixed, non-resizable window dimensions.
    # ----------------------------------------------------------
    root.update_idletasks()
    WIN_W = root.winfo_reqwidth()
    # Constrain the title label to the usable header width so that the text
    # always leaves SP (5 mm) of clear space on both the left and right sides.
    title_label.config(wraplength=WIN_W - 2 * SP)
    WIN_H = root.winfo_reqheight()

    # Lock the window to its natural content size; prevent any resizing
    root.resizable(False, False)

    # Centre the window on the monitor where the mouse pointer currently
    # resides, using the monitor geometry estimated earlier.
    ptr_x = root.winfo_pointerx()
    mon_index = min(ptr_x // mon_w, monitors - 1)  # Zero-based monitor index
    mon_origin_x = mon_index * mon_w               # Left edge of the active monitor
    x = mon_origin_x + (mon_w - WIN_W) // 2        # Horizontal centre of that monitor
    y = (phys_h - WIN_H) // 2                      # Vertical centre of the screen
    root.geometry(f"{WIN_W}x{WIN_H}+{x}+{y}")

    # ----------------------------------------------------------
    # Start the tkinter event loop
    # Blocks here until the root window is destroyed
    # ----------------------------------------------------------
    root.mainloop()


if __name__ == "__main__":
    open_main_window()
