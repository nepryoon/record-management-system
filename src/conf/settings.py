"""
Application-level configuration settings

Defines file path constants used by the storage layer. The JSONL data
file is located in the project-level ``data/`` directory, one level
above the ``src/`` package root.
"""

import os

# Absolute path to the JSONL record file stored in the project-level
# data/ directory.
DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "records.jsonl",
)

# Kept for backwards compatibility.
FILE_PATH = DATA_FILE
