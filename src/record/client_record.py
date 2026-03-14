"""CRUD operations for Client records."""
from src.exceptions import RecordNotFoundError


def _next_id(records: list[dict]) -> int:
    """Return the next available client id."""
    client_ids = [r["id"] for r in records if r.get("type") == "client"]
    return max(client_ids) + 1 if client_ids else 1


def create_client(
    records: list[dict],
    name: str,
    address_line1: str,
    address_line2: str,
    address_line3: str,
    city: str,
    state: str,
    zip_code: str,
    country: str,
    phone_number: str,
) -> dict:
    """Add a new client record and return it."""
    record = {
        "id": _next_id(records),
        "type": "client",
        "name": name,
        "address_line1": address_line1,
        "address_line2": address_line2,
        "address_line3": address_line3,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "country": country,
        "phone_number": phone_number,
    }
    records.append(record)
    return record


def delete_client(records: list[dict], client_id: int) -> None:
    """Remove a client record by id. Raises RecordNotFoundError if missing."""
    for i, r in enumerate(records):
        if r.get("type") == "client" and r.get("id") == client_id:
            records.pop(i)
            return
    raise RecordNotFoundError(f"No client record found with id={client_id}.")


def update_client(records: list[dict], client_id: int, **updates) -> None:
    """Update fields of a client record. Raises RecordNotFoundError if missing."""
    for r in records:
        if r.get("type") == "client" and r.get("id") == client_id:
            r.update(updates)
            return
    raise RecordNotFoundError(f"No client record found with id={client_id}.")


def search_clients(records: list[dict], **kwargs) -> list[dict]:
    """Return all client records matching the supplied key-value pairs."""
    results = [r for r in records if r.get("type") == "client"]
    for key, value in kwargs.items():
        results = [r for r in results if r.get(key) == value]
    return results
