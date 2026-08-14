"""Reproducible wrapper around BioTrace sequence analysis services."""

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
    RUNS_DIRECTORY,
)
from src.contracts import InputFormat
from src.logging_config import configure_logging
from src.reproducibility.contracts import (
    AnalysisParameters,
    ReproducibleAnalysisResult,
    RunStatus,
)
from src.reproducibility.manifest import (
    build_run_manifest,
    new_run_id,
    utc_now_iso,
    write_run_manifest,
)
from src.services.analysis_service import (
    ProgressCallback,
)
from src.services.sequence_analysis_service import (
    analyze_sequence_file,
)


LOGGER = configure_logging()


def _analysis_parameters(
    *,
    input_format: InputFormat,
    min_similarity: float,
    allow_n: bool,
    top_n: int,
    min_mean_quality: float,
    min_length: int,
    max_length: int,
    trim_ends: bool,
    trim_quality_threshold: int,
) -> AnalysisParameters:
    """Build a format-aware parameter snapshot."""

    if input_format == "fasta":
        return {
            "input_format": "fasta",
            "min_similarity": float(
                min_similarity
            ),
            "allow_n": bool(allow_n),
            "top_n": int(top_n),
            "min_mean_quality": None,
            "min_length": None,
            "max_length": None,
            "trim_ends": None,
            "trim_quality_threshold": None,
        }

    return {
        "input_format": "fastq",
        "min_similarity": float(
            min_similarity
        ),
        "allow_n": bool(allow_n),
        "top_n": int(top_n),
        "min_mean_quality": float(
            min_mean_quality
        ),
        "min_length": int(min_length),
        "max_length": int(max_length),
        "trim_ends": bool(trim_ends),
        "trim_quality_threshold": int(
            trim_quality_threshold
        ),
    }


def analyze_sequence_file_reproducibly(
    file_path: str,
    *,
    input_format: InputFormat,
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
    manifest_directory: str | Path = RUNS_DIRECTORY,
    min_mean_quality: float = (
        DEFAULT_FASTQ_MIN_MEAN_QUALITY
    ),
    min_length: int = DEFAULT_FASTQ_MIN_LENGTH,
    max_length: int = DEFAULT_FASTQ_MAX_LENGTH,
    trim_ends: bool = DEFAULT_FASTQ_TRIM_ENDS,
    trim_quality_threshold: int = (
        DEFAULT_FASTQ_TRIM_QUALITY
    ),
) -> ReproducibleAnalysisResult:
    """Run BioTrace and persist execution provenance."""

    run_id = new_run_id()
    started_at_utc = utc_now_iso()
    started_at = perf_counter()

    parameters = _analysis_parameters(
        input_format=input_format,
        min_similarity=min_similarity,
        allow_n=allow_n,
        top_n=top_n,
        min_mean_quality=min_mean_quality,
        min_length=min_length,
        max_length=max_length,
        trim_ends=trim_ends,
        trim_quality_threshold=(
            trim_quality_threshold
        ),
    )

    try:
        result = analyze_sequence_file(
            file_path=file_path,
            input_format=input_format,
            reference_database_path=(
                reference_database_path
            ),
            min_similarity=min_similarity,
            allow_n=allow_n,
            top_n=top_n,
            progress_callback=progress_callback,
            reference_metadata_path=(
                reference_metadata_path
            ),
            min_mean_quality=min_mean_quality,
            min_length=min_length,
            max_length=max_length,
            trim_ends=trim_ends,
            trim_quality_threshold=(
                trim_quality_threshold
            ),
        )

    except Exception as error:
        finished_at_utc = utc_now_iso()
        duration = (
            perf_counter()
            - started_at
        )

        try:
            failed_manifest = build_run_manifest(
                run_id=run_id,
                status="failed",
                started_at_utc=started_at_utc,
                finished_at_utc=(
                    finished_at_utc
                ),
                duration_seconds=duration,
                input_path=file_path,
                reference_database_path=(
                    reference_database_path
                ),
                reference_metadata_path=(
                    reference_metadata_path
                ),
                parameters=parameters,
                result=None,
                error=(
                    f"{type(error).__name__}: "
                    f"{error}"
                ),
            )

            manifest_path = write_run_manifest(
                failed_manifest,
                manifest_directory,
            )

            LOGGER.error(
                "Failed run manifest "
                "written | run_id=%s | "
                "manifest=%s",
                run_id,
                manifest_path,
            )

        except Exception:
            LOGGER.exception(
                "Could not persist failed "
                "run manifest | run_id=%s",
                run_id,
            )

        raise

    finished_at_utc = utc_now_iso()
    duration = (
        perf_counter()
        - started_at
    )

    status: RunStatus = (
        "completed"
        if result.get(
            "valid_count",
            0,
        ) > 0
        else "stopped"
    )

    manifest = build_run_manifest(
        run_id=run_id,
        status=status,
        started_at_utc=started_at_utc,
        finished_at_utc=finished_at_utc,
        duration_seconds=duration,
        input_path=file_path,
        reference_database_path=(
            reference_database_path
        ),
        reference_metadata_path=(
            reference_metadata_path
        ),
        parameters=parameters,
        result=result,
    )

    manifest_path = write_run_manifest(
        manifest,
        manifest_directory,
    )

    result["run_manifest"] = manifest
    result["run_manifest_path"] = str(
        manifest_path
    )

    return result


def analyze_fasta_reproducibly(
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
    manifest_directory: str | Path = RUNS_DIRECTORY,
) -> ReproducibleAnalysisResult:
    """Backward-compatible reproducible FASTA entry point."""

    return analyze_sequence_file_reproducibly(
        file_path=file_path,
        input_format="fasta",
        reference_database_path=(
            reference_database_path
        ),
        min_similarity=min_similarity,
        allow_n=allow_n,
        top_n=top_n,
        progress_callback=progress_callback,
        reference_metadata_path=(
            reference_metadata_path
        ),
        manifest_directory=(
            manifest_directory
        ),
    )
