import tkinter as tk
from tkinter import messagebox
import sys
import os

# Adjust the Python path to allow imports from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from .client_window import ClientWindow
from .airline_window import AirlineWindow
from .flight_window import FlightWindow


def open_main_window():
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
    # HiDPI / scaling-aware window sizing
    #
    # tkinter reports dimensions in logical pixels, but on HiDPI displays
    # (e.g. Retina, Wayland fractional scaling) the system applies a scaling
    # factor that makes the window appear smaller than intended.
    #
    # Strategy:
    #   1. Read the current tkinter scaling value.
    #   2. Divide by the standard baseline (96 DPI / 72 pt = 1.333) to obtain
    #      the effective HiDPI ratio (e.g. 2.667 / 1.333 ≈ 2.0 on a 2x display).
    #   3. Multiply the target pixel dimensions by that ratio so that the
    #      compositor scales the window back down to the intended visual size.
    #   4. Estimate the number of connected monitors by dividing the total
    #      virtual screen width by the screen height (assumes landscape monitors
    #      of roughly equal size).
    #   5. Centre the window on whichever monitor the mouse cursor resides on.
    # ----------------------------------------------------------

    BASE_SCALING = 96.0 / 72.0  # Standard tkinter baseline scaling factor
    actual_scaling = float(root.tk.call('tk', 'scaling'))  # Current system scaling
    ratio = actual_scaling / BASE_SCALING  # HiDPI multiplier (1.0 on normal displays)

    # Retrieve the total virtual desktop dimensions (spanning all monitors)
    phys_w = root.winfo_screenwidth()
    phys_h = root.winfo_screenheight()

    # Estimate the number of monitors based on the aspect ratio of the
    # virtual desktop (e.g. 6912 / 2160 ≈ 3 monitors side by side)
    monitors = max(1, round(phys_w / phys_h))
    mon_w = phys_w // monitors  # Approximate width of a single monitor in pixels

    # Target visual size in device-independent pixels
    TARGET_W, TARGET_H = 1024, 768

    # Scale up the target dimensions to compensate for HiDPI compositor scaling.
    # Clamp to the monitor bounds to avoid the window exceeding screen edges.
    WIN_W = min(int(TARGET_W * ratio), mon_w - 40)
    WIN_H = min(int(TARGET_H * ratio), phys_h - 80)

    root.resizable(True, True)       # Allow the user to resize the window freely
    root.minsize(WIN_W, WIN_H)       # Prevent the window from becoming too small

    # Force tkinter to calculate widget sizes before reading pointer position
    root.update_idletasks()

    # Determine which monitor the mouse cursor is currently on and centre
    # the window on that monitor rather than on the full virtual desktop
    ptr_x = root.winfo_pointerx()
    mon_index = min(ptr_x // mon_w, monitors - 1)  # Zero-based monitor index
    mon_origin_x = mon_index * mon_w               # Left edge of the active monitor
    x = mon_origin_x + (mon_w - WIN_W) // 2        # Horizontal centre
    y = (phys_h - WIN_H) // 2                      # Vertical centre
    root.geometry(f"{WIN_W}x{WIN_H}+{x}+{y}")

    # ----------------------------------------------------------
    # Header frame
    # Displays the application title and subtitle at the top of the window
    # ----------------------------------------------------------
    header_frame = tk.Frame(root, bg="#2c3e50")
    header_frame.pack(fill="x")

    tk.Label(
        header_frame,
        text="TRAVEL RECORD MANAGEMENT SYSTEM",
        font=("Arial", 20, "bold"),
        fg="white",
        bg="#2c3e50",
        wraplength=960,   # Wrap the title if the window is narrower than 960px
        justify="center"
    ).pack(pady=(16, 4), fill="x", expand=True)

    tk.Label(
        header_frame,
        text="Select a module to manage system records",
        font=("Arial", 12),
        fg="#d6eaf8",     # Light blue to contrast against the dark header
        bg="#2c3e50"
    ).pack(pady=(0, 16))

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

    def update_status(msg):
        """Update the footer status label with a real-time message."""
        status.config(text=f"Status: {msg}")
        root.update_idletasks()  # Flush pending UI events immediately

    def confirm_exit():
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
        client_icon  = tk.PhotoImage(file=os.path.join(assets_path, 'client.png'))
        airline_icon = tk.PhotoImage(file=os.path.join(assets_path, 'airline.png'))
        flight_icon  = tk.PhotoImage(file=os.path.join(assets_path, 'flight.png'))
    except Exception as e:
        print(f"Icon loading error: {e}")
        client_icon = airline_icon = flight_icon = None  # Graceful degradation

    # ----------------------------------------------------------
    # Module navigation buttons frame
    # Uses a 2-column grid so that Clients and Airlines sit side by side,
    # whilst Flights spans the full width on the second row.
    # ----------------------------------------------------------
    actions_frame = tk.Frame(root, bg="#f4f6f7")
    actions_frame.pack(expand=True, fill="both", padx=20, pady=10)

    # Both columns expand equally when the window is resized
    actions_frame.grid_columnconfigure(0, weight=1)
    actions_frame.grid_columnconfigure(1, weight=1)

    # Both rows expand equally to fill the available vertical space
    actions_frame.grid_rowconfigure(0, weight=1)
    actions_frame.grid_rowconfigure(1, weight=1)

    # ----------------------------------------------------------
    # Button hover effect callbacks
    # ----------------------------------------------------------
    def on_enter(e):
        """Highlight the button when the mouse cursor moves over it."""
        e.widget.config(bg="#465d75", relief="solid", bd=4)

    def on_leave(e):
        """Restore the default button style when the cursor leaves."""
        e.widget.config(bg="#34495e", relief="raised", bd=3)

    # ----------------------------------------------------------
    # Shared button style dictionary
    # Applied to all three module buttons for visual consistency
    # ----------------------------------------------------------
    btn_style = {
        "font"    : ("Arial", 16, "bold"),
        "fg"      : "white",
        "bg"      : "#34495e",   # Dark blue-grey background
        "relief"  : "raised",
        "bd"      : 3,
        "compound": "top",       # Icon rendered above the button label
        "padx"    : 20,
        "pady"    : 16,
        "cursor"  : "hand2"      # Pointer cursor to indicate interactivity
    }

    # ----------------------------------------------------------
    # Module window opener functions
    # Each function opens the corresponding Toplevel window and
    # registers a close handler to reset the status bar on exit.
    # ----------------------------------------------------------

    def open_clients():
        """Open the Client Record Management window."""
        update_status("Opening Clients Module...")
        client_window = ClientWindow(root)

        def on_close():
            update_status("System Ready")
            client_window.destroy()

        client_window.protocol("WM_DELETE_WINDOW", on_close)

    def open_airlines():
        """Open the Airline Record Management window."""
        update_status("Opening Airlines Module...")
        airline_window = AirlineWindow(root)

        def on_close():
            update_status("System Ready")
            airline_window.destroy()

        airline_window.protocol("WM_DELETE_WINDOW", on_close)

    def open_flights():
        """Open the Flight Record Management window."""
        update_status("Opening Flights Module...")
        flight_window = FlightWindow(root)

        def on_close():
            update_status("System Ready")
            flight_window.destroy()

        flight_window.protocol("WM_DELETE_WINDOW", on_close)

    def show_help():
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
    client_btn.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
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
    airline_btn.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")
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
    flight_btn.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
    flight_btn.bind("<Enter>", on_enter)
    flight_btn.bind("<Leave>", on_leave)

    # ----------------------------------------------------------
    # Footer action buttons
    # Packed right-to-left: Help appears outermost, Exit next to it
    # ----------------------------------------------------------
    help_btn = tk.Button(
        footer_frame, text="Help", width=14,
        bg="#7f8c8d", fg="white",
        font=("Arial", 11, "bold"),
        command=show_help
    )
    help_btn.pack(side="right", padx=10, pady=8)

    exit_btn = tk.Button(
        footer_frame, text="Exit", width=14,
        bg="#e74c3c", fg="white",   # Red background to signal a destructive action
        font=("Arial", 11, "bold"),
        command=confirm_exit
    )
    exit_btn.pack(side="right", padx=10, pady=8)

    # ----------------------------------------------------------
    # Start the tkinter event loop
    # Blocks here until the root window is destroyed
    # ----------------------------------------------------------
    root.mainloop()


if __name__ == "__main__":
    open_main_window()
