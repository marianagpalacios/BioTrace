from pathlib import Path

from src.services import classification_service


class FakeReferenceDatabase:
    warnings = []
    metadata = None

    def iter_records(self):
        return iter(
            [
                {
                    "id": "REF001",
                    "species": "Species alpha",
                    "sequence": "ATGCAATTCGGTACCGATCG",
                    "gene": "COI",
                    "accession": "ACC001.1",
                    "source": "NCBI",
                }
            ]
        )

    def statistics(self):
        return {
            "total_references": 1,
        }


class FakeReferenceDatabaseFactory:
    @classmethod
    def from_files(
        cls,
        database_path,
        metadata_path,
    ):
        return FakeReferenceDatabase()


def test_pairwise_remains_default_backend(
    monkeypatch,
):
    monkeypatch.setattr(
        classification_service,
        "ReferenceDatabase",
        FakeReferenceDatabaseFactory,
    )

    result = classification_service.analyze_valid_sequences(
        [
            {
                "id": "query1",
                "sequence": "ATGCAATTCGGTACCGATCG",
            }
        ],
        reference_database_path="unused.csv",
        reference_metadata_path="unused.json",
    )

    row = result["results"][0]

    assert row["Backend de busca"] == "pairwise"
    assert row["E-value"] is None
    assert row["Bit score"] is None


def test_blast_backend_uses_controlled_database(
    monkeypatch,
):
    monkeypatch.setattr(
        classification_service,
        "ReferenceDatabase",
        FakeReferenceDatabaseFactory,
    )

    blast_database = (
        Path("tests")
        / "data"
        / "blast"
        / "db"
        / "biotrace_test"
    )

    result = classification_service.analyze_valid_sequences(
        [
            {
                "id": "query1",
                "sequence": "ATGCAATTCGGTACCGATCG",
            }
        ],
        reference_database_path="unused.csv",
        reference_metadata_path="unused.json",
        search_backend="blast",
        blast_database_path=str(
            blast_database
        ),
        search_timeout_seconds=10.0,
    )

    row = result["results"][0]

    assert row["Backend de busca"] == "blast"
    assert row["Espécie escolhida"] == "Species alpha"
    assert row["E-value"] is not None
    assert row["Bit score"] is not None
