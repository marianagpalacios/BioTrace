from statistics import median, pstdev

from src.fasta import SequenceRecord


def sequence_length(sequence: str) -> int:
    """Return the number of nucleotides in a sequence."""

    return len(sequence)


def _percentage(count: int, total: int) -> float:
    if total == 0:
        return 0.0

    return round((count / total) * 100, 2)


def nucleotide_frequency(
    sequence: str,
    nucleotide: str,
) -> float:
    """Return one nucleotide percentage."""
    normalized = sequence.upper()

    return _percentage(
        normalized.count(nucleotide.upper()),
        len(normalized),
    )


def gc_content(sequence: str) -> float:
    """Return the percentage of guanine and cytosine nucleotides."""

    normalized = sequence.upper()

    gc = normalized.count("G") + normalized.count("C")

    return _percentage(gc, len(normalized))


def at_content(sequence: str) -> float:
    """Return the percentage of adenine and thymine nucleotides."""

    normalized = sequence.upper()

    at = normalized.count("A") + normalized.count("T")

    return _percentage(at, len(normalized))


def sequence_composition(
    sequence: str,
) -> dict[str, float | int]:
    """Return metrics for one sequence."""
    normalized = sequence.upper()

    return {
        "length": len(normalized),
        "a_frequency": nucleotide_frequency(normalized, "A"),
        "t_frequency": nucleotide_frequency(normalized, "T"),
        "c_frequency": nucleotide_frequency(normalized, "C"),
        "g_frequency": nucleotide_frequency(normalized, "G"),
        "at_content": at_content(normalized),
        "gc_content": gc_content(normalized),
        "n_count": normalized.count("N"),
    }


def summarize_sequences(
    sequences: list[SequenceRecord],
) -> dict[str, object]:
    """Aggregate length and nucleotide-composition statistics."""

    lengths = [
        len(item["sequence"])
        for item in sequences
    ]

    if not lengths:
        return {
            "total_sequences": 0,
            "min_length": 0,
            "max_length": 0,
            "average_length": 0.0,
            "median_length": 0.0,
            "length_std_dev": 0.0,
            "a_frequency": 0.0,
            "t_frequency": 0.0,
            "c_frequency": 0.0,
            "g_frequency": 0.0,
            "at_content": 0.0,
            "gc_content": 0.0,
            "gc_by_sequence": [],
            "sequence_metrics": [],
        }

    sequence_metrics = [
        {
            "id": item["id"],
            **sequence_composition(item["sequence"]),
        }
        for item in sequences
    ]

    combined_sequence = "".join(
        item["sequence"]
        for item in sequences
    )

    return {
        "total_sequences": len(sequences),
        "min_length": min(lengths),
        "max_length": max(lengths),
        "average_length": round(
            sum(lengths) / len(lengths),
            2,
        ),
        "median_length": round(
            float(median(lengths)),
            2,
        ),
        "length_std_dev": round(
            float(pstdev(lengths)),
            2,
        ),
        "a_frequency": nucleotide_frequency(
            combined_sequence,
            "A",
        ),
        "t_frequency": nucleotide_frequency(
            combined_sequence,
            "T",
        ),
        "c_frequency": nucleotide_frequency(
            combined_sequence,
            "C",
        ),
        "g_frequency": nucleotide_frequency(
            combined_sequence,
            "G",
        ),
        "at_content": at_content(combined_sequence),
        "gc_content": gc_content(combined_sequence),
        "gc_by_sequence": [
            {
                "id": item["id"],
                "gc_content": item["gc_content"],
            }
            for item in sequence_metrics
        ],
        "sequence_metrics": sequence_metrics,
    }
