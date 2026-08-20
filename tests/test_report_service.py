from src.reporting.report_service import (
    build_analysis_report,
)


def test_build_analysis_report():
    results = [
        {
            "Identificada": True,
            "Espécie escolhida": "Species alpha",
            "Identidade do alinhamento (%)": 99.0,
            "Cobertura do alinhamento (%)": 100.0,
            "Cache": "miss",
        }
    ]

    report = build_analysis_report(
        input_format="fasta",
        search_backend="pairwise",
        results=results,
        total_sequences=1,
        valid_sequences=1,
        identified_sequences=1,
        total_duration_seconds=0.5,
    )

    assert report.metadata.biotrace_version == "1.0.0-dev"
    assert report.metadata.input_format == "fasta"
    assert report.metadata.search_backend == "pairwise"

    assert report.indicators.total_sequences == 1
    assert report.indicators.identified_sequences == 1

    assert report.taxonomy.observed_species_count == 1

    assert report.quality.applicable is False

    assert report.search.mean_identity == 99.0
    assert report.search.mean_coverage == 100.0

    assert report.performance.cache_misses == 1

    assert report.warnings == []


def test_build_fasta_report_without_quality_metrics():
    results = [
        {
            "Identificada": True,
            "Espécie escolhida": "Species alpha",
            "Identidade do alinhamento (%)": 99.5,
            "Cobertura do alinhamento (%)": 100.0,
            "Cache": "hit",
        },
        {
            "Identificada": False,
            "Espécie escolhida": None,
            "Identidade do alinhamento (%)": 90.0,
            "Cobertura do alinhamento (%)": 80.0,
            "Cache": "miss",
        },
    ]

    report = build_analysis_report(
        input_format="fasta",
        search_backend="pairwise",
        results=results,
        total_sequences=2,
        valid_sequences=2,
        identified_sequences=1,
        total_duration_seconds=0.4,
    )

    assert report.metadata.input_format == "fasta"

    assert report.indicators.total_sequences == 2
    assert report.indicators.valid_sequences == 2
    assert report.indicators.identified_sequences == 1
    assert report.indicators.identification_rate == 50.0

    assert report.quality.applicable is False
    assert report.quality.mean_phred is None
    assert report.quality.mean_length is None

    assert report.taxonomy.observed_species_count == 1

    assert report.search.mean_identity == 94.75
    assert report.performance.cache_hits == 1
    assert report.performance.cache_misses == 1


def test_build_fastq_report_with_quality_metrics():
    results = [
        {
            "Identificada": True,
            "Espécie escolhida": "Species alpha",
            "Identidade do alinhamento (%)": 100.0,
            "Cobertura do alinhamento (%)": 100.0,
            "E-value": 1e-50,
            "Bit score": 200.0,
            "Cache": "miss",
        },
        {
            "Identificada": True,
            "Espécie escolhida": "Species alpha",
            "Identidade do alinhamento (%)": 98.0,
            "Cobertura do alinhamento (%)": 95.0,
            "E-value": 1e-20,
            "Bit score": 150.0,
            "Cache": "hit",
        },
    ]

    quality_records = [
        {
            "mean_quality": 30.0,
            "length": 100,
            "passed_qc": True,
            "trimmed_bases": 5,
        },
        {
            "mean_quality": 25.0,
            "length": 90,
            "passed_qc": True,
            "trimmed_bases": 0,
        },
    ]

    report = build_analysis_report(
        input_format="fastq",
        search_backend="blast",
        results=results,
        total_sequences=2,
        valid_sequences=2,
        identified_sequences=2,
        quality_records=quality_records,
        total_duration_seconds=1.0,
    )

    assert report.metadata.input_format == "fastq"
    assert report.metadata.search_backend == "blast"

    assert report.quality.applicable is True

    assert report.quality.mean_phred == 27.5
    assert report.quality.min_phred == 25.0
    assert report.quality.max_phred == 30.0

    assert report.quality.mean_length == 95.0
    assert report.quality.min_length == 90
    assert report.quality.max_length == 100

    assert report.quality.qc_passed_reads == 2
    assert report.quality.qc_rejected_reads == 0

    assert report.quality.trimmed_reads == 1
    assert report.quality.trimmed_bases == 5

    assert report.taxonomy.observed_species_count == 1

    assert report.search.mean_identity == 99.0
    assert report.search.mean_coverage == 97.5

    assert report.search.min_evalue == 1e-50
    assert report.search.max_evalue == 1e-20

    assert report.performance.cache_hits == 1
    assert report.performance.cache_misses == 1
