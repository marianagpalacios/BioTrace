from src.reporting.contracts import (
    AnalysisIndicators,
    PerformanceIndicators,
    QualityIndicators,
    SearchIndicators,
)


def generate_report_warnings(
    *,
    analysis: AnalysisIndicators,
    quality: QualityIndicators,
    search: SearchIndicators,
    performance: PerformanceIndicators,
) -> list[str]:
    """Generate objective warnings from report indicators."""

    warnings: list[str] = []

    if analysis.rejection_rate >= 25.0:
        warnings.append(
            "High rejection rate: "
            f"{analysis.rejection_rate:.2f}% "
            "of input sequences were rejected."
        )

    if analysis.identification_rate < 70.0:
        warnings.append(
            "Low identification rate: "
            f"{analysis.identification_rate:.2f}% "
            "of valid sequences were identified."
        )

    if (
        quality.applicable
        and quality.qc_rejected_reads is not None
        and analysis.total_sequences > 0
    ):
        qc_rejection_rate = (
            quality.qc_rejected_reads
            / analysis.total_sequences
            * 100.0
        )

        if qc_rejection_rate >= 25.0:
            warnings.append(
                "FASTQ quality-control rejection rate: "
                f"{qc_rejection_rate:.2f}%."
            )

    if search.below_95_identity > 0:
        warnings.append(
            f"{search.below_95_identity} search result(s) "
            "had identity below 95%."
        )

    if performance.search_timeouts > 0:
        warnings.append(
            f"{performance.search_timeouts} "
            "search timeout(s) occurred."
        )

    if performance.search_errors > 0:
        warnings.append(
            f"{performance.search_errors} "
            "search error(s) occurred."
        )

    return warnings