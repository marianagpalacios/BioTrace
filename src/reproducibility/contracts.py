"""Typed contracts for run reproducibility."""

from typing import Literal, TypedDict

from src.contracts import (
    AnalysisResult,
    InputFormat,
)


RunStatus = Literal[
    "completed",
    "stopped",
    "failed",
]


class AnalysisParameters(TypedDict):
    input_format: InputFormat

    min_similarity: float
    allow_n: bool
    top_n: int

    min_mean_quality: float | None
    min_length: int | None
    max_length: int | None
    trim_ends: bool | None
    trim_quality_threshold: int | None


class InputSnapshot(TypedDict):
    filename: str
    sha256: str
    size_bytes: int


class ReferenceSnapshot(TypedDict):
    database_filename: str
    csv_sha256: str | None

    metadata_filename: str
    metadata_sha256: str | None

    version: str | None
    marker: str | None
    source: str | None


class SoftwareSnapshot(TypedDict):
    name: str
    version: str

    git_commit: str | None
    git_dirty: bool | None


class EnvironmentSnapshot(TypedDict):
    python_version: str
    python_implementation: str
    platform: str


class RunCounts(TypedDict):
    total_sequences: int
    valid_count: int
    invalid_count: int
    result_count: int


class RunManifest(TypedDict):
    schema_version: str

    run_id: str
    run_fingerprint: str

    status: RunStatus

    started_at_utc: str
    finished_at_utc: str
    duration_seconds: float

    input: InputSnapshot

    reference_database: (
        ReferenceSnapshot
    )

    parameters: AnalysisParameters

    software: SoftwareSnapshot
    environment: EnvironmentSnapshot

    counts: RunCounts

    result_sha256: str | None
    error: str | None


class ReproducibleAnalysisResult(
    AnalysisResult
):
    run_manifest: RunManifest
    run_manifest_path: str
