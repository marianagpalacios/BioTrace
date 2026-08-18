from dataclasses import dataclass

from src.alignment import AlignmentResult, align_sequences
from src.contracts import SequenceOrientation
from src.orientation import reverse_complement


@dataclass(frozen=True)
class OrientationResolution:
    """Result of comparing forward and reverse-complement orientations."""

    orientation: SequenceOrientation
    oriented_sequence: str | None
    forward_alignment: AlignmentResult
    reverse_alignment: AlignmentResult


def resolve_orientation(
    sequence: str,
    reference_sequence: str,
) -> OrientationResolution:
    """Resolve sequence orientation using alignment scores."""

    candidate = sequence.strip().upper()
    reference = reference_sequence.strip().upper()

    if not candidate:
        raise ValueError("Sequence cannot be empty.")

    if not reference:
        raise ValueError("Reference sequence cannot be empty.")

    reverse_sequence = reverse_complement(candidate)

    forward_alignment = align_sequences(
        candidate,
        reference,
    )

    reverse_alignment = align_sequences(
        reverse_sequence,
        reference,
    )

    if forward_alignment.score > reverse_alignment.score:
        return OrientationResolution(
            orientation=SequenceOrientation.FORWARD,
            oriented_sequence=candidate,
            forward_alignment=forward_alignment,
            reverse_alignment=reverse_alignment,
        )

    if reverse_alignment.score > forward_alignment.score:
        return OrientationResolution(
            orientation=SequenceOrientation.REVERSE,
            oriented_sequence=reverse_sequence,
            forward_alignment=forward_alignment,
            reverse_alignment=reverse_alignment,
        )

    return OrientationResolution(
        orientation=SequenceOrientation.UNKNOWN,
        oriented_sequence=None,
        forward_alignment=forward_alignment,
        reverse_alignment=reverse_alignment,
    )