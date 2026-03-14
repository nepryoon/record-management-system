from src.exceptions import DuplicateRecordError, RecordNotFoundError


class RecordRepository:
    """In-memory repository for Client, Airline and Flight records."""

    def __init__(self, records: list[dict] | None = None):
        self.records: list[dict] = records if records is not None else []

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _find_index(self, record_id: int, record_type: str) -> int:
        for i, r in enumerate(self.records):
            if r.get("Type") == record_type and r.get("ID") == record_id:
                return i
        raise RecordNotFoundError(
            f"No {record_type} record found with ID={record_id}."
        )

    # ------------------------------------------------------------------ #
    # CRUD operations                                                      #
    # ------------------------------------------------------------------ #

    def add(self, record: dict) -> None:
        """Add a new record. Raises DuplicateRecordError if it already exists."""
        record_type = record.get("Type")
        record_id = record.get("ID")
        if record_id is not None:
            try:
                self._find_index(record_id, record_type)
                raise DuplicateRecordError(
                    f"A {record_type} record with ID={record_id} already exists."
                )
            except RecordNotFoundError:
                pass  # Expected — record does not exist yet.
        self.records.append(record)

    def delete(self, record_id: int, record_type: str) -> None:
        """Delete a record by ID and Type. Raises RecordNotFoundError if missing."""
        index = self._find_index(record_id, record_type)
        self.records.pop(index)

    def update(self, record_id: int, record_type: str, updates: dict) -> None:
        """Update specified fields of a record. Raises RecordNotFoundError if missing."""
        index = self._find_index(record_id, record_type)
        self.records[index].update(updates)

    def search(self, **kwargs) -> list[dict]:
        """Return all records matching every key-value pair supplied.

        Example: ``search(Type="Client", City="London")``
        """
        results = self.records
        for key, value in kwargs.items():
            results = [r for r in results if r.get(key) == value]
        return results

    def get_all(self) -> list[dict]:
        """Return a shallow copy of all records."""
        return list(self.records)
