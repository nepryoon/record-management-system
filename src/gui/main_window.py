import tkinter as tk
from tkinter import messagebox
import sys
import os

# Adjusting paths for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from .client_window import ClientWindow
from .airline_window import AirlineWindow
from .flight_window import FlightWindow



def open_main_window():
    """Initializes the primary dashboard for the Travel Management System."""
    root = tk.Tk()
    root.title("Travel Record Management System")
    root.geometry("1000x850") # Fixed window size 
    root.resizable(False, False) # Prevent resizing to maintain layout
    root.configure(bg="#f4f6f7") 

    # ----------------------------------------------------------
    # Header Frame
    header_frame = tk.Frame(root, bg="#2c3e50", pady=40)
    header_frame.pack(fill="x") # Stretch across width

    # Application Title
    tk.Label(
        header_frame,
        text="TRAVEL RECORD MANAGEMENT SYSTEM",
        font=("Arial", 28, "bold"),
        fg="white",
        bg="#2c3e50"
    ).pack(pady=(20, 5))

    # Dashboard Subtitle
    tk.Label(
        header_frame,
        text="Select a module to manage system records",
        font=("Arial", 14),
        fg="#d6eaf8",
        bg="#2c3e50"
    ).pack()
   
    # ----------------------------------------------------------
    # Footer
    footer_frame = tk.Frame(root, bg="#ecf0f1", height=50)
    footer_frame.pack(side="bottom", fill="x")
 
    # Status Label
    status = tk.Label(
        footer_frame,
        text="Status: System Ready", # Initial status
        bd=1,
        relief="sunken",
        anchor="w",
        font=("Arial",12)
    )
    status.pack(side="left", padx=10, fill="x", expand=True)

    def update_status(msg):
        """Update status label with real-time feedback"""
        status.config(text=f"Status: {msg}")
        root.update_idletasks() 

    def confirm_exit():
        """Confirm before closing the main window"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            root.destroy()

    # ----------------------------------------------------------
    # Load icons
    assets_path = os.path.join(os.path.dirname(__file__), 'assets')
    try:
        client_icon = tk.PhotoImage(file=os.path.join(assets_path, 'client.png'))
        airline_icon = tk.PhotoImage(file=os.path.join(assets_path, 'airline.png'))
        flight_icon = tk.PhotoImage(file=os.path.join(assets_path, 'flight.png'))
    except Exception as e:
        print(f"Icon error: {e}")
        client_icon = airline_icon = flight_icon = None # fallback if icons missing

    # ----------------------------------------------------------
    # Action Buttons Frame
    actions_frame = tk.Frame(root, bg="#f4f6f7", pady=60)
    actions_frame.pack(expand=True)
    actions_frame.grid_columnconfigure(0, weight=1)
    actions_frame.grid_columnconfigure(1, weight=1)

    # ----------------------------------------------------------
    # Hover effect functions
    def on_enter(e):
        e.widget.config(bg="#465d75", relief="solid", bd=4)

    def on_leave(e):
        e.widget.config(bg="#34495e", relief="raised", bd=3)

    # ----------------------------------------------------------
    # Common Button Style
    btn_style = {
        "font": ("Arial", 16, "bold"),
        "fg": "white",
        "bg":"#34495e",
        "relief": "raised",
        "bd": 3,
        "compound":"top",  # Icon above text
        "padx":20,
        "pady":20,
        "cursor": "hand2"
    }

    # ----------------------------------------------------------
    # Module commands
    def open_clients():
        update_status("Opening Clients Module...")
        client_window = ClientWindow(root)
        def on_client_close():
            update_status("Ready")
            client_window.destroy()
        client_window.protocol("WM_DELETE_WINDOW", on_client_close)

    def open_airlines():
        update_status("Opening Airlines Module...")
        airline_window = AirlineWindow(root)
        def on_airline_close():
            update_status("Ready")
            airline_window.destroy()
        airline_window.protocol("WM_DELETE_WINDOW", on_airline_close)

    def open_flights():
        update_status("Opening Flights Module...")
        flight_window = FlightWindow(root)
        def on_flight_close():
            update_status("Ready")
            flight_window.destroy()
        flight_window.protocol("WM_DELETE_WINDOW", on_flight_close)

    def show_help():
        messagebox.showinfo(
            "Help",
            "Select a module to manage records.\n\n"
            "Clients - Manage customer records\n"
            "Airlines - Manage airline companies\n"
            "Flights - Manage flight information" 
        )
    
    # ----------------------------------------------------------
    # Clients Button
    client_btn = tk.Button(
        actions_frame,
        text="Manage Clients",
        command=open_clients,
        **btn_style
    )
    if client_icon:
        client_btn.config(image=client_icon)
        client_btn.image = client_icon
    client_btn.grid(row=0, column=0, padx=30, pady=15, sticky="ew")
    client_btn.bind("<Enter>", on_enter); client_btn.bind("<Leave>", on_leave)

    # Airlines Button
    airline_btn = tk.Button(
        actions_frame,
        text="Manage Airlines",
        command=open_airlines,
        **btn_style
        )
    if airline_icon:
        airline_btn.config(image=airline_icon)
        airline_btn.image = airline_icon
    airline_btn.grid(row=0, column=1, padx=30, pady=15, sticky="ew")
    airline_btn.bind("<Enter>", on_enter); airline_btn.bind("<Leave>", on_leave)

    # Flights Button
    flight_btn = tk.Button(
        actions_frame,
        text="Manage Flights",
        command=open_flights,
        **btn_style
        )
    if flight_icon:
        flight_btn.config(image=flight_icon)
        flight_btn.image = flight_icon
    flight_btn.grid(row=1, column=0, columnspan=2, padx=50, pady=25, sticky="ew")
    flight_btn.bind("<Enter>", on_enter)
    flight_btn.bind("<Leave>", on_leave)

    # ---------------------------------------------------------- 
    # Footer buttons
    help_btn = tk.Button(
        footer_frame,
        text="Help",
        width=14,
        bg="#7f8c8d",
        fg="white",
        font=("Arial", 11, "bold"),
        command=show_help
        )
    help_btn.pack(side="right", padx=10, pady=8)

    exit_btn = tk.Button(
        footer_frame,
        text="Exit",
        width=14,
        bg="#e74c3c",
        fg="white",
        font=("Arial", 11, "bold"),
        command=confirm_exit
        )
    exit_btn.pack(side="right", padx=10, pady=8)

    # Run the main loop
    root.mainloop()

if __name__ == "__main__":
    open_main_window()
