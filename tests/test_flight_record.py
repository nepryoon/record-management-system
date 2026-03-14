"""Tests for src/record/flight_record.py."""
import pytest
from src.record.flight_record import (
    create_flight,
    delete_flight,
    update_flight,
    search_flights,
)
from src.exceptions import RecordNotFoundError

DATE = "2025-06-15T09:00:00"
DATE2 = "2025-07-20T14:00:00"


def _sample_records() -> list[dict]:
    return []


def _make_flight(records: list[dict], client_id: int = 1, airline_id: int = 10,
                 date: str = DATE, start_city: str = "London",
                 end_city: str = "Rome") -> dict:
    return create_flight(records, client_id=client_id, airline_id=airline_id,
                         date=date, start_city=start_city, end_city=end_city)


# ── create ──────────────────────────────────────────────────────────────────


class TestCreateFlight:
    def test_record_added(self):
        records = _sample_records()
        _make_flight(records)
        assert len(records) == 1

    def test_fields_stored_correctly(self):
        records = _sample_records()
        rec = _make_flight(records)
        assert rec["client_id"] == 1
        assert rec["airline_id"] == 10
        assert rec["date"] == DATE
        assert rec["start_city"] == "London"
        assert rec["end_city"] == "Rome"

    def test_type_is_flight(self):
        records = _sample_records()
        rec = _make_flight(records)
        assert rec["type"] == "flight"

    def test_multiple_flights_added(self):
        records = _sample_records()
        _make_flight(records, date=DATE)
        _make_flight(records, client_id=2, date=DATE2)
        assert len(records) == 2


# ── delete ──────────────────────────────────────────────────────────────────


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
        assert records[0]["client_id"] == 2


# ── update ──────────────────────────────────────────────────────────────────


class TestUpdateFlight:
    def test_field_changed(self):
        records = _sample_records()
        _make_flight(records)
        update_flight(records, client_id=1, airline_id=10, date=DATE,
                      end_city="Paris")
        assert records[0]["end_city"] == "Paris"

    def test_nonexistent_record_raises(self):
        records = _sample_records()
        with pytest.raises(RecordNotFoundError):
            update_flight(records, client_id=99, airline_id=99, date=DATE,
                          end_city="Paris")

    def test_other_fields_unchanged(self):
        records = _sample_records()
        _make_flight(records)
        update_flight(records, client_id=1, airline_id=10, date=DATE,
                      end_city="Paris")
        assert records[0]["start_city"] == "London"


# ── search ──────────────────────────────────────────────────────────────────


class TestSearchFlights:
    def test_returns_correct_record(self):
        records = _sample_records()
        _make_flight(records, client_id=1, start_city="London")
        _make_flight(records, client_id=2, start_city="Paris", date=DATE2)
        results = search_flights(records, start_city="London")
        assert len(results) == 1
        assert results[0]["client_id"] == 1

    def test_empty_result_when_no_match(self):
        records = _sample_records()
        _make_flight(records)
        assert search_flights(records, start_city="NoSuchCity") == []

    def test_returns_all_when_no_filter(self):
        records = _sample_records()
        _make_flight(records, date=DATE)
        _make_flight(records, client_id=2, date=DATE2)
        assert len(search_flights(records)) == 2
