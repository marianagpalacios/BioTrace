from src.alignment import AlignmentResult
from src.contracts import SequenceOrientation
from src.orientation_resolver import (
    OrientationResolution,
    resolve_orientation,
)
from src.reference.database import ReferenceDatabase
from src.similarity import calculate_similarity


UNKNOWN_SPECIES_LABEL = "Espécie não identificada"


def exact_match(
    sequence: str,
    database: ReferenceDatabase,
) -> str:
    """Return the species for an exact match."""
    normalized_sequence = sequence.upper()

    for record in database.iter_records():
        if normalized_sequence == record["sequence"]:
            return record["species"]

    return "Não identificado"


def _selected_alignment(
    resolution: OrientationResolution,
) -> AlignmentResult:
    """Return the alignment associated with the resolved orientation."""
    if (
        resolution.orientation
        == SequenceOrientation.REVERSE
    ):
        return resolution.reverse_alignment

    return resolution.forward_alignment


def rank_similarity_matches(
    sequence: str,
    database: ReferenceDatabase,
    top_n: int = 5,
) -> list[dict[str, object]]:
    """Return the best match for each species."""
    best_by_species: dict[
        str,
        dict[str, object],
    ] = {}

    for record in database.iter_records():
        species = record["species"]

        score = calculate_similarity(
            sequence,
            record["sequence"],
        )

        current_best = best_by_species.get(species)

        if (
            current_best is None
            or score > float(
                current_best["similarity"]
            )
        ):
            best_by_species[species] = {
                "species": species,
                "reference_id": record["id"],
                "similarity": score,
                "gene": record.get("gene", ""),
                "accession": record.get(
                    "accession",
                    "",
                ),
                "source": record.get("source", ""),
            }

    ranked_matches = sorted(
        best_by_species.values(),
        key=lambda item: float(
            item["similarity"]
        ),
        reverse=True,
    )

    return ranked_matches[:top_n]


def rank_alignment_matches(
    sequence: str,
    database: ReferenceDatabase,
    top_n: int = 5,
) -> list[dict[str, object]]:
    """Rank references using orientation-aware pairwise alignment."""
    best_by_species: dict[
        str,
        dict[str, object],
    ] = {}

    for record in database.iter_records():
        resolution = resolve_orientation(
            sequence,
            record["sequence"],
        )

        alignment = _selected_alignment(
            resolution
        )

        candidate = {
            "species": record["species"],
            "reference_id": record["id"],
            "similarity": round(
                alignment.identity,
                2,
            ),
            "gene": record.get("gene", ""),
            "accession": record.get(
                "accession",
                "",
            ),
            "source": record.get("source", ""),
            "orientation": int(
                resolution.orientation
            ),
            "alignment_score": round(
                alignment.score,
                2,
            ),
            "alignment_identity": round(
                alignment.identity,
                2,
            ),
            "alignment_coverage": round(
                alignment.coverage,
                2,
            ),
        }

        species = record["species"]

        current = best_by_species.get(
            species
        )

        if (
            current is None
            or (
                float(candidate["alignment_identity"]),
                float(candidate["alignment_coverage"]),
                float(candidate["alignment_score"]),
            )
            >
            (
                float(current["alignment_identity"]),
                float(current["alignment_coverage"]),
                float(current["alignment_score"]),
            )
        ):
            best_by_species[species] = candidate

    ranked_matches = sorted(
        best_by_species.values(),
        key=lambda item: (
            float(item["alignment_identity"]),
            float(item["alignment_coverage"]),
            float(item["alignment_score"]),
        ),
        reverse=True,
    )

    return ranked_matches[:top_n]


def classify_sequence(
    sequence: str,
    database: ReferenceDatabase,
    min_similarity: float = 95.0,
    top_n: int = 5,
) -> dict[str, object]:
    """Classify using a validated reference database."""
    ranking = rank_alignment_matches(
        sequence,
        database,
        top_n=top_n,
    )

    if not ranking:
        return {
            "species": UNKNOWN_SPECIES_LABEL,
            "similarity": 0.0,
            "reference_id": None,
            "gene": None,
            "accession": None,
            "source": None,
            "identified": False,
            "ranking": [],
        }

    best_match = ranking[0]
    best_similarity = float(
        best_match["similarity"]
    )

    identified = (
        best_similarity >= min_similarity
    )

    return {
        "species": (
            best_match["species"]
            if identified
            else UNKNOWN_SPECIES_LABEL
        ),
        "similarity": best_similarity,
        "reference_id": (
            best_match["reference_id"]
            if identified
            else None
        ),
        "gene": (
            best_match["gene"]
            if identified
            else None
        ),
        "accession": (
            best_match["accession"]
            if identified
            else None
        ),
        "source": (
            best_match["source"]
            if identified
            else None
        ),
        "identified": identified,
        "orientation": best_match.get(
            "orientation",
            0,
        ),
        "alignment_score": best_match.get(
            "alignment_score",
            0.0,
        ),
        "alignment_identity": best_match.get(
            "alignment_identity",
            best_match["similarity"],
        ),
        "alignment_coverage": best_match.get(
            "alignment_coverage",
            0.0,
        ),
        "ranking": ranking,
    }


def best_similarity_match(
    sequence: str,
    database: ReferenceDatabase,
) -> dict[str, object]:
    """Keep the original API for the best match."""
    classification = classify_sequence(
        sequence,
        database,
        min_similarity=0.0,
        top_n=1,
    )

    return {
        "species": classification["species"],
        "similarity": classification["similarity"],
    }
