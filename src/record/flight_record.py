"""
CRUD operations for Flight records

All functions operate directly on the shared ``records`` list (a list
of plain dictionaries), mutating it in place so that changes are
reflected immediately across the application without an additional
persistence round-trip.

Flight records have no surrogate ID; they are identified by a composite
key of (Client_ID, Airline_ID, Date).
"""

from src.exceptions import DuplicateRecordError, RecordNotFoundError
from src.models import FlightRecord


def create_flight(
    records: list[dict],
    client_id: int,
    airline_id: int,
    date: str,
    start_city: str,
    end_city: str,
) -> dict:
    """Add a new Flight record and return it.

    Raises RecordNotFoundError when Client or Airline records are
    present in *records* but none matches the supplied *client_id* or
    *airline_id* respectively, preventing orphaned Flight records.

    Parameters:
        records:    The shared list of all record dictionaries.
        client_id:  ID of the client who booked the flight.
        airline_id: ID of the operating airline.
        date:       ISO-8601 datetime string, e.g.
                    ``"2025-03-14T10:30:00"``.
        start_city: Departure city name.
        end_city:   Destination city name.

    Returns:
        The newly created Flight record dictionary.

    Raises:
        RecordNotFoundError: When Client records exist but none has the
                             given *client_id*, or when Airline records
                             exist but none has the given *airline_id*.
    """
    # Guard: raise if Client records exist but none matches client_id
    if any(r.get("Type") == "Client" for r in records) and not any(
        r.get("Type") == "Client" and r.get("ID") == client_id
        for r in records
    ):
        raise RecordNotFoundError(
            f"No client record found with ID={client_id}."
        )

    # Guard: raise if Airline records exist but none matches airline_id
    if any(r.get("Type") == "Airline" for r in records) and not any(
        r.get("Type") == "Airline" and r.get("ID") == airline_id
        for r in records
    ):
        raise RecordNotFoundError(
            f"No airline record found with ID={airline_id}."
        )

    # Guard: composite key (Client_ID, Airline_ID, Date) must be unique
    if any(
        r.get("Type") == "Flight"
        and r.get("Client_ID") == client_id
        and r.get("Airline_ID") == airline_id
        and r.get("Date") == date
        for r in records
    ):
        raise DuplicateRecordError(
            f"A Flight record already exists for Client_ID={client_id}, "
            f"Airline_ID={airline_id}, Date={date}."
        )

    flight = FlightRecord(
        client_id=client_id,
        airline_id=airline_id,
        date=date,
        start_city=start_city,
        end_city=end_city,
    )
    record = flight.to_dict()
    records.append(record)
    return record


def delete_flight(
    records: list[dict],
    client_id: int,
    airline_id: int,
    date: str,
) -> None:
    """Remove a Flight record identified by composite key.

    The composite key is ``(Client_ID, Airline_ID, Date)``.

    Parameters:
        records:    The shared list of all record dictionaries.
        client_id:  Client_ID component of the composite key.
        airline_id: Airline_ID component of the composite key.
        date:       Date component of the composite key.

    Raises:
        RecordNotFoundError: When no matching Flight record is found.
    """
    # Search for the first matching flight and remove it
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
    records: list[dict],
    client_id: int,
    airline_id: int,
    date: str,
    **updates,
) -> None:
    """Update fields of a Flight record identified by composite key.

    Parameters:
        records:    The shared list of all record dictionaries.
        client_id:  Client_ID component of the composite key.
        airline_id: Airline_ID component of the composite key.
        date:       Date component of the composite key.
        **updates:  Keyword arguments specifying fields to overwrite.

    Raises:
        RecordNotFoundError: When no matching Flight record is found.
    """
    # Locate and update the matching flight record
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
    """Return all Flight records matching the supplied key-value pairs.

    Starts from the full set of Flight records and applies each
    filter criterion in turn.

    Parameters:
        records:  The shared list of all record dictionaries.
        **kwargs: Arbitrary field-name / value filter pairs.

    Returns:
        A list of matching Flight record dictionaries (may be empty).
    """
    results = [r for r in records if r.get("Type") == "Flight"]
    # Apply each additional filter in sequence
    for key, value in kwargs.items():
        results = [r for r in results if r.get(key) == value]
    return results
