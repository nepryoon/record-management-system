# Record Management System

A desktop application for specialist travel agents to manage Client,
Airline, and Flight records. Built with Python and tkinter, it
provides a graphical interface for full CRUD (Create, Read, Update,
Delete) operations, persisting all data in a human-readable JSONL
file. Originally developed as a group project for the MSc in Data
Science and Artificial Intelligence at the University of Liverpool.

---

## Getting Started

### Linux / macOS

```bash
# Clone the repository from GitHub
git clone https://github.com/nepryoon/record-management-system.git

# Change into the project directory
cd record-management-system

# Create an isolated virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install development dependencies (pytest)
pip install -r requirements-dev.txt

# Run the full test suite to verify the installation
python -m pytest tests/ -v

# Launch the graphical application
python -m src.main

# Pull latest changes and reinstall dependencies if updated
git pull && pip install -r requirements-dev.txt
```

### Windows (PowerShell)

```powershell
# Clone the repository from GitHub
git clone https://github.com/nepryoon/record-management-system.git

# Change into the project directory
cd record-management-system

# Create an isolated virtual environment
python -m venv .venv

# Activate the virtual environment
.venv\Scripts\Activate.ps1

# Install development dependencies (pytest)
pip install -r requirements-dev.txt

# Run the full test suite to verify the installation
python -m pytest tests/ -v

# Launch the graphical application
python -m src.main

# Pull latest changes and reinstall dependencies if updated
git pull; pip install -r requirements-dev.txt
```

### Windows (CMD)

```cmd
REM Clone the repository from GitHub
git clone https://github.com/nepryoon/record-management-system.git

REM Change into the project directory
cd record-management-system

REM Create an isolated virtual environment
python -m venv .venv

REM Activate the virtual environment
.venv\Scripts\activate.bat

REM Install development dependencies (pytest)
pip install -r requirements-dev.txt

REM Run the full test suite to verify the installation
python -m pytest tests/ -v

REM Launch the graphical application
python -m src.main

REM Pull latest changes and reinstall dependencies if updated
git pull && pip install -r requirements-dev.txt
```

---

## Technical & Functional Overview

### What the Application Does

The Record Management System is a standalone desktop application
designed for use by travel agency staff. It allows operators to
maintain a registry of clients, airlines, and the flights that link
them. The three core record types are:

- **Client** — personal details (name, address, phone number)
  for each customer of the travel agency.
- **Airline** — a company record containing only the airline's
  unique ID and trading name.
- **Flight** — a booking that associates a client with an airline,
  recording the departure date/time, origin city, and destination
  city. A flight record is always owned by both a client and an
  airline; deleting either causes cascade deletion of all related
  flight records.

The primary target user is a travel agency operator who needs a
simple, keyboard-friendly interface without the overhead of a
full database server. All data is stored locally on disk in JSONL
format, making records easy to inspect and back up manually.

### Technology Stack

| Component        | Technology                                  |
|------------------|---------------------------------------------|
| Language         | Python 3.11+                                |
| GUI framework    | tkinter (stdlib) + ttk themed widgets       |
| Data persistence | JSONL (JSON Lines) flat file                |
| Testing          | pytest ≥ 8.0                                |
| Runtime deps     | None (stdlib only)                          |

### Architecture Overview

The project follows a **layered architecture** combined with the
**Repository pattern**:

```
┌──────────────────────────────────────────────────┐
│                   GUI Layer                       │
│  main_window.py  client_window.py                │
│  airline_window.py  flight_window.py             │
└───────────────────────┬──────────────────────────┘
                        │ calls
┌───────────────────────▼──────────────────────────┐
│               Record Layer (src/record/)          │
│  client_record.py  airline_record.py             │
│  flight_record.py                                │
└───────────────────────┬──────────────────────────┘
                        │ uses
┌───────────────────────▼──────────────────────────┐
│           Storage Layer (src/storage.py)          │
│         load_records() / save_records()           │
└───────────────────────┬──────────────────────────┘
                        │ reads/writes
┌───────────────────────▼──────────────────────────┐
│              data/records.jsonl                   │
└──────────────────────────────────────────────────┘
```

- **GUI Layer** — tkinter `Toplevel` windows handle user interaction.
  Each window loads the full record list on open and saves it on
  close, delegating business logic to the record layer.
- **Record Layer** — pure functions that operate on an in-memory
  `list[dict]`. They implement the CRUD operations for each record
  type, including cascading deletes and ID propagation.
- **Repository Layer** — `RecordRepository` wraps the in-memory list
  and provides a typed, exception-raising CRUD interface. Used
  primarily by the test suite.
- **Storage Layer** — two stateless functions (`load_records` and
  `save_records`) handle reading and writing the JSONL file.
- **Data File** — `data/records.jsonl` stores one JSON object per
  line, one line per record. All three record types coexist in a
  single file, distinguished by a `"Type"` field.

### Data Model

**Client**

| Field           | JSONL key         | Type   |
|-----------------|-------------------|--------|
| Unique ID       | `"ID"`            | int    |
| Type tag        | `"Type"`          | str    |
| Full name       | `"Name"`          | str    |
| Address line 1  | `"Address Line 1"`| str    |
| Address line 2  | `"Address Line 2"`| str    |
| Address line 3  | `"Address Line 3"`| str    |
| City            | `"City"`          | str    |
| State/county    | `"State"`         | str    |
| Postal code     | `"Zip Code"`      | str    |
| Country         | `"Country"`       | str    |
| Phone number    | `"Phone Number"`  | str    |

