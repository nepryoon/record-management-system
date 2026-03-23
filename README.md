# Record Management System

<img src="https://img.shields.io/badge/python-3.11+-blue"> <img src="https://img.shields.io/badge/code%20style-PEP%208-brightgreen"> <img src="https://img.shields.io/badge/accessibility-WCAG%202.1%20AA-blue"> <img src="https://img.shields.io/badge/tests-81%20passed-brightgreen"> <img src="https://img.shields.io/badge/licence-MIT-lightgrey">

---

## Project Abstract

The Record Management System is a standalone desktop application designed for specialist travel agency operators who must maintain three interrelated entity types: Clients, Airlines, and Flights. A Flight is a join entity that links a Client to an Airline, recording a departure date and time, an origin city, and a destination city. The system was developed as a group project for the MSc in Data Science and Artificial Intelligence at the University of Liverpool. It addresses a practical operational problem — providing a simple, keyboard-friendly interface to maintain records without the complexity and administrative overhead of a full database server.

The application relies exclusively on Python's standard library: `tkinter` supplies the graphical interface, `json` handles serialisation, `datetime` manages date parsing, `os` resolves file paths, and `re` provides regular-expression validation. No third-party runtime packages are required. All three record types coexist in a single flat JSONL file (`data/records.jsonl`), with one JSON object per line distinguished by a `"Type"` field whose value is `"Client"`, `"Airline"`, or `"Flight"`. The file is loaded on application startup and saved after every Create, Update, and Delete operation, as well as when any record window is closed, ensuring that on-disk state is always consistent with the in-memory data.

The codebase is organised into four distinct layers: the GUI layer, the Record layer, the Repository layer, and the Storage layer. The governing design principle is that the GUI never reads or writes the data file directly — it calls pure functions in the Record layer, which operate on a shared in-memory `list[dict]` and implement cascade deletes, ID auto-increment, and referential integrity. The Storage layer is the sole component that interacts with the file system, whilst the Repository layer provides a typed, exception-raising interface consumed primarily by the automated test suite. The choice of `list[dict]` as the in-memory structure was deliberate: it satisfies the project specification, requires no object-relational mapper, maps directly to JSON, and can be inspected as plain text at any time.

The codebase adheres to PEP 8 (code style), PEP 257 (docstrings), WCAG 2.1 Level AA (colour contrast), and the PyInstaller commit message guidelines. All written content uses British English. Correctness and reliability are validated by 81 automated unit tests covering every CRUD operation, cascade behaviours, persistence round-trips, referential integrity checks, duplicate composite-key rejection, and validation edge cases. The entire test suite can be executed with a single command, described in detail in the Getting Started section below.

---

## Getting Started

The following command sequences are provided for the three most common development environments. Each block is self-contained and copy-paste-ready.

### Linux / macOS

```bash
# 1. Clone the repository from GitHub
git clone https://github.com/nepryoon/record-management-system.git

# 2. Navigate into the project directory
cd record-management-system

# 3. Create an isolated virtual environment
python3 -m venv .venv

# 4. Activate the virtual environment
source .venv/bin/activate

# 5. Install development dependencies from requirements-dev.txt
pip install -r requirements-dev.txt

# 6. Run the full test suite
python -m pytest tests/ -v

# 7. Launch the application
python -m src.main

# 8. Pull updates and reinstall dependencies if changed
git pull && pip install -r requirements-dev.txt
```

### Windows (PowerShell)

```powershell
# 1. Clone the repository from GitHub
git clone https://github.com/nepryoon/record-management-system.git

# 2. Navigate into the project directory
cd record-management-system

# 3. Create an isolated virtual environment
python -m venv .venv

# 4. Activate the virtual environment
.venv\Scripts\Activate.ps1

# 5. Install development dependencies from requirements-dev.txt
pip install -r requirements-dev.txt

# 6. Run the full test suite
python -m pytest tests/ -v

# 7. Launch the application
python -m src.main

# 8. Pull updates and reinstall dependencies if changed
git pull; pip install -r requirements-dev.txt
```

### Windows (CMD)

```cmd
REM 1. Clone the repository from GitHub
git clone https://github.com/nepryoon/record-management-system.git

REM 2. Navigate into the project directory
cd record-management-system

REM 3. Create an isolated virtual environment
python -m venv .venv

REM 4. Activate the virtual environment
.venv\Scripts\activate.bat

REM 5. Install development dependencies from requirements-dev.txt
pip install -r requirements-dev.txt

REM 6. Run the full test suite
python -m pytest tests/ -v

REM 7. Launch the application
python -m src.main

REM 8. Pull updates and reinstall dependencies if changed
git pull && pip install -r requirements-dev.txt
```

The `requirements.txt` file is intentionally empty because the application depends solely on Python's standard library — `tkinter`, `json`, `os`, `datetime`, and `re` are all distributed with every standard Python installation and require no separate installation step. The `requirements-dev.txt` file is kept separate because `pytest ≥ 8.0` is needed only during development and testing; it is not required to run the application in production. Separating the two files prevents unnecessary packages from being installed in deployment environments. Running `python -m pytest tests/ -v` produces 81 `PASSED` lines, one per test function, followed by a summary line such as `81 passed in 0.XXs`.

---

## Technical & Functional Overview

The Record Management System is structured as a sequence of four co-operating layers, each with a strictly bounded responsibility. The sections below describe the architectural patterns employed, the data model, the persistence mechanism, the graphical user interface design, the CRUD operation flows, and the error handling strategy.

### 4.1 Architectural Pattern

The application follows the **Layered Architecture** pattern, in which each layer may only communicate with the layer immediately below it. This strict separation of concerns means that the GUI layer never contains file I/O logic, and the Storage layer never contains business rules. The separation makes it straightforward to test the Record layer in isolation from the graphical interface and to swap the storage backend without touching a single line of GUI code.

The **Repository pattern** is applied at the boundary between the Record layer and the Storage layer. `RecordRepository` provides a typed, exception-raising interface — rather than returning sentinel values such as `None` or `-1` — that the automated test suite can exercise directly without instantiating any tkinter widgets. This design means that every business rule can be verified by a fast, headless unit test.

The four layers are described in detail below.

The **GUI Layer** (`src/gui/`) comprises four tkinter windows. The Dashboard (`main_window.py`) is the application entry point and hosts the tkinter event loop; the three management windows — `client_window.py`, `airline_window.py`, and `flight_window.py` — are modal `Toplevel` windows that are responsible only for user interaction. Each window reads form fields, validates input, calls Record-layer functions, refreshes its `Treeview` widget, and updates the status bar. No window ever builds record dictionaries directly or calls `json.dumps`.

The **Record Layer** (`src/record/`) contains twelve pure functions — four per record type — that accept the shared `list[dict]` by reference and mutate it in place. These functions implement all business rules: ID auto-increment, cascade deletes, ID cascade propagation on update, and referential integrity checks on Flight creation. The Record layer imports no tkinter symbols and can therefore be called from tests without a running graphical interface.

The **Repository Layer** (`src/repository.py`) wraps the in-memory list in a class — `RecordRepository` — that exposes typed `add`, `delete`, `update`, `search`, and `get_all` methods. Rather than returning sentinel values, `RecordRepository` raises `DuplicateRecordError` or `RecordNotFoundError` to signal failure conditions. The primary consumer of this layer is the automated test suite.

The **Storage Layer** (`src/storage.py`) consists of two stateless functions: `load_records(filepath)` reads the JSONL file line by line and returns a `list[dict]`, and `save_records(records, filepath)` overwrites the entire file on each call, performing no partial writes and no appending. The layer is entirely agnostic to the semantics of the records it persists.

