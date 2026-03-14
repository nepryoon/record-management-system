"""Tests for src/record/client_record.py."""
import pytest
from src.record.client_record import (
    create_client,
    delete_client,
    update_client,
    search_clients,
)
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
        assert rec["id"] == 1

    def test_id_auto_increments(self):
        records = _sample_records()
        _make_client(records, name="Alice")
        rec2 = _make_client(records, name="Bob")
        assert rec2["id"] == 2

    def test_type_is_client(self):
        records = _sample_records()
        rec = _make_client(records)
        assert rec["type"] == "client"

    def test_fields_stored_correctly(self):
        records = _sample_records()
        rec = _make_client(records, name="Carol", city="Bristol")
        assert rec["name"] == "Carol"
        assert rec["city"] == "Bristol"


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
        assert records[0]["name"] == "Bob"


# ── update ──────────────────────────────────────────────────────────────────


class TestUpdateClient:
    def test_field_changed(self):
        records = _sample_records()
        _make_client(records)
        update_client(records, 1, city="Manchester")
        assert records[0]["city"] == "Manchester"

    def test_nonexistent_id_raises(self):
        records = _sample_records()
        with pytest.raises(RecordNotFoundError):
            update_client(records, 999, city="Manchester")

    def test_other_fields_unchanged(self):
        records = _sample_records()
        _make_client(records, name="Alice", city="London")
        update_client(records, 1, city="Manchester")
        assert records[0]["name"] == "Alice"


# ── search ──────────────────────────────────────────────────────────────────


class TestSearchClients:
    def test_returns_correct_record(self):
        records = _sample_records()
        _make_client(records, name="Alice", city="London")
        _make_client(records, name="Bob", city="Rome")
        results = search_clients(records, city="London")
        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_empty_result_when_no_match(self):
        records = _sample_records()
        _make_client(records)
        assert search_clients(records, city="NoSuchCity") == []

    def test_returns_all_when_no_filter(self):
        records = _sample_records()
        _make_client(records, name="Alice")
        _make_client(records, name="Bob")
        assert len(search_clients(records)) == 2
