from src.contracts import SequenceOrientation
from src.services import classification_service


class FakeReferenceDatabase:
    """Minimal reference database used by shared-service integration tests."""

    warnings: tuple[str, ...] = ()
    metadata = None

    def iter_records(self):
        return iter(
            [
                {
                    "id": "REF001",
                    "species": "Species alpha",
                    "sequence": "ATGCAA",
                    "gene": "COI",
                    "accession": "ACC001.1",
                    "source": "NCBI",
                }
            ]
        )

    def statistics(self):
        return {
            "references": 1,
            "species": 1,
            "unique_ids": 1,
        }


class FakeReferenceDatabaseFactory:
    @classmethod
    def from_files(
        cls,
        database_path,
        metadata_path,
    ):
        return FakeReferenceDatabase()


def test_shared_service_preserves_forward_orientation(
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
                "id": "forward_read",
                "sequence": "ATGCAA",
            }
        ],
        reference_database_path="unused.csv",
        reference_metadata_path="unused.json",
    )

    row = result["results"][0]

    assert row["Espécie escolhida"] == "Species alpha"
    assert (
        row["Orientação"]
        == int(SequenceOrientation.FORWARD)
    )
    assert row["Identidade do alinhamento (%)"] == 100.0
    assert row["Cobertura do alinhamento (%)"] == 100.0


def test_shared_service_resolves_reverse_complement(
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
                "id": "reverse_read",
                "sequence": "TTGCAT",
            }
        ],
        reference_database_path="unused.csv",
        reference_metadata_path="unused.json",
    )

    row = result["results"][0]

    assert row["Espécie escolhida"] == "Species alpha"
    assert (
        row["Orientação"]
        == int(SequenceOrientation.REVERSE)
    )
    assert row["Identidade do alinhamento (%)"] == 100.0
    assert row["Cobertura do alinhamento (%)"] == 100.0