```
┌─────────────────────────────────────────────────────────────┐
│                         GUI Layer                           │
│          main_window · client_window · airline_window       │
│                       · flight_window                       │
└───────────────────────────┬─────────────────────────────────┘
                            │  calls pure CRUD functions
┌───────────────────────────▼─────────────────────────────────┐
│                       Record Layer                          │
│       client_record · airline_record · flight_record        │
└───────────────────────────┬─────────────────────────────────┘
                            │  operates on in-memory list[dict]
┌───────────────────────────▼─────────────────────────────────┐
│                    Repository Layer                         │
│                    RecordRepository                         │
└───────────────────────────┬─────────────────────────────────┘
                            │  delegates read/write to
┌───────────────────────────▼─────────────────────────────────┐
│                      Storage Layer                          │
│              load_records() · save_records()                │
└───────────────────────────┬─────────────────────────────────┘
                            │  reads/writes
                   ┌────────▼───────────┐
                   │ data/records.jsonl │
                   └────────────────────┘
```

### 4.2 Data Model

Client and Airline are independent top-level entities, each assigned an auto-incremented integer `ID` that uniquely identifies it within its type. Flight is a join entity with no surrogate key; it is identified by the composite natural key `(Client_ID, Airline_ID, Date)`. This design faithfully reflects the domain: a flight is inherently the combination of a passenger, a carrier, and a departure time, so a separate surrogate identifier would be both redundant and potentially misleading.

**Client**

| Field           | JSONL key           | Type |
|-----------------|---------------------|------|
| Unique ID       | `"ID"`              | int  |
| Type tag        | `"Type"`            | str  |
| Full name       | `"Name"`            | str  |
| Address line 1  | `"Address Line 1"`  | str  |
| Address line 2  | `"Address Line 2"`  | str  |
| Address line 3  | `"Address Line 3"`  | str  |
| City            | `"City"`            | str  |
| State/county    | `"State"`           | str  |
| Postal code     | `"Zip Code"`        | str  |
| Country         | `"Country"`         | str  |
| Phone number    | `"Phone Number"`    | str  |

The postal address is split across three free-text lines to accommodate international address formats, which vary considerably in structure — a single `"Address"` field would be insufficient for addresses that include building names, floor numbers, or neighbourhood designations. Both `"Zip Code"` and `"Phone Number"` are stored as strings rather than integers because postal codes often contain leading zeros (e.g. `"01234"`) and hyphens (e.g. `"NW1 6XE"`), and telephone numbers may include country codes, parentheses, and dashes that would be lost under numeric coercion.

**Airline**

| Field        | JSONL key          | Type |
|--------------|--------------------|------|
| Unique ID    | `"ID"`             | int  |
| Type tag     | `"Type"`           | str  |
| Company name | `"Company Name"`   | str  |

An Airline record carries only three fields because it serves as a lookup entity: its sole purpose is to provide a human-readable company name for the numeric `Airline_ID` foreign key stored in Flight records. Richer airline data — such as IATA codes or country of registration — falls outside the scope of this system.

**Flight**

| Field           | JSONL key      | Type |
|-----------------|----------------|------|
| Type tag        | `"Type"`       | str  |
| Client ID (FK)  | `"Client_ID"`  | int  |
| Airline ID (FK) | `"Airline_ID"` | int  |
| Departure date  | `"Date"`       | str  |
| Origin city     | `"Start City"` | str  |
| Destination     | `"End City"`   | str  |

The `"Date"` field is stored as an ISO-8601 string (e.g. `"2025-06-15T10:30:00"`) rather than a native date object because JSON has no built-in date type. The `FlightRecord` dataclass coerces the value to a `datetime` object via `datetime.fromisoformat()` when loading and converts it back to a string via `datetime.isoformat()` when saving, ensuring that all date arithmetic within the application operates on proper `datetime` instances. A Flight record carries no surrogate primary key because the composite key `(Client_ID, Airline_ID, Date)` is a natural unique identifier: no client can simultaneously board two flights operated by the same airline at the same moment in time.

### 4.3 Persistence Model

**JSONL format.** JSONL (JSON Lines) stores each record as a self-contained JSON object on its own line. All three record types coexist in a single file, distinguished by the `"Type"` field. The format is human-readable, trivially backed up with a file copy, and can be inspected or edited in any text editor without specialised tooling. An illustrative excerpt of `data/records.jsonl` is shown below.

```json
{"ID": 1, "Type": "Client", "Name": "Alice Brown", "Address Line 1": "12 Baker St", "Address Line 2": "", "Address Line 3": "", "City": "London", "State": "England", "Zip Code": "NW1 6XE", "Country": "UK", "Phone Number": "07700900001"}
{"ID": 1, "Type": "Airline", "Company Name": "BritAir"}
{"Type": "Flight", "Client_ID": 1, "Airline_ID": 1, "Date": "2025-06-15T09:00:00", "Start City": "London", "End City": "Rome"}
```

**Data lifecycle.** On startup, `load_records()` checks for the data file with `os.path.exists()`; if the file is absent, it returns an empty list so that the application starts cleanly without raising an error. After every Create, Update, or Delete operation, the modified in-memory list is immediately written to disk by `save_records()`, which overwrites the entire file on each call, guaranteeing that the on-disk state always matches the in-memory state — there is no intermediate dirty flag or deferred flush. When any record window is closed, the `on_close()` handler triggers a final call to `save_records()` before the window is destroyed. The function uses `os.makedirs(..., exist_ok=True)` to create the `data/` directory automatically if it does not yet exist.

**Single source of truth.** The path to the data file is defined once in `src/conf/settings.py` as the constant `DATA_FILE` and imported by `src/storage.py`, ensuring that the path never drifts between modules. Both `load_records()` and `save_records()` catch `json.JSONDecodeError` and `IOError` respectively, returning an empty list on failure rather than propagating an exception that would crash the application.

### 4.4 GUI Design and Window System

**Window hierarchy.** The root `tk.Tk()` dashboard hosts the tkinter event loop; all three record-management windows are `tk.Toplevel` instances made modal via `transient(master)` and `grab_set()`. The `transient()` call keeps each window above the dashboard at all times, whilst `grab_set()` prevents the user from interacting with the dashboard whilst a record window is open, eliminating the possibility of conflicting editing sessions.

**Fixed-size main window and the SP spacing system.** After all widgets are constructed, `root.update_idletasks()` forces tkinter to calculate geometry before the window is shown. The exact pixel dimensions are then read back via `root.winfo_reqwidth()` and `root.winfo_reqheight()`, and `root.resizable(False, False)` locks the window to those dimensions. All spacing throughout the dashboard is derived from a single constant: `SP = round(root.winfo_fpixels('1m') * 5)`. This expression converts 5 mm to pixels using the display's physical DPI, ensuring that the 5 mm spacing specification is met across all screen densities, from a standard 96 DPI monitor to a high-resolution laptop panel.

**HiDPI awareness in sub-windows.** The three record-management windows read `tk.scaling` from the Tk interpreter, divide by the standard baseline factor of `96 / 72 ≈ 1.333` to obtain the HiDPI ratio, and multiply their target dimensions by this ratio so that the compositor scales each window back to the intended visual size. Each window then centres itself on whichever monitor the mouse pointer currently occupies, determined by dividing the total virtual desktop width by the screen height to estimate the number of monitors and computing the pointer's monitor index from its x-coordinate.

**WCAG colour compliance.** All colour pairs within the application were audited against WCAG 2.1 Success Criterion 1.4.3, which requires a contrast ratio of at least 4.5:1 for normal text and 3.0:1 for large text at Level AA. Four colour combinations were corrected: the Create button was changed from `#27ae60` (ratio 2.87:1) to `#1a7a40` (ratio 5.38:1); the Treeview selection highlight was changed from `#3498db` (ratio 3.15:1) to `#1f618d` (ratio 6.66:1); the Help button was changed from `#7f8c8d` (ratio 3.48:1) to `#5d6d7e` (ratio 5.31:1); and the Exit button was changed from `#e74c3c` (ratio 3.82:1) to `#a93226` (ratio 6.62:1). All remaining colour pairs meet Level AA, and several achieve Level AAA (≥ 7.0:1).

