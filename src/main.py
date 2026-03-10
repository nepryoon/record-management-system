import atexit

from src.storage import load_records, save_records
from src.repository import RecordRepository

DATA_FILE = "data/records.jsonl"

_repo: RecordRepository | None = None


def get_repository() -> RecordRepository:
    """Return the global repository instance, initialising it on first call."""
    global _repo
    if _repo is None:
        records = load_records(DATA_FILE)
        _repo = RecordRepository(records)
        atexit.register(_shutdown)
    return _repo


def _shutdown() -> None:
    """Persist all records to disk when the application exits."""
    if _repo is not None:
        save_records(_repo.records, DATA_FILE)
