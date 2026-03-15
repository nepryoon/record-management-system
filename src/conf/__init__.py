"""
Configuration sub-package for the Record Management System.

Re-exports the FILE_PATH constant from the settings module so that
other packages can import it directly from ``src.conf``.
"""

from .settings import FILE_PATH

__all__ = ["FILE_PATH"]