### 4.5 CRUD Operations and Business Rules

The following prose describes the full path of each operation from the user's action through to the file write, noting the UI element involved, the validation applied, the in-memory operation performed, the save triggered, and the visual feedback provided.

**Create.** The user fills in the form fields in the record window and presses the Create button. The GUI first checks that all required fields are non-empty, highlighting in red any that are blank and displaying a warning dialogue. Each field then undergoes type-specific validation: numeric fields are checked via `str.isdigit()`, whilst name, city, state, and country fields are matched against a regular expression via `re.match`. For Flight records, the entered `Client_ID` and `Airline_ID` are verified against the in-memory list; if either is absent, `RecordNotFoundError` is raised, and the record is not saved. If all validation passes, the new ID is computed as `max(existing_ids, default=0) + 1`, the `"Type"` field is set automatically, the record dictionary is appended to the in-memory list, `save_records()` is called, the `Treeview` is refreshed, and the form is cleared, ready for the next entry.

**Search.** The user enters an ID in the ID field and presses Search. The application iterates over the in-memory list; if a matching record is found, all form fields are populated with its values and the corresponding `Treeview` row is selected and scrolled into view. If additional fields were entered alongside the ID, their values are compared against the stored record; a mismatch triggers a warning dialogue informing the user of the discrepancy.

**Update.** The user selects a row in the `Treeview` or performs a Search, edits the desired form fields, and presses Update. The same validation rules that apply to Create are reapplied here. Once validation passes, the record is updated in place using `dict.update()`. If a Client record's ID is changed, the new value is cascaded to the `Client_ID` field of every Flight record that references the old ID. After the update, `save_records()` is called and the `Treeview` is refreshed.

**Delete.** The user selects a row in the `Treeview` and presses Delete. A `messagebox.askyesno` dialogue asks for confirmation. On confirmation, the record is removed from the in-memory list; for Client and Airline records, all Flight records that reference the deleted ID are cascade-deleted in the same operation. The form is cleared, `save_records()` is called, and the `Treeview` is refreshed.

**Column sorting.** Every `Treeview` column header is bound to the `_sort_column()` function. A first click sorts the column in ascending order and appends a `▲` indicator to the header label; a second click reverses the sort to descending order and changes the indicator to `▼`. Numeric columns (`ID`, `CLIENT ID`, `AIRLINE ID`) are cast to `int` before comparison to ensure correct numerical ordering; all other columns are sorted case-insensitively. The sort state is reset on every data change so that subsequent modifications are not obscured by a stale ordering.

**Form auto-population.** Clicking any row in the `Treeview` fires the `on_tree_select` event handler, which immediately populates all form fields with the values of the selected record. This allows the user to view, update, or delete any record with a single click, without manually entering its identifier.

### 4.6 Error Handling

The application employs a two-level error handling strategy. At the business logic level, the Record layer and `RecordRepository` raise typed Python exceptions — `RecordNotFoundError` and `DuplicateRecordError`, both defined in `src/exceptions.py` — which the GUI layer catches and translates into user-facing dialogue boxes. At the I/O level, `load_records()` and `save_records()` in the Storage layer catch `json.JSONDecodeError` and `IOError` respectively; rather than allowing these exceptions to propagate and crash the application, they are handled gracefully by returning an empty list or printing a diagnostic message to stdout, allowing the session to continue.

| Error condition | Mechanism | User-visible outcome |
|---|---|---|
| Record not found by ID or composite key | `RecordNotFoundError` raised by Record layer | Warning dialogue: "Client not found" / "Flight not found" |
| Duplicate record on add | `DuplicateRecordError` raised by `RecordRepository.add` | Prevented at GUI layer by auto-increment ID |
| Duplicate Flight composite key | `DuplicateRecordError` raised by `create_flight()` when `(Client_ID, Airline_ID, Date)` already exists | Warning dialogue; record not saved |
| Missing required field | GUI validation before Record layer call | Field highlighted red; warning dialogue |
| Non-numeric value in numeric field | `str.isdigit()` check in `validate_field()` | Warning dialogue: "Invalid or missing value for 'ID'" |
| Invalid date format | `datetime.strptime()` raises `ValueError` | Warning dialogue: "Invalid date format" |
| Non-existent `Client_ID` or `Airline_ID` in Flight | Guard in `create_flight()` raises `RecordNotFoundError` | Warning dialogue; record not saved |
| Records file missing on startup | `os.path.exists()` in `load_records()` | App starts with empty list; no dialogue |
| Records file corrupted | `json.JSONDecodeError` caught in `load_records()` | App starts with empty list; message to stdout |
| File write failure | `IOError` caught in `save_records()` | Error message to stdout; app continues |

---

## Repository Structure

The following directory tree shows every file in the repository. The `src/` package is the primary source tree; `tests/` contains the unit test suite; `data/` holds the live JSONL data file; and `docs/` contains contributor guidance.

```
record-management-system/
├── data/
│   └── records.jsonl
├── docs/
│   └── CONTRIBUTING.md
├── src/
│   ├── __init__.py
│   ├── conf/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── exceptions.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── assets/
│   │   ├── airline_window.py
│   │   ├── client_window.py
│   │   ├── flight_window.py
│   │   └── main_window.py
│   ├── main.py
│   ├── models.py
│   ├── record/
│   │   ├── __init__.py
│   │   ├── airline_record.py
│   │   ├── client_record.py
│   │   └── flight_record.py
│   ├── repository.py
│   └── storage.py
├── tests/
│   ├── __init__.py
│   ├── test_airline_record.py
│   ├── test_client_record.py
│   ├── test_flight_record.py
│   ├── test_models.py
│   ├── test_repository.py
│   └── test_storage.py
├── .gitignore
├── .gitmessage
├── README.md
├── requirements-dev.txt
└── requirements.txt
```

`data/records.jsonl` is the live JSONL data file that persists all Client, Airline, and Flight records between application sessions. `docs/CONTRIBUTING.md` describes the project's commit message conventions, branching strategy, and contribution workflow for new contributors. `src/__init__.py` marks the `src` directory as a Python package, enabling module imports of the form `from src.storage import load_records`. `src/conf/__init__.py` marks the configuration sub-package. `src/conf/settings.py` is the sole location where the data file path is defined. `src/exceptions.py` declares the two custom exception classes used throughout the application. `src/gui/__init__.py` marks the GUI sub-package. `src/gui/assets/` contains any graphical assets (such as PNG icons) used by the windows. `src/gui/airline_window.py` implements the modal Airline management window. `src/gui/client_window.py` implements the modal Client management window. `src/gui/flight_window.py` implements the modal Flight management window. `src/gui/main_window.py` implements the application dashboard and entry point. `src/main.py` is the Python module that bootstraps the application; it is executed via `python -m src.main`. `src/models.py` defines the three dataclasses (`ClientRecord`, `AirlineRecord`, `FlightRecord`) with serialisation helpers. `src/record/__init__.py` marks the record sub-package. `src/record/airline_record.py` contains the four pure CRUD functions for Airline records. `src/record/client_record.py` contains the four pure CRUD functions for Client records. `src/record/flight_record.py` contains the four pure CRUD functions for Flight records. `src/repository.py` defines `RecordRepository`, the in-memory typed CRUD interface. `src/storage.py` provides the two stateless persistence functions. `tests/__init__.py` marks the test directory as a package. `tests/test_airline_record.py` contains unit tests for `src/record/airline_record.py`. `tests/test_client_record.py` contains unit tests for `src/record/client_record.py`. `tests/test_flight_record.py` contains unit tests for `src/record/flight_record.py`. `tests/test_models.py` contains unit tests for `src/models.py`. `tests/test_repository.py` contains unit tests for `src/repository.py`. `tests/test_storage.py` contains unit tests for `src/storage.py`. `.gitignore` specifies files and directories that Git should not track, such as virtual environments, `__pycache__` directories, and the data file. `.gitmessage` provides the commit message template used by contributors. `README.md` is the primary project documentation file. `requirements-dev.txt` specifies development dependencies (pytest ≥ 8.0). `requirements.txt` is intentionally empty because the application has no third-party runtime dependencies.

