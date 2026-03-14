"""Tests for src/record/airline_record.py."""
import pytest
from src.record.airline_record import (
    create_airline,
    delete_airline,
    update_airline,
    search_airlines,
)
from src.exceptions import RecordNotFoundError


def _sample_records() -> list[dict]:
    return []


# ── create ──────────────────────────────────────────────────────────────────


class TestCreateAirline:
    def test_record_added(self):
        records = _sample_records()
        create_airline(records, company_name="BritAir")
        assert len(records) == 1

    def test_id_starts_at_one(self):
        records = _sample_records()
        rec = create_airline(records, company_name="BritAir")
        assert rec["id"] == 1

    def test_id_auto_increments(self):
        records = _sample_records()
        create_airline(records, company_name="BritAir")
        rec2 = create_airline(records, company_name="SkyLine")
        assert rec2["id"] == 2

    def test_type_is_airline(self):
        records = _sample_records()
        rec = create_airline(records, company_name="BritAir")
        assert rec["type"] == "airline"

    def test_company_name_stored(self):
        records = _sample_records()
        rec = create_airline(records, company_name="EuroJet")
        assert rec["company_name"] == "EuroJet"


# ── delete ──────────────────────────────────────────────────────────────────


class TestDeleteAirline:
    def test_record_removed(self):
        records = _sample_records()
        create_airline(records, company_name="BritAir")
        delete_airline(records, 1)
        assert records == []

    def test_nonexistent_id_raises(self):
        records = _sample_records()
        with pytest.raises(RecordNotFoundError):
            delete_airline(records, 999)

    def test_only_matching_record_removed(self):
        records = _sample_records()
        create_airline(records, company_name="BritAir")
        create_airline(records, company_name="SkyLine")
        delete_airline(records, 1)
        assert len(records) == 1
        assert records[0]["company_name"] == "SkyLine"


# ── update ──────────────────────────────────────────────────────────────────


class TestUpdateAirline:
    def test_field_changed(self):
        records = _sample_records()
        create_airline(records, company_name="BritAir")
        update_airline(records, 1, company_name="NewAir")
        assert records[0]["company_name"] == "NewAir"

    def test_nonexistent_id_raises(self):
        records = _sample_records()
        with pytest.raises(RecordNotFoundError):
            update_airline(records, 999, company_name="NewAir")


# ── search ──────────────────────────────────────────────────────────────────


class TestSearchAirlines:
    def test_returns_correct_record(self):
        records = _sample_records()
        create_airline(records, company_name="BritAir")
        create_airline(records, company_name="SkyLine")
        results = search_airlines(records, company_name="BritAir")
        assert len(results) == 1
        assert results[0]["company_name"] == "BritAir"

    def test_empty_result_when_no_match(self):
        records = _sample_records()
        create_airline(records, company_name="BritAir")
        assert search_airlines(records, company_name="NoSuchAirline") == []

    def test_returns_all_when_no_filter(self):
        records = _sample_records()
        create_airline(records, company_name="BritAir")
        create_airline(records, company_name="SkyLine")
        assert len(search_airlines(records)) == 2
