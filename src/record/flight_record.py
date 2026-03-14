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
    """Add a new flight record and return it.

    ``date`` must be an ISO-8601 datetime string, e.g. ``"2025-03-14T10:30:00"``.
    """
    record = {
        "client_id": client_id,
        "airline_id": airline_id,
        "date": date,
        "start_city": start_city,
        "end_city": end_city,
        "type": "flight",
    }
    records.append(record)
    return record


def delete_flight(
    records: list[dict], client_id: int, airline_id: int, date: str
) -> None:
    """Remove a flight record by composite key (client_id, airline_id, date).

    Raises RecordNotFoundError if no matching record is found.
    """
    for i, r in enumerate(records):
        if (
            r.get("type") == "flight"
            and r.get("client_id") == client_id
            and r.get("airline_id") == airline_id
            and r.get("date") == date
        ):
            records.pop(i)
            return
    raise RecordNotFoundError(
        f"No flight record found for client_id={client_id}, "
        f"airline_id={airline_id}, date={date}."
    )


def update_flight(
    records: list[dict], client_id: int, airline_id: int, date: str, **updates
) -> None:
    """Update fields of a flight record identified by composite key.

    Raises RecordNotFoundError if no matching record is found.
    """
    for r in records:
        if (
            r.get("type") == "flight"
            and r.get("client_id") == client_id
            and r.get("airline_id") == airline_id
            and r.get("date") == date
        ):
            r.update(updates)
            return
    raise RecordNotFoundError(
        f"No flight record found for client_id={client_id}, "
        f"airline_id={airline_id}, date={date}."
    )


def search_flights(records: list[dict], **kwargs) -> list[dict]:
    """Return all flight records matching the supplied key-value pairs."""
    results = [r for r in records if r.get("type") == "flight"]
    for key, value in kwargs.items():
        results = [r for r in results if r.get(key) == value]
    return results