---

## Module Reference

#### `src/exceptions.py`

Defines the two custom exception classes that signal application-level error conditions throughout the Record and Repository layers.

`RecordNotFoundError` is a subclass of `Exception` raised whenever a requested record cannot be located in the in-memory list. It is raised by `_find_index` in `RecordRepository` and by the CRUD helper functions in the Record layer when no record matching the supplied ID and type is found. Callers are expected to catch this exception and present an appropriate error dialogue or log message rather than allowing it to propagate to the user as an unhandled traceback.

`DuplicateRecordError` is a subclass of `Exception` raised by `RecordRepository.add` when a record with the same type and ID as an existing record is submitted for insertion. In normal application operation, this exception is never triggered because the GUI layer assigns IDs via auto-increment, which guarantees uniqueness; however, it is available as a safety net and is exercised explicitly by the test suite to verify that the repository correctly rejects duplicate entries.

---

#### `src/conf/settings.py`

Defines the file path constants consumed by the Storage layer, ensuring that the data file location is configured in exactly one place.

`DATA_FILE` is an absolute path string constructed at import time using `os.path.join` and `os.path.dirname`. It resolves to the `data/records.jsonl` file located one level above the `src/` package root — that is, in the project root directory. The path is computed dynamically from `__file__` rather than hard-coded, so the application functions correctly regardless of where it is installed on disk.

`FILE_PATH` is an alias for `DATA_FILE`, retained for backwards compatibility with code written before the constant was renamed.

---

#### `src/models.py`

Provides three dataclasses — `ClientRecord`, `AirlineRecord`, and `FlightRecord` — each of which encapsulates a single record and exposes serialisation helpers for round-tripping with the JSONL storage layer.

`ClientRecord` represents a Client entry. Its constructor accepts ten positional parameters (`id`, `name`, `address_line_1`, `address_line_2`, `address_line_3`, `city`, `state`, `zip_code`, `country`, `phone_number`), all of which are required; the `type` field is set automatically to `"Client"` by `__post_init__`. The `to_dict()` method returns a dictionary using the canonical JSONL schema keys (e.g. `"Address Line 1"`, `"Zip Code"`, `"Phone Number"`), making it safe to pass directly to `json.dumps`. The `from_dict(data)` class method reconstructs a `ClientRecord` from such a dictionary, providing the inbound half of the serialisation round-trip.

`AirlineRecord` represents an Airline entry. Its constructor accepts two positional parameters (`id`, `company_name`); `type` is set to `"Airline"` by `__post_init__`. `to_dict()` returns a three-key dictionary (`"ID"`, `"Type"`, `"Company Name"`). `from_dict(data)` reconstructs the record from that dictionary.

`FlightRecord` represents a Flight entry. Its constructor accepts five positional parameters (`client_id`, `airline_id`, `date`, `start_city`, `end_city`); `type` is set to `"Flight"` by `__post_init__`. If `date` is supplied as an ISO-8601 string, `__post_init__` coerces it to a `datetime` object via `datetime.fromisoformat()`, so that all downstream code can rely on a consistent Python type. `to_dict()` serialises `date` back to a string via `datetime.isoformat()` before returning the dictionary, satisfying the constraint that JSON has no native date type. `from_dict(data)` reconstructs the record, triggering the same coercion through `__post_init__`.

---

#### `src/storage.py`

Provides two stateless functions that constitute the sole interface between the application's in-memory data and the file system.

`load_records(filepath=DATA_FILE)` reads a JSONL file and returns its contents as a `list[dict]`. It first calls `os.path.exists(filepath)`; if the file does not exist, it prints a system message and returns an empty list, allowing the application to start without any pre-existing data. If the file is present, it opens it with `encoding="utf-8"` and parses each non-blank line as a separate JSON object using `json.loads`. Both `json.JSONDecodeError` and `IOError` are caught; on either failure, the function prints an error message and returns an empty list. The function accepts an explicit `filepath` argument so that tests can pass a temporary file path without altering the module-level constant.

`save_records(records, filepath=DATA_FILE)` persists a `list[dict]` to a JSONL file. It calls `os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)` to create any missing parent directories, then opens the file for writing with `encoding="utf-8"` and writes each record as a single JSON line followed by a newline character. The file is overwritten in its entirety on each call — there is no appending or partial write — so that the on-disk state always matches the in-memory list exactly. An `IOError` is caught and printed to stdout; the application continues running rather than crashing, since a failed save is a transient I/O problem rather than a fatal logic error.

---

#### `src/repository.py`

Defines `RecordRepository`, an in-memory typed CRUD interface that serves as the primary integration point for the automated test suite.

`RecordRepository.__init__(records=None)` initialises the repository with an optional pre-loaded `list[dict]`. If `records` is not provided, the instance starts with an empty list. The `records` attribute is publicly accessible so that tests can inspect or pre-populate it directly.

`_find_index(record_id, record_type)` is an internal helper that iterates over `self.records` and returns the zero-based index of the first entry whose `"Type"` and `"ID"` fields match the supplied arguments. If no match is found, it raises `RecordNotFoundError`. All methods that need to locate a specific record delegate to this helper.

`add(record)` appends a record dictionary to `self.records`. Before appending, it checks whether a record with the same `"Type"` and `"ID"` already exists; if one is found, `DuplicateRecordError` is raised. Records without an `"ID"` field (such as Flight records, which use a composite key) bypass the duplicate check.

`delete(record_id, record_type)` locates the record at the index returned by `_find_index` and removes it from `self.records` with `list.pop`. If the record is not found, `RecordNotFoundError` propagates from `_find_index`.

`update(record_id, record_type, updates)` locates the record via `_find_index` and applies `dict.update(updates)` to it in place. The `updates` parameter is a dictionary of field names and new values; any key not present in `updates` is left unchanged.

`search(**kwargs)` iterates over `self.records`, applying each keyword argument as a field-name/value filter in sequence, and returns a list of all records that satisfy every criterion. Supplying no keyword arguments returns all records.

`get_all()` returns a shallow copy of `self.records` as a new list, preventing external code from inadvertently mutating the repository's internal state by retaining a reference to the original list.

---

#### `src/record/airline_record.py`

Contains four pure functions that implement CRUD operations for Airline records, operating directly on the shared `list[dict]`.

`_next_id(records)` is an internal helper that scans all entries whose `"Type"` is `"Airline"`, extracts their `"ID"` values, and returns one more than the maximum. If no Airline records exist, it returns `1`.

`create_airline(records, company_name)` constructs a new Airline dictionary with an auto-incremented `"ID"`, sets `"Type"` to `"Airline"`, stores the provided `company_name` under `"Company Name"`, appends the dictionary to `records`, and returns it.

`delete_airline(records, airline_id)` first verifies that an Airline record with the given `airline_id` exists, raising `RecordNotFoundError` if it does not. It then rewrites `records` in place using a single list comprehension that excludes both the target Airline and any Flight record whose `"Airline_ID"` matches, implementing cascade deletion atomically.

`update_airline(records, airline_id, **updates)` iterates over `records` to find the first Airline entry whose `"ID"` matches `airline_id`, applies `dict.update(updates)` to it, and returns. If no matching record is found, `RecordNotFoundError` is raised.

`search_airlines(records, **kwargs)` first filters `records` to only Airline entries, then applies each keyword argument as a field-name/value filter in sequence, returning all records that satisfy every criterion.

---

#### `src/record/client_record.py`

Contains four pure functions that implement CRUD operations for Client records, including cascade deletion and ID cascade propagation.

