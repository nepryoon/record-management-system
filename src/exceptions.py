"""
Custom exception classes for the Record Management System

These exceptions are raised by the repository and CRUD layers to signal
application-level errors that callers are expected to handle explicitly.
"""


class RecordNotFoundError(Exception):
    """Raised when a requested record cannot be found in the repository

    Typically raised by ``_find_index`` or CRUD helpers when no record
    matching the supplied ID and type exists in the data store.
    """


class DuplicateRecordError(Exception):
    """Raised when attempting to add a record that already exists

    Typically raised by ``RecordRepository.add`` when a record with
    the same type and ID is already present in the repository.
    """
