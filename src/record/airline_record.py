"""CRUD operations for Airline records."""
from src.exceptions import RecordNotFoundError


def _next_id(records: list[dict]) -> int:
    """Return the next available airline id."""
    airline_ids = [r["id"] for r in records if r.get("type") == "airline"]
    return max(airline_ids) + 1 if airline_ids else 1


def create_airline(records: list[dict], company_name: str) -> dict:
    """Add a new airline record and return it."""
    record = {
        "id": _next_id(records),
        "type": "airline",
        "company_name": company_name,
    }
    records.append(record)
    return record


def delete_airline(records: list[dict], airline_id: int) -> None:
    """Remove an airline record by id. Raises RecordNotFoundError if missing."""
    for i, r in enumerate(records):
        if r.get("type") == "airline" and r.get("id") == airline_id:
            records.pop(i)
            return
    raise RecordNotFoundError(f"No airline record found with id={airline_id}.")


def update_airline(records: list[dict], airline_id: int, **updates) -> None:
    """Update fields of an airline record. Raises RecordNotFoundError if missing."""
    for r in records:
        if r.get("type") == "airline" and r.get("id") == airline_id:
            r.update(updates)
            return
    raise RecordNotFoundError(f"No airline record found with id={airline_id}.")


def search_airlines(records: list[dict], **kwargs) -> list[dict]:
    """Return all airline records matching the supplied key-value pairs."""
    results = [r for r in records if r.get("type") == "airline"]
    for key, value in kwargs.items():
        results = [r for r in results if r.get(key) == value]
    return results