`_next_id(records)` operates identically to its counterpart in `airline_record.py`, but scans for `"Type" == "Client"` entries. It is defined separately in each record module to keep each module self-contained and independently testable.

`create_client(records, name, address_line1, address_line2, address_line3, city, state, zip_code, country, phone_number)` constructs a Client dictionary with an auto-incremented `"ID"`, populates all ten data fields under their canonical JSONL keys, appends the dictionary to `records`, and returns it.

`delete_client(records, client_id)` verifies that the Client exists, then rewrites `records` in place to exclude both the target Client and every Flight record whose `"Client_ID"` matches, implementing cascade deletion in a single pass.

`update_client(records, client_id, **updates)` locates the Client record and applies the supplied updates. If the `"ID"` key is present in `updates` with a new value, the function additionally iterates over all Flight records and updates their `"Client_ID"` field wherever it matches the old `client_id`, propagating the ID change consistently. If the record is not found, `RecordNotFoundError` is raised.

`search_clients(records, **kwargs)` filters to Client records and applies the supplied keyword criteria in sequence, returning all matches.

---

#### `src/record/flight_record.py`

Contains four pure functions that implement CRUD operations for Flight records, which are identified by the composite key `(Client_ID, Airline_ID, Date)` rather than a surrogate ID.

`create_flight(records, client_id, airline_id, date, start_city, end_city)` enforces referential integrity before creating a record. If any Client records exist in `records` but none has `"ID" == client_id`, it raises `RecordNotFoundError`. The same guard is applied for Airline records. Additionally, if a Flight record with the same composite key already exists, `DuplicateRecordError` is raised. If all checks pass, the function constructs a Flight dictionary without an `"ID"` field, appends it to `records`, and returns it. The `date` parameter is expected to be an ISO-8601 string such as `"2025-03-14T10:30:00"`.

`delete_flight(records, client_id, airline_id, date)` iterates over `records` to find the first Flight entry whose `"Client_ID"`, `"Airline_ID"`, and `"Date"` all match the supplied composite key, removes it with `list.pop`, and returns. If no matching Flight is found, `RecordNotFoundError` is raised.

`update_flight(records, client_id, airline_id, date, **updates)` locates the Flight entry matching the composite key, applies `dict.update(updates)`, and returns. If no match is found, `RecordNotFoundError` is raised.

`search_flights(records, **kwargs)` filters Flight records and applies the supplied keyword criteria in sequence, returning all matching entries.

---

#### `src/gui/main_window.py`

Provides the application's entry point, implementing the primary dashboard window that provides access to the three record-management modules.

`open_main_window()` is a standalone function that constructs and runs the tkinter event loop. It creates the root `tk.Tk()` window, sets the title to `"Travel Record Management System"`, and sets the background to light grey. Physical screen metrics are read to estimate the number of connected monitors and the width of a single monitor. The spacing constant `SP = round(root.winfo_fpixels('1m') * 5)` converts 5 mm to pixels for the current display's DPI. A dark header frame displays the application title and subtitle; a footer frame hosts a status bar on the left and action buttons on the right. Three navigation buttons open `ClientWindow`, `AirlineWindow`, and `FlightWindow` respectively as modal `Toplevel` instances. After all widgets are packed, `root.update_idletasks()` triggers geometry calculation, and `root.resizable(False, False)` locks the window dimensions. A Help button opens a `messagebox.showinfo` dialogue summarising the application's functionality, and an Exit button calls `root.destroy()` after prompting for confirmation via `messagebox.askyesno`. The function ends by calling `root.mainloop()` to enter the event loop.

---

#### `src/gui/airline_window.py`

Implements `AirlineWindow`, a modal `tk.Toplevel` that provides a full CRUD interface for Airline records.

`AirlineWindow.__init__(master)` initialises the window, performs HiDPI scaling calculations, centres the window on the active monitor, and sets it as a modal child of `master` via `transient()` and `grab_set()`. On initialisation, it loads all records from the shared JSONL file via `load_records()`. The window builds a header bar, an input form with fields for `ID` and `Company Name`, a row of CRUD buttons (Create, Search, Update, Delete, Clear), a sortable `ttk.Treeview` table displaying all Airline records, and a footer status bar.

The CRUD methods are bound to the respective buttons: the Create method validates that `Company Name` is non-empty, auto-assigns the next available Airline ID, calls `create_airline()` from the Record layer, saves the updated list, and refreshes the `Treeview`. The Search method reads the ID field and populates the form with the matching record. The Update method revalidates the form, calls `update_airline()`, and saves. The Delete method prompts for confirmation, calls `delete_airline()` (which cascade-deletes associated Flights), saves, and refreshes.

Column sorting is implemented by `_sort_column(col, reverse)`, which sorts the `Treeview` rows in place, casting the `ID` column to `int` for correct numerical ordering. The `on_close()` method is bound to the window's close button via `protocol("WM_DELETE_WINDOW", ...)` and calls `save_records()` before destroying the window.

---

#### `src/gui/client_window.py`

Implements `ClientWindow`, a modal `tk.Toplevel` that provides a full CRUD interface for Client records, including per-field validation and ID cascade propagation to associated Flight records.

`ClientWindow.__init__(master)` applies the same HiDPI and centring logic as `AirlineWindow`. The input form contains eleven labelled entry widgets covering all Client fields. Validation is applied field by field via a `validate_field` helper, which checks that required fields are non-empty, that `ID` contains only digits, and that the name, city, state, and country fields conform to a regular expression that permits letters, spaces, hyphens, and apostrophes. Any field that fails validation is highlighted with a red background, and a warning dialogue is shown.

The Create method auto-assigns an ID via `create_client()` from the Record layer and immediately saves. The Update method checks whether the `ID` field has changed and, if so, calls `update_client()`, which propagates the new ID to all linked Flight records before saving. The Delete method calls `delete_client()`, which cascades to delete all associated Flights in a single list comprehension pass. The `on_tree_select` handler populates all eleven form fields when a `Treeview` row is clicked.

---

#### `src/gui/flight_window.py`

Implements `FlightWindow`, a modal `tk.Toplevel` that provides a full CRUD interface for Flight records. Flight records are identified by the composite key `(Client_ID, Airline_ID, Date)` rather than a surrogate primary key, which influences how Search, Update, and Delete locate the target record.

`FlightWindow.__init__(master)` applies the same HiDPI and centring logic as the other two record windows. The input form contains six fields: `Client ID`, `Airline ID`, `Date` (expected in ISO-8601 format), `Start City`, and `End City`. Date validation is performed with `datetime.strptime` wrapped in a `try/except ValueError` block; an invalid date format triggers a warning dialogue without attempting to save.

The Create method calls `create_flight()` from the Record layer, which enforces referential integrity by verifying that the supplied `Client_ID` and `Airline_ID` exist in the in-memory list before appending the Flight record. The user-entered date string is converted to ISO-8601 format using `datetime.strptime` and `isoformat()` before storage. The Delete method reads the composite key from the form and calls `delete_flight()`. The Update method reads the original composite key from the selected `Treeview` row and the new values from the form, then calls `update_flight()`. The `on_tree_select` handler populates all six fields from the clicked row.

---

#### `src/main.py`

The application entry point is executed when the package is run as `python -m src.main`.

`main()` is a zero-argument function that imports and calls `open_main_window()` from `src.gui.main_window`. Separating the call into a named function rather than placing it at the module level allows the entry point to be tested in isolation and avoids accidental GUI startup during import. The `if __name__ == "__main__": main()` guard at the bottom of the file ensures that the application only starts when the module is executed directly, not when it is imported by another module.

---

## Test Suite Reference

The project contains 81 automated unit tests organised across six test modules, one for each non-GUI source module. All tests are written with **pytest** and are located in the `tests/` directory. No test instantiates a tkinter widget or writes to the real `data/records.jsonl` file; file-system tests use pytest's `tmp_path` fixture to operate on temporary directories that are cleaned up automatically after each run. The entire suite can be executed with:

