import pytest
from src.repository import RecordRepository
from src.exceptions import DuplicateRecordError, RecordNotFoundError


@pytest.fixture
def repo():
    return RecordRepository()


@pytest.fixture
def client_record():
    return {"Type": "Client", "ID": 1, "Name": "Alice", "City": "London"}


def test_add_and_search(repo, client_record):
    repo.add(client_record)
    results = repo.search(Type="Client", ID=1)
    assert len(results) == 1
    assert results[0]["Name"] == "Alice"


def test_add_duplicate_raises(repo, client_record):
    repo.add(client_record)
    with pytest.raises(DuplicateRecordError):
        repo.add(client_record)


def test_delete_record(repo, client_record):
    repo.add(client_record)
    repo.delete(1, "Client")
    assert repo.search(Type="Client", ID=1) == []


def test_delete_nonexistent_raises(repo):
    with pytest.raises(RecordNotFoundError):
        repo.delete(999, "Client")


def test_update_record(repo, client_record):
    repo.add(client_record)
    repo.update(1, "Client", {"City": "Manchester"})
    assert repo.search(ID=1)[0]["City"] == "Manchester"


def test_update_nonexistent_raises(repo):
    with pytest.raises(RecordNotFoundError):
        repo.update(999, "Client", {"Name": "Bob"})


def test_search_by_arbitrary_field(repo):
    repo.add({"Type": "Client", "ID": 1, "City": "London"})
    repo.add({"Type": "Client", "ID": 2, "City": "Rome"})
    assert len(repo.search(City="London")) == 1


def test_get_all(repo, client_record):
    repo.add(client_record)
    all_records = repo.get_all()
    assert len(all_records) == 1
