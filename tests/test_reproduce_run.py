import pytest

from scripts.reproduce_run import (
    _validate_alignment_parameters,
    _validate_search_parameters,
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


def valid_search_parameters():
    return {
        "search_backend": "blast",
        "search_timeout_seconds": 30.0,
        "blast_version": "2.17.0+",
        "blast_database_path": "db/biotrace",
        "blast_database_sha256": "abc123",
        "cache_enabled": True,
    }


def test_matching_search_parameters_are_accepted():
    parameters = valid_search_parameters()

    _validate_search_parameters(
        parameters,
        expected_backend="blast",
        expected_timeout=30.0,
        expected_blast_version="2.17.0+",
        expected_database_path="db/biotrace",
        expected_database_sha256="abc123",
        expected_cache_enabled=True,
    )


def test_changed_backend_is_rejected():
    parameters = valid_search_parameters()

    with pytest.raises(
        ValueError,
        match="Search parameter mismatch",
    ):
        _validate_search_parameters(
            parameters,
            expected_backend="pairwise",
            expected_timeout=30.0,
            expected_blast_version="2.17.0+",
            expected_database_path="db/biotrace",
            expected_database_sha256="abc123",
            expected_cache_enabled=True,
        )


def test_changed_blast_version_is_rejected():
    parameters = valid_search_parameters()

    with pytest.raises(
        ValueError,
        match="Search parameter mismatch",
    ):
        _validate_search_parameters(
            parameters,
            expected_backend="blast",
            expected_timeout=30.0,
            expected_blast_version="2.18.0+",
            expected_database_path="db/biotrace",
            expected_database_sha256="abc123",
            expected_cache_enabled=True,
        )


def test_changed_database_hash_is_rejected():
    parameters = valid_search_parameters()

    with pytest.raises(
        ValueError,
        match="Search parameter mismatch",
    ):
        _validate_search_parameters(
            parameters,
            expected_backend="blast",
            expected_timeout=30.0,
            expected_blast_version="2.17.0+",
            expected_database_path="db/biotrace",
            expected_database_sha256="different-hash",
            expected_cache_enabled=True,
        )
