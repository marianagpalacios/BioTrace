from src.contracts import SequenceOrientation
from src.orientation_resolver import resolve_orientation
from src.reference.database import ReferenceDatabase
from src.search.contracts import (
    SearchHit,
    SearchParameters,
)


class PairwiseAlignmentBackend:
    """Search backend based on BioTrace pairwise alignment."""

    def __init__(
        self,
        database: ReferenceDatabase,
    ) -> None:
        self.database = database

    @property
    def name(self) -> str:
        return "pairwise"

    def search(
        self,
        sequence: str,
        parameters: SearchParameters,
    ) -> list[SearchHit]:
        candidate_sequence = (
            sequence.strip().upper()
        )

        if not candidate_sequence:
            raise ValueError(
                "Sequence cannot be empty."
            )

        best_by_species: dict[
            str,
            SearchHit,
        ] = {}

        for record in self.database.iter_records():
            resolution = resolve_orientation(
                candidate_sequence,
                record["sequence"],
            )

            if (
                resolution.orientation
                == SequenceOrientation.REVERSE
            ):
                alignment = (
                    resolution.reverse_alignment
                )
            else:
                alignment = (
                    resolution.forward_alignment
                )

            hit = SearchHit(
                species=record["species"],
                reference_id=record["id"],
                identity=round(
                    alignment.identity,
                    2,
                ),
                coverage=round(
                    alignment.coverage,
                    2,
                ),
                score=round(
                    alignment.score,
                    2,
                ),
                evalue=None,
                bit_score=None,
                accession=record.get(
                    "accession",
                    "",
                ),
                gene=record.get(
                    "gene",
                    "",
                ),
                source=record.get(
                    "source",
                    "",
                ),
                backend=self.name,
                orientation=int(
                    resolution.orientation
                ),
            )

            species = hit.species

            current = best_by_species.get(
                species
            )

            if (
                current is None
                or (
                    hit.identity,
                    hit.coverage,
                    hit.score,
                )
                >
                (
                    current.identity,
                    current.coverage,
                    current.score,
                )
            ):
                best_by_species[
                    species
                ] = hit

        ranked_hits = sorted(
            best_by_species.values(),
            key=lambda hit: (
                hit.identity,
                hit.coverage,
                hit.score,
            ),
            reverse=True,
        )

        return ranked_hits[
            : parameters.top_n
        ]
