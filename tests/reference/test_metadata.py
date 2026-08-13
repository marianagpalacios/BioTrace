from src.config import (
    DEFAULT_REFERENCE_DATABASE_PATH,
    DEFAULT_REFERENCE_METADATA_PATH,
)
from src.reference.curation_validator import (
    validate_curated_reference_dataframe,
)
from src.reference.loader import (
    load_reference_csv,
)
from src.reference.metadata import (
    calculate_sha256,
    load_reference_metadata,
    validate_reference_metadata,
)
from src.reference.validator import (
    validate_reference_dataframe,
)


def test_metadata_matches_curated_database() -> None:
    loaded = load_reference_csv(
        DEFAULT_REFERENCE_DATABASE_PATH
    )

    generic = validate_reference_dataframe(
        loaded
    )

    curated = (
        validate_curated_reference_dataframe(
            generic.dataframe
        )
    )

    metadata = load_reference_metadata(
        DEFAULT_REFERENCE_METADATA_PATH
    )

    validate_reference_metadata(
        metadata,
        DEFAULT_REFERENCE_DATABASE_PATH,
        curated.dataframe,
    )

    assert metadata.version == "1.0.0"
    assert metadata.marker == "COI-5P"
    assert metadata.taxonomic_scope == (
        "Actinopterygii"
    )
    assert metadata.source == "NCBI GenBank"

    assert metadata.record_count == 10
    assert metadata.species_count == 5

    assert metadata.csv_sha256 == (
        calculate_sha256(
            DEFAULT_REFERENCE_DATABASE_PATH
        )
    )