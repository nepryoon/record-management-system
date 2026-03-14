class RecordNotFoundError(Exception):
    """Raised when a record cannot be found in the repository."""


class DuplicateRecordError(Exception):
    """Raised when attempting to add a record that already exists."""
