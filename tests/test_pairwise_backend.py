from src.search.contracts import SearchParameters
from src.search.pairwise_backend import PairwiseAlignmentBackend


class FakeReferenceDatabase:
    def __init__(self, records):
        self._records = records

    def iter_records(self):
        return iter(self._records)


def test_pairwise_backend_name():
    database = FakeReferenceDatabase([])

    backend = PairwiseAlignmentBackend(
        database
    )

    assert backend.name == "pairwise"


def test_exact_match_returns_full_identity():
    database = FakeReferenceDatabase(
        [
            {
                "id": "REF001",
                "species": "Species alpha",
                "sequence": "ATGCAA",
                "accession": "ACC001.1",
                "gene": "COI",
                "source": "NCBI",
            }
        ]
    )

    backend = PairwiseAlignmentBackend(
        database
    )

    hits = backend.search(
        "ATGCAA",
        SearchParameters(),
    )

    assert len(hits) == 1
    assert hits[0].species == "Species alpha"
    assert hits[0].identity == 100.0
    assert hits[0].coverage == 100.0
    assert hits[0].backend == "pairwise"
    assert hits[0].evalue is None
    assert hits[0].bit_score is None


def test_reverse_complement_is_supported():
    database = FakeReferenceDatabase(
        [
            {
                "id": "REF001",
                "species": "Species alpha",
                "sequence": "ATGCAA",
            }
        ]
    )

    backend = PairwiseAlignmentBackend(
        database
    )

    hits = backend.search(
        "TTGCAT",
        SearchParameters(),
    )

    assert hits[0].identity == 100.0


def test_top_n_limits_results():
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

    backend = PairwiseAlignmentBackend(
        database
    )

    hits = backend.search(
        "ATGCAA",
        SearchParameters(top_n=2),
    )

    assert len(hits) == 2


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

    backend = PairwiseAlignmentBackend(
        database
    )

    hits = backend.search(
        "ATGCAA",
        SearchParameters(),
    )

    assert len(hits) == 1
    assert hits[0].reference_id == "REF002"
    assert hits[0].identity == 100.0