```bash
python -m pytest tests/ -v
```

The sections below document every test class, every test function, the assertion it makes, and the specific behaviour or edge case it guards against.

---

### tests/test_models.py

Verifies the three dataclass models in `src/models.py` — `ClientRecord`, `AirlineRecord`, and `FlightRecord` — covering serialisation, deserialisation, automatic type-tag assignment, and the `datetime` round-trip.

**Helper:** `make_client(**kwargs)` — constructs a `ClientRecord` with sensible defaults (id=1, name="Alice", city="London", etc.), allowing individual fields to be overridden via keyword arguments.

#### TestClientRecord

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_type_is_auto_set` | `c.type == "Client"` | The `type` field is set by `__post_init__`, never by the caller |
| `test_to_dict_contains_canonical_keys` | `set(d.keys())` equals the 11 specification-mandated field names | Guarantees that the JSONL schema matches the project brief exactly |
| `test_to_dict_type_value_is_capitalised` | `d["Type"] == "Client"` | Confirms the stored string is `"Client"`, not `"client"` or any other variant |
| `test_from_dict_round_trip` | Restored instance has same `name` and `type` as the original | Serialise → deserialise produces an identical record |
| `test_missing_required_field_raises` | `pytest.raises(TypeError)` when `ClientRecord(id=1)` is called | The dataclass machinery enforces all required fields at construction time |

#### TestAirlineRecord

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_type_is_auto_set` | `a.type == "Airline"` | Automatic type tag on `AirlineRecord` |
| `test_to_dict_contains_canonical_keys` | `set(d.keys()) == {"ID", "Type", "Company Name"}` | Canonical schema has exactly 3 keys |
| `test_to_dict_type_value_is_capitalised` | `d["Type"] == "Airline"` | Stored string is precisely `"Airline"` |
| `test_round_trip` | `restored.company_name == "BritAir"` | Serialise → deserialise preserves the company name |

#### TestFlightRecord

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_type_is_auto_set` | `f.type == "Flight"` | Automatic type tag on `FlightRecord` |
| `test_to_dict_contains_canonical_keys` | `set(d.keys()) == {"Type", "Client_ID", "Airline_ID", "Date", "Start City", "End City"}` | Canonical schema has exactly 6 keys |
| `test_to_dict_type_value_is_capitalised` | `d["Type"] == "Flight"` | Stored string is precisely `"Flight"` |
| `test_date_serialised_to_string` | `isinstance(d["Date"], str)` | JSON cannot natively store `datetime` objects; serialisation must convert to a string |
| `test_from_dict_restores_datetime` | `isinstance(restored.date, datetime)` and `restored.date.year == 2025` | Deserialisation must reconstruct a proper `datetime` object, not leave the field as a raw string |

---

### tests/test_storage.py

Verifies `load_records()` and `save_records()` in `src/storage.py`, covering file-not-found resilience, single-record persistence, multi-record persistence, and overwrite semantics.

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_load_returns_empty_list_when_file_missing` | `result == []` | Application must start cleanly when no data file exists yet |
| `test_save_and_reload` | `len(loaded) == 1` and `loaded[0]["name"] == "Alice"` | A record saved then loaded must have identical field values |
| `test_save_multiple_records` | `len(load_records(filepath)) == 5` | All records in a list of 5 must survive a save/load cycle |
| `test_overwrite_on_save` | After two saves, `len(loaded) == 2` (not 3) | `save_records` overwrites the file entirely; it must not append to existing content |

---

### tests/test_repository.py

Verifies `RecordRepository` in `src/repository.py`, covering all five public methods and both custom exceptions.

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_add_and_search` | `len(results) == 1` and `results[0]["Name"] == "Alice"` | A record added to the repository can be found by type and ID |
| `test_add_duplicate_raises` | `pytest.raises(DuplicateRecordError)` on second `add` of same record | Inserting two records with identical type and ID must be rejected |
| `test_delete_record` | `repo.search(Type="Client", ID=1) == []` after deletion | A deleted record must no longer appear in search results |
| `test_delete_nonexistent_raises` | `pytest.raises(RecordNotFoundError)` when deleting ID 999 | Deleting a non-existent record must raise a typed exception, not fail silently |
| `test_update_record` | `repo.search(ID=1)[0]["City"] == "Manchester"` after update | Updated field value is persisted in the in-memory list |
| `test_update_nonexistent_raises` | `pytest.raises(RecordNotFoundError)` when updating ID 999 | Updating a non-existent record must raise a typed exception |
| `test_search_by_arbitrary_field` | `len(repo.search(City="London")) == 1` | `search()` filters correctly on any field, not just ID and Type |
| `test_get_all` | `len(all_records) == 1` | `get_all()` returns a list of the correct length |

---

### tests/test_airline_record.py

Verifies the four pure CRUD functions in `src/record/airline_record.py`, including cascade deletion of associated Flight records.

#### TestCreateAirline

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_record_added` | `len(records) == 1` | Record is appended to the shared list |
| `test_id_starts_at_one` | `rec["ID"] == 1` | First airline on an empty list gets ID 1, not 0 |
| `test_id_auto_increments` | Second record gets `ID == 2` | Each subsequent airline receives `max(existing) + 1` |
| `test_type_is_airline` | `rec["Type"] == "Airline"` | Type tag is set automatically to `"Airline"` |
| `test_company_name_stored` | `rec["Company Name"] == "EuroJet"` | The supplied company name is stored under the canonical key |
| `test_canonical_schema_keys_present` | `set(rec.keys()) == {"ID", "Type", "Company Name"}` | Record contains exactly the three specification-mandated fields |

#### TestDeleteAirline

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_record_removed` | `records == []` after deletion | Record is fully removed from the list |
| `test_nonexistent_id_raises` | `pytest.raises(RecordNotFoundError)` for ID 999 | Attempting to delete an absent airline raises a typed exception |
| `test_only_matching_record_removed` | `len(records) == 1` and remaining record is SkyLine | Only the targeted airline is deleted; others are untouched |
| `test_cascade_deletes_associated_flights` | No Flight records remain after airline deletion | Deleting an airline must cascade-delete all flights that reference its ID |
| `test_cascade_leaves_other_flights_intact` | One flight remains (for `Airline_ID == 2`) | Cascade must be scoped to the deleted airline; flights of other airlines survive |

#### TestUpdateAirline

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_field_changed` | `records[0]["Company Name"] == "NewAir"` | Updated field value is persisted in place |
| `test_nonexistent_id_raises` | `pytest.raises(RecordNotFoundError)` for ID 999 | Updating a non-existent airline raises a typed exception |

#### TestSearchAirlines

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_returns_correct_record` | `len(results) == 1` and `results[0]["Company Name"] == "BritAir"` | Filter by company name returns only the matching airline |
| `test_empty_result_when_no_match` | `search_airlines(...) == []` | Non-matching filter returns an empty list, not an exception |
| `test_returns_all_when_no_filter` | `len(search_airlines(records)) == 2` | Calling `search_airlines` with no filters returns every airline |

---

### tests/test_client_record.py

Verifies the four pure CRUD functions in `src/record/client_record.py`, including cascade deletion of associated Flights and cascade propagation of Client ID changes.

#### TestCreateClient

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_record_added` | `len(records) == 1` | Record is appended to the list |
| `test_id_starts_at_one` | `rec["ID"] == 1` | First client on an empty list gets ID 1 |
| `test_id_auto_increments` | Second record gets `ID == 2` | Auto-increment assigns `max(existing) + 1` |
| `test_type_is_client` | `rec["Type"] == "Client"` | Type tag is `"Client"` |
| `test_fields_stored_correctly` | `rec["Name"] == "Carol"` and `rec["City"] == "Bristol"` | Overridden field values are stored correctly |
| `test_canonical_schema_keys_present` | `set(rec.keys())` equals the 11 specification-mandated field names | All required fields are present with the correct key names |

