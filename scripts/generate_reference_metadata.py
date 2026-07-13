"""Generate metadata for the curated reference database."""

import argparse
from datetime import date
import json
from pathlib import Path

from src.config import (
    DEFAULT_REFERENCE_DATABASE_PATH,
    DEFAULT_REFERENCE_METADATA_PATH,
    REFERENCE_EXPECTED_MARKER_REGION,
    REFERENCE_EXPECTED_SOURCE,
)
from src.reference.loader import (
    load_reference_csv,
)
from src.reference.metadata import (
    calculate_sha256,
)
from src.reference.validator import (
    validate_reference_dataframe,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the reference CSV and "
            "generate versioned metadata."
        )
    )

    parser.add_argument(
        "--database",
        type=Path,
        default=(
            DEFAULT_REFERENCE_DATABASE_PATH
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=(
            DEFAULT_REFERENCE_METADATA_PATH
        ),
    )

    parser.add_argument(
        "--name",
        default=(
            "BioTrace Fish COI "
            "Reference Database"
        ),
    )

    parser.add_argument(
        "--version",
        required=True,
    )

    parser.add_argument(
        "--marker",
        default=(
            REFERENCE_EXPECTED_MARKER_REGION
        ),
    )

    parser.add_argument(
        "--taxonomic-scope",
        default="Actinopterygii",
    )

    parser.add_argument(
        "--source",
        default=REFERENCE_EXPECTED_SOURCE,
    )

    parser.add_argument(
        "--created-at",
        default=date.today().isoformat(),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    loaded = load_reference_csv(
        args.database
    )

    validation = (
        validate_reference_dataframe(
            loaded
        )
    )

    dataframe = validation.dataframe

    payload = {
        "name": args.name,
        "version": args.version,
        "marker": args.marker,
        "taxonomic_scope": (
            args.taxonomic_scope
        ),
        "source": args.source,
        "created_at": args.created_at,
        "record_count": len(dataframe),
        "species_count": (
            dataframe["species"].nunique()
        ),
        "csv_sha256": calculate_sha256(
            args.database
        ),
    }

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    args.output.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        f"Metadados gerados em: "
        f"{args.output}"
    )

    print(
        f"Registros: "
        f"{payload['record_count']}"
    )

    print(
        f"Espécies: "
        f"{payload['species_count']}"
    )

    print(
        f"SHA-256: "
        f"{payload['csv_sha256']}"
    )

    for warning in validation.warnings:
        print(f"Aviso: {warning}")


if __name__ == "__main__":
    main()