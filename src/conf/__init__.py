"""
Configuration sub-package for the Record Management System.

Re-exports path constants from the settings module so that other
packages can import them directly from ``src.conf``.
"""

from .settings import DATA_FILE, FILE_PATH

__all__ = ["DATA_FILE", "FILE_PATH"]
