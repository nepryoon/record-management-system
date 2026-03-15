"""
CRUD operations for Client records.

All functions operate directly on the shared ``records`` list (a list
of plain dictionaries), mutating it in place so that changes are
reflected immediately across the application without an additional
persistence round-trip.
"""

from src.exceptions import RecordNotFoundError


def _next_id(records: list[dict]) -> int:
    """Return the next available Client ID.

    Scans all Client records and returns one more than the current
    maximum ID. Returns ``1`` when no Client records exist yet.

    Parameters:
        records: The shared list of all record dictionaries.

    Returns:
        A positive integer suitable for use as the next Client ID.
    """
    client_ids = [
        r["ID"] for r in records if r.get("Type") == "Client"
    ]
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
    """Add a new Client record and return it.

    Automatically assigns the next available ID before appending the
    record to the shared list.

    Parameters:
        records:       The shared list of all record dictionaries.
        name:          Full name of the client.
        address_line1: First line of the postal address.
        address_line2: Second line of the postal address.
        address_line3: Third line of the postal address.
        city:          City of residence.
        state:         State or county.
        zip_code:      Postal or ZIP code.
        country:       Country of residence.
        phone_number:  Contact telephone number.

    Returns:
        The newly created Client record dictionary.
    """
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
    """Remove a Client record and cascade-delete associated Flights.

    Raises RecordNotFoundError if no Client with the given ID exists.

    Parameters:
        records:   The shared list of all record dictionaries.
        client_id: Numeric ID of the client to remove.

    Raises:
        RecordNotFoundError: When no Client record with ``client_id``
                             is found.
    """
    # Verify the client exists before attempting deletion
    found = any(
        r.get("Type") == "Client" and r.get("ID") == client_id
        for r in records
    )
    if not found:
        raise RecordNotFoundError(
            f"No client record found with ID={client_id}."
        )

    # Remove the client and all of their associated flight records
    # in a single list comprehension pass
    records[:] = [
        r for r in records
        if not (
            (r.get("Type") == "Client" and r.get("ID") == client_id)
            or (
                r.get("Type") == "Flight"
                and r.get("Client_ID") == client_id
            )
        )
    ]


def update_client(
    records: list[dict],
    client_id: int,
    **updates,
) -> None:
    """Update fields of a Client record.

    If the ``"ID"`` key is present in *updates*, the new ID value is
    cascaded to the ``"Client_ID"`` field of all associated Flight
    records.

    Parameters:
        records:   The shared list of all record dictionaries.
        client_id: Numeric ID of the client to update.
        **updates: Keyword arguments specifying fields to overwrite.

    Raises:
        RecordNotFoundError: When no Client record with ``client_id``
                             is found.
    """
    for r in records:
        if r.get("Type") == "Client" and r.get("ID") == client_id:
            new_id = updates.get("ID", client_id)
            r.update(updates)
            # Cascade: propagate the new ID to linked flight records
            if new_id != client_id:
                for flight in records:
                    if (
                        flight.get("Type") == "Flight"
                        and flight.get("Client_ID") == client_id
                    ):
                        flight["Client_ID"] = new_id
            return
    raise RecordNotFoundError(
        f"No client record found with ID={client_id}."
    )


def search_clients(records: list[dict], **kwargs) -> list[dict]:
    """Return all Client records matching the supplied key-value pairs.

    Starts from the full set of Client records and applies each
    filter criterion in turn.

    Parameters:
        records:  The shared list of all record dictionaries.
        **kwargs: Arbitrary field-name / value filter pairs.

    Returns:
        A list of matching Client record dictionaries (may be empty).
    """
    results = [r for r in records if r.get("Type") == "Client"]
    # Apply each additional filter in sequence
    for key, value in kwargs.items():
        results = [r for r in results if r.get(key) == value]
    return results
