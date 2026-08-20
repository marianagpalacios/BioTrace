from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SearchParameters:
    """Parameters shared by sequence-search backends."""

    top_n: int = 5
    timeout_seconds: float = 30.0


@dataclass(frozen=True)
class SearchHit:
    """Normalized result returned by a search backend."""

    species: str
    reference_id: str

    identity: float
    coverage: float

    score: float

    evalue: float | None = None
    bit_score: float | None = None

    accession: str = ""
    gene: str = ""
    source: str = ""

    backend: str = ""
    orientation: int = 0


class SearchBackend(Protocol):
    """Common contract implemented by sequence-search backends."""

    @property
    def name(self) -> str:
        """Return the backend identifier."""
        ...

    def search(
        self,
        sequence: str,
        parameters: SearchParameters,
    ) -> list[SearchHit]:
        """Search references for a nucleotide sequence."""
        ...
