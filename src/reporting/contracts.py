from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AnalysisIndicators:
    """Aggregated indicators for one BioTrace analysis."""

    total_sequences: int

    valid_sequences: int
    rejected_sequences: int

    identified_sequences: int
    unidentified_sequences: int

    validation_rate: float
    rejection_rate: float

    identification_rate: float
    unidentified_rate: float


@dataclass(frozen=True)
class SpeciesFrequency:
    """Frequency of one identified species."""

    species: str
    count: int
    proportion: float


@dataclass(frozen=True)
class TaxonomyIndicators:
    """Taxonomic summary of identified sequences."""

    observed_species_count: int
    most_frequent_species: str | None
    most_frequent_species_count: int

    species_frequencies: list[SpeciesFrequency]


@dataclass(frozen=True)
class QualityIndicators:
    """Quality summary for FASTQ analyses."""

    applicable: bool

    mean_phred: float | None
    min_phred: float | None
    max_phred: float | None

    mean_length: float | None
    min_length: int | None
    max_length: int | None

    qc_passed_reads: int | None
    qc_rejected_reads: int | None

    trimmed_reads: int | None
    trimmed_bases: int | None


@dataclass(frozen=True)
class SearchIndicators:
    """Summary of search-quality metrics."""

    mean_identity: float | None
    min_identity: float | None
    max_identity: float | None

    mean_coverage: float | None
    min_coverage: float | None
    max_coverage: float | None

    mean_evalue: float | None
    min_evalue: float | None
    max_evalue: float | None

    mean_bit_score: float | None
    min_bit_score: float | None
    max_bit_score: float | None

    above_99_identity: int
    between_95_and_99_identity: int
    below_95_identity: int


@dataclass(frozen=True)
class PerformanceIndicators:
    """Operational summary for one BioTrace analysis."""

    total_duration_seconds: float | None
    mean_seconds_per_sequence: float | None

    cache_hits: int
    cache_misses: int
    cache_hit_rate: float

    search_errors: int
    search_timeouts: int


@dataclass(frozen=True)
class ReportMetadata:
    """Metadata describing a generated analysis report."""

    biotrace_version: str

    input_format: str
    search_backend: str

    generated_at: str


@dataclass(frozen=True)
class AnalysisReport:
    """Structured BioTrace analysis report."""

    metadata: ReportMetadata
    indicators: AnalysisIndicators
    taxonomy: TaxonomyIndicators
    quality: QualityIndicators
    search: SearchIndicators
    performance: PerformanceIndicators

    results: list[dict[str, Any]]

    warnings: list[str] = field(
        default_factory=list
    )
