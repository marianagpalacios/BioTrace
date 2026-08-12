from collections import Counter

from src.config import (
    CURATED_REFERENCE_VALID_BASES,
    DEFAULT_REFERENCE_DATABASE_PATH,
    REFERENCE_EXPECTED_GENE,
    REFERENCE_EXPECTED_MARKER_REGION,
    REFERENCE_EXPECTED_SOURCE,
    REFERENCE_MAX_SEQUENCE_LENGTH,
    REFERENCE_MIN_SEQUENCE_LENGTH,
)
from src.reference.curation_validator import (
    validate_curated_reference_dataframe,
)
from src.reference.loader import (
    load_reference_csv,
)
from src.reference.validator import (
    validate_reference_dataframe,
)


EXPECTED_SPECIES_COUNTS = {
    "Danio rerio": 2,
    "Cyprinus carpio": 2,
    "Oreochromis niloticus": 2,
    "Salmo salar": 2,
    "Gadus morhua": 2,
}


EXPECTED_ACCESSIONS = {
    "HQ141077.1",
    "HQ141079.1",
    "HQ600722.1",
    "KR809733.1",
    "PV812904.1",
    "PP727595.1",
    "KX781876.1",
    "KX781935.1",
    "KJ204885.1",
    "KJ204884.1",
}


def load_curated_database():
    loaded = load_reference_csv(
        DEFAULT_REFERENCE_DATABASE_PATH
    )

    generic = validate_reference_dataframe(
        loaded
    )

    return validate_curated_reference_dataframe(
        generic.dataframe
    )


def test_curated_dataset_has_expected_size() -> None:
    result = load_curated_database()

    dataframe = result.dataframe

    assert len(dataframe) == 10
    assert dataframe["species"].nunique() == 5


def test_curated_dataset_has_two_records_per_species() -> None:
    result = load_curated_database()

    counts = Counter(
        result.dataframe["species"]
    )

    assert counts == EXPECTED_SPECIES_COUNTS


def test_curated_dataset_has_expected_accessions() -> None:
    result = load_curated_database()

    accessions = set(
        result.dataframe["accession"]
    )

    assert accessions == EXPECTED_ACCESSIONS
    assert len(accessions) == 10


def test_all_accessions_have_versions() -> None:
    result = load_curated_database()

    assert result.dataframe[
        "accession"
    ].str.fullmatch(
        r"[A-Za-z0-9_]+\.\d+"
    ).all()


def test_curated_dataset_uses_expected_gene() -> None:
    result = load_curated_database()

    assert set(
        result.dataframe["gene"]
    ) == {
        REFERENCE_EXPECTED_GENE
    }


def test_curated_dataset_uses_expected_marker() -> None:
    result = load_curated_database()

    assert set(
        result.dataframe["marker_region"]
    ) == {
        REFERENCE_EXPECTED_MARKER_REGION
    }


def test_curated_dataset_uses_expected_source() -> None:
    result = load_curated_database()

    assert set(
        result.dataframe["source"]
    ) == {
        REFERENCE_EXPECTED_SOURCE
    }


def test_curated_sequences_have_valid_lengths() -> None:
    result = load_curated_database()

    lengths = result.dataframe[
        "sequence"
    ].str.len()

    assert lengths.between(
        REFERENCE_MIN_SEQUENCE_LENGTH,
        REFERENCE_MAX_SEQUENCE_LENGTH,
    ).all()


def test_curated_sequences_only_contain_acgt() -> None:
    result = load_curated_database()

    for sequence in result.dataframe[
        "sequence"
    ]:
        assert set(sequence).issubset(
            CURATED_REFERENCE_VALID_BASES
        )

        assert "N" not in sequence


def test_identical_gadus_sequences_are_warning() -> None:
    result = load_curated_database()

    assert any(
        "Gadus morhua" in warning
        for warning in result.warnings
    )