**Airline**

| Field        | JSONL key        | Type   |
|--------------|------------------|--------|
| Unique ID    | `"ID"`           | int    |
| Type tag     | `"Type"`         | str    |
| Company name | `"Company Name"` | str    |

**Flight**

| Field          | JSONL key      | Type   |
|----------------|----------------|--------|
| Type tag       | `"Type"`       | str    |
| Client ID (FK) | `"Client_ID"`  | int    |
| Airline ID (FK)| `"Airline_ID"` | int    |
| Departure date | `"Date"`       | str    |
| Origin city    | `"Start City"` | str    |
| Destination    | `"End City"`   | str    |

Flights do not carry their own surrogate key; they are identified
by the composite natural key `(Client_ID, Airline_ID, Date)`.

### Interface Layer

| Window              | Class / Function    | Role                                       |
|---------------------|---------------------|--------------------------------------------|
| Dashboard           | `open_main_window()`| Entry point; links to the three modules    |
| Client Management   | `ClientWindow`      | Full CRUD for client records               |
| Airline Management  | `AirlineWindow`     | Full CRUD for airline records              |
| Flight Management   | `FlightWindow`      | Full CRUD for flight records               |

Each management window contains:
- A **header** bar with title and optional PNG icon.
- An **input form** with labelled entry widgets for all record fields.
- A row of **CRUD action buttons** (Create, Update, Delete, Search,
  Clear), each colour-coded by destructive intent.
- A **Treeview table** showing all existing records of that type,
  with alternating row colours and scrollbars.
- A **status bar** at the foot of the window reporting the outcome
  of the most recent action.

All windows are HiDPI-aware: they calculate an effective scaling
ratio from tkinter's reported DPI and adjust their pixel dimensions
accordingly, then centre themselves on whichever physical monitor
the mouse cursor resides on.

### Testing Strategy

The test suite (74 tests) is written with **pytest** and is located
in the `tests/` directory. Tests are entirely unit-level; they do
not touch the file system except through `tmp_path` fixtures, and
they never instantiate any tkinter widgets. Key aspects:

- **test_models.py** — verifies round-trip serialisation
  (`to_dict` / `from_dict`) and automatic type-tag assignment for
  all three dataclasses.
- **test_storage.py** — verifies `load_records` and `save_records`
  using temporary files.
- **test_repository.py** — verifies the `RecordRepository` CRUD
  interface including duplicate detection and not-found errors.
- **test_airline_record.py** — verifies all four airline CRUD
  functions, including cascade delete of associated flights.
- **test_client_record.py** — verifies all four client CRUD
  functions, including cascade delete and ID propagation.
- **test_flight_record.py** — verifies all four flight CRUD
  functions using the composite natural key.

---

### Standards & Conventions

