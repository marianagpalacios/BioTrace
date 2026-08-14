import pytest

from src.quality import (
    QualityControlConfig,
    QualityControlConfigurationError,
    quality_control_fastq,
    trim_low_quality_ends,
)


def test_trim_low_quality_ends_removes_only_terminal_bases() -> None:
    record = {
        "id": "read_1",
        "sequence": "AACGTAA",
        "qualities": [10, 10, 35, 5, 35, 10, 10],
    }

    trimmed, left, right = trim_low_quality_ends(record, threshold=20)

    assert trimmed == {
        "id": "read_1",
        "sequence": "CGT",
        "qualities": [35, 5, 35],
    }
    assert left == 2
    assert right == 2


def test_quality_control_approves_good_record() -> None:
    record = {
        "id": "good",
        "sequence": "A" * 500,
        "qualities": [30] * 500,
    }

    result = quality_control_fastq([record], QualityControlConfig())

    assert result.approved_sequences == [
        {
            "id": "good",
            "sequence": "A" * 500,
        }
    ]
    assert result.rejected_records == []
    assert result.report[0]["passed"] is True
    assert result.report[0]["mean_phred"] == 30.0
    assert result.report[0]["q20_percent"] == 100.0
    assert result.report[0]["q30_percent"] == 100.0


def test_quality_control_rejects_low_mean_quality() -> None:
    record = {
        "id": "low_quality",
        "sequence": "A" * 500,
        "qualities": [18] * 500,
    }

    result = quality_control_fastq(
        [record],
        QualityControlConfig(
            trim_ends=False,
            min_mean_quality=20.0,
        ),
    )

    assert result.approved_sequences == []
    assert result.report[0]["passed"] is False
    assert (
        "Qualidade Phred média abaixo"
        in result.rejected_records[0]["reason"]
    )


def test_quality_control_rejects_short_read_after_trimming() -> None:
    record = {
        "id": "short",
        "sequence": "A" * 502,
        "qualities": [10, 10] + [35] * 498 + [10, 10],
    }

    result = quality_control_fastq(
        [record],
        QualityControlConfig(
            min_length=500,
            max_length=800,
            trim_quality_threshold=20,
        ),
    )

    assert result.approved_sequences == []
    assert result.report[0]["retained_length"] == 498
    assert "abaixo do mínimo" in result.rejected_records[0]["reason"]


def test_quality_control_rejects_long_read() -> None:
    record = {
        "id": "long",
        "sequence": "A" * 801,
        "qualities": [35] * 801,
    }

    result = quality_control_fastq([record], QualityControlConfig())

    assert result.approved_sequences == []
    assert "acima do máximo" in result.rejected_records[0]["reason"]


def test_quality_control_respects_allow_n() -> None:
    record = {
        "id": "ambiguous",
        "sequence": "A" * 499 + "N",
        "qualities": [35] * 500,
    }

    permissive = quality_control_fastq(
        [record],
        QualityControlConfig(),
        allow_n=True,
    )
    strict = quality_control_fastq(
        [record],
        QualityControlConfig(),
        allow_n=False,
    )

    assert permissive.report[0]["passed"] is True
    assert strict.report[0]["passed"] is False


def test_quality_summary_counts_trimmed_bases() -> None:
    record = {
        "id": "trimmed",
        "sequence": "A" * 502,
        "qualities": [10] + [35] * 500 + [10],
    }

    result = quality_control_fastq([record], QualityControlConfig())

    assert result.summary["raw_bases"] == 502
    assert result.summary["retained_bases"] == 500
    assert result.summary["trimmed_bases"] == 2
    assert result.summary["passed_records"] == 1


def test_invalid_quality_configuration_fails() -> None:
    config = QualityControlConfig(
        min_length=800,
        max_length=500,
    )

    with pytest.raises(
        QualityControlConfigurationError,
        match="max_length",
    ):
        config.validate()
