"""Reproduce an analysis from a BioTrace run manifest."""

import argparse
import sys

from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from src.config import (  # noqa: E402
    DEFAULT_REFERENCE_DATABASE_PATH,
    DEFAULT_REFERENCE_METADATA_PATH,
    RUNS_DIRECTORY,
)
from src.reproducibility.hashing import (  # noqa: E402
    sha256_file,
)
from src.reproducibility.manifest import (  # noqa: E402
    load_run_manifest,
)
from src.services.reproducible_analysis_service import (  # noqa: E402
    analyze_fasta_reproducibly,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Reproduce a BioTrace run "
            "using its saved manifest."
        )
    )

    parser.add_argument(
        "--manifest",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--input",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--database",
        type=Path,
        default=(
            DEFAULT_REFERENCE_DATABASE_PATH
        ),
    )

    parser.add_argument(
        "--metadata",
        type=Path,
        default=(
            DEFAULT_REFERENCE_METADATA_PATH
        ),
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=RUNS_DIRECTORY,
    )

    return parser.parse_args()


def fail(
    message: str,
) -> int:
    print(
        f"ERRO: {message}"
    )

    return 1


def main() -> int:
    args = parse_args()

    original = (
        load_run_manifest(
            args.manifest
        )
    )

    if original[
        "software"
    ]["git_dirty"]:
        return fail(
            "O manifesto original foi "
            "produzido com working tree "
            "suja. A reprodução exata "
            "não pode ser garantida."
        )

    input_sha = sha256_file(
        args.input
    )

    if input_sha != original[
        "input"
    ]["sha256"]:
        return fail(
            "O arquivo de entrada não "
            "corresponde ao SHA-256 "
            "do manifesto."
        )

    database_sha = sha256_file(
        args.database
    )

    if database_sha != original[
        "reference_database"
    ]["csv_sha256"]:
        return fail(
            "O banco de referência atual "
            "não corresponde ao banco "
            "registrado no manifesto."
        )

    metadata_sha = sha256_file(
        args.metadata
    )

    if metadata_sha != original[
        "reference_database"
    ]["metadata_sha256"]:
        return fail(
            "A metadata atual não "
            "corresponde à metadata "
            "do manifesto."
        )

    parameters = original[
        "parameters"
    ]

    result = (
        analyze_fasta_reproducibly(
            file_path=str(
                args.input
            ),
            reference_database_path=(
                args.database
            ),
            reference_metadata_path=(
                args.metadata
            ),
            min_similarity=(
                parameters[
                    "min_similarity"
                ]
            ),
            allow_n=(
                parameters[
                    "allow_n"
                ]
            ),
            top_n=(
                parameters[
                    "top_n"
                ]
            ),
            manifest_directory=(
                args.output_dir
            ),
        )
    )

    reproduced = result[
        "run_manifest"
    ]

    if (
        reproduced[
            "run_fingerprint"
        ]
        != original[
            "run_fingerprint"
        ]
    ):
        return fail(
            "O fingerprint da nova "
            "execução não corresponde "
            "ao original. Verifique "
            "versão/commit do BioTrace."
        )

    if (
        reproduced[
            "result_sha256"
        ]
        != original[
            "result_sha256"
        ]
    ):
        return fail(
            "Os resultados não são "
            "idênticos aos registrados "
            "na execução original."
        )

    print(
        "REPRODUCTION OK"
    )

    print(
        "Original run:",
        original["run_id"],
    )

    print(
        "New run:",
        reproduced["run_id"],
    )

    print(
        "Fingerprint:",
        reproduced[
            "run_fingerprint"
        ],
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())