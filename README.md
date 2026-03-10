# Record Management System

A backend system for a specialist travel agent, managing Client, Flight and Airline records.
Built as a group project for the MSc in Data Science and Artificial Intelligence at the University of Liverpool.

## Project Structure
```
record-management-system/
├── src/
│   ├── models.py        # ClientRecord, AirlineRecord, FlightRecord dataclasses
│   ├── storage.py       # JSONL load/save functions
│   ├── repository.py    # CRUD operations
│   ├── exceptions.py    # Custom exceptions
│   └── main.py          # Application entry point
├── tests/
│   ├── test_models.py
│   ├── test_storage.py
│   └── test_repository.py
├── data/                # Auto-generated at runtime (gitignored)
├── requirements.txt
└── requirements-dev.txt
```

## Record Types

- **Client**: personal and contact details
- **Airline**: company name
- **Flight**: links a client to an airline with date and route

## Setup
```bash
pip install -r requirements-dev.txt
```

## Running Tests
```bash
python -m pytest tests/ -v
```

## Storage

Records are persisted to `data/records.jsonl` (JSON Lines format) automatically on application exit.

## Usage (for GUI integration)
```python
from src.main import get_repository

repo = get_repository()

repo.add({"type": "client", "id": 1, "name": "Alice", ...})
repo.search(type="client", city="London")
repo.update(1, "client", {"city": "Manchester"})
repo.delete(1, "client")
```

## Contributors

- Backend:
- GUI:
