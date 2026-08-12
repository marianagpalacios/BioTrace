"""Build the curated reference CSV from a downloaded FASTA."""

import argparse
from pathlib import Path

import pandas as pd

from src.config import (
    DEFAULT_REFERENCE_DATABASE_PATH,
    PROJECT_ROOT,
    REFERENCE_EXPECTED_GENE,
    REFERENCE_EXPECTED_MARKER_REGION,
    REFERENCE_EXPECTED_SOURCE,
)
from src.fasta import read_fasta
from src.reference.curation_validator import (
    validate_curated_reference_dataframe,
)
from src.reference.validator import (
    validate_reference_dataframe,
)


DEFAULT_FASTA_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "selected_sequences.fasta"
)


REFERENCE_MAP = {
    "HQ141077.1": (
        "Danio rerio",
        "DRE001",
    ),
    "HQ141079.1": (
        "Danio rerio",
        "DRE002",
    ),
    "HQ600722.1": (
        "Cyprinus carpio",
        "CCA001",
    ),
    "KR809733.1": (
        "Cyprinus carpio",
        "CCA002",
    ),
    "PV812904.1": (
        "Oreochromis niloticus",
        "ONI001",
    ),
    "PP727595.1": (
        "Oreochromis niloticus",
        "ONI002",
    ),
    "KX781876.1": (
        "Salmo salar",
        "SSA001",
    ),
    "KX781935.1": (
        "Salmo salar",
        "SSA002",
    ),
    "KJ204885.1": (
        "Gadus morhua",
        "GMO001",
    ),
    "KJ204884.1": (
        "Gadus morhua",
        "GMO002",
    ),
}


OUTPUT_COLUMNS = [
    "species",
    "id",
    "gene",
    "marker_region",
    "accession",
    "source",
    "retrieved_at",
    "sequence",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the curated BioTrace "
            "reference database CSV."
        )
    )

    parser.add_argument(
        "--fasta",
        type=Path,
        default=DEFAULT_FASTA_PATH,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_REFERENCE_DATABASE_PATH,
    )

    parser.add_argument(
        "--retrieved-at",
        required=True,
        help="NCBI retrieval date in YYYY-MM-DD.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    fasta_records = read_fasta(
        str(args.fasta)
    )

    fasta_ids = [
        record["id"]
        for record in fasta_records
    ]

    if len(fasta_ids) != len(set(fasta_ids)):
        raise SystemExit(
            "O FASTA possui accessions duplicados."
        )

    sequences = {
        record["id"]: record["sequence"]
        for record in fasta_records
    }

    expected = set(
        REFERENCE_MAP
    )

    downloaded = set(
        sequences
    )

    missing = expected.difference(
        downloaded
    )

    unexpected = downloaded.difference(
        expected
    )

    if missing:
        raise SystemExit(
            "Accessions ausentes no FASTA: "
            + ", ".join(sorted(missing))
        )

    if unexpected:
        raise SystemExit(
            "Accessions inesperados no FASTA: "
            + ", ".join(sorted(unexpected))
        )

    rows: list[dict[str, str]] = []

    for accession, (
        species,
        reference_id,
    ) in REFERENCE_MAP.items():
        rows.append(
            {
                "species": species,
                "id": reference_id,
                "gene": REFERENCE_EXPECTED_GENE,
                "marker_region": (
                    REFERENCE_EXPECTED_MARKER_REGION
                ),
                "accession": accession,
                "source": REFERENCE_EXPECTED_SOURCE,
                "retrieved_at": args.retrieved_at,
                "sequence": (
                    sequences[accession]
                    .replace(" ", "")
                    .replace("\n", "")
                    .upper()
                ),
            }
        )

    dataframe = pd.DataFrame(
        rows,
        columns=OUTPUT_COLUMNS,
    )

    generic_validation = (
        validate_reference_dataframe(
            dataframe
        )
    )

    curated_validation = (
        validate_curated_reference_dataframe(
            generic_validation.dataframe
        )
    )

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    curated_validation.dataframe.to_csv(
        args.output,
        index=False,
    )

    print(
        f"Banco gerado em: {args.output}"
    )
    print(
        f"Registros: "
        f"{len(curated_validation.dataframe)}"
    )
    print(
        "Espécies: "
        f"{curated_validation.dataframe['species'].nunique()}"
    )

    for warning in (
        *generic_validation.warnings,
        *curated_validation.warnings,
    ):
        print(
            f"Aviso: {warning}"
        )


if __name__ == "__main__":
    main()