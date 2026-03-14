"""Tests for src/record/client_record.py."""
import pytest
from src.record.client_record import (
    create_client,
    delete_client,
    update_client,
    search_clients,
)
from src.record.flight_record import create_flight
from src.exceptions import RecordNotFoundError


def _sample_records() -> list[dict]:
    return []


def _make_client(records: list[dict], name: str = "Alice", **kwargs) -> dict:
    defaults = dict(
        address_line1="1 High St",
        address_line2="",
        address_line3="",
        city="London",
        state="England",
        zip_code="EC1A 1BB",
        country="UK",
        phone_number="07700900000",
    )
    defaults.update(kwargs)
    return create_client(records, name=name, **defaults)


# ── create ──────────────────────────────────────────────────────────────────


class TestCreateClient:
    def test_record_added(self):
        records = _sample_records()
        _make_client(records)
        assert len(records) == 1

    def test_id_starts_at_one(self):
        records = _sample_records()
        rec = _make_client(records)
        assert rec["ID"] == 1

    def test_id_auto_increments(self):
        records = _sample_records()
        _make_client(records, name="Alice")
        rec2 = _make_client(records, name="Bob")
        assert rec2["ID"] == 2

    def test_type_is_client(self):
        records = _sample_records()
        rec = _make_client(records)
        assert rec["Type"] == "Client"

    def test_fields_stored_correctly(self):
        records = _sample_records()
        rec = _make_client(records, name="Carol", city="Bristol")
        assert rec["Name"] == "Carol"
        assert rec["City"] == "Bristol"

    def test_canonical_schema_keys_present(self):
        """Verify all brief-mandated field names are present in the record dict."""
        records = _sample_records()
        rec = _make_client(records)
        expected_keys = {
            "ID", "Type", "Name",
            "Address Line 1", "Address Line 2", "Address Line 3",
            "City", "State", "Zip Code", "Country", "Phone Number",
        }
        assert expected_keys == set(rec.keys())


# ── delete ──────────────────────────────────────────────────────────────────


class TestDeleteClient:
    def test_record_removed(self):
        records = _sample_records()
        _make_client(records)
        delete_client(records, 1)
        assert records == []

    def test_nonexistent_id_raises(self):
        records = _sample_records()
        with pytest.raises(RecordNotFoundError):
            delete_client(records, 999)

    def test_only_matching_record_removed(self):
        records = _sample_records()
        _make_client(records, name="Alice")
        _make_client(records, name="Bob")
        delete_client(records, 1)
        assert len(records) == 1
        assert records[0]["Name"] == "Bob"

    def test_cascade_deletes_associated_flights(self):
        """Deleting a Client must also remove all Flight records for that client."""
        records = _sample_records()
        _make_client(records)
        create_flight(records, client_id=1, airline_id=10,
                      date="2025-06-15T09:00:00", start_city="London", end_city="Rome")
        delete_client(records, 1)
        assert all(r.get("Type") != "Flight" for r in records)

    def test_cascade_leaves_other_flights_intact(self):
        """Deleting a Client must not remove flights belonging to other clients."""
        records = _sample_records()
        _make_client(records, name="Alice")
        _make_client(records, name="Bob")
        create_flight(records, client_id=1, airline_id=10,
                      date="2025-06-15T09:00:00", start_city="London", end_city="Rome")
        create_flight(records, client_id=2, airline_id=10,
                      date="2025-07-20T14:00:00", start_city="Paris", end_city="Berlin")
        delete_client(records, 1)
        flights = [r for r in records if r.get("Type") == "Flight"]
        assert len(flights) == 1
        assert flights[0]["Client_ID"] == 2


# ── update ──────────────────────────────────────────────────────────────────


class TestUpdateClient:
    def test_field_changed(self):
        records = _sample_records()
        _make_client(records)
        update_client(records, 1, City="Manchester")
        assert records[0]["City"] == "Manchester"

    def test_nonexistent_id_raises(self):
        records = _sample_records()
        with pytest.raises(RecordNotFoundError):
            update_client(records, 999, City="Manchester")

    def test_other_fields_unchanged(self):
        records = _sample_records()
        _make_client(records, name="Alice", city="London")
        update_client(records, 1, City="Manchester")
        assert records[0]["Name"] == "Alice"

    def test_cascade_updates_flight_client_id(self):
        """Updating a Client ID must propagate to Client_ID in associated flights."""
        records = _sample_records()
        _make_client(records)
        create_flight(records, client_id=1, airline_id=10,
                      date="2025-06-15T09:00:00", start_city="London", end_city="Rome")
        update_client(records, 1, ID=99)
        flights = [r for r in records if r.get("Type") == "Flight"]
        assert flights[0]["Client_ID"] == 99


# ── search ──────────────────────────────────────────────────────────────────


class TestSearchClients:
    def test_returns_correct_record(self):
        records = _sample_records()
        _make_client(records, name="Alice", city="London")
        _make_client(records, name="Bob", city="Rome")
        results = search_clients(records, City="London")
        assert len(results) == 1
        assert results[0]["Name"] == "Alice"

    def test_empty_result_when_no_match(self):
        records = _sample_records()
        _make_client(records)
        assert search_clients(records, City="NoSuchCity") == []

    def test_returns_all_when_no_filter(self):
        records = _sample_records()
        _make_client(records, name="Alice")
        _make_client(records, name="Bob")
        assert len(search_clients(records)) == 2
