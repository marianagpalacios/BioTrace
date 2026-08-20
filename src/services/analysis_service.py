from collections.abc import Callable
from pathlib import Path
from time import perf_counter

from src.config import (
    DEFAULT_ALLOW_N,
    DEFAULT_MIN_SIMILARITY,
    DEFAULT_REFERENCE_DATABASE_PATH,
    DEFAULT_REFERENCE_METADATA_PATH,
    DEFAULT_TOP_N,
)
from src.contracts import AnalysisResult
from src.fasta import read_fasta
from src.logging_config import configure_logging
from src.reference.curation_validator import CuratedReferenceValidationError
from src.reference.loader import ReferenceDatabaseLoadError
from src.reference.metadata import ReferenceMetadataError
from src.reference.validator import ReferenceDatabaseValidationError
from src.search.cache import SearchCache
from src.services.classification_service import analyze_valid_sequences
from src.stats import summarize_sequences
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
    reference_database_path: str | Path = DEFAULT_REFERENCE_DATABASE_PATH,
    min_similarity: float = DEFAULT_MIN_SIMILARITY,
    allow_n: bool = DEFAULT_ALLOW_N,
    top_n: int = DEFAULT_TOP_N,
    progress_callback: ProgressCallback | None = None,
    reference_metadata_path: str | Path = DEFAULT_REFERENCE_METADATA_PATH,
    search_backend: str = "pairwise",
    blast_database_path: str | None = None,
    search_timeout_seconds: float = 30.0,
    search_database_hash: str = "",
    blast_version: str | None = None,
    search_cache: SearchCache | None = None,
) -> AnalysisResult:
    """Run the complete BioTrace FASTA analysis pipeline."""

    started_at = perf_counter()

    LOGGER.info(
        "Analysis started | format=fasta | file=%s | "
        "min_similarity=%.2f | allow_n=%s | top_n=%d",
        Path(file_path).name,
        min_similarity,
        allow_n,
        top_n,
    )

    _notify(progress_callback, 0.1, "Lendo arquivo FASTA...")
    sequences = read_fasta(str(file_path))

    LOGGER.info("FASTA loaded | sequence_count=%d", len(sequences))

    if not sequences:
        raise AnalysisError(
            "Nenhuma sequência foi encontrada no arquivo FASTA."
        )

    _notify(progress_callback, 0.25, "Validando sequências...")
    valid_sequences, invalid_sequences = validate_sequences(
        sequences,
        allow_n=allow_n,
    )

    if invalid_sequences:
        invalid_ids = [str(item["id"]) for item in invalid_sequences]
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
            "Análise interrompida por sequências inválidas.",
        )
        return {
            "input_format": "fasta",
            "summary": summarize_sequences([]),
            "total_sequences": len(sequences),
            "valid_count": 0,
            "invalid_count": len(invalid_sequences),
            "invalid_sequences": invalid_sequences,
            "results": [],
            "rankings": {},
            "reference_warnings": [],
            "execution_time_seconds": round(elapsed, 4),
        }

    _notify(
        progress_callback,
        0.45,
        "Calculando estatísticas e carregando referências...",
    )

    try:
        core_result = analyze_valid_sequences(
            valid_sequences,
            reference_database_path=reference_database_path,
            reference_metadata_path=reference_metadata_path,
            min_similarity=min_similarity,
            top_n=top_n,
            progress_callback=progress_callback,
            progress_start=0.6,
            progress_end=0.95,
            search_backend=search_backend,
            blast_database_path=blast_database_path,
            search_timeout_seconds=search_timeout_seconds,
            search_database_hash=search_database_hash,
            blast_version=blast_version,
            search_cache=search_cache,
        )
    except (
        ReferenceDatabaseLoadError,
        ReferenceDatabaseValidationError,
        CuratedReferenceValidationError,
        ReferenceMetadataError,
    ) as error:
        LOGGER.error("Reference database error | error=%s", error)
        raise AnalysisError(str(error)) from error

    for warning in core_result["reference_warnings"]:
        LOGGER.warning("Reference database warning | %s", warning)

    elapsed = perf_counter() - started_at
    _notify(progress_callback, 1.0, "Análise concluída.")

    LOGGER.info(
        "Analysis completed | format=fasta | valid=%d | invalid=%d | "
        "elapsed_seconds=%.4f",
        len(valid_sequences),
        len(invalid_sequences),
        elapsed,
    )

    return {
        "input_format": "fasta",
        "total_sequences": len(sequences),
        "valid_count": len(valid_sequences),
        "invalid_count": len(invalid_sequences),
        "invalid_sequences": invalid_sequences,
        **core_result,
        "execution_time_seconds": round(elapsed, 4),
    }
