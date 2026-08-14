"""FASTQ analysis service with basic quality control."""

from pathlib import Path
from time import perf_counter

from src.config import (
    DEFAULT_ALLOW_N,
    DEFAULT_FASTQ_MAX_LENGTH,
    DEFAULT_FASTQ_MIN_LENGTH,
    DEFAULT_FASTQ_MIN_MEAN_QUALITY,
    DEFAULT_FASTQ_TRIM_ENDS,
    DEFAULT_FASTQ_TRIM_QUALITY,
    DEFAULT_MIN_SIMILARITY,
    DEFAULT_REFERENCE_DATABASE_PATH,
    DEFAULT_REFERENCE_METADATA_PATH,
    DEFAULT_TOP_N,
)
from src.contracts import AnalysisResult
from src.fastq import (
    FastqReadError,
    read_fastq,
)
from src.logging_config import configure_logging
from src.quality import (
    QualityControlConfig,
    QualityControlConfigurationError,
    quality_control_fastq,
)
from src.reference.curation_validator import (
    CuratedReferenceValidationError,
)
from src.reference.loader import (
    ReferenceDatabaseLoadError,
)
from src.reference.metadata import (
    ReferenceMetadataError,
)
from src.reference.validator import (
    ReferenceDatabaseValidationError,
)
from src.services.analysis_service import (
    AnalysisError,
    ProgressCallback,
)
from src.services.classification_service import (
    analyze_valid_sequences,
)
from src.stats import summarize_sequences


LOGGER = configure_logging()


def _notify(
    progress_callback: ProgressCallback | None,
    value: float,
    message: str,
) -> None:
    if progress_callback:
        progress_callback(
            value,
            message,
        )


def analyze_fastq_file(
    file_path: str,
    reference_database_path: str | Path = (
        DEFAULT_REFERENCE_DATABASE_PATH
    ),
    min_similarity: float = DEFAULT_MIN_SIMILARITY,
    allow_n: bool = DEFAULT_ALLOW_N,
    top_n: int = DEFAULT_TOP_N,
    progress_callback: ProgressCallback | None = None,
    reference_metadata_path: str | Path = (
        DEFAULT_REFERENCE_METADATA_PATH
    ),
    min_mean_quality: float = (
        DEFAULT_FASTQ_MIN_MEAN_QUALITY
    ),
    min_length: int = DEFAULT_FASTQ_MIN_LENGTH,
    max_length: int = DEFAULT_FASTQ_MAX_LENGTH,
    trim_ends: bool = DEFAULT_FASTQ_TRIM_ENDS,
    trim_quality_threshold: int = (
        DEFAULT_FASTQ_TRIM_QUALITY
    ),
) -> AnalysisResult:
    """Run FASTQ parsing, QC and classification."""

    started_at = perf_counter()

    LOGGER.info(
        "Analysis started | "
        "format=fastq | file=%s | "
        "min_similarity=%.2f | "
        "min_mean_quality=%.2f | "
        "min_length=%d | max_length=%d | "
        "trim_ends=%s | trim_quality=%d",
        Path(file_path).name,
        min_similarity,
        min_mean_quality,
        min_length,
        max_length,
        trim_ends,
        trim_quality_threshold,
    )

    _notify(
        progress_callback,
        0.1,
        "Lendo arquivo FASTQ...",
    )

    try:
        records = read_fastq(
            file_path
        )

    except FastqReadError as error:
        raise AnalysisError(
            str(error)
        ) from error

    if not records:
        raise AnalysisError(
            "Nenhum registro foi "
            "encontrado no arquivo FASTQ."
        )

    _notify(
        progress_callback,
        0.3,
        "Aplicando controle "
        "de qualidade FASTQ...",
    )

    config = QualityControlConfig(
        min_mean_quality=min_mean_quality,
        min_length=min_length,
        max_length=max_length,
        trim_ends=trim_ends,
        trim_quality_threshold=(
            trim_quality_threshold
        ),
    )

    try:
        qc = quality_control_fastq(
            records,
            config,
            allow_n=allow_n,
        )

    except QualityControlConfigurationError as error:
        raise AnalysisError(
            str(error)
        ) from error

    valid_sequences = (
        qc.approved_sequences
    )

    invalid_sequences = (
        qc.rejected_records
    )

    if not valid_sequences:
        elapsed = (
            perf_counter()
            - started_at
        )

        _notify(
            progress_callback,
            1.0,
            "Análise interrompida: "
            "nenhum read passou no QC.",
        )

        return {
            "input_format": "fastq",
            "summary": summarize_sequences([]),
            "quality_summary": qc.summary,
            "quality_report": qc.report,
            "total_sequences": len(records),
            "valid_count": 0,
            "invalid_count": len(
                invalid_sequences
            ),
            "invalid_sequences": (
                invalid_sequences
            ),
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
        0.5,
        "Classificando "
        "reads aprovados...",
    )

    try:
        core_result = analyze_valid_sequences(
            valid_sequences,
            reference_database_path=(
                reference_database_path
            ),
            reference_metadata_path=(
                reference_metadata_path
            ),
            min_similarity=min_similarity,
            top_n=top_n,
            progress_callback=(
                progress_callback
            ),
            progress_start=0.55,
            progress_end=0.95,
        )

    except (
        ReferenceDatabaseLoadError,
        ReferenceDatabaseValidationError,
        CuratedReferenceValidationError,
        ReferenceMetadataError,
    ) as error:
        raise AnalysisError(
            str(error)
        ) from error

    elapsed = (
        perf_counter()
        - started_at
    )

    _notify(
        progress_callback,
        1.0,
        "Análise FASTQ concluída.",
    )

    return {
        "input_format": "fastq",
        "quality_summary": qc.summary,
        "quality_report": qc.report,
        "total_sequences": len(records),
        "valid_count": len(
            valid_sequences
        ),
        "invalid_count": len(
            invalid_sequences
        ),
        "invalid_sequences": (
            invalid_sequences
        ),
        **core_result,
        "execution_time_seconds": round(
            elapsed,
            4,
        ),
    }