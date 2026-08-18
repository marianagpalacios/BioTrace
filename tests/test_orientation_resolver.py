import pytest

from src.contracts import SequenceOrientation
from src.orientation_resolver import resolve_orientation


def test_resolve_forward_orientation():
    result = resolve_orientation(
        "ATGC",
        "ATGC",
    )

    assert result.orientation == SequenceOrientation.FORWARD
    assert result.oriented_sequence == "ATGC"
    assert (
        result.forward_alignment.score
        > result.reverse_alignment.score
    )


def test_resolve_reverse_orientation():
    result = resolve_orientation(
        "GCAT",
        "ATGC",
    )

    assert result.orientation == SequenceOrientation.REVERSE
    assert result.oriented_sequence == "ATGC"
    assert (
        result.reverse_alignment.score
        > result.forward_alignment.score
    )


def test_equal_scores_return_unknown_orientation():
    result = resolve_orientation(
        "ATAT",
        "ATAT",
    )

    assert result.orientation == SequenceOrientation.UNKNOWN
    assert result.oriented_sequence is None
    assert (
        result.forward_alignment.score
        == result.reverse_alignment.score
    )


def test_empty_sequence_is_rejected():
    with pytest.raises(
        ValueError,
        match="Sequence cannot be empty",
    ):
        resolve_orientation(
            "",
            "ATGC",
        )


def test_empty_reference_is_rejected():
    with pytest.raises(
        ValueError,
        match="Reference sequence cannot be empty",
    ):
        resolve_orientation(
            "ATGC",
            "",
        )