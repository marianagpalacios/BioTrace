from src.config import (
    DEFAULT_REFERENCE_DATABASE_PATH,
    DEFAULT_REFERENCE_METADATA_PATH,
)
from src.reference.database import (
    ReferenceDatabase,
)


def test_versioned_reference_database_loads() -> None:
    database = ReferenceDatabase.from_files(
        DEFAULT_REFERENCE_DATABASE_PATH,
        DEFAULT_REFERENCE_METADATA_PATH,
    )

    assert database.statistics() == {
        "reference_count": 10,
        "species_count": 5,
        "id_count": 10,
    }

    assert database.metadata is not None

    assert database.metadata.version == "1.0.0"
    assert database.metadata.marker == "COI-5P"

    assert any(
        "Gadus morhua" in warning
        for warning in database.warnings
    )