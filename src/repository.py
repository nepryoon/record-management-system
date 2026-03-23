"""
In-memory repository for the Record Management System.

RecordRepository stores all record dictionaries in a plain Python list
and exposes CRUD operations plus a flexible keyword-based search method.
Records are distinguished by their ``"Type"`` and ``"ID"`` fields.
"""

from src.conf.settings import DATA_FILE
from src.exceptions import DuplicateRecordError, RecordNotFoundError
from src.storage import load_records, save_records


class RecordRepository:
    """In-memory repository for Client, Airline, and Flight records.

    Attributes:
        records: Mutable list of record dictionaries held in memory.
    """

    def __init__(self, records: list[dict] | None = None) -> None:
        """Initialise the repository with an optional pre-loaded record list.

        Parameters:
            records: Existing records to seed the repository. Defaults
                     to an empty list when not provided.
        """
        self.records: list[dict] = (
            records if records is not None else []
        )

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _find_index(self, record_id: int, record_type: str) -> int:
        """Return the list index of a record identified by ID and type.

        Iterates through ``self.records`` and returns the index of the
        first entry whose ``"Type"`` and ``"ID"`` fields match the
        supplied arguments.

        Parameters:
            record_id:   The numeric ID of the record to locate.
            record_type: The record type string, e.g. ``"Client"``.

        Returns:
            The zero-based index of the matching record.

        Raises:
            RecordNotFoundError: When no matching record is found.
        """
        # Search for a record matching both type and ID
        for i, r in enumerate(self.records):
            if (
                r.get("Type") == record_type
                and r.get("ID") == record_id
            ):
                return i
        raise RecordNotFoundError(
            f"No {record_type} record found with ID={record_id}."
        )

    # ------------------------------------------------------------------ #
    # CRUD operations                                                    #
    # ------------------------------------------------------------------ #

    def add(self, record: dict) -> None:
        """Add a new record to the repository.

        Checks for an existing record with the same type and ID before
        appending to prevent duplicates.

        Parameters:
            record: Dictionary representing the record to add.

        Raises:
            DuplicateRecordError: When a record with the same type and
                                  ID already exists in the repository.
        """
        record_type = record.get("Type")
        record_id = record.get("ID")

        # Only check for duplicates when the record carries an ID field
        if record_id is not None:
            try:
                self._find_index(record_id, record_type)
                raise DuplicateRecordError(
                    f"A {record_type} record with ID={record_id} "
                    "already exists."
                )
            except RecordNotFoundError:
                pass  # Expected — record does not exist yet

        self.records.append(record)

    def delete(self, record_id: int, record_type: str) -> None:
        """Delete a record by ID and type.

        Parameters:
            record_id:   Numeric ID of the record to remove.
            record_type: Type string of the record to remove.

        Raises:
            RecordNotFoundError: When no matching record exists.
        """
        index = self._find_index(record_id, record_type)
        self.records.pop(index)

    def update(
        self,
        record_id: int,
        record_type: str,
        updates: dict,
    ) -> None:
        """Update specified fields of an existing record.

        Parameters:
            record_id:   Numeric ID of the record to update.
            record_type: Type string of the record to update.
            updates:     Dictionary of field names and their new values.

        Raises:
            RecordNotFoundError: When no matching record exists.
        """
        index = self._find_index(record_id, record_type)
        self.records[index].update(updates)

    def search(self, **kwargs) -> list[dict]:
        """Return all records matching every key-value pair supplied.

        Each keyword argument is treated as a field filter; only records
        whose fields match all supplied criteria are returned.

        Example::

            search(Type="Client", City="London")

        Parameters:
            **kwargs: Arbitrary field-name / value filter pairs.

        Returns:
            A list of matching record dictionaries (may be empty).
        """
        results = self.records
        # Apply each filter criterion in sequence
        for key, value in kwargs.items():
            results = [r for r in results if r.get(key) == value]
        return results

    def get_all(self) -> list[dict]:
        """Return a shallow copy of all records in the repository.

        Returns:
            A new list containing every stored record dictionary.
        """
        return list(self.records)

    # ------------------------------------------------------------------ #
    # Persistence helpers                                                #
    # ------------------------------------------------------------------ #

    def load(self, filepath: str = DATA_FILE) -> None:
        """Load records from the JSONL storage file into the repository.

        Updates ``self.records`` in-place so that any external reference
        to the list (e.g. held by a GUI layer) remains valid after the
        reload.

        Parameters:
            filepath: Path to the JSONL data file. Defaults to the
                      application-wide DATA_FILE constant.
        """
        loaded = load_records(filepath) or []
        self.records.clear()
        self.records.extend(loaded)

    def save(self, filepath: str = DATA_FILE) -> None:
        """Persist all in-memory records to the JSONL storage file.

        Delegates entirely to the Storage layer so that the GUI never
        needs to import or call storage functions directly.

        Parameters:
            filepath: Path to the JSONL data file. Defaults to the
                      application-wide DATA_FILE constant.
        """
        save_records(self.records, filepath)
