from src.reporting.contracts import (
    AnalysisIndicators,
    PerformanceIndicators,
    QualityIndicators,
    SearchIndicators,
    SpeciesFrequency,
    TaxonomyIndicators,
)


def _percentage(
    numerator: int,
    denominator: int,
) -> float:
    if denominator == 0:
        return 0.0

    return round(
        numerator / denominator * 100.0,
        2,
    )


def calculate_analysis_indicators(
    *,
    total_sequences: int,
    valid_sequences: int,
    identified_sequences: int,
) -> AnalysisIndicators:
    """Calculate high-level indicators for one BioTrace analysis."""

    if total_sequences < 0:
        raise ValueError(
            "total_sequences cannot be negative."
        )

    if valid_sequences < 0:
        raise ValueError(
            "valid_sequences cannot be negative."
        )

    if identified_sequences < 0:
        raise ValueError(
            "identified_sequences cannot be negative."
        )

    if valid_sequences > total_sequences:
        raise ValueError(
            "valid_sequences cannot exceed total_sequences."
        )

    if identified_sequences > valid_sequences:
        raise ValueError(
            "identified_sequences cannot exceed valid_sequences."
        )

    rejected_sequences = (
        total_sequences
        - valid_sequences
    )

    unidentified_sequences = (
        valid_sequences
        - identified_sequences
    )

    return AnalysisIndicators(
        total_sequences=total_sequences,
        valid_sequences=valid_sequences,
        rejected_sequences=rejected_sequences,
        identified_sequences=identified_sequences,
        unidentified_sequences=unidentified_sequences,
        validation_rate=_percentage(
            valid_sequences,
            total_sequences,
        ),
        rejection_rate=_percentage(
            rejected_sequences,
            total_sequences,
        ),
        identification_rate=_percentage(
            identified_sequences,
            valid_sequences,
        ),
        unidentified_rate=_percentage(
            unidentified_sequences,
            valid_sequences,
        ),
    )


def calculate_taxonomy_indicators(
    results: list[dict[str, object]],
) -> TaxonomyIndicators:
    """Calculate species frequencies for identified results."""

    counts: dict[str, int] = {}

    for result in results:
        identified = bool(
            result.get("Identificada")
            or result.get("identified")
        )

        if not identified:
            continue

        species = (
            result.get("Espécie escolhida")
            or result.get("species")
        )

        if not species:
            continue

        species_name = str(species)

        counts[species_name] = (
            counts.get(species_name, 0)
            + 1
        )

    identified_total = sum(
        counts.values()
    )

    frequencies = [
        SpeciesFrequency(
            species=species,
            count=count,
            proportion=(
                round(
                    count
                    / identified_total
                    * 100.0,
                    2,
                )
                if identified_total
                else 0.0
            ),
        )
        for species, count in counts.items()
    ]

    frequencies.sort(
        key=lambda item: (
            item.count,
            item.species,
        ),
        reverse=True,
    )

    if frequencies:
        most_frequent = frequencies[0]
        most_frequent_species = (
            most_frequent.species
        )
        most_frequent_count = (
            most_frequent.count
        )
    else:
        most_frequent_species = None
        most_frequent_count = 0

    return TaxonomyIndicators(
        observed_species_count=len(
            frequencies
        ),
        most_frequent_species=(
            most_frequent_species
        ),
        most_frequent_species_count=(
            most_frequent_count
        ),
        species_frequencies=frequencies,
    )


def calculate_quality_indicators(
    *,
    input_format: str,
    quality_records: list[dict[str, object]] | None,
) -> QualityIndicators:
    """Calculate FASTQ quality indicators."""

    normalized_format = (
        input_format
        .strip()
        .lower()
    )

    if normalized_format != "fastq":
        return QualityIndicators(
            applicable=False,
            mean_phred=None,
            min_phred=None,
            max_phred=None,
            mean_length=None,
            min_length=None,
            max_length=None,
            qc_passed_reads=None,
            qc_rejected_reads=None,
            trimmed_reads=None,
            trimmed_bases=None,
        )

    records = quality_records or []

    if not records:
        return QualityIndicators(
            applicable=True,
            mean_phred=None,
            min_phred=None,
            max_phred=None,
            mean_length=None,
            min_length=None,
            max_length=None,
            qc_passed_reads=0,
            qc_rejected_reads=0,
            trimmed_reads=0,
            trimmed_bases=0,
        )

    phred_values = [
        float(record["mean_quality"])
        for record in records
        if record.get("mean_quality") is not None
    ]

    lengths = [
        int(record["length"])
        for record in records
        if record.get("length") is not None
    ]

    qc_passed = sum(
        bool(record.get("passed_qc"))
        for record in records
    )

    qc_rejected = (
        len(records) - qc_passed
    )

    trimmed_reads = sum(
        int(record.get("trimmed_bases", 0)) > 0
        for record in records
    )

    trimmed_bases = sum(
        int(record.get("trimmed_bases", 0))
        for record in records
    )

    return QualityIndicators(
        applicable=True,
        mean_phred=(
            round(
                sum(phred_values)
                / len(phred_values),
                2,
            )
            if phred_values
            else None
        ),
        min_phred=(
            min(phred_values)
            if phred_values
            else None
        ),
        max_phred=(
            max(phred_values)
            if phred_values
            else None
        ),
        mean_length=(
            round(
                sum(lengths)
                / len(lengths),
                2,
            )
            if lengths
            else None
        ),
        min_length=(
            min(lengths)
            if lengths
            else None
        ),
        max_length=(
            max(lengths)
            if lengths
            else None
        ),
        qc_passed_reads=qc_passed,
        qc_rejected_reads=qc_rejected,
        trimmed_reads=trimmed_reads,
        trimmed_bases=trimmed_bases,
    )


