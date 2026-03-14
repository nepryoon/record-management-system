import os

# Absolute path to the JSONL record file stored in the project-level data/ directory.
FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "records.jsonl",
)
