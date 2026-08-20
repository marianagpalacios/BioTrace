from src.reporting.contracts import (
    AnalysisIndicators,
    PerformanceIndicators,
    QualityIndicators,
    SearchIndicators,
)
from src.reporting.warnings import (
    generate_report_warnings,
)


def test_generate_multiple_report_warnings():
    analysis = AnalysisIndicators(
        total_sequences=100,
        valid_sequences=60,
        rejected_sequences=40,
        identified_sequences=30,
        unidentified_sequences=30,
        validation_rate=60.0,
        rejection_rate=40.0,
        identification_rate=50.0,
        unidentified_rate=50.0,
    )

    quality = QualityIndicators(
        applicable=True,
        mean_phred=20.0,
        min_phred=10.0,
        max_phred=30.0,
        mean_length=90.0,
        min_length=80,
        max_length=100,
        qc_passed_reads=60,
        qc_rejected_reads=40,
        trimmed_reads=10,
        trimmed_bases=50,
    )

    search = SearchIndicators(
        mean_identity=92.0,
        min_identity=90.0,
        max_identity=94.0,
        mean_coverage=90.0,
        min_coverage=80.0,
        max_coverage=100.0,
        mean_evalue=None,
        min_evalue=None,
        max_evalue=None,
        mean_bit_score=None,
        min_bit_score=None,
        max_bit_score=None,
        above_99_identity=0,
        between_95_and_99_identity=0,
        below_95_identity=3,
    )

    performance = PerformanceIndicators(
        total_duration_seconds=2.0,
        mean_seconds_per_sequence=0.02,
        cache_hits=0,
        cache_misses=100,
        cache_hit_rate=0.0,
        search_errors=1,
        search_timeouts=2,
    )

    warnings = generate_report_warnings(
        analysis=analysis,
        quality=quality,
        search=search,
        performance=performance,
    )

    assert any(
        "High rejection rate" in warning
        for warning in warnings
    )

    assert any(
        "Low identification rate" in warning
        for warning in warnings
    )

    assert any(
        "quality-control rejection rate" in warning
        for warning in warnings
    )

    assert any(
        "identity below 95%" in warning
        for warning in warnings
    )

    assert any(
        "timeout" in warning
        for warning in warnings
    )

    assert any(
        "search error" in warning
        for warning in warnings
    )

    from src.reporting.contracts import (
    AnalysisIndicators,
    PerformanceIndicators,
    QualityIndicators,
    SearchIndicators,
)
from src.reporting.warnings import (
    generate_report_warnings,
)


def test_generate_multiple_report_warnings():
    analysis = AnalysisIndicators(
        total_sequences=100,
        valid_sequences=60,
        rejected_sequences=40,
        identified_sequences=30,
        unidentified_sequences=30,
        validation_rate=60.0,
        rejection_rate=40.0,
        identification_rate=50.0,
        unidentified_rate=50.0,
    )

    quality = QualityIndicators(
        applicable=True,
        mean_phred=20.0,
        min_phred=10.0,
        max_phred=30.0,
        mean_length=90.0,
        min_length=80,
        max_length=100,
        qc_passed_reads=60,
        qc_rejected_reads=40,
        trimmed_reads=10,
        trimmed_bases=50,
    )

    search = SearchIndicators(
        mean_identity=92.0,
        min_identity=90.0,
        max_identity=94.0,
        mean_coverage=90.0,
        min_coverage=80.0,
        max_coverage=100.0,
        mean_evalue=None,
        min_evalue=None,
        max_evalue=None,
        mean_bit_score=None,
        min_bit_score=None,
        max_bit_score=None,
        above_99_identity=0,
        between_95_and_99_identity=0,
        below_95_identity=3,
    )

    performance = PerformanceIndicators(
        total_duration_seconds=2.0,
        mean_seconds_per_sequence=0.02,
        cache_hits=0,
        cache_misses=100,
        cache_hit_rate=0.0,
        search_errors=1,
        search_timeouts=2,
    )

    warnings = generate_report_warnings(
        analysis=analysis,
        quality=quality,
        search=search,
        performance=performance,
    )

    assert any(
        "High rejection rate" in warning
        for warning in warnings
    )

    assert any(
        "Low identification rate" in warning
        for warning in warnings
    )

    assert any(
        "quality-control rejection rate" in warning
        for warning in warnings
    )

    assert any(
        "identity below 95%" in warning
        for warning in warnings
    )

    assert any(
        "timeout" in warning
        for warning in warnings
    )

    assert any(
        "search error" in warning
        for warning in warnings
    )