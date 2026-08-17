from enum import IntEnum


class SequenceOrientation(IntEnum):
    """Explicit orientation contract for nucleotide sequences."""

    REVERSE = -1
    UNKNOWN = 0
    FORWARD = 1