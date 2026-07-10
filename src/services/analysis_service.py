from collections.abc import Callable
from pathlib import Path
from time import perf_counter
from typing import Any

from src.config import (
    DEFAULT_ALLOW_N,
    DEFAULT_MIN_SIMILARITY,
    DEFAULT_REFERENCE_DATABASE_PATH,
    DEFAULT_TOP_N,
)
from src.fasta import read_fasta
from src.logging_config import configure_logging
from src.reference.database import ReferenceDatabase
from src.reference.loader import ReferenceDatabaseLoadError
from src.reference.validator import (
    ReferenceDatabaseValidationError,
)
from src.stats import summarize_sequences
from src.taxonomy import classify_sequence
from src.validation import validate_sequences


ProgressCallback = Callable[[float, str], None]
LOGGER = configure_logging()


class AnalysisError(Exception):
    """Raised when the workflow cannot continue safely."""


def _notify(
    progress_callback: ProgressCallback | None,
    value: float,
    message: str,
) -> None:
    if progress_callback:
        progress_callback(value, message)


def analyze_fasta_file(
    file_path: str,
    reference_database_path: str | Path = (
        DEFAULT_REFERENCE_DATABASE_PATH
    ),
    min_similarity: float = DEFAULT_MIN_SIMILARITY,
    allow_n: bool = DEFAULT_ALLOW_N,
    top_n: int = DEFAULT_TOP_N,
    progress_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    """Run the complete BioTrace analysis pipeline."""
    started_at = perf_counter()

    LOGGER.info(
        "Analysis started | file=%s | "
        "min_similarity=%.2f | allow_n=%s | top_n=%d",
        Path(file_path).name,
        min_similarity,
        allow_n,
        top_n,
    )

    _notify(
        progress_callback,
        0.1,
        "Lendo arquivo FASTA...",
    )

    sequences = read_fasta(str(file_path))

    LOGGER.info(
        "FASTA loaded | sequence_count=%d",
        len(sequences),
    )

    if not sequences:
        LOGGER.error(
            "Analysis failed | no FASTA sequences found"
        )

        raise AnalysisError(
            "Nenhuma sequência foi encontrada "
            "no arquivo FASTA."
        )

    _notify(
        progress_callback,
        0.25,
        "Validando sequências...",
    )

    valid_sequences, invalid_sequences = (
        validate_sequences(
            sequences,
            allow_n=allow_n,
        )
    )

    if invalid_sequences:
        invalid_ids = [
            str(item["id"])
            for item in invalid_sequences
        ]

        LOGGER.warning(
            "Invalid sequences found | count=%d | ids=%s",
            len(invalid_sequences),
            ",".join(invalid_ids),
        )

    if not valid_sequences:
        elapsed = perf_counter() - started_at

        _notify(
            progress_callback,
            1.0,
            "Análise interrompida por "
            "sequências inválidas.",
        )

        LOGGER.warning(
            "Analysis stopped | valid=0 | "
            "invalid=%d | elapsed_seconds=%.4f",
            len(invalid_sequences),
            elapsed,
        )

        return {
            "summary": summarize_sequences([]),
            "total_sequences": len(sequences),
            "valid_count": 0,
            "invalid_count": len(
                invalid_sequences
            ),
            "invalid_sequences": invalid_sequences,
            "results": [],
            "rankings": {},
            "reference_warnings": [],
            "execution_time_seconds": round(
                elapsed,
                4,
            ),
        }

    _notify(
        progress_callback,
        0.45,
        "Calculando estatísticas...",
    )

    summary = summarize_sequences(
        valid_sequences
    )

    metrics_by_id = {
        str(item["id"]): item
        for item in summary["sequence_metrics"]
    }

    _notify(
        progress_callback,
        0.6,
        "Carregando banco de referência local...",
    )

    try:
        database = ReferenceDatabase.from_csv(
            reference_database_path
        )

    except (
        ReferenceDatabaseLoadError,
        ReferenceDatabaseValidationError,
    ) as error:
        LOGGER.error(
            "Reference database error | error=%s",
            error,
        )

        raise AnalysisError(str(error)) from error

    for warning in database.warnings:
        LOGGER.warning(
            "Reference database warning | %s",
            warning,
        )

    results: list[dict[str, object]] = []

    rankings: dict[
        str,
        list[dict[str, object]],
    ] = {}

    total_valid = len(valid_sequences)

    for index, item in enumerate(
        valid_sequences,
        start=1,
    ):
        progress = (
            0.6
            + 0.35 * index / total_valid
        )

        _notify(
            progress_callback,
            progress,
            f"Classificando sequência "
            f"{index} de {total_valid}...",
        )

        classification = classify_sequence(
            item["sequence"],
            database,
            min_similarity=min_similarity,
            top_n=top_n,
        )

        rankings[item["id"]] = (
            classification["ranking"]
        )

        metrics = metrics_by_id[item["id"]]

        results.append(
            {
                "ID": item["id"],
                "Espécie escolhida": (
                    classification["species"]
                ),
                "Melhor similaridade (%)": (
                    classification["similarity"]
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
                "A (%)": metrics["a_frequency"],
                "T (%)": metrics["t_frequency"],
                "C (%)": metrics["c_frequency"],
                "G (%)": metrics["g_frequency"],
                "AT (%)": metrics["at_content"],
                "GC (%)": metrics["gc_content"],
                "N (bases)": metrics["n_count"],
            }
        )

    elapsed = perf_counter() - started_at

    _notify(
        progress_callback,
        1.0,
        "Análise concluída.",
    )

    LOGGER.info(
        "Analysis completed | valid=%d | "
        "invalid=%d | elapsed_seconds=%.4f",
        len(valid_sequences),
        len(invalid_sequences),
        elapsed,
    )

    return {
        "summary": summary,
        "total_sequences": len(sequences),
        "valid_count": len(valid_sequences),
        "invalid_count": len(invalid_sequences),
        "invalid_sequences": invalid_sequences,
        "results": results,
        "rankings": rankings,
        "reference_statistics": (
            database.statistics()
        ),
        "reference_warnings": list(
            database.warnings
        ),
        "execution_time_seconds": round(
            elapsed,
            4,
        ),
    }