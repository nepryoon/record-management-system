"""
JSONL persistence layer for the Record Management System.

Provides two public functions — ``load_records`` and ``save_records``
— for reading and writing the shared JSONL data file. Each line in
the file represents one record serialised as a JSON object.
"""

import json
import os

from src.conf.settings import DATA_FILE


def load_records(filepath: str = DATA_FILE) -> list[dict]:
    """Load all records from a JSONL file and return them as a list of dicts.

    If the file does not exist, an empty list is returned so that the
    application can start without pre-existing data.

    Parameters:
        filepath: Absolute or relative path to the JSONL file.

    Returns:
        A list of record dictionaries, one per non-blank line.
    """
    # Return early with an empty list when no data file exists yet
    if not os.path.exists(filepath):
        print(
            f"System Message: {filepath} not found. "
            "Starting with empty database."
        )
        return []

    records = []
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            # Parse each non-blank line as a separate JSON object
            for line in file:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading records: {e}")
        # Return empty list if the file is empty or corrupted
        return []


def save_records(
    records: list[dict],
    filepath: str = DATA_FILE,
) -> None:
    """Persist records to a JSONL file (one JSON object per line).

    Creates any missing parent directories before writing. Existing
    file contents are overwritten entirely on each call.

    Parameters:
        records:  List of record dictionaries to serialise.
        filepath: Absolute or relative path to the target JSONL file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            # Write each record as a single JSON line
            for record in records:
                file.write(json.dumps(record) + "\n")
        print(
            f"System Message: Records successfully saved to {filepath}."
        )
    except IOError as e:
        print(f"Error saving records: {e}")
