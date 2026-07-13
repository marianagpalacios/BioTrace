from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_REFERENCE_DATABASE_PATH = (
    PROJECT_ROOT / "data" / "reference" / "species_database.csv"
)

DEFAULT_REFERENCE_METADATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "database_metadata.json"
)

LOG_DIRECTORY = PROJECT_ROOT / "logs"
LOG_FILE_PATH = LOG_DIRECTORY / "biotrace.log"

DEFAULT_MIN_SIMILARITY = 95.0
MIN_SIMILARITY = 0.0
MAX_SIMILARITY = 100.0
SIMILARITY_STEP = 0.5

DEFAULT_ALLOW_N = True
DEFAULT_TOP_N = 5
MAX_RANKING_RESULTS = 20

REFERENCE_REQUIRED_COLUMNS = frozenset(
    {"species", "id", "sequence"}
)

REFERENCE_OPTIONAL_COLUMNS = frozenset(
    {
        "gene",
        "marker_region",
        "accession",
        "source",
        "retrieved_at",
    }
)

REFERENCE_VALID_BASES = frozenset(
    {"A", "T", "C", "G", "N"}
)

CURATED_REFERENCE_REQUIRED_COLUMNS = frozenset(
    {
        "species",
        "id",
        "gene",
        "marker_region",
        "accession",
        "source",
        "retrieved_at",
        "sequence",
    }
)

CURATED_REFERENCE_VALID_BASES = frozenset(
    {"A", "T", "C", "G"}
)

REFERENCE_EXPECTED_GENE = "COI"
REFERENCE_EXPECTED_MARKER_REGION = "COI-5P"
REFERENCE_EXPECTED_SOURCE = "NCBI GenBank"

REFERENCE_MIN_SEQUENCE_LENGTH = 500
REFERENCE_MAX_SEQUENCE_LENGTH = 800

REFERENCE_MIN_RECORDS_PER_SPECIES = 2
REFERENCE_MAX_LENGTH_SPREAD = 100