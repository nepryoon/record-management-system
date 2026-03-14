"""Tests for src/record/airline_record.py."""
import pytest
from src.record.airline_record import (
    create_airline,
    delete_airline,
    update_airline,
    search_airlines,
)
from src.record.flight_record import create_flight
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
        assert rec["ID"] == 1

    def test_id_auto_increments(self):
        records = _sample_records()
        create_airline(records, company_name="BritAir")
        rec2 = create_airline(records, company_name="SkyLine")
        assert rec2["ID"] == 2

    def test_type_is_airline(self):
        records = _sample_records()
        rec = create_airline(records, company_name="BritAir")
        assert rec["Type"] == "Airline"

    def test_company_name_stored(self):
        records = _sample_records()
        rec = create_airline(records, company_name="EuroJet")
        assert rec["Company Name"] == "EuroJet"

    def test_canonical_schema_keys_present(self):
        """Verify all brief-mandated field names are present in the record dict."""
        records = _sample_records()
        rec = create_airline(records, company_name="BritAir")
        assert set(rec.keys()) == {"ID", "Type", "Company Name"}


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
        assert records[0]["Company Name"] == "SkyLine"

    def test_cascade_deletes_associated_flights(self):
        """Deleting an Airline must also remove all Flight records for that airline."""
        records = _sample_records()
        create_airline(records, company_name="BritAir")
        create_flight(records, client_id=1, airline_id=1,
                      date="2025-06-15T09:00:00", start_city="London", end_city="Rome")
        delete_airline(records, 1)
        assert all(r.get("Type") != "Flight" for r in records)

    def test_cascade_leaves_other_flights_intact(self):
        """Deleting an Airline must not remove flights belonging to other airlines."""
        records = _sample_records()
        create_airline(records, company_name="BritAir")
        create_airline(records, company_name="SkyLine")
        create_flight(records, client_id=1, airline_id=1,
                      date="2025-06-15T09:00:00", start_city="London", end_city="Rome")
        create_flight(records, client_id=1, airline_id=2,
                      date="2025-07-20T14:00:00", start_city="Paris", end_city="Berlin")
        delete_airline(records, 1)
        flights = [r for r in records if r.get("Type") == "Flight"]
        assert len(flights) == 1
        assert flights[0]["Airline_ID"] == 2


# ── update ──────────────────────────────────────────────────────────────────


class TestUpdateAirline:
    def test_field_changed(self):
        records = _sample_records()
        create_airline(records, company_name="BritAir")
        update_airline(records, 1, **{"Company Name": "NewAir"})
        assert records[0]["Company Name"] == "NewAir"

    def test_nonexistent_id_raises(self):
        records = _sample_records()
        with pytest.raises(RecordNotFoundError):
            update_airline(records, 999, **{"Company Name": "NewAir"})


# ── search ──────────────────────────────────────────────────────────────────


class TestSearchAirlines:
    def test_returns_correct_record(self):
        records = _sample_records()
        create_airline(records, company_name="BritAir")
        create_airline(records, company_name="SkyLine")
        results = search_airlines(records, **{"Company Name": "BritAir"})
        assert len(results) == 1
        assert results[0]["Company Name"] == "BritAir"

    def test_empty_result_when_no_match(self):
        records = _sample_records()
        create_airline(records, company_name="BritAir")
        assert search_airlines(records, **{"Company Name": "NoSuchAirline"}) == []

    def test_returns_all_when_no_filter(self):
        records = _sample_records()
        create_airline(records, company_name="BritAir")
        create_airline(records, company_name="SkyLine")
        assert len(search_airlines(records)) == 2
