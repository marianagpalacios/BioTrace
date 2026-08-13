"""Reproducible wrapper around the BioTrace analysis service."""

from pathlib import Path
from time import perf_counter

from src.config import (
    DEFAULT_ALLOW_N,
    DEFAULT_MIN_SIMILARITY,
    DEFAULT_REFERENCE_DATABASE_PATH,
    DEFAULT_REFERENCE_METADATA_PATH,
    DEFAULT_TOP_N,
    RUNS_DIRECTORY,
)
from src.logging_config import (
    configure_logging,
)
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
    analyze_fasta_file,
)


LOGGER = configure_logging()


def analyze_fasta_reproducibly(
    file_path: str,
    reference_database_path: str | Path = (
        DEFAULT_REFERENCE_DATABASE_PATH
    ),
    min_similarity: float = (
        DEFAULT_MIN_SIMILARITY
    ),
    allow_n: bool = DEFAULT_ALLOW_N,
    top_n: int = DEFAULT_TOP_N,
    progress_callback: (
        ProgressCallback | None
    ) = None,
    reference_metadata_path: str | Path = (
        DEFAULT_REFERENCE_METADATA_PATH
    ),
    manifest_directory: str | Path = (
        RUNS_DIRECTORY
    ),
) -> ReproducibleAnalysisResult:
    """Run BioTrace and persist execution provenance."""

    run_id = new_run_id()

    started_at_utc = (
        utc_now_iso()
    )

    started_at = perf_counter()

    parameters: AnalysisParameters = {
        "min_similarity": float(
            min_similarity
        ),
        "allow_n": bool(allow_n),
        "top_n": int(top_n),
    }

    try:
        result = analyze_fasta_file(
            file_path=file_path,
            reference_database_path=(
                reference_database_path
            ),
            min_similarity=min_similarity,
            allow_n=allow_n,
            top_n=top_n,
            progress_callback=(
                progress_callback
            ),
            reference_metadata_path=(
                reference_metadata_path
            ),
        )

    except Exception as error:
        finished_at_utc = (
            utc_now_iso()
        )

        duration = (
            perf_counter()
            - started_at
        )

        try:
            failed_manifest = (
                build_run_manifest(
                    run_id=run_id,
                    status="failed",
                    started_at_utc=(
                        started_at_utc
                    ),
                    finished_at_utc=(
                        finished_at_utc
                    ),
                    duration_seconds=(
                        duration
                    ),
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
            )

            manifest_path = (
                write_run_manifest(
                    failed_manifest,
                    manifest_directory,
                )
            )

            LOGGER.error(
                "Failed run manifest written | "
                "run_id=%s | manifest=%s",
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

    finished_at_utc = (
        utc_now_iso()
    )

    duration = (
        perf_counter()
        - started_at
    )

    status: RunStatus

    if result.get(
        "valid_count",
        0,
    ) > 0:
        status = "completed"

    else:
        status = "stopped"

    manifest = build_run_manifest(
        run_id=run_id,
        status=status,
        started_at_utc=(
            started_at_utc
        ),
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
        result=result,
    )

    manifest_path = (
        write_run_manifest(
            manifest,
            manifest_directory,
        )
    )

    result["run_manifest"] = (
        manifest
    )

    result["run_manifest_path"] = (
        str(manifest_path)
    )

    LOGGER.info(
        "Run manifest written | "
        "run_id=%s | fingerprint=%s",
        manifest["run_id"],
        manifest["run_fingerprint"],
    )

    return result