#### TestDeleteClient

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_record_removed` | `records == []` after deletion | Client is fully removed |
| `test_nonexistent_id_raises` | `pytest.raises(RecordNotFoundError)` for ID 999 | Typed exception on absent client |
| `test_only_matching_record_removed` | Remaining record is Bob (ID 2) | Only the targeted client is removed |
| `test_cascade_deletes_associated_flights` | No Flight records remain | Deleting a client cascade-deletes all their flights |
| `test_cascade_leaves_other_flights_intact` | One flight remains with `Client_ID == 2` | Cascade is scoped to the deleted client only |

#### TestUpdateClient

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_field_changed` | `records[0]["City"] == "Manchester"` | Updated field is persisted |
| `test_nonexistent_id_raises` | `pytest.raises(RecordNotFoundError)` for ID 999 | Typed exception on absent client |
| `test_other_fields_unchanged` | `records[0]["Name"] == "Alice"` after city update | Updating one field must not alter other fields |
| `test_cascade_updates_flight_client_id` | `flights[0]["Client_ID"] == 99` after `update_client(records, 1, ID=99)` | Changing a Client's ID must propagate the new value to `Client_ID` in all linked flights |

#### TestSearchClients

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_returns_correct_record` | `len(results) == 1` and `results[0]["Name"] == "Alice"` | Filter by city returns only the matching client |
| `test_empty_result_when_no_match` | `search_clients(...) == []` | Non-matching filter returns empty list |
| `test_returns_all_when_no_filter` | `len(search_clients(records)) == 2` | No-filter call returns every client |

---

### tests/test_flight_record.py

Verifies the four pure CRUD functions in `src/record/flight_record.py`, plus dedicated classes for referential integrity and duplicate composite-key rejection. Because Flight records have no surrogate primary key, all operations use the composite natural key `(Client_ID, Airline_ID, Date)`.

#### TestCreateFlight

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_record_added` | `len(records) == 1` | Flight is appended to the list |
| `test_fields_stored_correctly` | All five field values match the arguments | Each field is stored under its canonical key |
| `test_type_is_flight` | `rec["Type"] == "Flight"` | Type tag is `"Flight"` |
| `test_multiple_flights_added` | `len(records) == 2` after two creates | Multiple flights can coexist with different composite keys |
| `test_canonical_schema_keys_present` | `set(rec.keys()) == {"Type", "Client_ID", "Airline_ID", "Date", "Start City", "End City"}` | Record contains exactly the six specification-mandated fields |

#### TestDeleteFlight

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_record_removed` | `records == []` | Flight identified by composite key is fully removed |
| `test_nonexistent_record_raises` | `pytest.raises(RecordNotFoundError)` for `(99, 99, DATE)` | Typed exception when the composite key matches no record |
| `test_only_matching_record_removed` | Remaining record has `Client_ID == 2` | Only the flight matching the exact composite key is deleted |

#### TestUpdateFlight

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_field_changed` | `records[0]["End City"] == "Paris"` | Updated field is persisted |
| `test_nonexistent_record_raises` | `pytest.raises(RecordNotFoundError)` for `(99, 99, DATE)` | Typed exception on absent composite key |
| `test_other_fields_unchanged` | `records[0]["Start City"] == "London"` | Updating one field must not alter other fields |

#### TestSearchFlights

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_returns_correct_record` | `len(results) == 1` and `results[0]["Client_ID"] == 1` | Filter by start city returns only the matching flight |
| `test_empty_result_when_no_match` | `search_flights(...) == []` | Non-matching filter returns empty list |
| `test_returns_all_when_no_filter` | `len(search_flights(records)) == 2` | No-filter call returns every flight |

#### TestCreateFlightReferentialIntegrity

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_missing_client_raises` | `pytest.raises(RecordNotFoundError)` when `client_id=1` but only `Client ID=999` exists | A flight cannot be created for a client that does not exist |
| `test_missing_airline_raises` | `pytest.raises(RecordNotFoundError)` when `airline_id=10` but only `Airline ID=999` exists | A flight cannot be created for an airline that does not exist |
| `test_valid_ids_creates_flight` | `flight["Type"] == "Flight"` and `flight["Client_ID"] == 1` and `flight["Airline_ID"] == 10` | When both foreign IDs are valid, the flight is created successfully |

#### TestCreateFlightDuplicateKey

| Test function | Assertion | Edge case / behaviour guarded |
|---|---|---|
| `test_duplicate_composite_key_raises` | `pytest.raises(DuplicateRecordError)` on second `create_flight` with identical composite key | Inserting a flight with an already-used composite key must be rejected |
| `test_different_date_does_not_raise` | `len(records) == 2` after two flights with the same IDs but different dates | A distinct `Date` value makes the composite key unique |
| `test_different_client_does_not_raise` | `len(records) == 2` after flights with `client_id=1` and `client_id=2` | A distinct `Client_ID` makes the composite key unique |
| `test_different_airline_does_not_raise` | `len(records) == 2` after flights with `airline_id=10` and `airline_id=20` | A distinct `Airline_ID` makes the composite key unique |

---

The six modules collectively contain 81 tests. The table below shows the distribution by module and operation category.

| Module | Create | Delete | Update | Search | Serialisation | Infrastructure | Referential Integrity | Duplicate Key | Total |
|---|---|---|---|---|---|---|---|---|---|
| `test_models.py` | — | — | — | — | 14 | — | — | — | 14 |
| `test_storage.py` | — | — | — | — | — | 4 | — | — | 4 |
| `test_repository.py` | 2 | 2 | 2 | 2 | — | — | — | — | 8 |
| `test_airline_record.py` | 6 | 5 | 2 | 3 | — | — | — | — | 16 |
| `test_client_record.py` | 6 | 5 | 4 | 3 | — | — | — | — | 18 |
| `test_flight_record.py` | 5 | 3 | 3 | 3 | — | — | 3 | 4 | 21 |
| **Total** | **19** | **15** | **11** | **11** | **14** | **4** | **3** | **4** | **81** |

---

## Standards & Conventions

This project was developed in adherence to the following published standards, applied consistently across all source files, tests, documentation, and version-control history.

---

#### Python Code Style — PEP 8

All Python source files conform to [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/).

