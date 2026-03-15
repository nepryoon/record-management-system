"""
CRUD operations for Airline records.

All functions operate directly on the shared ``records`` list (a list
of plain dictionaries), mutating it in place so that changes are
reflected immediately across the application without an additional
persistence round-trip.
"""

from src.exceptions import RecordNotFoundError


def _next_id(records: list[dict]) -> int:
    """Return the next available Airline ID.

    Scans all Airline records and returns one more than the current
    maximum ID. Returns ``1`` when no Airline records exist yet.

    Parameters:
        records: The shared list of all record dictionaries.

    Returns:
        A positive integer suitable for use as the next Airline ID.
    """
    airline_ids = [
        r["ID"] for r in records if r.get("Type") == "Airline"
    ]
    return max(airline_ids) + 1 if airline_ids else 1


def create_airline(
    records: list[dict],
    company_name: str,
) -> dict:
    """Add a new Airline record and return it.

    Automatically assigns the next available ID before appending the
    record to the shared list.

    Parameters:
        records:      The shared list of all record dictionaries.
        company_name: Trading name of the airline company.

    Returns:
        The newly created Airline record dictionary.
    """
    record = {
        "ID": _next_id(records),
        "Type": "Airline",
        "Company Name": company_name,
    }
    records.append(record)
    return record


def delete_airline(records: list[dict], airline_id: int) -> None:
    """Remove an Airline record and cascade-delete associated Flights.

    Raises RecordNotFoundError if no Airline with the given ID exists.

    Parameters:
        records:    The shared list of all record dictionaries.
        airline_id: Numeric ID of the airline to remove.

    Raises:
        RecordNotFoundError: When no Airline record with ``airline_id``
                             is found.
    """
    # Verify the airline exists before attempting deletion
    found = any(
        r.get("Type") == "Airline" and r.get("ID") == airline_id
        for r in records
    )
    if not found:
        raise RecordNotFoundError(
            f"No airline record found with ID={airline_id}."
        )

    # Remove the airline and all of its associated flight records
    # in a single list comprehension pass
    records[:] = [
        r for r in records
        if not (
            (r.get("Type") == "Airline" and r.get("ID") == airline_id)
            or (
                r.get("Type") == "Flight"
                and r.get("Airline_ID") == airline_id
            )
        )
    ]


def update_airline(
    records: list[dict],
    airline_id: int,
    **updates,
) -> None:
    """Update fields of an Airline record.

    Applies ``updates`` to the first Airline record whose ID matches
    ``airline_id``.

    Parameters:
        records:    The shared list of all record dictionaries.
        airline_id: Numeric ID of the airline to update.
        **updates:  Keyword arguments specifying fields to overwrite.

    Raises:
        RecordNotFoundError: When no Airline record with ``airline_id``
                             is found.
    """
    # Locate and update the matching airline record
    for r in records:
        if r.get("Type") == "Airline" and r.get("ID") == airline_id:
            r.update(updates)
            return
    raise RecordNotFoundError(
        f"No airline record found with ID={airline_id}."
    )


def search_airlines(records: list[dict], **kwargs) -> list[dict]:
    """Return all Airline records matching the supplied key-value pairs.

    Starts from the full set of Airline records and applies each
    filter criterion in turn.

    Parameters:
        records:  The shared list of all record dictionaries.
        **kwargs: Arbitrary field-name / value filter pairs.

    Returns:
        A list of matching Airline record dictionaries (may be empty).
    """
    results = [r for r in records if r.get("Type") == "Airline"]
    # Apply each additional filter in sequence
    for key, value in kwargs.items():
        results = [r for r in results if r.get(key) == value]
    return results
