import pytest

from src.reporting.indicators import (
    calculate_analysis_indicators,
    calculate_performance_indicators,
    calculate_quality_indicators,
    calculate_search_indicators,
    calculate_taxonomy_indicators,
)


def test_calculate_basic_analysis_indicators():
    indicators = calculate_analysis_indicators(
        total_sequences=100,
        valid_sequences=92,
        identified_sequences=80,
    )

    assert indicators.total_sequences == 100
    assert indicators.valid_sequences == 92
    assert indicators.rejected_sequences == 8

    assert indicators.identified_sequences == 80
    assert indicators.unidentified_sequences == 12

    assert indicators.validation_rate == 92.0
    assert indicators.rejection_rate == 8.0

    assert indicators.identification_rate == 86.96
    assert indicators.unidentified_rate == 13.04


def test_zero_sequences_are_supported():
    indicators = calculate_analysis_indicators(
        total_sequences=0,
        valid_sequences=0,
        identified_sequences=0,
    )

    assert indicators.validation_rate == 0.0
    assert indicators.rejection_rate == 0.0
    assert indicators.identification_rate == 0.0
    assert indicators.unidentified_rate == 0.0


def test_valid_sequences_cannot_exceed_total():
    with pytest.raises(
        ValueError,
        match="valid_sequences cannot exceed",
    ):
        calculate_analysis_indicators(
            total_sequences=10,
            valid_sequences=11,
            identified_sequences=5,
        )


def test_identified_sequences_cannot_exceed_valid():
    with pytest.raises(
        ValueError,
        match="identified_sequences cannot exceed",
    ):
        calculate_analysis_indicators(
            total_sequences=10,
            valid_sequences=8,
            identified_sequences=9,
        )


def test_calculate_taxonomy_indicators():
    results = [
        {
            "Identificada": True,
            "Espécie escolhida": "Species alpha",
        },
        {
            "Identificada": True,
            "Espécie escolhida": "Species alpha",
        },
        {
            "Identificada": True,
            "Espécie escolhida": "Species beta",
        },
        {
            "Identificada": False,
            "Espécie escolhida": None,
        },
    ]

    indicators = calculate_taxonomy_indicators(
        results
    )

    assert indicators.observed_species_count == 2

    assert (
        indicators.most_frequent_species
        == "Species alpha"
    )

    assert (
        indicators.most_frequent_species_count
        == 2
    )

    frequencies = {
        item.species: item
        for item in indicators.species_frequencies
    }

    assert frequencies["Species alpha"].count == 2
    assert frequencies["Species beta"].count == 1

    assert (
        frequencies["Species alpha"].proportion
        == 66.67
    )

    assert (
        frequencies["Species beta"].proportion
        == 33.33
    )


def test_taxonomy_indicators_ignore_unidentified_results():
    results = [
        {
            "Identificada": False,
            "Espécie escolhida": "Species alpha",
        },
        {
            "Identificada": False,
            "Espécie escolhida": None,
        },
    ]

    indicators = calculate_taxonomy_indicators(
        results
    )

    assert indicators.observed_species_count == 0
    assert indicators.most_frequent_species is None

    assert (
        indicators.most_frequent_species_count
        == 0
    )

    assert indicators.species_frequencies == []


def test_taxonomy_indicators_support_internal_field_names():
    results = [
        {
            "identified": True,
            "species": "Species alpha",
        },
        {
            "identified": True,
            "species": "Species beta",
        },
    ]

    indicators = calculate_taxonomy_indicators(
        results
    )

    assert indicators.observed_species_count == 2


def test_calculate_fastq_quality_indicators():
    records = [
        {
            "mean_quality": 30.0,
            "length": 100,
            "passed_qc": True,
            "trimmed_bases": 5,
        },
        {
            "mean_quality": 20.0,
            "length": 80,
            "passed_qc": False,
            "trimmed_bases": 0,
        },
        {
            "mean_quality": 25.0,
            "length": 90,
            "passed_qc": True,
            "trimmed_bases": 10,
        },
    ]

    indicators = calculate_quality_indicators(
        input_format="fastq",
        quality_records=records,
    )

    assert indicators.applicable is True

    assert indicators.mean_phred == 25.0
    assert indicators.min_phred == 20.0
    assert indicators.max_phred == 30.0

    assert indicators.mean_length == 90.0
    assert indicators.min_length == 80
    assert indicators.max_length == 100

    assert indicators.qc_passed_reads == 2
    assert indicators.qc_rejected_reads == 1

    assert indicators.trimmed_reads == 2
    assert indicators.trimmed_bases == 15


