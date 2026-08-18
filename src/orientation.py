from Bio.Seq import Seq

from src.contracts import SequenceOrientation


def reverse_complement(sequence: str) -> str:
    """Return the reverse complement of a nucleotide sequence."""

    normalized_sequence = sequence.strip().upper()

    if not normalized_sequence:
        raise ValueError("Sequence cannot be empty.")

    return str(Seq(normalized_sequence).reverse_complement())


def orient_sequence(
    sequence: str,
    orientation: SequenceOrientation,
) -> str:
    """Return a nucleotide sequence in the requested orientation."""

    normalized_sequence = sequence.strip().upper()

    if not normalized_sequence:
        raise ValueError("Sequence cannot be empty.")

    try:
        orientation = SequenceOrientation(orientation)
    except ValueError as exc:
        raise ValueError(
            "Orientation must be -1, 0, or 1."
        ) from exc

    if orientation == SequenceOrientation.FORWARD:
        return normalized_sequence

    if orientation == SequenceOrientation.REVERSE:
        return reverse_complement(normalized_sequence)

    raise ValueError(
        "Unknown orientation must be resolved before orienting the sequence."
    )