def _mean_or_none(
    values: list[float],
) -> float | None:
    if not values:
        return None

    return round(
        sum(values) / len(values),
        2,
    )


def calculate_search_indicators(
    results: list[dict[str, object]],
) -> SearchIndicators:
    """Calculate identity, coverage and BLAST metric summaries."""

    identities: list[float] = []
    coverages: list[float] = []
    evalues: list[float] = []
    bit_scores: list[float] = []

    for result in results:
        identity = (
            result.get("Identidade do alinhamento (%)")
            or result.get("alignment_identity")
        )

        coverage = (
            result.get("Cobertura do alinhamento (%)")
            or result.get("alignment_coverage")
        )

        evalue = (
            result.get("E-value")
            if "E-value" in result
            else result.get("evalue")
        )

        bit_score = (
            result.get("Bit score")
            if "Bit score" in result
            else result.get("bit_score")
        )

        if identity is not None:
            identities.append(
                float(identity)
            )

        if coverage is not None:
            coverages.append(
                float(coverage)
            )

        if evalue is not None:
            evalues.append(
                float(evalue)
            )

        if bit_score is not None:
            bit_scores.append(
                float(bit_score)
            )

    return SearchIndicators(
        mean_identity=_mean_or_none(
            identities
        ),
        min_identity=(
            min(identities)
            if identities
            else None
        ),
        max_identity=(
            max(identities)
            if identities
            else None
        ),
        mean_coverage=_mean_or_none(
            coverages
        ),
        min_coverage=(
            min(coverages)
            if coverages
            else None
        ),
        max_coverage=(
            max(coverages)
            if coverages
            else None
        ),
        mean_evalue=_mean_or_none(
            evalues
        ),
        min_evalue=(
            min(evalues)
            if evalues
            else None
        ),
        max_evalue=(
            max(evalues)
            if evalues
            else None
        ),
        mean_bit_score=_mean_or_none(
            bit_scores
        ),
        min_bit_score=(
            min(bit_scores)
            if bit_scores
            else None
        ),
        max_bit_score=(
            max(bit_scores)
            if bit_scores
            else None
        ),
        above_99_identity=sum(
            value >= 99.0
            for value in identities
        ),
        between_95_and_99_identity=sum(
            95.0 <= value < 99.0
            for value in identities
        ),
        below_95_identity=sum(
            value < 95.0
            for value in identities
        ),
    )


def calculate_performance_indicators(
    *,
    total_sequences: int,
    total_duration_seconds: float | None,
    results: list[dict[str, object]],
    search_errors: int = 0,
    search_timeouts: int = 0,
) -> PerformanceIndicators:
    """Calculate timing and cache indicators."""

    if total_sequences < 0:
        raise ValueError(
            "total_sequences cannot be negative."
        )

    if search_errors < 0:
        raise ValueError(
            "search_errors cannot be negative."
        )

    if search_timeouts < 0:
        raise ValueError(
            "search_timeouts cannot be negative."
        )

    cache_hits = 0
    cache_misses = 0

    for result in results:
        cache_state = (
            result.get("Cache")
            or result.get("cache")
        )

        if cache_state == "hit":
            cache_hits += 1

        elif cache_state == "miss":
            cache_misses += 1

    cache_total = (
        cache_hits
        + cache_misses
    )

    cache_hit_rate = (
        round(
            cache_hits
            / cache_total
            * 100.0,
            2,
        )
        if cache_total
        else 0.0
    )

    mean_seconds_per_sequence = None

    if (
        total_duration_seconds is not None
        and total_sequences > 0
    ):
        mean_seconds_per_sequence = round(
            total_duration_seconds
            / total_sequences,
            4,
        )

    return PerformanceIndicators(
        total_duration_seconds=(
            round(
                total_duration_seconds,
                4,
            )
            if total_duration_seconds
            is not None
            else None
        ),
        mean_seconds_per_sequence=(
            mean_seconds_per_sequence
        ),
        cache_hits=cache_hits,
        cache_misses=cache_misses,
        cache_hit_rate=cache_hit_rate,
        search_errors=search_errors,
        search_timeouts=search_timeouts,
    )
