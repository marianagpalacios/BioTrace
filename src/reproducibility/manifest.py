"""Build and persist reproducible BioTrace run manifests."""

import json
import platform
import subprocess

from datetime import (
    datetime,
    timezone,
)
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

from src.config import (
    PROJECT_ROOT,
    RUNS_DIRECTORY,
)
from src.reproducibility.contracts import (
    AnalysisParameters,
    EnvironmentSnapshot,
    InputSnapshot,
    ReferenceSnapshot,
    RunCounts,
    RunManifest,
    RunStatus,
    SoftwareSnapshot,
)
from src.reproducibility.hashing import (
    sha256_file,
    sha256_json,
)
from src.version import __version__


MANIFEST_SCHEMA_VERSION = "1.4"


_RESULT_HASH_FIELDS = (
    "input_format",
    "quality_summary",
    "quality_report",
    "summary",
    "total_sequences",
    "valid_count",
    "invalid_count",
    "invalid_sequences",
    "results",
    "rankings",
    "reference_statistics",
    "reference_warnings",
    "reference_metadata",
)


def new_run_id() -> str:
    """Return a unique ID for one execution."""

    return str(uuid4())


def utc_now_iso() -> str:
    """Return current UTC time in ISO-8601."""

    return (
        datetime.now(
            timezone.utc
        )
        .isoformat(
            timespec="seconds"
        )
        .replace(
            "+00:00",
            "Z",
        )
    )


def _optional_sha256(
    path: Path,
) -> str | None:
    if not path.exists():
        return None

    return sha256_file(path)


def _read_reference_metadata(
    path: Path,
) -> dict[str, str | None]:
    result: dict[
        str,
        str | None,
    ] = {
        "version": None,
        "marker": None,
        "source": None,
    }

    if not path.exists():
        return result

    try:
        payload = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    except (
        OSError,
        json.JSONDecodeError,
    ):
        return result

    for key in result:
        value = payload.get(key)

        if value is not None:
            result[key] = str(value)

    return result