- All Python source code follows **PEP 8**
  (<https://peps.python.org/pep-0008/>): 4-space indentation,
  maximum 79-character lines, snake\_case identifiers, PascalCase
  class names, and UPPER\_SNAKE\_CASE constants.
- All Git commit messages follow the **PyInstaller commit message
  guidelines**
  (<https://pyinstaller.org/en/stable/development/commit-messages.html>).
- All written content (docstrings, comments, documentation) is in
  **British English**.

---

### Project Requirements Compliance

This subsection maps every requirement from the original project
specification to its implementation status following the compliance
audit.

#### Record Types

| Requirement | Status | Notes |
|---|---|---|
| Client record with 11 specified fields | ✅ | All fields present in `create_client`, `ClientRecord.to_dict`, and `ClientWindow` form |
| Airline record with 3 specified fields | ✅ | All fields present in `create_airline`, `AirlineRecord.to_dict`, and `AirlineWindow` form |
| Flight record with 5 specified fields | ✅ | All fields present in `create_flight`, `FlightRecord.to_dict`, and `FlightWindow` form |
| `Type` field auto-set (not user-editable) | ✅ | Set automatically in all record creation functions and dataclass `__post_init__` |
| `ID` auto-assigned (not user-entered) | ✅ | Fixed in this audit: Client and Airline IDs now auto-assigned from `max(existing_ids) + 1`; the ID entry field is used only for Search/Update |
| `Client_ID` / `Airline_ID` validated against existing records | ✅ | Validated in `FlightWindow.create_flight` and `update_flight` before saving |
| `Date` field stored as proper date/time (not raw string) | ✅ | Fixed in this audit: `FlightWindow.create_flight` and `update_flight` now convert user input via `datetime.strptime` + `isoformat()` before storing in ISO-8601 format |

#### Internal Storage

| Requirement | Status | Notes |
|---|---|---|
| All records stored as `list[dict]` | ✅ | All three types stored in a single shared `list[dict]`; distinguished by the `"Type"` field |
| Canonical field names used as dict keys | ✅ | Keys match specification exactly (e.g. `"Address Line 1"`, `"Zip Code"`, `"Phone Number"`) |
| Single list, `"Type"` field distinguishes records | ✅ | Documented throughout README and consistent across all modules |

#### Persistence

| Requirement | Status | Notes |
|---|---|---|
| Persisted in pickle / JSON / JSONL | ✅ | JSONL (JSON Lines) used throughout |
| Single format used consistently | ✅ | Only JSONL; no mixing |
| Save on application close | ✅ | Fixed in this audit: `main_window.py` `on_close` callbacks now call `window.on_close()` (saves + destroys) instead of `window.destroy()` (destroy only). Each CRUD operation also saves immediately. |
| Check file existence on start | ✅ | `load_records()` in `storage.py` returns `[]` when the file is absent |
| File path as named constant | ✅ | `DATA_FILE` constant in `src/storage.py`; `FILE_PATH` in `src/conf/settings.py` |
| `datetime` values serialised/deserialised correctly (ISO-8601) | ✅ | Fixed in this audit: dates now stored as ISO-8601 strings (e.g. `"2025-06-15T10:30:00"`); `FlightRecord.from_dict` parses them back with `datetime.fromisoformat` |
| Error handling for corrupted files | ✅ | `load_records` catches `json.JSONDecodeError` and `IOError`, returning `[]` |

#### Graphical User Interface — CRUD

| Requirement | Status | Notes |
|---|---|---|
| Create / Delete / Update / Search for **Client** records | ✅ | All four operations implemented in `ClientWindow` |
| Create / Delete / Update / Search for **Airline** records | ✅ | All four operations implemented in `AirlineWindow` |
| Create / Delete / Update / Search for **Flight** records | ✅ | All four operations implemented in `FlightWindow` |
| IDs auto-assigned on Create | ✅ | Fixed in this audit for Client and Airline; Flights have no surrogate ID |
| `Type` field not exposed as user input | ✅ | Set automatically in all record creation paths |
| Input validation before saving | ✅ | Required fields, numeric checks, date format validation, and foreign-key checks |
| Confirmation prompt before Delete | ✅ | `messagebox.askyesno` used in all three windows |
| Update form pre-populated from selected row | ✅ | `on_tree_select` populates all entry widgets from the Treeview row |
| Cascade delete when Client or Airline is deleted | ✅ | Implemented in both `delete_client` / `delete_airline` (data layer) and the GUI windows |
| "No results" message on unsuccessful Search | ✅ | Each window shows an `showinfo` or `showwarning` dialogue on no match |
| Flight search displays Client name and Airline name | ⚠️ | Flight Treeview displays raw integer IDs (`Client_ID`, `Airline_ID`); resolved names are not shown. This is a usability improvement rather than a hard requirement — the raw IDs are correct and unambiguous |

#### Unit Tests

| Requirement | Status | Notes |
|---|---|---|
| Test module for each non-GUI module | ✅ | `test_models.py`, `test_storage.py`, `test_repository.py`, `test_client_record.py`, `test_airline_record.py`, `test_flight_record.py` |
| Tests cover Create for all three record types | ✅ | 6 + 6 + 5 Create tests across the three record test modules |
| Tests cover Delete (including orphan-record scenario) | ✅ | Cascade delete tested for both Client→Flight and Airline→Flight |
| Tests cover Update for all three record types | ✅ | Including cascade ID propagation for Client |
| Tests cover Search (including no-results case) | ✅ | All three modules test the empty-result path |
| Tests cover persistence round-trip | ✅ | `test_storage.py` verifies save + reload fidelity |
| Tests cover input validation | ✅ | `RecordNotFoundError` and `DuplicateRecordError` tested; date parsing tested via `test_models.py` |
| Tests cover file-existence start-up check | ✅ | `test_load_returns_empty_list_when_file_missing` in `test_storage.py` |
| All tests pass | ✅ | 74 tests pass with `python -m pytest tests/ -v` |

---

## Code Reference

### `src/exceptions.py`

Defines the two custom exception classes raised throughout the
application when record-level errors occur.

- **`RecordNotFoundError(Exception)`** — raised by
  `RecordRepository._find_index` and the CRUD helpers in
  `src/record/` when no record matching the supplied ID (and, for
  typed lookups, the record type) can be located. Callers are
  expected to catch this and report the failure to the user.
- **`DuplicateRecordError(Exception)`** — raised by
  `RecordRepository.add` when a record with the same `"Type"` and
  `"ID"` already exists in the repository. Guards against accidental
  overwrites when creating new records.

> 💬 **Comments added:** British English module-level docstring and
> expanded class docstrings added throughout.

---

### `src/conf/settings.py`

Defines the `FILE_PATH` constant — the absolute path to the JSONL
data file used by the storage layer.

- **`FILE_PATH`** — computed via `os.path.join` by navigating three
  levels up from `__file__` (i.e., from `src/conf/settings.py` to
  the repository root) and then into `data/records.jsonl`. This
  ensures the path is correct regardless of the working directory
  from which the application is launched.

> 💬 **Comments added:** British English module-level docstring and
> explanatory inline comment added.

---

### `src/conf/__init__.py`

Re-exports `FILE_PATH` from `settings.py` so that other modules
can import the constant directly from `src.conf`.

- **`from .settings import FILE_PATH`** — makes `FILE_PATH`
  available as `src.conf.FILE_PATH`.
- **`__all__`** — restricts the public API of the sub-package to
  `FILE_PATH` alone.

> 💬 **Comments added:** British English module-level docstring added.

---

### `src/models.py`

Defines three `@dataclass` classes — `ClientRecord`, `AirlineRecord`,
and `FlightRecord` — each providing `to_dict` / `from_dict` helpers
for round-tripping with the JSONL storage layer.

**`ClientRecord`**

- `TYPE: ClassVar[str] = "Client"` — class-level constant used to
  set the `"Type"` field on every instance automatically.
- `__post_init__` — called by the dataclass machinery immediately
  after `__init__`; sets `self.type = self.TYPE`.
- `to_dict() -> dict` — serialises the instance to a dict whose
  keys match the canonical JSONL storage schema (e.g.,
  `"Address Line 1"`, `"Zip Code"`, `"Phone Number"`).
- `from_dict(cls, data: dict) -> "ClientRecord"` — class method that
  deserialises a canonical-schema dict back into a `ClientRecord`
  instance.

**`AirlineRecord`**

- `TYPE: ClassVar[str] = "Airline"` — type tag constant.
- `__post_init__`, `to_dict`, `from_dict` — same pattern as
  `ClientRecord` but with only two user-supplied fields (`id`,
  `company_name`).

**`FlightRecord`**

- `TYPE: ClassVar[str] = "Flight"` — type tag constant.
- `__post_init__` — in addition to setting `self.type`, it coerces
  the `date` field from an ISO-8601 string to a `datetime` object
  if necessary. This allows callers to supply either a string or a
  `datetime` instance.
- `to_dict` — serialises `date` back to an ISO-8601 string via
  `self.date.isoformat()`.
- `from_dict` — passes the raw `"Date"` string to the constructor,
  relying on `__post_init__` to perform the coercion.

> 💬 **Comments added:** British English module-level docstring,
> expanded class docstrings with `Attributes:` sections, and
> `__post_init__` docstrings added throughout.

---

### `src/storage.py`

Provides two stateless functions for reading and writing the JSONL
data file. Neither function is aware of record types; it treats each
line simply as a JSON object.

- **`DATA_FILE`** — module-level constant holding the default path
  to `data/records.jsonl`, computed relative to the location of
  `storage.py` itself. This is a fallback path used when no
  `filepath` argument is supplied; the GUI always uses the path from
  `src.conf.FILE_PATH`.
- **`load_records(filepath: str = DATA_FILE) -> list[dict]`** —
  reads the file line-by-line, strips whitespace, skips blank lines,
  and deserialises each line with `json.loads`. Returns an empty
  list if the file does not exist or if a `JSONDecodeError` or
  `IOError` is raised during reading.
- **`save_records(records: list[dict], filepath: str = DATA_FILE) -> None`** —
  creates the parent directory with `os.makedirs(..., exist_ok=True)`
  if it does not already exist, then overwrites the file by writing
  one `json.dumps(record)` per line. Any `IOError` is caught and
  printed to stdout.

> 💬 **Comments added:** British English module-level docstring and
> block comments above error-handling sections added throughout.

---

### `src/repository.py`

Implements `RecordRepository`, an in-memory CRUD store that wraps a
plain `list[dict]`. Primarily consumed by the test suite; the GUI
windows use the record-layer functions directly.

**`RecordRepository`**

- `__init__(self, records: list[dict] | None = None)` — initialises
  the repository with an optional pre-populated list. If `None` is
  supplied, an empty list is used.
- `_find_index(self, record_id: int, record_type: str) -> int` —
  private helper that iterates `self.records` and returns the index
  of the first record whose `"Type"` and `"ID"` match the
  arguments. Raises `RecordNotFoundError` if no such record exists.
- `add(self, record: dict) -> None` — appends the record to
  `self.records`. Before appending, it attempts to find an existing
  record with the same type and ID; if one is found, it raises
  `DuplicateRecordError`. Records without an `"ID"` field (e.g.,
  Flight records) are appended unconditionally.
- `delete(self, record_id: int, record_type: str) -> None` — removes
  the record at the index returned by `_find_index`, raising
  `RecordNotFoundError` if not found.
- `update(self, record_id: int, record_type: str, updates: dict) -> None` —
  merges `updates` into the existing record dict via `dict.update`,
  raising `RecordNotFoundError` if not found.
- `search(self, **kwargs) -> list[dict]` — filters `self.records`
  by iteratively narrowing the result set for each supplied
  key-value pair. Returns all records when called with no arguments.
- `get_all(self) -> list[dict]` — returns a shallow copy of
  `self.records` so that callers cannot inadvertently mutate the
  repository's internal state.

> 💬 **Comments added:** British English module-level docstring,
> expanded class and method docstrings, and block comments above
> internal helper sections added throughout.

---

### `src/record/__init__.py`

Re-exports all twelve public CRUD functions (four per record type)
from the three sub-modules so that callers can import them directly
from `src.record`.

- Imports `create_client`, `delete_client`, `update_client`,
  `search_clients` from `.client_record`.
- Imports `create_airline`, `delete_airline`, `update_airline`,
  `search_airlines` from `.airline_record`.
- Imports `create_flight`, `delete_flight`, `update_flight`,
  `search_flights` from `.flight_record`.
- `__all__` — declares the complete public surface area of the
  sub-package, enabling `from src.record import *` to work
  predictably.

> 💬 **Comments added:** British English module-level docstring added.

---

### `src/record/airline_record.py`

Pure functions for CRUD operations on Airline records. Each function
receives the full in-memory record list by reference and mutates it
in place (or raises an exception on failure).

- **`_next_id(records: list[dict]) -> int`** — private helper that
  collects all `"ID"` values from existing Airline records and
  returns `max + 1`, or `1` if no airlines exist yet.
- **`create_airline(records, company_name) -> dict`** — builds a new
  Airline dict with an auto-incremented ID, appends it to `records`,
  and returns it.
- **`delete_airline(records, airline_id) -> None`** — first checks
  that an airline with the given ID exists (raising
  `RecordNotFoundError` if not), then removes both the airline and
  all Flight records whose `"Airline_ID"` matches, in a single list
  comprehension that overwrites `records[:]`.
- **`update_airline(records, airline_id, **updates) -> None`** —
  iterates `records` to find the matching airline and calls
  `dict.update` with the supplied keyword arguments. Raises
  `RecordNotFoundError` if no match is found.
- **`search_airlines(records, **kwargs) -> list[dict]`** — starts
  from the subset of Airline records and iteratively filters by each
  supplied key-value pair.

> 💬 **Comments added:** British English docstrings and block
> comments added throughout.

---

### `src/record/client_record.py`

Pure functions for CRUD operations on Client records. Structurally
identical to `airline_record.py` but with additional cascade logic
for ID propagation.

- **`_next_id(records: list[dict]) -> int`** — same auto-increment
  logic as in `airline_record.py` but scoped to `"Client"` records.
- **`create_client(records, name, address_line1, address_line2, address_line3, city, state, zip_code, country, phone_number) -> dict`** —
  builds and appends a new Client dict with all ten user-supplied
  fields plus an auto-incremented ID.
- **`delete_client(records, client_id) -> None`** — verifies the
  client exists, then removes the client and all associated Flight
  records (`"Client_ID" == client_id`) in a single slice assignment.
- **`update_client(records, client_id, **updates) -> None`** —
  updates the matching client record. If `"ID"` is present in
  `updates` and the new ID differs from the old one, it cascades the
  new value to the `"Client_ID"` field of all related Flight records.
  Raises `RecordNotFoundError` if the client is not found.
- **`search_clients(records, **kwargs) -> list[dict]`** — filters
  Client records by the supplied key-value pairs.

> 💬 **Comments added:** British English docstrings and block
> comments added throughout.

---

### `src/record/flight_record.py`

Pure functions for CRUD operations on Flight records. Because Flight
records have no surrogate primary key, they are identified by the
composite natural key `(Client_ID, Airline_ID, Date)`.

- **`create_flight(records, client_id, airline_id, date, start_city, end_city) -> dict`** —
  builds and appends a new Flight dict. `date` is expected to be an
  ISO-8601 datetime string (e.g. `"2025-03-14T10:30:00"`).
- **`delete_flight(records, client_id, airline_id, date) -> None`** —
  iterates `records` with `enumerate`, removes the first matching
  Flight using `list.pop`, and raises `RecordNotFoundError` if none
  is found.
- **`update_flight(records, client_id, airline_id, date, **updates) -> None`** —
  iterates `records`, calls `dict.update` on the first matching
  Flight, and raises `RecordNotFoundError` if none is found.
- **`search_flights(records, **kwargs) -> list[dict]`** — filters
  Flight records by the supplied key-value pairs.

> 💬 **Comments added:** British English docstrings and block
> comments added throughout.

---

### `src/gui/__init__.py`

Package initialiser for the `src.gui` sub-package. Contains only a
module-level docstring; all GUI classes are imported directly from
their respective modules by callers.

> 💬 **Comments added:** British English module-level docstring added.

---

### `src/gui/main_window.py`

Contains the single top-level function `open_main_window()`, which
builds and runs the primary dashboard window of the application.

**`open_main_window() -> None`**

- Creates the root `tk.Tk()` window with a light grey background.
- Implements **HiDPI-aware sizing**: reads the current tkinter
  scaling factor, divides by the standard baseline (96 DPI / 72 pt),
  and multiplies target dimensions by the resulting ratio. Clamps
  the final size to the monitor bounds.
- Estimates the number of connected monitors from the ratio of the
  total virtual desktop width to the screen height, then centres the
  window on whichever monitor the mouse pointer currently occupies.
- Builds a **header frame** (dark navy, white text) showing the
  application title and subtitle.
- Builds a **footer frame** with a dynamic status label (left) and
  Exit / Help action buttons (right).
- Attempts to load PNG icons from the `assets/` subdirectory; falls
  back to text-only buttons if the files are absent.
- Builds an **actions frame** laid out as a 2-column grid. The
  Clients and Airlines buttons occupy row 0 (one per column); the
  Flights button spans both columns in row 1.
- Binds `<Enter>` / `<Leave>` events to each module button to
  produce a hover effect (colour darkens on hover, restores on
  leave).
- Defines inner functions: `update_status`, `confirm_exit`,
  `on_enter`, `on_leave`, `open_clients`, `open_airlines`,
  `open_flights`, and `show_help`.
- Calls `root.mainloop()` to start the tkinter event loop.

> 💬 **Comments added:** PEP 8 fixes applied (quote consistency,
> alignment spaces removed); British English docstrings confirmed and
> supplemented throughout.
> ⚠️ **Audit fix — PEP 8:** Module-level docstring was missing; added.
> Type annotations added to `open_main_window()` and all inner
> functions (`update_status`, `confirm_exit`, `on_enter`, `on_leave`,
> `open_clients`, `open_airlines`, `open_flights`, `show_help`, and
> their nested `on_close` callbacks).
> 🔍 **Audit fix — Requirements:** The `on_close` callbacks inside
> `open_clients`, `open_airlines`, and `open_flights` previously called
> `window.destroy()` directly, bypassing each window's `on_close()`
> method and therefore skipping the final save to the JSONL file.
> Fixed: callbacks now call `window.on_close()`, which saves records
> and then destroys the window, satisfying the specification requirement
> to save to the file system when the application is closed.

---

### `src/gui/airline_window.py`

Implements `AirlineWindow(tk.Toplevel)` — the modal window for
managing Airline records.

**`__init__(self, master=None)`**

- Applies HiDPI-aware sizing and monitor-centring logic identical to
  `main_window.py`.
- Calls `self.transient(master)` and `self.grab_set()` to make the
  window modal.
- Loads records from the JSONL file via `load_records()`.
- Configures `ttk.Style` with the `"clam"` theme, custom Treeview
  fonts, selection colour, and scrollbar dimensions.
- Attempts to load `airline.png` from the assets folder, subsampling
  it to roughly one-quarter of its original size.
- Calls `create_widgets()` and `populate_treeview()`, then binds
  `WM_DELETE_WINDOW`, `<Return>`, and sets initial focus.

**`create_widgets(self)`**

- Builds the header bar, main container, input form (Airline ID +
  Company Name), CRUD button row, Treeview table, empty-state label,
  record counter, and status bar.

**`populate_treeview(self)`**

- Clears the Treeview, iterates `self.records` to insert Airline
  records with alternating row colours, toggles the empty-state label,
  and updates the counter label.

**`clear_form(self)`** — clears both entry fields and deselects any
  highlighted Treeview row.

**`create_airline(self)`** — validates the Company Name (must be
  non-empty), auto-assigns the next available Airline ID (the user
  never enters an ID manually for Create), appends the record,
  saves, and refreshes.

**`search_airline(self)`** — looks up an airline by ID; optionally
  verifies a supplied Company Name matches.

**`update_airline(self)`** — updates the Company Name of the airline
  identified by the entered ID.

**`delete_airline(self)`** — deletes the selected airline and all
  associated Flight records after confirmation.

**`on_tree_select(self, event)`** — populates the form when a
  Treeview row is clicked.

**`on_close(self)`** — saves records and destroys the window.

> ⚠️ **Fix applied:** Extra alignment spaces removed from
> `aid  =` assignments (`# PEP 8 fix` comments added).
> ⚠️ **Audit fix — PEP 8:** Module-level docstring was missing; added.
> Single quotes in `self.tk.call('tk', 'scaling')` corrected to double
> quotes for file-wide consistency (`# PEP 8 fix` comment added).
> Type annotations added to `__init__` and all public methods
> (`create_widgets`, `populate_treeview`, `clear_form`,
> `create_airline`, `search_airline`, `update_airline`,
> `delete_airline`, `on_tree_select`, `on_close`) and inner functions
> (`on_enter`, `on_leave`).
> 💬 **Comments added:** British English module-level docstring and
> comprehensive method docstrings added throughout.
> 🔍 **Audit fix — Requirements:** `create_airline` now auto-assigns
> the next available Airline ID from existing records instead of
> requiring the user to enter one manually, satisfying the specification
> requirement that "IDs are assigned automatically".  The Airline ID
> field in the form is retained for Search and Update operations.
> Initial focus moved from `id_entry` to `name_entry` for a smoother
> Create workflow.

---

### `src/gui/client_window.py`

Implements `ClientWindow(tk.Toplevel)` — the modal window for
managing Client records.

**`__init__(self, master)`**

- Same HiDPI sizing, modality, and icon-loading pattern as
  `AirlineWindow.__init__`.
- Sets `self.required_fields = ["Name", "Phone Number"]` to
  distinguish mandatory from optional fields.  The `ID` field is
  intentionally excluded: it is auto-assigned on creation and only
  entered manually when searching or updating by ID.

**`create_widgets(self)`**

- Builds a two-column grid form with all ten client fields, labelling
  required fields with an asterisk.
- Builds the CRUD button row, a horizontally and vertically scrollable
  Treeview with ten columns, the empty-state label, counter, and
  status bar.

**`populate_treeview(self)`** — inserts all Client records into the
  Treeview with alternating row colours.

**`get_client_id(self) -> int | None`** — parses the ID entry as an
  integer; returns `None` and shows a warning if the value is
  non-numeric.

**`clear_form(self)`** — clears all entries, removes validation
  highlights, and resets focus.

**`get_entry_values(self) -> dict`** — returns a stripped dict of all
  field values.

**`validate_field(self, field, value) -> bool`** — applies per-field
  validation rules: numeric fields must be digit-only; name/city/
  state/country fields must match a letters-and-spaces regex.

**`validate_entries(self, values) -> tuple[bool, str | None]`** —
  checks required fields first, then delegates to `validate_field`.

**`create_client(self)`** — highlights missing required fields in red,
  validates all entries, auto-assigns the next available Client ID
  (the user never enters an ID manually for Create), appends the
  record, saves, and refreshes.

**`search_client(self)`** — finds a client by ID and optionally
  verifies additionally entered field values.

**`update_client(self)`** — updates all client fields and cascades
  any ID change to related flight records.

**`delete_client(self)`** — deletes the selected client and all their
  associated flights after confirmation.

**`on_tree_select(self, event)`** — populates the form from the
  selected Treeview row.

**`on_close(self)`** — saves records and destroys the window.

> ⚠️ **Fix applied:** Extra alignment spaces removed from
> `values["ID"]   =` assignment and the `delete_client` filter
> (`# PEP 8 fix` comments added).
> ⚠️ **Audit fix — PEP 8:** Module-level docstring was missing; added.
> Single quotes in `self.tk.call('tk', 'scaling')` corrected to double
> quotes for file-wide consistency (`# PEP 8 fix` comment added).
> Type annotations added to `__init__` and all public methods
> (`create_widgets`, `populate_treeview`, `get_client_id`,
> `clear_form`, `get_entry_values`, `validate_field`,
> `validate_entries`, `create_client`, `search_client`,
> `update_client`, `delete_client`, `on_tree_select`, `on_close`)
> and inner functions (`on_enter`, `on_leave`).
> 💬 **Comments added:** British English module-level docstring and
> comprehensive method docstrings added throughout.
> 🔍 **Audit fix — Requirements:** `create_client` now auto-assigns
> the next available Client ID from existing records instead of
> requiring the user to enter one manually, satisfying the specification
> requirement that "IDs are assigned automatically".  `"ID"` removed
> from `required_fields`; the ID field in the form is retained for
> Search and Update operations.  Initial focus moved from `entries["ID"]`
> to `entries["Name"]` for a smoother Create workflow.

---

### `src/gui/flight_window.py`

Implements `FlightWindow(tk.Toplevel)` — the modal window for
managing Flight records.

**`__init__(self, master=None)`**

- Same HiDPI sizing, modality, and icon-loading pattern as the
  other windows.
- All five form fields are treated as mandatory; the entry dict is
  keyed by the label strings (including the trailing `" *"`).

**`create_widgets(self)`**

- Builds a single-column form with five fields: Client ID, Airline
  ID, Date (YYYY-MM-DD HH:MM), Start City, End City.
- Builds the CRUD button row, a scrollable Treeview with five
  columns, the empty-state label, counter, and status bar.

**`populate_treeview(self)`** — inserts all Flight records into the
  Treeview with alternating row colours.

**`clear_form(self)`** — clears all entry fields and resets focus.

**`create_flight(self)`** — reloads records from disk (to avoid
  stale data), validates all entries, parses the date string with
  `datetime.strptime`, converts to ISO-8601 via `isoformat()` before
  storing, verifies the referenced Client and Airline
  exist, then appends and saves.

**`search_flight(self)`** — searches all flights for a given Client
  ID and highlights each matching Treeview row.

**`update_flight(self)`** — reads the original composite key from the
  selected Treeview row, locates the matching record in memory,
  validates and converts the new date to ISO-8601, and overwrites
  all five fields with the form values.

**`delete_flight(self)`** — removes the selected flight record after
  confirmation, matching by composite key.

**`on_tree_select(self, event)`** — populates all form entries from
  the selected Treeview row values.

**`on_close(self)`** — releases the modal grab, saves records, and
  destroys the window.

> ⚠️ **Fix applied:** Eight instances of extra alignment spaces
> removed from variable assignments and dict literals in
  `create_flight`, `update_flight`, and `on_tree_select`
> (`# PEP 8 fix` comments added).
> ⚠️ **Audit fix — PEP 8:** Module-level docstring was missing; added.
> Single quotes in `self.tk.call('tk', 'scaling')` corrected to double
> quotes for file-wide consistency (`# PEP 8 fix` comment added).
> Type annotations added to `__init__` and all public methods
> (`create_widgets`, `populate_treeview`, `clear_form`,
> `create_flight`, `search_flight`, `update_flight`, `delete_flight`,
> `on_tree_select`, `on_close`) and inner functions (`on_enter`,
> `on_leave`).
> 💬 **Comments added:** British English module-level docstring and
> comprehensive method docstrings added throughout.
> 🔍 **Audit fix — Requirements:** `create_flight` and `update_flight`
> now convert the user-entered date string to ISO-8601 format via
> `datetime.strptime` + `isoformat()` before storing, satisfying the
> requirement that the Date field be handled as a proper date/time
> value with correct serialisation to the file system.

---

### `src/main.py`

Application entry point. Importing this module as `python -m src.main`
invokes `main()`, which delegates immediately to `open_main_window()`.

- **`main() -> None`** — calls `open_main_window()` from
  `src.gui.main_window`. The tkinter event loop runs inside that
  function and blocks until the root window is closed.
- **`if __name__ == "__main__": main()`** — guards the entry point
  so the module can be imported by tests without launching the GUI.

> 💬 **Comments added:** British English module-level docstring and
> function docstring added.

---

### `src/__init__.py`

Top-level package initialiser for the `src` package. Contains only a
module-level docstring summarising the package's role. No imports or
runtime logic are present; consumers import directly from the
sub-modules.

> 💬 **Comments added:** British English module-level docstring added.

---

### `tests/__init__.py`

Package initialiser for the `tests` directory. Previously an empty
file; now contains a module-level docstring summarising the scope
of the test suite and the tools required to run it.

> 💬 **Audit fix — Comments:** Module-level docstring was missing;
> added a British English summary describing the test suite contents.

---

### `tests/test_models.py`

Verifies the three dataclass models in `src/models.py`.

- **`make_client(**kwargs)`** — helper factory that constructs a
  `ClientRecord` with sensible defaults, allowing individual fields
  to be overridden.
- **`TestClientRecord`** — 5 tests covering: automatic type tag
  (`test_type_is_auto_set`), canonical schema key presence
  (`test_to_dict_contains_canonical_keys`), correct type value
  (`test_to_dict_type_value_is_capitalised`), round-trip fidelity
  (`test_from_dict_round_trip`), and `TypeError` on missing required
  fields (`test_missing_required_field_raises`).
- **`TestAirlineRecord`** — 4 tests covering type tag, canonical
  keys, type value, and round-trip.
- **`TestFlightRecord`** — 5 tests covering type tag, canonical
  keys, type value, date serialisation to string, and
  `from_dict` restoring a `datetime` object.

---

### `tests/test_storage.py`

Verifies `load_records` and `save_records` in `src/storage.py` using
pytest's `tmp_path` fixture so no test data touches the working tree.

- **`test_load_returns_empty_list_when_file_missing`** — confirms
  that loading from a non-existent path returns `[]`.
- **`test_save_and_reload`** — writes a single record and confirms
  it can be read back with the correct field values.
- **`test_save_multiple_records`** — writes five records and confirms
  all five are reloaded.
- **`test_overwrite_on_save`** — confirms that saving a second list
  completely replaces the first (no appending).

---

### `tests/test_repository.py`

Verifies `RecordRepository` in `src/repository.py` using two pytest
fixtures: `repo` (empty repository) and `client_record` (a sample
Client dict).

- **`test_add_and_search`** — adds a record and searches by type
  and ID.
- **`test_add_duplicate_raises`** — confirms `DuplicateRecordError`
  when the same record is added twice.
- **`test_delete_record`** — adds then deletes a record and confirms
  the search returns empty.
- **`test_delete_nonexistent_raises`** — confirms
  `RecordNotFoundError` when deleting a non-existent ID.
- **`test_update_record`** — updates a field and confirms the
  change persists.
- **`test_update_nonexistent_raises`** — confirms
  `RecordNotFoundError` when updating a non-existent ID.
- **`test_search_by_arbitrary_field`** — adds two records with
  different cities and confirms filtering returns exactly one.
- **`test_get_all`** — confirms `get_all` returns a list with the
  correct length.

---

### `tests/test_airline_record.py`

Verifies the four functions in `src/record/airline_record.py`.

- **`TestCreateAirline`** (6 tests) — covers: record added to list,
  ID starts at 1, ID auto-increments, type tag is `"Airline"`,
  company name stored, canonical schema keys present.
- **`TestDeleteAirline`** (5 tests) — covers: record removed, non-
  existent ID raises `RecordNotFoundError`, only the matching record
  is removed, cascade delete removes associated flights, cascade
  delete leaves other airlines' flights intact.
- **`TestUpdateAirline`** (2 tests) — covers: field changed, non-
  existent ID raises `RecordNotFoundError`.
- **`TestSearchAirlines`** (3 tests) — covers: returns correct
  record, empty result on no match, returns all when no filter.

---

### `tests/test_client_record.py`

Verifies the four functions in `src/record/client_record.py`.
Uses the `_make_client` helper to create fully-formed Client records.

- **`TestCreateClient`** (6 tests) — covers: record added, ID starts
  at 1, ID auto-increments, type is `"Client"`, fields stored
  correctly, canonical schema keys present.
- **`TestDeleteClient`** (5 tests) — covers: record removed, non-
  existent ID raises, only matching record removed, cascade delete
  removes associated flights, cascade delete leaves other clients'
  flights intact.
- **`TestUpdateClient`** (4 tests) — covers: field changed, non-
  existent ID raises, other fields unchanged, ID change cascades to
  flight `Client_ID`.
- **`TestSearchClients`** (3 tests) — covers: returns correct record,
  empty result on no match, returns all when no filter.

---

### `tests/test_flight_record.py`

Verifies the four functions in `src/record/flight_record.py`.
Uses two date constants (`DATE`, `DATE2`) and the `_make_flight`
helper.

- **`TestCreateFlight`** (5 tests) — covers: record added, fields
  stored correctly, type is `"Flight"`, multiple flights can be
  added, canonical schema keys present.
- **`TestDeleteFlight`** (3 tests) — covers: record removed, non-
  existent composite key raises `RecordNotFoundError`, only the
  matching record is removed.
- **`TestUpdateFlight`** (3 tests) — covers: field changed, non-
  existent composite key raises, other fields unchanged.
- **`TestSearchFlights`** (3 tests) — covers: returns correct record,
  empty result on no match, returns all when no filter.
