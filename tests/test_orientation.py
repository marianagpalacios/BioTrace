import pytest

from src.contracts import SequenceOrientation
from src.orientation import orient_sequence, reverse_complement


def test_reverse_complement():
    assert reverse_complement("ATGC") == "GCAT"


def test_reverse_complement_normalizes_input():
    assert reverse_complement("  atgc  ") == "GCAT"


def test_reverse_complement_rejects_empty_sequence():
    with pytest.raises(ValueError, match="Sequence cannot be empty"):
        reverse_complement("")


def test_orient_sequence_forward():
    result = orient_sequence(
        "ATGC",
        SequenceOrientation.FORWARD,
    )

    assert result == "ATGC"


def test_orient_sequence_reverse():
    result = orient_sequence(
        "ATGC",
        SequenceOrientation.REVERSE,
    )

    assert result == "GCAT"


def test_orient_sequence_rejects_unknown_orientation():
    with pytest.raises(
        ValueError,
        match="Unknown orientation must be resolved",
    ):
        orient_sequence(
            "ATGC",
            SequenceOrientation.UNKNOWN,
        )


def test_orient_sequence_rejects_invalid_orientation():
    with pytest.raises(
        ValueError,
        match="Orientation must be -1, 0, or 1",
    ):
        orient_sequence("ATGC", 2)