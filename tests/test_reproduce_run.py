import pytest

from scripts.reproduce_run import (
    _validate_alignment_parameters,
)


def valid_alignment_parameters():
    return {
        "alignment_mode": "global",
        "alignment_match_score": 2.0,
        "alignment_mismatch_score": -1.0,
        "alignment_open_gap_score": -2.0,
        "alignment_extend_gap_score": -0.5,
    }


def test_matching_alignment_parameters_are_accepted():
    parameters = valid_alignment_parameters()

    _validate_alignment_parameters(
        parameters
    )


def test_changed_alignment_parameter_is_rejected():
    parameters = valid_alignment_parameters()

    parameters[
        "alignment_match_score"
    ] = 1.0

    with pytest.raises(
        ValueError,
        match="Alignment parameter mismatch",
    ):
        _validate_alignment_parameters(
            parameters
        )


def test_missing_alignment_parameter_is_rejected():
    parameters = valid_alignment_parameters()

    del parameters[
        "alignment_mode"
    ]

    with pytest.raises(
        ValueError,
        match="Alignment parameter mismatch",
    ):
        _validate_alignment_parameters(
            parameters
        )