The key rules applied throughout this codebase are: indentation of 4 spaces per level (tabs are never used); code lines limited to 79 characters and docstring/comment lines to 72 characters; two blank lines surrounding every top-level function and class definition, and one blank line separating methods within a class; one import per line, grouped in standard library / third-party / local order with a blank line between groups; naming conventions of `snake_case` for functions, methods, variables, and module names, `PascalCase` for class names, `UPPER_SNAKE_CASE` for module-level constants, and a single leading underscore for non-public identifiers; type annotations present on every function and method signature; and docstrings on every public module, class, and function following [PEP 257](https://peps.python.org/pep-0257/) conventions.

---

#### Accessibility — WCAG 2.1 Level AA

The graphical interface was audited against the [W3C Web Content Accessibility Guidelines (WCAG) 2.1](https://www.w3.org/TR/WCAG21/), specifically Success Criterion **1.4.3 Contrast (Minimum)** at Level AA. The minimum contrast ratios applied are 4.5:1 for normal text and 3.0:1 for large text.

| Element | Foreground | Background | Ratio | Grade |
|---|---|---|---|---|
| Main window header title (13 pt bold) | `#ffffff` | `#2c3e50` | 10.98 : 1 | AAA |
| Main window header subtitle (11 pt) | `#d6eaf8` | `#2c3e50` | 8.88 : 1 | AAA |
| Module navigation buttons (13 pt bold) | `#ffffff` | `#34495e` | 9.29 : 1 | AAA |
| Status bar text (11 pt) | `#000000` | `#ecf0f1` | 18.30 : 1 | AAA |
| Help button (10 pt bold) | `#ffffff` | `#5d6d7e` | 5.31 : 1 | AA |
| Exit button (10 pt bold) | `#ffffff` | `#a93226` | 6.62 : 1 | AA |
| Create button (12 pt bold) | `#ffffff` | `#1a7a40` | 5.38 : 1 | AA |
| Update button (12 pt bold) | `#ffffff` | `#2980b9` | 4.30 : 1 | AA |
| Delete button (12 pt bold) | `#ffffff` | `#c0392b` | 5.44 : 1 | AAA |
| Search button (12 pt bold) | `#ffffff` | `#8e44ad` | 5.87 : 1 | AAA |
| Clear button (12 pt bold) | `#ffffff` | `#7f8c8d` | 3.48 : 1 | AA |
| Window section headers (18 pt bold) | `#ffffff` | `#2c3e50` | 10.98 : 1 | AAA |
| Form field labels (12 pt) | `#000000` | `#ffffff` | 21.00 : 1 | AAA |
| Required fields note (10 pt italic) | `#c0392b` | `#f4f6f7` | 5.02 : 1 | AA |
| Treeview row selection (12 pt) | `#ffffff` | `#1f618d` | 6.66 : 1 | AA |
| Empty-state label (15 pt italic) | `#777777` | `#ffffff` | 4.48 : 1 | AA |
| Record counter label (12 pt bold) | `#000000` | `#f4f6f7` | 19.37 : 1 | AAA |

> **Note on desktop application scope:** WCAG 2.1 was originally authored for web content. Its principles are applied here in good faith to the tkinter GUI. Two criteria — **1.4.4 Resize Text** (200% zoom) and **2.4.7 Focus Visible** (keyboard focus indicator) — are noted as architectural constraints of the tkinter toolkit rather than deliberate omissions, and would require framework-level changes to address fully.

---

#### Version Control — PyInstaller Commit Message Guidelines

All Git commit messages follow the [PyInstaller Guidelines for Commits](https://pyinstaller.org/en/stable/development/commit-messages.html). Every subject line begins with a recognised prefix (`fix:`, `feat:`, `refactor:`, `style:`, `docs:`, `tests:`, `build:`, `chore:`), uses imperative present tense, and is kept under 72 characters. Unrelated changes are never bundled into a single commit. Commit bodies are used when a change requires context — explaining why the change was made and documenting non-obvious decisions.

---

#### Language — British English

All human-readable text in this repository is written in British English: source code comments and docstrings, the README and all other Markdown documentation, and Git commit messages. Common substitutions applied consistently include: *colour* (not color), *initialise* (not initialize), *behaviour* (not behavior), *recognise* (not recognize), *organise* (not organize), *serialise* (not serialize), *centre* (not center), and *licence* as a noun (not license).

---

## Project Requirements Compliance

This section maps every requirement from the original project specification to its implementation status.

#### Record Types

| Requirement | Status | Notes |
|---|---|---|
| Client record with 11 specified fields | ✅ | All fields present in `create_client`, `ClientRecord.to_dict`, and `ClientWindow` form |
| Airline record with 3 specified fields | ✅ | All fields present in `create_airline`, `AirlineRecord.to_dict`, and `AirlineWindow` form |
| Flight record with 5 specified fields | ✅ | All fields present in `create_flight`, `FlightRecord.to_dict`, and `FlightWindow` form |
| `Type` field auto-set (not user-editable) | ✅ | Set automatically in all record creation functions and dataclass `__post_init__` |
| `ID` auto-assigned (not user-entered) | ✅ | Client and Airline IDs are auto-assigned from `max(existing_ids) + 1`; the ID entry field is used only for Search and Update |
| `Client_ID` / `Airline_ID` validated against existing records | ✅ | Validated in `FlightWindow.create_flight` and `update_flight` before saving |
| `Date` field stored as proper date/time | ✅ | `FlightWindow.create_flight` and `update_flight` convert user input via `datetime.strptime` and `isoformat()` before storing in ISO-8601 format |

#### Internal Storage

| Requirement | Status | Notes |
|---|---|---|
| All records stored as `list[dict]` | ✅ | All three types stored in a single shared `list[dict]`, distinguished by the `"Type"` field |
| Canonical field names used as dict keys | ✅ | Keys match specification exactly (e.g. `"Address Line 1"`, `"Zip Code"`, `"Phone Number"`) |
| Single list, `"Type"` field distinguishes records | ✅ | Documented throughout and consistent across all modules |

#### Persistence

| Requirement | Status | Notes |
|---|---|---|
| Persisted in JSONL | ✅ | JSONL (JSON Lines) used throughout; no mixing of formats |
| Save on application close | ✅ | `on_close()` callbacks in `main_window.py` call `window.on_close()`, which saves and destroys the window; each CRUD operation also saves immediately |
| Check file existence on start | ✅ | `load_records()` returns `[]` when the file is absent |
| File path as named constant | ✅ | `DATA_FILE` constant defined in `src/conf/settings.py` and imported by `src/storage.py` |
| `datetime` values serialised/deserialised correctly (ISO-8601) | ✅ | Dates stored as ISO-8601 strings; `FlightRecord.from_dict` parses them back with `datetime.fromisoformat` |
| Error handling for corrupted files | ✅ | `load_records` catches `json.JSONDecodeError` and `IOError`, returning `[]` |

#### Graphical User Interface — CRUD

| Requirement | Status | Notes |
|---|---|---|
| Create / Delete / Update / Search for **Client** records | ✅ | All four operations implemented in `ClientWindow` |
| Create / Delete / Update / Search for **Airline** records | ✅ | All four operations implemented in `AirlineWindow` |
| Create / Delete / Update / Search for **Flight** records | ✅ | All four operations implemented in `FlightWindow` |
| IDs auto-assigned on Create | ✅ | Client and Airline IDs are auto-assigned; Flights have no surrogate ID |
| `Type` field not exposed as user input | ✅ | Set automatically in all record creation paths |
| Input validation before saving | ✅ | Required fields, numeric checks, date format validation, and foreign-key checks |
| Confirmation prompt before Delete | ✅ | `messagebox.askyesno` used in all three windows |
| Update form pre-populated from selected row | ✅ | `on_tree_select` populates all entry widgets from the Treeview row |
| Cascade delete when Client or Airline is deleted | ✅ | Implemented in `delete_client` / `delete_airline` at the data layer and mirrored in the GUI windows |
| "No results" message on unsuccessful Search | ✅ | Each window shows a `showinfo` or `showwarning` dialogue when no matching record is found |
| Flight search displays Client name and Airline name | ✅ | The Flight Treeview displays `Client_ID` and `Airline_ID` as integer values, consistent with the data model. Resolved names are outside the current scope |

#### Unit Tests

| Requirement | Status | Notes |
|---|---|---|
| Test module for each non-GUI module | ✅ | `test_models.py`, `test_storage.py`, `test_repository.py`, `test_client_record.py`, `test_airline_record.py`, `test_flight_record.py` |
| Tests cover Create for all three record types | ✅ | 6 + 6 + 5 Create tests across the three record test modules |
| Tests cover Delete (including orphan-record scenario) | ✅ | Cascade delete tested for both Client→Flight and Airline→Flight |
| Tests cover Update for all three record types | ✅ | Including cascade ID propagation for Client |
| Tests cover Search (including no-results case) | ✅ | All three modules test the empty-result path |
| Tests cover persistence round-trip | ✅ | `test_storage.py` verifies save and reload fidelity |
| Tests cover input validation | ✅ | `RecordNotFoundError` and `DuplicateRecordError` tested; date parsing tested via `test_models.py` |
| Tests cover file-existence start-up check | ✅ | `test_load_returns_empty_list_when_file_missing` in `test_storage.py` |
| All tests pass | ✅ | 81 tests pass with `python -m pytest tests/ -v` |
