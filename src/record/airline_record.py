"""CRUD operations for Airline records."""
from src.exceptions import RecordNotFoundError


def _next_id(records: list[dict]) -> int:
    """Return the next available Airline ID."""
    airline_ids = [r["ID"] for r in records if r.get("Type") == "Airline"]
    return max(airline_ids) + 1 if airline_ids else 1


def create_airline(records: list[dict], company_name: str) -> dict:
    """Add a new Airline record and return it."""
    record = {
        "ID": _next_id(records),
        "Type": "Airline",
        "Company Name": company_name,
    }
    records.append(record)
    return record


def delete_airline(records: list[dict], airline_id: int) -> None:
    """Remove an Airline record by ID and cascade-delete associated Flight records.

    Raises RecordNotFoundError if no Airline with the given ID exists.
    """
    found = any(r.get("Type") == "Airline" and r.get("ID") == airline_id for r in records)
    if not found:
        raise RecordNotFoundError(f"No airline record found with ID={airline_id}.")
    # Remove the airline and all of its associated flight records in one pass.
    records[:] = [
        r for r in records
        if not (
            (r.get("Type") == "Airline" and r.get("ID") == airline_id)
            or (r.get("Type") == "Flight" and r.get("Airline_ID") == airline_id)
        )
    ]


def update_airline(records: list[dict], airline_id: int, **updates) -> None:
    """Update fields of an Airline record. Raises RecordNotFoundError if missing."""
    for r in records:
        if r.get("Type") == "Airline" and r.get("ID") == airline_id:
            r.update(updates)
            return
    raise RecordNotFoundError(f"No airline record found with ID={airline_id}.")


def search_airlines(records: list[dict], **kwargs) -> list[dict]:
    """Return all Airline records matching the supplied key-value pairs."""
    results = [r for r in records if r.get("Type") == "Airline"]
    for key, value in kwargs.items():
        results = [r for r in results if r.get(key) == value]
    return results
