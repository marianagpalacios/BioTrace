from datetime import date

import pandas as pd
import pytest

from src.reference.curation_validator import (
    CuratedReferenceValidationError,
    validate_curated_reference_dataframe,
)


TODAY = date(
    2026,
    8,
    12,
)


def make_valid_database() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "species": "Danio rerio",
                "id": "DRE001",
                "gene": "COI",
                "marker_region": "COI-5P",
                "accession": "HQ141077.1",
                "source": "NCBI GenBank",
                "retrieved_at": "2026-08-12",
                "sequence": "A" * 500,
            },
            {
                "species": "Danio rerio",
                "id": "DRE002",
                "gene": "COI",
                "marker_region": "COI-5P",
                "accession": "HQ141079.1",
                "source": "NCBI GenBank",
                "retrieved_at": "2026-08-12",
                "sequence": (
                    "A" * 499 + "C"
                ),
            },
            {
                "species": "Cyprinus carpio",
                "id": "CCA001",
                "gene": "COI",
                "marker_region": "COI-5P",
                "accession": "HQ600722.1",
                "source": "NCBI GenBank",
                "retrieved_at": "2026-08-12",
                "sequence": "C" * 500,
            },
            {
                "species": "Cyprinus carpio",
                "id": "CCA002",
                "gene": "COI",
                "marker_region": "COI-5P",
                "accession": "KR809733.1",
                "source": "NCBI GenBank",
                "retrieved_at": "2026-08-12",
                "sequence": (
                    "C" * 499 + "G"
                ),
            },
        ]
    )


def validate(
    database: pd.DataFrame,
):
    return validate_curated_reference_dataframe(
        database,
        today=TODAY,
    )


def test_valid_curated_dataset_passes() -> None:
    result = validate(
        make_valid_database()
    )

    assert len(result.dataframe) == 4
    assert result.warnings == ()


def test_missing_required_column_fails() -> None:
    database = make_valid_database().drop(
        columns=["marker_region"]
    )

    with pytest.raises(
        CuratedReferenceValidationError,
        match="Colunas obrigatórias",
    ):
        validate(database)


def test_species_must_be_binomial() -> None:
    database = make_valid_database()
    database.loc[0, "species"] = "danio rerio"

    with pytest.raises(
        CuratedReferenceValidationError,
        match="formato binomial",
    ):
        validate(database)


def test_accession_without_version_fails() -> None:
    database = make_valid_database()
    database.loc[0, "accession"] = "HQ141077"

    with pytest.raises(
        CuratedReferenceValidationError,
        match="sem versão",
    ):
        validate(database)


def test_duplicate_accession_fails() -> None:
    database = make_valid_database()

    database.loc[
        1,
        "accession",
    ] = database.loc[
        0,
        "accession",
    ]

    with pytest.raises(
        CuratedReferenceValidationError,
        match="Accessions duplicados",
    ):
        validate(database)


def test_n_base_fails() -> None:
    database = make_valid_database()

    database.loc[
        0,
        "sequence",
    ] = (
        "A" * 499 + "N"
    )

    with pytest.raises(
        CuratedReferenceValidationError,
        match="Bases inválidas",
    ):
        validate(database)


def test_invalid_base_fails() -> None:
    database = make_valid_database()

    database.loc[
        0,
        "sequence",
    ] = (
        "A" * 499 + "X"
    )

    with pytest.raises(
        CuratedReferenceValidationError,
        match="Bases inválidas",
    ):
        validate(database)


def test_sequence_shorter_than_500_fails() -> None:
    database = make_valid_database()

    database.loc[
        0,
        "sequence",
    ] = "A" * 499

    with pytest.raises(
        CuratedReferenceValidationError,
        match="500-800",
    ):
        validate(database)


def test_sequence_longer_than_800_fails() -> None:
    database = make_valid_database()

    database.loc[
        0,
        "sequence",
    ] = "A" * 801

    with pytest.raises(
        CuratedReferenceValidationError,
        match="500-800",
    ):
        validate(database)


def test_wrong_gene_fails() -> None:
    database = make_valid_database()
    database.loc[0, "gene"] = "16S"

    with pytest.raises(
        CuratedReferenceValidationError,
        match="Gene diferente",
    ):
        validate(database)


def test_wrong_marker_fails() -> None:
    database = make_valid_database()
    database.loc[
        0,
        "marker_region",
    ] = "COI-3P"

    with pytest.raises(
        CuratedReferenceValidationError,
        match="Marcador diferente",
    ):
        validate(database)


def test_wrong_source_fails() -> None:
    database = make_valid_database()
    database.loc[
        0,
        "source",
    ] = "Other source"

    with pytest.raises(
        CuratedReferenceValidationError,
        match="Fonte diferente",
    ):
        validate(database)


def test_invalid_retrieved_at_fails() -> None:
    database = make_valid_database()
    database.loc[
        0,
        "retrieved_at",
    ] = "12/08/2026"

    with pytest.raises(
        CuratedReferenceValidationError,
        match="retrieved_at inválida",
    ):
        validate(database)


def test_future_retrieved_at_fails() -> None:
    database = make_valid_database()
    database.loc[
        0,
        "retrieved_at",
    ] = "2026-08-13"

    with pytest.raises(
        CuratedReferenceValidationError,
        match="futuro",
    ):
        validate(database)


def test_species_with_less_than_two_records_fails() -> None:
    database = (
        make_valid_database()
        .drop(index=1)
        .reset_index(drop=True)
    )

    with pytest.raises(
        CuratedReferenceValidationError,
        match="mínimo esperado",
    ):
        validate(database)


def test_identical_sequence_across_species_fails() -> None:
    database = make_valid_database()

    database.loc[
        2,
        "sequence",
    ] = database.loc[
        0,
        "sequence",
    ]

    with pytest.raises(
        CuratedReferenceValidationError,
        match="espécies diferentes",
    ):
        validate(database)


def test_identical_sequence_within_species_warns() -> None:
    database = make_valid_database()

    database.loc[
        1,
        "sequence",
    ] = database.loc[
        0,
        "sequence",
    ]

    result = validate(database)

    assert any(
        "Sequência idêntica dentro da espécie"
        in warning
        for warning in result.warnings
    )