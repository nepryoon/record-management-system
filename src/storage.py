import json
import os

# Default path to the record file
DATA_FILE = os.path.join(os.path.dirname(__file__), "record", "record.jsonl")


def load_records(filepath: str = DATA_FILE) -> list[dict]:
    """
    Load all records from a JSONL file.
    Returns a list of dictionaries.
    If file doesn't exist, returns empty list.
    """
    if not os.path.exists(filepath):
        print(f"System Message: {filepath} not found. Starting with empty database")
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
        print(f"Error loading records:{e}")
        return []  # Return empty list if file is empty or corrupted


def save_records(records: list[dict], filepath: str = DATA_FILE) -> None:
    """
    Save records to JSONL file (one JSON object per line).
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            for record in records:
                file.write(json.dumps(record) + "\n")
        print(f"System Message: Records successfully saved to {filepath}.")
    except IOError as e:
        print(f"Error saving records: {e}")