import pytest

from src.alignment import AlignmentResult, align_sequences


def test_perfect_global_alignment():
    result = align_sequences(
        "ATGC",
        "ATGC",
    )

    assert isinstance(result, AlignmentResult)
    assert result.identity == 100.0
    assert result.coverage == 100.0
    assert result.matches == 4
    assert result.aligned_length == 4


def test_alignment_with_mismatch():
    result = align_sequences(
        "ATGC",
        "ATGT",
    )

    assert result.identity == 75.0
    assert result.matches == 3
    assert result.aligned_length == 4


def test_alignment_normalizes_sequences():
    result = align_sequences(
        " atgc ",
        "ATGC",
    )

    assert result.identity == 100.0


def test_empty_candidate_is_rejected():
    with pytest.raises(
        ValueError,
        match="Candidate sequence cannot be empty",
    ):
        align_sequences("", "ATGC")


def test_empty_reference_is_rejected():
    with pytest.raises(
        ValueError,
        match="Reference sequence cannot be empty",
    ):
        align_sequences("ATGC", "")


def test_invalid_alignment_mode_is_rejected():
    with pytest.raises(
        ValueError,
        match="Alignment mode must be",
    ):
        align_sequences(
            "ATGC",
            "ATGC",
            mode="invalid",
        )


def test_local_alignment_is_supported():
    result = align_sequences(
        "ATGC",
        "GGATGCAA",
        mode="local",
    )

    assert result.score > 0
    assert result.identity == 100.0