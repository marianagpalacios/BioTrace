from src.search.cache import SearchCache
from src.services import classification_service


class FakeReferenceDatabase:
    warnings = []
    metadata = None

    def iter_records(self):
        return iter([])

    def statistics(self):
        return {
            "total_references": 0,
        }


class FakeReferenceDatabaseFactory:
    @classmethod
    def from_files(
        cls,
        database_path,
        metadata_path,
    ):
        return FakeReferenceDatabase()


class CountingBackend:
    def __init__(self):
        self.calls = 0

    @property
    def name(self):
        return "fake"

    def search(
        self,
        sequence,
        parameters,
    ):
        self.calls += 1

        return []


def test_second_equal_search_uses_cache(
    monkeypatch,
):
    backend = CountingBackend()
    cache = SearchCache()

    monkeypatch.setattr(
        classification_service,
        "ReferenceDatabase",
        FakeReferenceDatabaseFactory,
    )

    monkeypatch.setattr(
        classification_service,
        "create_search_backend",
        lambda *args, **kwargs: backend,
    )

    kwargs = {
        "valid_sequences": [
            {
                "id": "query1",
                "sequence": "ATGC",
            }
        ],
        "reference_database_path": "unused.csv",
        "reference_metadata_path": "unused.json",
        "search_cache": cache,
        "search_database_hash": "db123",
    }

    first = (
        classification_service
        .analyze_valid_sequences(
            **kwargs
        )
    )

    second = (
        classification_service
        .analyze_valid_sequences(
            **kwargs
        )
    )

    assert backend.calls == 1

    assert (
        first["results"][0]["Cache"]
        == "miss"
    )

    assert (
        second["results"][0]["Cache"]
        == "hit"
    )
