"""Quality-control rules for FASTQ records."""

from dataclasses import dataclass
from statistics import fmean
from typing import TypedDict

from src.config import (
    DEFAULT_FASTQ_MAX_LENGTH,
    DEFAULT_FASTQ_MIN_LENGTH,
    DEFAULT_FASTQ_MIN_MEAN_QUALITY,
    DEFAULT_FASTQ_TRIM_ENDS,
    DEFAULT_FASTQ_TRIM_QUALITY,
)
from src.fasta import SequenceRecord
from src.fastq import FastqRecord
from src.validation import find_invalid_bases


class QualityControlConfigurationError(ValueError):
    """Raised when FASTQ QC parameters are inconsistent."""


class QualityReportRow(TypedDict):
    id: str
    raw_length: int
    retained_length: int
    trimmed_left: int
    trimmed_right: int
    mean_phred: float
    min_phred: int | None
    max_phred: int | None
    q20_percent: float
    q30_percent: float
    passed: bool
    reasons: list[str]


class QualitySummary(TypedDict):
    total_records: int
    passed_records: int
    rejected_records: int
    raw_bases: int
    retained_bases: int
    trimmed_bases: int
    retained_mean_phred: float
    retained_q20_percent: float
    retained_q30_percent: float


@dataclass(frozen=True)
class QualityControlConfig:
    """Configuration for basic FASTQ quality control."""

    min_mean_quality: float = DEFAULT_FASTQ_MIN_MEAN_QUALITY
    min_length: int = DEFAULT_FASTQ_MIN_LENGTH
    max_length: int = DEFAULT_FASTQ_MAX_LENGTH
    trim_ends: bool = DEFAULT_FASTQ_TRIM_ENDS
    trim_quality_threshold: int = DEFAULT_FASTQ_TRIM_QUALITY

    def validate(self) -> None:
        if self.min_mean_quality < 0:
            raise QualityControlConfigurationError(
                "min_mean_quality deve ser maior ou igual a zero."
            )
        if self.min_length < 1:
            raise QualityControlConfigurationError(
                "min_length deve ser maior ou igual a 1."
            )
        if self.max_length < self.min_length:
            raise QualityControlConfigurationError(
                "max_length deve ser maior ou igual a min_length."
            )
        if self.trim_quality_threshold < 0:
            raise QualityControlConfigurationError(
                "trim_quality_threshold deve ser maior ou igual a zero."
            )


@dataclass(frozen=True)
class QualityControlResult:
    """Approved sequences plus an auditable FASTQ quality report."""

    approved_sequences: list[SequenceRecord]
    rejected_records: list[dict[str, object]]
    report: list[QualityReportRow]
    summary: QualitySummary


def _mean_quality(qualities: list[int]) -> float:
    if not qualities:
        return 0.0
    return round(float(fmean(qualities)), 2)


def _quality_percentage(qualities: list[int], threshold: int) -> float:
    if not qualities:
        return 0.0
    passing = sum(score >= threshold for score in qualities)
    return round(passing / len(qualities) * 100, 2)


def trim_low_quality_ends(
    record: FastqRecord,
    threshold: int,
) -> tuple[FastqRecord, int, int]:
    """Trim low-quality bases only from the 5' and 3' ends."""

    if threshold < 0:
        raise QualityControlConfigurationError(
            "O limiar de trimming não pode ser negativo."
        )

    sequence = record["sequence"]
    qualities = record["qualities"]
    left = 0
    right = len(qualities)

    while left < right and qualities[left] < threshold:
        left += 1
    while right > left and qualities[right - 1] < threshold:
        right -= 1

    return (
        {
            "id": record["id"],
            "sequence": sequence[left:right],
            "qualities": qualities[left:right],
        },
        left,
        len(qualities) - right,
    )


def _rejection_reason(
    *,
    invalid_bases: list[str],
    retained_length: int,
    mean_quality: float,
    config: QualityControlConfig,
) -> list[str]:
    reasons: list[str] = []

    if invalid_bases:
        reasons.append(
            "Bases inválidas encontradas: " + ", ".join(invalid_bases) + "."
        )
    if retained_length == 0:
        reasons.append("Nenhuma base permaneceu após o trimming.")
    elif retained_length < config.min_length:
        reasons.append(
            "Comprimento após QC abaixo do mínimo "
            f"({retained_length} < {config.min_length} bp)."
        )
    elif retained_length > config.max_length:
        reasons.append(
            "Comprimento após QC acima do máximo "
            f"({retained_length} > {config.max_length} bp)."
        )

    if retained_length > 0 and mean_quality < config.min_mean_quality:
        reasons.append(
            "Qualidade Phred média abaixo do mínimo "
            f"({mean_quality} < {config.min_mean_quality})."
        )

    return reasons


def quality_control_fastq(
    records: list[FastqRecord],
    config: QualityControlConfig,
    *,
    allow_n: bool = True,
) -> QualityControlResult:
    """Trim, filter and summarize FASTQ records."""

    config.validate()
    approved_sequences: list[SequenceRecord] = []
    rejected_records: list[dict[str, object]] = []
    report: list[QualityReportRow] = []
    raw_bases = 0
    retained_bases = 0
    retained_qualities: list[int] = []

    for record in records:
        raw_length = len(record["sequence"])
        raw_bases += raw_length

        if config.trim_ends:
            processed, trimmed_left, trimmed_right = trim_low_quality_ends(
                record,
                config.trim_quality_threshold,
            )
        else:
            processed = {
                "id": record["id"],
                "sequence": record["sequence"],
                "qualities": list(record["qualities"]),
            }
            trimmed_left = 0
            trimmed_right = 0

        sequence = processed["sequence"].upper().strip()
        qualities = processed["qualities"]
        retained_length = len(sequence)
        retained_bases += retained_length
        retained_qualities.extend(qualities)
        mean_quality = _mean_quality(qualities)
        invalid_bases = find_invalid_bases(sequence, allow_n=allow_n)
        reasons = _rejection_reason(
            invalid_bases=invalid_bases,
            retained_length=retained_length,
            mean_quality=mean_quality,
            config=config,
        )
        passed = not reasons

        report.append(
            {
                "id": record["id"],
                "raw_length": raw_length,
                "retained_length": retained_length,
                "trimmed_left": trimmed_left,
                "trimmed_right": trimmed_right,
                "mean_phred": mean_quality,
                "min_phred": min(qualities) if qualities else None,
                "max_phred": max(qualities) if qualities else None,
                "q20_percent": _quality_percentage(qualities, 20),
                "q30_percent": _quality_percentage(qualities, 30),
                "passed": passed,
                "reasons": reasons,
            }
        )

        if passed:
            approved_sequences.append({"id": record["id"], "sequence": sequence})
        else:
            rejected_records.append(
                {
                    "id": record["id"],
                    "invalid_bases": invalid_bases,
                    "reason": " ".join(reasons),
                }
            )

    summary: QualitySummary = {
        "total_records": len(records),
        "passed_records": len(approved_sequences),
        "rejected_records": len(rejected_records),
        "raw_bases": raw_bases,
        "retained_bases": retained_bases,
        "trimmed_bases": raw_bases - retained_bases,
        "retained_mean_phred": _mean_quality(retained_qualities),
        "retained_q20_percent": _quality_percentage(retained_qualities, 20),
        "retained_q30_percent": _quality_percentage(retained_qualities, 30),
    }

    return QualityControlResult(
        approved_sequences=approved_sequences,
        rejected_records=rejected_records,
        report=report,
        summary=summary,
    )
