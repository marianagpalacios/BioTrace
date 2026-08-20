"""Reproducible wrapper around BioTrace sequence analysis services."""

from dataclasses import asdict
from pathlib import Path
from time import perf_counter

from src.config import (
    DEFAULT_ALLOW_N,
    DEFAULT_ALIGNMENT_EXTEND_GAP_SCORE,
    DEFAULT_ALIGNMENT_MATCH_SCORE,
    DEFAULT_ALIGNMENT_MISMATCH_SCORE,
    DEFAULT_ALIGNMENT_MODE,
    DEFAULT_ALIGNMENT_OPEN_GAP_SCORE,
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
from src.contracts import AnalysisResult, InputFormat
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
from src.reporting.exporters import (
    build_export_metadata,
    export_report_bundle,
)
from src.reporting.report_service import build_analysis_report
from src.search.cache import SearchCache
from src.services.analysis_service import (
    ProgressCallback,
)
from src.services.sequence_analysis_service import (
    analyze_sequence_file,
)


LOGGER = configure_logging()


def _quality_records(
    result: AnalysisResult,
) -> list[dict[str, object]] | None:
    """Normalize the FASTQ QC report for reporting indicators."""

    if result.get("input_format") != "fastq":
        return None

    return [
        {
            "mean_quality": row.get("mean_phred"),
            "length": row.get("retained_length"),
            "passed_qc": row.get("passed"),
            "trimmed_bases": (
                int(row.get("trimmed_left", 0))
                + int(row.get("trimmed_right", 0))
            ),
        }
        for row in result.get("quality_report", [])
        if isinstance(row, dict)
    ]


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
    alignment_mode: str,
    alignment_match_score: float,
    alignment_mismatch_score: float,
    alignment_open_gap_score: float,
    alignment_extend_gap_score: float,
    search_backend: str,
    search_timeout_seconds: float,
    blast_version: str | None,
    blast_database_path: str | None,
    blast_database_sha256: str | None,
    cache_enabled: bool,
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
            "alignment_mode": (
                alignment_mode
            ),
            "alignment_match_score": (
                float(
                    alignment_match_score
                )
            ),
            "alignment_mismatch_score": (
                float(
                    alignment_mismatch_score
                )
            ),
            "alignment_open_gap_score": (
                float(
                    alignment_open_gap_score
                )
            ),
            "alignment_extend_gap_score": (
                float(
                    alignment_extend_gap_score
                )
            ),
            "search_backend": search_backend,
            "search_timeout_seconds": float(
                search_timeout_seconds
            ),
            "blast_version": blast_version,
            "blast_database_path": blast_database_path,
            "blast_database_sha256": blast_database_sha256,
            "cache_enabled": bool(
                cache_enabled
            ),
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
        "alignment_mode": (
            alignment_mode
        ),
        "alignment_match_score": (
            float(
                alignment_match_score
            )
        ),
        "alignment_mismatch_score": (
            float(
                alignment_mismatch_score
            )
        ),
        "alignment_open_gap_score": (
            float(
                alignment_open_gap_score
            )
        ),
        "alignment_extend_gap_score": (
            float(
                alignment_extend_gap_score
            )
        ),
        "search_backend": search_backend,
        "search_timeout_seconds": float(
            search_timeout_seconds
        ),
        "blast_version": blast_version,
        "blast_database_path": blast_database_path,
        "blast_database_sha256": blast_database_sha256,
        "cache_enabled": bool(
            cache_enabled
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
    search_backend: str = "pairwise",
    blast_database_path: str | None = None,
    blast_database_sha256: str | None = None,
    blast_version: str | None = None,
    search_timeout_seconds: float = 30.0,
    cache_enabled: bool = True,
) -> ReproducibleAnalysisResult:
    """Run BioTrace and persist execution provenance."""

    run_id = new_run_id()
    started_at_utc = utc_now_iso()
    started_at = perf_counter()

    if search_backend.strip().lower() == "pairwise":
        blast_version = None
        blast_database_path = None
        blast_database_sha256 = None

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
        alignment_mode=(
            DEFAULT_ALIGNMENT_MODE
        ),
        alignment_match_score=(
            DEFAULT_ALIGNMENT_MATCH_SCORE
        ),
        alignment_mismatch_score=(
            DEFAULT_ALIGNMENT_MISMATCH_SCORE
        ),
        alignment_open_gap_score=(
            DEFAULT_ALIGNMENT_OPEN_GAP_SCORE
        ),
        alignment_extend_gap_score=(
            DEFAULT_ALIGNMENT_EXTEND_GAP_SCORE
        ),
        search_backend=search_backend,
        search_timeout_seconds=search_timeout_seconds,
        blast_version=blast_version,
        blast_database_path=blast_database_path,
        blast_database_sha256=blast_database_sha256,
        cache_enabled=cache_enabled,
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
            search_backend=search_backend,
            blast_database_path=blast_database_path,
            search_timeout_seconds=search_timeout_seconds,
            search_database_hash=(
                blast_database_sha256 or ""
            ),
            blast_version=blast_version,
            search_cache=(
                SearchCache()
                if cache_enabled
                else None
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

    analysis_results = list(
        result.get("results", [])
    )

    identified_sequences = sum(
        bool(row.get("Identificada"))
        for row in analysis_results
    )

    report = build_analysis_report(
        input_format=input_format,
        search_backend=search_backend,
        results=analysis_results,
        total_sequences=int(
            result.get("total_sequences", 0)
        ),
        valid_sequences=int(
            result.get("valid_count", 0)
        ),
        identified_sequences=identified_sequences,
        quality_records=_quality_records(result),
        total_duration_seconds=float(
            result.get(
                "execution_time_seconds",
                duration,
            )
        ),
        warnings=list(
            result.get("reference_warnings", [])
        ),
        generated_at=finished_at_utc,
    )

    report_payload = asdict(report)
    report_directory = (
        Path(manifest_directory)
        / run_id
    )
    report_paths = export_report_bundle(
        report,
        report_directory,
    )
    report_exports = build_export_metadata(
        list(report_paths.values())
    )

    result["analysis_report"] = report_payload
    result["report_export_paths"] = {
        name: str(path)
        for name, path in report_paths.items()
    }

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
        report_version=report.metadata.biotrace_version,
        report_indicators={
            "general": report_payload["indicators"],
            "taxonomy": report_payload["taxonomy"],
            "quality": report_payload["quality"],
            "search": report_payload["search"],
            "performance": report_payload["performance"],
        },
        report_warnings=list(report.warnings),
        report_exports=report_exports,
        analysis_duration_seconds=(
            report.performance.total_duration_seconds
        ),
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
