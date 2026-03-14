import sys
import os
sys.path.append(os.path.dirname(__file__))

from gui.main_window import open_main_window


def main():
    open_main_window()


if __name__ == "__main__":
    main()