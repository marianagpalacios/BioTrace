from src.config import PROJECT_ROOT
from src.services.fastq_analysis_service import (
    analyze_fastq_file,
)


EXAMPLE_FASTQ = (
    PROJECT_ROOT
    / "data"
    / "examples"
    / "example_reads.fastq"
)


def test_fastq_analysis_applies_quality_control() -> None:
    result = analyze_fastq_file(
        str(EXAMPLE_FASTQ)
    )

    assert (
        result["input_format"]
        == "fastq"
    )

    assert (
        result["total_sequences"]
        == 3
    )

    assert (
        result["valid_count"]
        == 1
    )

    assert (
        result["invalid_count"]
        == 2
    )

    quality_summary = result[
        "quality_summary"
    ]

    assert (
        quality_summary["passed_records"]
        == 1
    )

    assert (
        quality_summary["rejected_records"]
        == 2
    )

    assert (
        len(result["quality_report"])
        == 3
    )

    assert (
        len(result["results"])
        == 1
    )


def test_fastq_passed_read_is_classified() -> None:
    result = analyze_fastq_file(
        str(EXAMPLE_FASTQ)
    )

    row = result["results"][0]

    assert (
        row["ID"]
        == "read_pass_trimmed"
    )

    assert (
        row["Espécie escolhida"]
        == "Danio rerio"
    )

    assert (
        float(
            row[
                "Melhor similaridade (%)"
            ]
        )
        >= 95.0
    )