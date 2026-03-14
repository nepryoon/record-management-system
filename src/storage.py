import json
import os

# Default path to the JSONL record file — stored in the project-level data/ directory.
DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "records.jsonl"
)


def load_records(filepath: str = DATA_FILE) -> list[dict]:
    """Load all records from a JSONL file and return them as a list of dicts.

    If the file does not exist, an empty list is returned so that the
    application can start without pre-existing data.
    """
    if not os.path.exists(filepath):
        print(f"System Message: {filepath} not found. Starting with empty database.")
        return []
    records = []
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading records: {e}")
        return []  # Return empty list if the file is empty or corrupted.


def save_records(records: list[dict], filepath: str = DATA_FILE) -> None:
    """Persist records to a JSONL file (one JSON object per line)."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            for record in records:
                file.write(json.dumps(record) + "\n")
        print(f"System Message: Records successfully saved to {filepath}.")
    except IOError as e:
        print(f"Error saving records: {e}")