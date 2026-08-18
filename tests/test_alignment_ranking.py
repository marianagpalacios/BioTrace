from src.contracts import SequenceOrientation
from src.taxonomy import rank_alignment_matches


class FakeReferenceDatabase:
    def __init__(self, records):
        self._records = records

    def iter_records(self):
        return iter(self._records)


def test_exact_forward_match_ranks_first():
    database = FakeReferenceDatabase(
        [
            {
                "id": "REF001",
                "species": "Species alpha",
                "sequence": "ATGCAA",
                "gene": "COI",
                "accession": "ACC001.1",
                "source": "NCBI",
            },
            {
                "id": "REF002",
                "species": "Species beta",
                "sequence": "CCCCCC",
                "gene": "COI",
                "accession": "ACC002.1",
                "source": "NCBI",
            },
        ]
    )

    results = rank_alignment_matches(
        "ATGCAA",
        database,
    )

    assert results[0]["species"] == "Species alpha"
    assert results[0]["alignment_identity"] == 100.0
    assert results[0]["alignment_coverage"] == 100.0
    assert (
        results[0]["orientation"]
        == int(SequenceOrientation.FORWARD)
    )


def test_reverse_complement_can_rank_first():
    database = FakeReferenceDatabase(
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

    results = rank_alignment_matches(
        "TTGCAT",
        database,
    )

    assert results[0]["species"] == "Species alpha"
    assert results[0]["alignment_identity"] == 100.0
    assert (
        results[0]["orientation"]
        == int(SequenceOrientation.REVERSE)
    )


def test_top_n_limits_alignment_ranking():
    database = FakeReferenceDatabase(
        [
            {
                "id": "REF001",
                "species": "Species alpha",
                "sequence": "ATGCAA",
            },
            {
                "id": "REF002",
                "species": "Species beta",
                "sequence": "ATGCTA",
            },
            {
                "id": "REF003",
                "species": "Species gamma",
                "sequence": "CCCCCC",
            },
        ]
    )

    results = rank_alignment_matches(
        "ATGCAA",
        database,
        top_n=2,
    )

    assert len(results) == 2


def test_only_best_reference_per_species_is_kept():
    database = FakeReferenceDatabase(
        [
            {
                "id": "REF001",
                "species": "Species alpha",
                "sequence": "ATGCTA",
            },
            {
                "id": "REF002",
                "species": "Species alpha",
                "sequence": "ATGCAA",
            },
        ]
    )

    results = rank_alignment_matches(
        "ATGCAA",
        database,
    )

    assert len(results) == 1
    assert results[0]["reference_id"] == "REF002"
    assert results[0]["alignment_identity"] == 100.0