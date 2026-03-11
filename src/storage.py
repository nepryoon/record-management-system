import json
import os

# Path to the record file
DATA_FILE = os.path.join(os.path.dirname(__file__), "record", "record.jsonl")


def load_records():
    """
    Load all records from record.jsonl.
    Returns a list of dictionaries. 
    If file doesn't exist, returns empty list.
    """
    if not os.path.exists(DATA_FILE):
        print(f"System Message: {DATA_FILE} not found. Starting with empty database")
        return []
    records = []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            for line in file:
                 line = line.strip()
                 if line:
                      records.append(json.loads(line))
        return records
    except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading records:{e}")
            return []  # Return empty list if file is empty or corrupted


def save_records(records):
    """
    Save records to JSONL file (one JSON object per line)
    """
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    try: 
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            for record in records:
                file.write(json.dumps(record) + "\n")
        print(f"System Message: Records successfully saved to {DATA_FILE}.")
    except IOError as e:
        print(f"Error saving records: {e}")