def _git_snapshot() -> tuple[
    str | None,
    bool | None,
]:
    """Read current Git commit and dirty status."""

    try:
        commit_result = subprocess.run(
            [
                "git",
                "rev-parse",
                "HEAD",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )

        status_result = subprocess.run(
            [
                "git",
                "status",
                "--porcelain",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )

    except (
        OSError,
        subprocess.CalledProcessError,
    ):
        return None, None

    return (
        commit_result.stdout.strip(),
        bool(
            status_result.stdout.strip()
        ),
    )


def _software_snapshot() -> SoftwareSnapshot:
    commit, dirty = _git_snapshot()

    return {
        "name": "BioTrace",
        "version": __version__,
        "git_commit": commit,
        "git_dirty": dirty,
    }


def _environment_snapshot() -> EnvironmentSnapshot:
    return {
        "python_version": (
            platform.python_version()
        ),
        "python_implementation": (
            platform.python_implementation()
        ),
        "platform": platform.platform(),
    }


def _input_snapshot(
    input_path: Path,
) -> InputSnapshot:
    return {
        "filename": input_path.name,
        "sha256": sha256_file(
            input_path
        ),
        "size_bytes": (
            input_path.stat().st_size
        ),
    }


def _reference_snapshot(
    database_path: Path,
    metadata_path: Path,
) -> ReferenceSnapshot:
    metadata = (
        _read_reference_metadata(
            metadata_path
        )
    )

    return {
        "database_filename": (
            database_path.name
        ),
        "csv_sha256": (
            _optional_sha256(
                database_path
            )
        ),
        "metadata_filename": (
            metadata_path.name
        ),
        "metadata_sha256": (
            _optional_sha256(
                metadata_path
            )
        ),
        "version": (
            metadata["version"]
        ),
        "marker": (
            metadata["marker"]
        ),
        "source": (
            metadata["source"]
        ),
    }


def _run_counts(
    result: dict[str, Any] | None,
) -> RunCounts:
    if result is None:
        return {
            "total_sequences": 0,
            "valid_count": 0,
            "invalid_count": 0,
            "result_count": 0,
        }

    return {
        "total_sequences": int(
            result.get(
                "total_sequences",
                0,
            )
        ),
        "valid_count": int(
            result.get(
                "valid_count",
                0,
            )
        ),
        "invalid_count": int(
            result.get(
                "invalid_count",
                0,
            )
        ),
        "result_count": len(
            result.get(
                "results",
                [],
            )
        ),
    }


def _result_sha256(
    result: dict[str, Any] | None,
) -> str | None:
    if result is None:
        return None

    stable_payload = {
        key: result[key]
        for key in _RESULT_HASH_FIELDS
        if key in result
    }

    return sha256_json(
        stable_payload
    )


def build_run_fingerprint(
    *,
    input_snapshot: InputSnapshot,
    reference_snapshot: ReferenceSnapshot,
    parameters: AnalysisParameters,
    software: SoftwareSnapshot,
) -> str:
    """Hash inputs that define the computational run."""

    payload = {
        "schema_version": (
            MANIFEST_SCHEMA_VERSION
        ),
        "input_sha256": (
            input_snapshot["sha256"]
        ),
        "reference_csv_sha256": (
            reference_snapshot[
                "csv_sha256"
            ]
        ),
        "reference_metadata_sha256": (
            reference_snapshot[
                "metadata_sha256"
            ]
        ),
        "parameters": parameters,
        "software_version": (
            software["version"]
        ),
        "git_commit": (
            software["git_commit"]
        ),
    }

    return sha256_json(payload)


def build_run_manifest(
    *,
    run_id: str,
    status: RunStatus,
    started_at_utc: str,
    finished_at_utc: str,
    duration_seconds: float,
    input_path: str | Path,
    reference_database_path: str | Path,
    reference_metadata_path: str | Path,
    parameters: AnalysisParameters,
    result: dict[str, Any] | None,
    error: str | None = None,
    report_version: str | None = None,
    report_indicators: dict[str, object] | None = None,
    report_warnings: list[str] | None = None,
    report_exports: list[dict[str, object]] | None = None,
    analysis_duration_seconds: float | None = None,
) -> RunManifest:
    """Create a complete execution manifest."""

    input_snapshot = (
        _input_snapshot(
            Path(input_path)
        )
    )

    reference_snapshot = (
        _reference_snapshot(
            Path(
                reference_database_path
            ),
            Path(
                reference_metadata_path
            ),
        )
    )

    software = (
        _software_snapshot()
    )

    fingerprint = (
        build_run_fingerprint(
            input_snapshot=(
                input_snapshot
            ),
            reference_snapshot=(
                reference_snapshot
            ),
            parameters=parameters,
            software=software,
        )
    )

    return {
        "schema_version": (
            MANIFEST_SCHEMA_VERSION
        ),
        "run_id": run_id,
        "run_fingerprint": fingerprint,
        "status": status,
        "started_at_utc": (
            started_at_utc
        ),
        "finished_at_utc": (
            finished_at_utc
        ),
        "duration_seconds": round(
            max(
                duration_seconds,
                0.0,
            ),
            4,
        ),
        "input": input_snapshot,
        "reference_database": (
            reference_snapshot
        ),
        "parameters": parameters,
        "software": software,
        "environment": (
            _environment_snapshot()
        ),
        "counts": (
            _run_counts(result)
        ),
        "result_sha256": (
            _result_sha256(result)
        ),
        "error": error,
        "report_version": report_version,
        "report_indicators": report_indicators,
        "report_warnings": report_warnings,
        "report_exports": report_exports,
        "analysis_duration_seconds": (
            analysis_duration_seconds
        ),
    }


def write_run_manifest(
    manifest: RunManifest,
    directory: str | Path = (
        RUNS_DIRECTORY
    ),
) -> Path:
    """Persist one manifest as formatted JSON."""

    output_directory = Path(
        directory
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_directory
        / f"{manifest['run_id']}.json"
    )

    output_path.write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return output_path


def load_run_manifest(
    manifest_path: str | Path,
) -> RunManifest:
    """Load one persisted run manifest."""

    payload = json.loads(
        Path(
            manifest_path
        ).read_text(
            encoding="utf-8"
        )
    )

    return cast(
        RunManifest,
        payload,
    )
