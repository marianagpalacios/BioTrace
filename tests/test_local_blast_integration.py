from pathlib import Path

from src.search.blast_backend import LocalBlastBackend
from src.search.contracts import SearchParameters


def test_local_blast_backend_finds_exact_match():
    database_prefix = (
        Path("tests")
        / "data"
        / "blast"
        / "db"
        / "biotrace_test"
    )

    backend = LocalBlastBackend(
        database_prefix
    )

    hits = backend.search(
        "ATGCAATTCGGTACCGATCG",
        SearchParameters(
            top_n=5,
            timeout_seconds=10,
        ),
    )

    assert hits
    assert hits[0].reference_id == "REF001"
    assert hits[0].species == "Species alpha"
    assert hits[0].accession == "ACC001.1"
    assert hits[0].identity == 100.0
    assert hits[0].coverage == 100.0
    assert hits[0].evalue is not None
    assert hits[0].bit_score is not None
    assert hits[0].backend == "blast"