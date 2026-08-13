"""Typed contracts shared by BioTrace services."""

from typing import Any, TypedDict


class AnalysisResult(TypedDict, total=False):
    """Contract returned by the core analysis service."""

    summary: dict[str, Any]

    total_sequences: int
    valid_count: int
    invalid_count: int

    invalid_sequences: list[
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