"""Typed contracts shared by BioTrace services."""

from enum import IntEnum
from typing import Any, Literal, TypedDict


InputFormat = Literal[
    "fasta",
    "fastq",
]


class SequenceOrientation(IntEnum):
    """Explicit orientation contract for nucleotide sequences."""

    REVERSE = -1
    UNKNOWN = 0
    FORWARD = 1


class AnalysisResult(TypedDict, total=False):
    """Contract returned by BioTrace analysis services."""

    input_format: InputFormat

    summary: dict[str, Any]

    total_sequences: int
    valid_count: int
    invalid_count: int

    invalid_sequences: list[
        dict[str, Any]
    ]

    quality_summary: dict[
        str,
        Any,
    ]

    quality_report: list[
        dict[str, Any]
    ]

    results: list[
        dict[str, object]
    ]

    rankings: dict[
        str,
        list[dict[str, object]],
    ]

    reference_statistics: dict[
        str,
        int,
    ]

    reference_warnings: list[str]

    reference_metadata: (
        dict[str, Any] | None
    )

    execution_time_seconds: float

    analysis_report: dict[str, Any]
    report_export_paths: dict[str, str]
