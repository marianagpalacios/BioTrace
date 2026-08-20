from pathlib import Path

from src.reference.database import ReferenceDatabase
from src.search.blast_backend import LocalBlastBackend
from src.search.pairwise_backend import PairwiseAlignmentBackend


def create_search_backend(
    backend_name: str,
    *,
    reference_database: ReferenceDatabase,
    blast_database_path: str | Path | None = None,
):
    """Create a configured search backend."""

    normalized_name = (
        backend_name
        .strip()
        .lower()
    )

    if normalized_name == "pairwise":
        return PairwiseAlignmentBackend(
            reference_database
        )

    if normalized_name == "blast":
        if blast_database_path is None:
            raise ValueError(
                "blast_database_path is required "
                "when backend='blast'."
            )

        return LocalBlastBackend(
            blast_database_path
        )

    raise ValueError(
        "Search backend must be "
        "'pairwise' or 'blast'."
    )