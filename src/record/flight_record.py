"""CRUD operations for Flight records."""
from src.exceptions import RecordNotFoundError


def create_flight(
    records: list[dict],
    client_id: int,
    airline_id: int,
    date: str,
    start_city: str,
    end_city: str,
) -> dict:
    """Add a new Flight record and return it.

    ``date`` must be an ISO-8601 datetime string, e.g. ``"2025-03-14T10:30:00"``.
    """
    record = {
        "Type": "Flight",
        "Client_ID": client_id,
        "Airline_ID": airline_id,
        "Date": date,
        "Start City": start_city,
        "End City": end_city,
    }
    records.append(record)
    return record


def delete_flight(
    records: list[dict], client_id: int, airline_id: int, date: str
) -> None:
    """Remove a Flight record identified by composite key (Client_ID, Airline_ID, Date).

    Raises RecordNotFoundError if no matching record is found.
    """
    for i, r in enumerate(records):
        if (
            r.get("Type") == "Flight"
            and r.get("Client_ID") == client_id
            and r.get("Airline_ID") == airline_id
            and r.get("Date") == date
        ):
            records.pop(i)
            return
    raise RecordNotFoundError(
        f"No flight record found for Client_ID={client_id}, "
        f"Airline_ID={airline_id}, Date={date}."
    )


def update_flight(
    records: list[dict], client_id: int, airline_id: int, date: str, **updates
) -> None:
    """Update fields of a Flight record identified by composite key.

    Raises RecordNotFoundError if no matching record is found.
    """
    for r in records:
        if (
            r.get("Type") == "Flight"
            and r.get("Client_ID") == client_id
            and r.get("Airline_ID") == airline_id
            and r.get("Date") == date
        ):
            r.update(updates)
            return
    raise RecordNotFoundError(
        f"No flight record found for Client_ID={client_id}, "
        f"Airline_ID={airline_id}, Date={date}."
    )


def search_flights(records: list[dict], **kwargs) -> list[dict]:
    """Return all Flight records matching the supplied key-value pairs."""
    results = [r for r in records if r.get("Type") == "Flight"]
    for key, value in kwargs.items():
        results = [r for r in results if r.get(key) == value]
    return results
