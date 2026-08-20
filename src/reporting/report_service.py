from datetime import datetime, timezone

from src.reporting.contracts import (
    AnalysisReport,
    ReportMetadata,
)
from src.reporting.indicators import (
    calculate_analysis_indicators,
    calculate_performance_indicators,
    calculate_quality_indicators,
    calculate_search_indicators,
    calculate_taxonomy_indicators,
)
from src.reporting.warnings import (
    generate_report_warnings,
)
from src.version import __version__


def build_analysis_report(
    *,
    input_format: str,
    search_backend: str,
    results: list[dict[str, object]],
    total_sequences: int,
    valid_sequences: int,
    identified_sequences: int,
    quality_records: list[dict[str, object]] | None = None,
    total_duration_seconds: float | None = None,
    search_errors: int = 0,
    search_timeouts: int = 0,
    warnings: list[str] | None = None,
) -> AnalysisReport:
    """Build a structured report from one BioTrace analysis."""

    metadata = ReportMetadata(
        biotrace_version=__version__,
        input_format=input_format,
        search_backend=search_backend,
        generated_at=datetime.now(
            timezone.utc
        ).isoformat(),
    )

    indicators = calculate_analysis_indicators(
        total_sequences=total_sequences,
        valid_sequences=valid_sequences,
        identified_sequences=identified_sequences,
    )

    taxonomy = calculate_taxonomy_indicators(
        results
    )

    quality = calculate_quality_indicators(
        input_format=input_format,
        quality_records=quality_records,
    )

    search = calculate_search_indicators(
        results
    )

    performance = calculate_performance_indicators(
        total_sequences=total_sequences,
        total_duration_seconds=total_duration_seconds,
        results=results,
        search_errors=search_errors,
        search_timeouts=search_timeouts,
    )

    automatic_warnings = generate_report_warnings(
        analysis=indicators,
        quality=quality,
        search=search,
        performance=performance,
    )

    return AnalysisReport(
        metadata=metadata,
        indicators=indicators,
        taxonomy=taxonomy,
        quality=quality,
        search=search,
        performance=performance,
        results=results,
        warnings=[
            *automatic_warnings,
            *(warnings or []),
        ],
    )
