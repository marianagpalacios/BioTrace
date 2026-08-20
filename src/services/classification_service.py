"""Shared classification core for validated sequence inputs."""

from collections.abc import Callable
from pathlib import Path

from src.config import (
    DEFAULT_MIN_SIMILARITY,
    DEFAULT_REFERENCE_DATABASE_PATH,
    DEFAULT_REFERENCE_METADATA_PATH,
    DEFAULT_TOP_N,
)
from src.fasta import SequenceRecord
from src.reference.database import ReferenceDatabase
from src.search.cache import (
    SearchCache,
    build_search_cache_key,
)
from src.search.contracts import SearchParameters
from src.search.factory import create_search_backend
from src.stats import summarize_sequences
from src.taxonomy import (
    classify_sequence,
    classify_with_backend,
)
from src.version import __version__


ProgressCallback = Callable[
    [float, str],
    None,
]


def analyze_valid_sequences(
    valid_sequences: list[SequenceRecord],
    *,
    reference_database_path: str | Path = (
        DEFAULT_REFERENCE_DATABASE_PATH
    ),
    reference_metadata_path: str | Path = (
        DEFAULT_REFERENCE_METADATA_PATH
    ),
    min_similarity: float = DEFAULT_MIN_SIMILARITY,
    top_n: int = DEFAULT_TOP_N,
    progress_callback: ProgressCallback | None = None,
    progress_start: float = 0.55,
    progress_end: float = 0.95,
    search_backend: str = "pairwise",
    blast_database_path: str | None = None,
    search_timeout_seconds: float = 30.0,
    search_cache: SearchCache | None = None,
    search_database_hash: str = "",
    blast_version: str | None = None,
) -> dict[str, object]:
    """Calculate metrics, load references and classify validated sequences."""

    summary = summarize_sequences(
        valid_sequences
    )

    metrics_by_id = {
        str(item["id"]): item
        for item in summary[
            "sequence_metrics"
        ]
    }

    database = ReferenceDatabase.from_files(
        reference_database_path,
        reference_metadata_path,
    )

    backend = create_search_backend(
        search_backend,
        reference_database=database,
        blast_database_path=blast_database_path,
    )

    cache = (
        search_cache
        if search_cache is not None
        else SearchCache()
    )

    results: list[
        dict[str, object]
    ] = []

    rankings: dict[
        str,
        list[dict[str, object]],
    ] = {}

    total_valid = len(
        valid_sequences
    )

    for index, item in enumerate(
        valid_sequences,
        start=1,
    ):
        if progress_callback:
            progress = (
                progress_start
                + (
                    progress_end
                    - progress_start
                )
                * index
                / total_valid
            )

            progress_callback(
                progress,
                "Classificando sequência "
                f"{index} de "
                f"{total_valid}...",
            )

        sequence = item["sequence"]

        parameters = SearchParameters(
            top_n=top_n,
            timeout_seconds=search_timeout_seconds,
        )

        cache_key = build_search_cache_key(
            sequence=sequence,
            database_hash=search_database_hash,
            parameters=parameters,
            backend=backend.name,
            blast_version=blast_version,
            biotrace_version=__version__,
        )

        cached = cache.lookup(
            cache_key
        )

        if cached.hit:
            classification = cached.value
            cache_hit = True
        else:
            classification = classify_with_backend(
                sequence,
                backend=backend,
                min_similarity=min_similarity,
                top_n=top_n,
                timeout_seconds=search_timeout_seconds,
            )

            cache.set(
                cache_key,
                classification,
            )

            cache_hit = False

        rankings[item["id"]] = (
            classification["ranking"]
        )

        metrics = metrics_by_id[
            item["id"]
        ]

        results.append(
            {
                "ID": item["id"],
                "Espécie escolhida": (
                    classification["species"]
                ),
                "Melhor similaridade (%)": (
                    classification["similarity"]
                ),
                "Orientação": (
                    classification.get(
                        "orientation",
                        0,
                    )
                ),
                "Score de alinhamento": (
                    classification.get(
                        "alignment_score",
                        0.0,
                    )
                ),
                "Identidade do alinhamento (%)": (
                    classification.get(
                        "alignment_identity",
                        classification[
                            "similarity"
                        ],
                    )
                ),
                "Cobertura do alinhamento (%)": (
                    classification.get(
                        "alignment_coverage",
                        0.0,
                    )
                ),
                "Backend de busca": (
                    classification["backend"]
                ),
                "E-value": (
                    classification.get(
                        "evalue"
                    )
                ),
                "Bit score": (
                    classification.get(
                        "bit_score"
                    )
                ),
                "Cache": (
                    "hit"
                    if cache_hit
                    else "miss"
                ),
                "Referência escolhida": (
                    classification["reference_id"]
                    or "-"
                ),
                "Gene": (
                    classification["gene"]
                    or "-"
                ),
                "Accession": (
                    classification["accession"]
                    or "-"
                ),
                "Fonte": (
                    classification["source"]
                    or "-"
                ),
                "Status": (
                    "Identificada"
                    if classification["identified"]
                    else "Não identificada"
                ),
                "Comprimento (bp)": (
                    metrics["length"]
                ),
                "A (%)": (
                    metrics["a_frequency"]
                ),
                "T (%)": (
                    metrics["t_frequency"]
                ),
                "C (%)": (
                    metrics["c_frequency"]
                ),
                "G (%)": (
                    metrics["g_frequency"]
                ),
                "AT (%)": (
                    metrics["at_content"]
                ),
                "GC (%)": (
                    metrics["gc_content"]
                ),
                "N (bases)": (
                    metrics["n_count"]
                ),
            }
        )

    return {
        "summary": summary,
        "results": results,
        "rankings": rankings,
        "reference_statistics": (
            database.statistics()
        ),
        "reference_warnings": list(
            database.warnings
        ),
        "reference_metadata": (
            database.metadata.to_dict()
            if database.metadata
            else None
        ),
    }
