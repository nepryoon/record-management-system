"""
Application entry point for the Travel Record Management System

Running this module launches the main tkinter dashboard window from
which the Client, Airline, and Flight management modules are accessed.
"""

from src.gui.main_window import open_main_window


def main() -> None:
    """Launch the Travel Record Management System dashboard."""
    open_main_window()


if __name__ == "__main__":
    main()
