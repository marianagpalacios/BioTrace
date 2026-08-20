from pathlib import Path

from src.search.blast_backend import LocalBlastBackend
from src.search.contracts import SearchParameters
from src.search.pairwise_backend import PairwiseAlignmentBackend


class FakeReferenceDatabase:
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


BLAST_DATABASE = (
    Path("tests")
    / "data"
    / "blast"
    / "db"
    / "biotrace_test"
)


def test_pairwise_and_blast_agree_on_exact_match():
    parameters = SearchParameters(
        top_n=5,
        timeout_seconds=10.0,
    )

    pairwise = PairwiseAlignmentBackend(
        FakeReferenceDatabase()
    )

    blast = LocalBlastBackend(
        BLAST_DATABASE
    )

    sequence = "ATGCAATTCGGTACCGATCG"

    pairwise_hits = pairwise.search(
        sequence,
        parameters,
    )

    blast_hits = blast.search(
        sequence,
        parameters,
    )

    assert pairwise_hits
    assert blast_hits

    assert (
        pairwise_hits[0].species
        == blast_hits[0].species
        == "Species alpha"
    )

    assert pairwise_hits[0].identity == 100.0
    assert blast_hits[0].identity == 100.0

    assert pairwise_hits[0].coverage == 100.0
    assert blast_hits[0].coverage == 100.0


def test_pairwise_still_supports_reverse_complement():
    backend = PairwiseAlignmentBackend(
        FakeReferenceDatabase()
    )

    hits = backend.search(
        "CGATCGGTACCGAATTGCAT",
        SearchParameters(),
    )

    assert hits
    assert hits[0].species == "Species alpha"
    assert hits[0].identity == 100.0
