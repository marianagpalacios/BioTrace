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
    DEFAULT_ALIGNMENT_EXTEND_GAP_SCORE,
    DEFAULT_ALIGNMENT_MATCH_SCORE,
    DEFAULT_ALIGNMENT_MISMATCH_SCORE,
    DEFAULT_ALIGNMENT_MODE,
    DEFAULT_ALIGNMENT_OPEN_GAP_SCORE,
    DEFAULT_FASTQ_MAX_LENGTH,
    DEFAULT_FASTQ_MIN_LENGTH,
    DEFAULT_FASTQ_MIN_MEAN_QUALITY,
    DEFAULT_FASTQ_TRIM_ENDS,
    DEFAULT_FASTQ_TRIM_QUALITY,
    DEFAULT_REFERENCE_DATABASE_PATH,
    DEFAULT_REFERENCE_METADATA_PATH,
    RUNS_DIRECTORY,
)
from src.reproducibility.hashing import (  # noqa: E402
    sha256_file,
)
from src.reproducibility.manifest import (  # noqa: E402
    MANIFEST_SCHEMA_VERSION,
    load_run_manifest,
)
from src.services.reproducible_analysis_service import (  # noqa: E402
    analyze_sequence_file_reproducibly,
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


def _validate_alignment_parameters(
    parameters: dict[str, object],
) -> None:
    """Ensure the manifest uses the current alignment configuration."""
    expected = {
        "alignment_mode": DEFAULT_ALIGNMENT_MODE,
        "alignment_match_score": (
            DEFAULT_ALIGNMENT_MATCH_SCORE
        ),
        "alignment_mismatch_score": (
            DEFAULT_ALIGNMENT_MISMATCH_SCORE
        ),
        "alignment_open_gap_score": (
            DEFAULT_ALIGNMENT_OPEN_GAP_SCORE
        ),
        "alignment_extend_gap_score": (
            DEFAULT_ALIGNMENT_EXTEND_GAP_SCORE
        ),
    }

    for parameter_name, expected_value in expected.items():
        recorded_value = parameters.get(
            parameter_name
        )

        if recorded_value != expected_value:
            raise ValueError(
                "Alignment parameter mismatch for "
                f"{parameter_name!r}: "
                f"manifest={recorded_value!r}, "
                f"current={expected_value!r}."
            )


def _validate_search_parameters(
    parameters: dict[str, object],
    *,
    expected_backend: str,
    expected_timeout: float,
    expected_blast_version: str | None,
    expected_database_path: str | None,
    expected_database_sha256: str | None,
    expected_cache_enabled: bool,
) -> None:
    """Validate search configuration recorded in a run manifest."""

    expected = {
        "search_backend": expected_backend,
        "search_timeout_seconds": expected_timeout,
        "blast_version": expected_blast_version,
        "blast_database_path": expected_database_path,
        "blast_database_sha256": expected_database_sha256,
        "cache_enabled": expected_cache_enabled,
    }

    for parameter_name, expected_value in expected.items():
        recorded_value = parameters.get(
            parameter_name
        )

        if recorded_value != expected_value:
            raise ValueError(
                "Search parameter mismatch for "
                f"{parameter_name!r}: "
                f"manifest={recorded_value!r}, "
                f"current={expected_value!r}."
            )


def main() -> int:
    args = parse_args()

    original = (
        load_run_manifest(
            args.manifest
        )
    )

    if (
        original[
            "schema_version"
        ]
        != MANIFEST_SCHEMA_VERSION
    ):
        return fail(
            "A versão do schema do "
            "manifesto é "
            f"{original['schema_version']}, "
            "mas esta versão do BioTrace "
            "usa "
            f"{MANIFEST_SCHEMA_VERSION}. "
            "Faça checkout da versão do "
            "BioTrace registrada no manifesto."
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

    _validate_alignment_parameters(
        parameters
    )

    input_format = parameters[
        "input_format"
    ]

    result = (
        analyze_sequence_file_reproducibly(
            file_path=str(
                args.input
            ),
            input_format=input_format,
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
            min_mean_quality=(
                parameters[
                    "min_mean_quality"
                ]
                if parameters[
                    "min_mean_quality"
                ]
                is not None
                else
                DEFAULT_FASTQ_MIN_MEAN_QUALITY
            ),
            min_length=(
                parameters[
                    "min_length"
                ]
                if parameters[
                    "min_length"
                ]
                is not None
                else
                DEFAULT_FASTQ_MIN_LENGTH
            ),
            max_length=(
                parameters[
                    "max_length"
                ]
                if parameters[
                    "max_length"
                ]
                is not None
                else
                DEFAULT_FASTQ_MAX_LENGTH
            ),
            trim_ends=(
                parameters[
                    "trim_ends"
                ]
                if parameters[
                    "trim_ends"
                ]
                is not None
                else
                DEFAULT_FASTQ_TRIM_ENDS
            ),
            trim_quality_threshold=(
                parameters[
                    "trim_quality_threshold"
                ]
                if parameters[
                    "trim_quality_threshold"
                ]
                is not None
                else
                DEFAULT_FASTQ_TRIM_QUALITY
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
