"""CRUD operations for Client records."""
from src.exceptions import RecordNotFoundError


def _next_id(records: list[dict]) -> int:
    """Return the next available Client ID."""
    client_ids = [r["ID"] for r in records if r.get("Type") == "Client"]
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
    """Add a new Client record and return it."""
    record = {
        "ID": _next_id(records),
        "Type": "Client",
        "Name": name,
        "Address Line 1": address_line1,
        "Address Line 2": address_line2,
        "Address Line 3": address_line3,
        "City": city,
        "State": state,
        "Zip Code": zip_code,
        "Country": country,
        "Phone Number": phone_number,
    }
    records.append(record)
    return record


def delete_client(records: list[dict], client_id: int) -> None:
    """Remove a Client record by ID and cascade-delete associated Flight records.

    Raises RecordNotFoundError if no Client with the given ID exists.
    """
    found = any(r.get("Type") == "Client" and r.get("ID") == client_id for r in records)
    if not found:
        raise RecordNotFoundError(f"No client record found with ID={client_id}.")
    # Remove the client and all of their associated flight records in one pass.
    records[:] = [
        r for r in records
        if not (
            (r.get("Type") == "Client" and r.get("ID") == client_id)
            or (r.get("Type") == "Flight" and r.get("Client_ID") == client_id)
        )
    ]


def update_client(records: list[dict], client_id: int, **updates) -> None:
    """Update fields of a Client record.

    If the ``"ID"`` key is present in *updates*, the new ID value is cascaded
    to the ``"Client_ID"`` field of all associated Flight records.

    Raises RecordNotFoundError if no Client with the given ID exists.
    """
    for r in records:
        if r.get("Type") == "Client" and r.get("ID") == client_id:
            new_id = updates.get("ID", client_id)
            r.update(updates)
            # Cascade: propagate the new ID to linked flight records.
            if new_id != client_id:
                for flight in records:
                    if flight.get("Type") == "Flight" and flight.get("Client_ID") == client_id:
                        flight["Client_ID"] = new_id
            return
    raise RecordNotFoundError(f"No client record found with ID={client_id}.")


def search_clients(records: list[dict], **kwargs) -> list[dict]:
    """Return all Client records matching the supplied key-value pairs."""
    results = [r for r in records if r.get("Type") == "Client"]
    for key, value in kwargs.items():
        results = [r for r in results if r.get(key) == value]
    return results
