import pytest
from src.storage import load_records, save_records


def test_load_returns_empty_list_when_file_missing(tmp_path):
    result = load_records(str(tmp_path / "nonexistent.jsonl"))
    assert result == []


def test_save_and_reload(tmp_path):
    filepath = str(tmp_path / "records.jsonl")
    records = [{"type": "client", "id": 1, "name": "Alice"}]
    save_records(records, filepath)
    loaded = load_records(filepath)
    assert len(loaded) == 1
    assert loaded[0]["name"] == "Alice"


def test_save_multiple_records(tmp_path):
    filepath = str(tmp_path / "records.jsonl")
    records = [{"id": i, "type": "airline"} for i in range(5)]
    save_records(records, filepath)
    assert len(load_records(filepath)) == 5


def test_overwrite_on_save(tmp_path):
    filepath = str(tmp_path / "records.jsonl")
    save_records([{"id": 1}], filepath)
    save_records([{"id": 2}, {"id": 3}], filepath)
    loaded = load_records(filepath)
    assert len(loaded) == 2
