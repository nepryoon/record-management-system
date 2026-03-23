"""Tests for src/record/flight_record.py."""
import pytest
from src.record.flight_record import (
    create_flight,
    delete_flight,
    update_flight,
    search_flights,
)
from src.exceptions import DuplicateRecordError, RecordNotFoundError

DATE = "2025-06-15T09:00:00"
DATE2 = "2025-07-20T14:00:00"


def _sample_records() -> list[dict]:
    return []


def _make_flight(records: list[dict], client_id: int = 1, airline_id: int = 10,
                 date: str = DATE, start_city: str = "London",
                 end_city: str = "Rome") -> dict:
    return create_flight(records, client_id=client_id, airline_id=airline_id,
                         date=date, start_city=start_city, end_city=end_city)


# ── create ─────────────────────────────────────────────────────────────────


class TestCreateFlight:
    def test_record_added(self):
        records = _sample_records()
        _make_flight(records)
        assert len(records) == 1

    def test_fields_stored_correctly(self):
        records = _sample_records()
        rec = _make_flight(records)
        assert rec["Client_ID"] == 1
        assert rec["Airline_ID"] == 10
        assert rec["Date"] == DATE
        assert rec["Start City"] == "London"
        assert rec["End City"] == "Rome"

    def test_type_is_flight(self):
        records = _sample_records()
        rec = _make_flight(records)
        assert rec["Type"] == "Flight"

    def test_multiple_flights_added(self):
        records = _sample_records()
        _make_flight(records, date=DATE)
        _make_flight(records, client_id=2, date=DATE2)
        assert len(records) == 2

    def test_canonical_schema_keys_present(self):
        """Verify all brief-mandated field names are present in the record dict."""
        records = _sample_records()
        rec = _make_flight(records)
        assert set(rec.keys()) == {"Type", "Client_ID", "Airline_ID", "Date", "Start City", "End City"}


# ── delete ─────────────────────────────────────────────────────────────────


class TestDeleteFlight:
    def test_record_removed(self):
        records = _sample_records()
        _make_flight(records)
        delete_flight(records, client_id=1, airline_id=10, date=DATE)
        assert records == []

    def test_nonexistent_record_raises(self):
        records = _sample_records()
        with pytest.raises(RecordNotFoundError):
            delete_flight(records, client_id=99, airline_id=99, date=DATE)

    def test_only_matching_record_removed(self):
        records = _sample_records()
        _make_flight(records, client_id=1, date=DATE)
        _make_flight(records, client_id=2, date=DATE2)
        delete_flight(records, client_id=1, airline_id=10, date=DATE)
        assert len(records) == 1
        assert records[0]["Client_ID"] == 2


# ── update ─────────────────────────────────────────────────────────────────


class TestUpdateFlight:
    def test_field_changed(self):
        records = _sample_records()
        _make_flight(records)
        update_flight(records, client_id=1, airline_id=10, date=DATE,
                      **{"End City": "Paris"})
        assert records[0]["End City"] == "Paris"

    def test_nonexistent_record_raises(self):
        records = _sample_records()
        with pytest.raises(RecordNotFoundError):
            update_flight(records, client_id=99, airline_id=99, date=DATE,
                          **{"End City": "Paris"})

    def test_other_fields_unchanged(self):
        records = _sample_records()
        _make_flight(records)
        update_flight(records, client_id=1, airline_id=10, date=DATE,
                      **{"End City": "Paris"})
        assert records[0]["Start City"] == "London"


# ── search ─────────────────────────────────────────────────────────────────


class TestSearchFlights:
    def test_returns_correct_record(self):
        records = _sample_records()
        _make_flight(records, client_id=1, start_city="London")
        _make_flight(records, client_id=2, start_city="Paris", date=DATE2)
        results = search_flights(records, **{"Start City": "London"})
        assert len(results) == 1
        assert results[0]["Client_ID"] == 1

    def test_empty_result_when_no_match(self):
        records = _sample_records()
        _make_flight(records)
        assert search_flights(records, **{"Start City": "NoSuchCity"}) == []

    def test_returns_all_when_no_filter(self):
        records = _sample_records()
        _make_flight(records, date=DATE)
        _make_flight(records, client_id=2, date=DATE2)
        assert len(search_flights(records)) == 2


# ── referential integrity ───────────────────────────────────────────────────


class TestCreateFlightReferentialIntegrity:
    """Verifies that create_flight() enforces referential integrity.

    When Client or Airline records are already present in the shared
    records list, create_flight() must reject any foreign ID that does
    not correspond to an existing record of that type.
    """

    # Asserts that a non-existent client_id raises RecordNotFoundError
    def test_missing_client_raises(self):
        records = [{"Type": "Client", "ID": 999, "Name": "Other"}]
        with pytest.raises(RecordNotFoundError):
            create_flight(
                records, client_id=1, airline_id=10,
                date=DATE, start_city="London", end_city="Rome",
            )

    # Asserts that a non-existent airline_id raises RecordNotFoundError
    def test_missing_airline_raises(self):
        records = [
            {"Type": "Client", "ID": 1, "Name": "Alice"},
            {"Type": "Airline", "ID": 999, "Company Name": "Other"},
        ]
        with pytest.raises(RecordNotFoundError):
            create_flight(
                records, client_id=1, airline_id=10,
                date=DATE, start_city="London", end_city="Rome",
            )

    # Asserts that a flight is created when both Client and Airline exist
    def test_valid_ids_creates_flight(self):
        records = [
            {"Type": "Client", "ID": 1, "Name": "Alice"},
            {"Type": "Airline", "ID": 10, "Company Name": "BA"},
        ]
        flight = create_flight(
            records, client_id=1, airline_id=10,
            date=DATE, start_city="London", end_city="Rome",
        )
        assert flight["Type"] == "Flight"
        assert flight["Client_ID"] == 1
        assert flight["Airline_ID"] == 10


# ── duplicate key ───────────────────────────────────────────────────────────


class TestCreateFlightDuplicateKey:
    """Verifies that create_flight() rejects duplicate composite keys.

    The composite key is (Client_ID, Airline_ID, Date).  A second
    attempt to insert a flight with the same key must raise
    DuplicateRecordError.
    """

    def test_duplicate_composite_key_raises(self):
        records = _sample_records()
        _make_flight(records)
        with pytest.raises(DuplicateRecordError):
            _make_flight(records)  # Same client_id=1, airline_id=10, date=DATE

    def test_different_date_does_not_raise(self):
        records = _sample_records()
        _make_flight(records, date=DATE)
        # Different date — should succeed without raising
        _make_flight(records, date=DATE2)
        assert len(records) == 2

    def test_different_client_does_not_raise(self):
        records = _sample_records()
        _make_flight(records, client_id=1)
        _make_flight(records, client_id=2)
        assert len(records) == 2

    def test_different_airline_does_not_raise(self):
        records = _sample_records()
        _make_flight(records, airline_id=10)
        _make_flight(records, airline_id=20)
        assert len(records) == 2