def test_fasta_quality_indicators_are_not_applicable():
    indicators = calculate_quality_indicators(
        input_format="fasta",
        quality_records=None,
    )

    assert indicators.applicable is False
    assert indicators.mean_phred is None
    assert indicators.mean_length is None
    assert indicators.qc_passed_reads is None
    assert indicators.trimmed_bases is None


def test_empty_fastq_quality_indicators_are_supported():
    indicators = calculate_quality_indicators(
        input_format="fastq",
        quality_records=[],
    )

    assert indicators.applicable is True

    assert indicators.mean_phred is None
    assert indicators.min_phred is None
    assert indicators.max_phred is None

    assert indicators.mean_length is None
    assert indicators.min_length is None
    assert indicators.max_length is None

    assert indicators.qc_passed_reads == 0
    assert indicators.qc_rejected_reads == 0
    assert indicators.trimmed_reads == 0
    assert indicators.trimmed_bases == 0


def test_calculate_blast_search_indicators():
    results = [
        {
            "Identidade do alinhamento (%)": 100.0,
            "Cobertura do alinhamento (%)": 98.0,
            "E-value": 1e-50,
            "Bit score": 200.0,
        },
        {
            "Identidade do alinhamento (%)": 97.0,
            "Cobertura do alinhamento (%)": 90.0,
            "E-value": 1e-20,
            "Bit score": 150.0,
        },
        {
            "Identidade do alinhamento (%)": 90.0,
            "Cobertura do alinhamento (%)": 80.0,
            "E-value": 1e-5,
            "Bit score": 100.0,
        },
    ]

    indicators = calculate_search_indicators(
        results
    )

    assert indicators.mean_identity == 95.67
    assert indicators.min_identity == 90.0
    assert indicators.max_identity == 100.0

    assert indicators.mean_coverage == 89.33
    assert indicators.min_coverage == 80.0
    assert indicators.max_coverage == 98.0

    assert indicators.min_evalue == 1e-50
    assert indicators.max_evalue == 1e-5

    assert indicators.mean_bit_score == 150.0

    assert indicators.above_99_identity == 1
    assert indicators.between_95_and_99_identity == 1
    assert indicators.below_95_identity == 1


def test_pairwise_search_indicators_allow_missing_blast_metrics():
    results = [
        {
            "alignment_identity": 99.0,
            "alignment_coverage": 100.0,
            "evalue": None,
            "bit_score": None,
        }
    ]

    indicators = calculate_search_indicators(
        results
    )

    assert indicators.mean_identity == 99.0
    assert indicators.mean_coverage == 100.0

    assert indicators.mean_evalue is None
    assert indicators.min_evalue is None
    assert indicators.max_evalue is None

    assert indicators.mean_bit_score is None


def test_empty_search_results_are_supported():
    indicators = calculate_search_indicators([])

    assert indicators.mean_identity is None
    assert indicators.mean_coverage is None
    assert indicators.mean_evalue is None
    assert indicators.mean_bit_score is None

    assert indicators.above_99_identity == 0
    assert indicators.between_95_and_99_identity == 0
    assert indicators.below_95_identity == 0


def test_calculate_performance_indicators():
    results = [
        {"Cache": "hit"},
        {"Cache": "miss"},
        {"Cache": "hit"},
        {"Cache": "miss"},
    ]

    indicators = calculate_performance_indicators(
        total_sequences=4,
        total_duration_seconds=2.0,
        results=results,
        search_errors=1,
        search_timeouts=1,
    )

    assert indicators.total_duration_seconds == 2.0
    assert indicators.mean_seconds_per_sequence == 0.5

    assert indicators.cache_hits == 2
    assert indicators.cache_misses == 2
    assert indicators.cache_hit_rate == 50.0

    assert indicators.search_errors == 1
    assert indicators.search_timeouts == 1


def test_performance_without_cache_information():
    indicators = calculate_performance_indicators(
        total_sequences=2,
        total_duration_seconds=1.0,
        results=[
            {},
            {},
        ],
    )

    assert indicators.cache_hits == 0
    assert indicators.cache_misses == 0
    assert indicators.cache_hit_rate == 0.0


def test_zero_sequences_do_not_calculate_mean_time():
    indicators = calculate_performance_indicators(
        total_sequences=0,
        total_duration_seconds=0.0,
        results=[],
    )

    assert indicators.total_duration_seconds == 0.0
    assert indicators.mean_seconds_per_sequence is None


def test_negative_performance_counts_are_rejected():
    with pytest.raises(
        ValueError,
        match="search_errors cannot be negative",
    ):
        calculate_performance_indicators(
            total_sequences=1,
            total_duration_seconds=1.0,
            results=[],
            search_errors=-1,
        )
