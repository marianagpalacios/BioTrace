from pathlib import Path

from src.config import (
    PROJECT_ROOT,
)
from src.reproducibility.hashing import (
    sha256_file,
)
from src.services.reproducible_analysis_service import (
    analyze_fasta_reproducibly,
)


EXAMPLE_FASTA = (
    PROJECT_ROOT
    / "data"
    / "examples"
    / "example_query.fasta"
)


def test_reproducible_analysis_writes_manifest(
    tmp_path,
) -> None:
    result = (
        analyze_fasta_reproducibly(
            file_path=str(
                EXAMPLE_FASTA
            ),
            manifest_directory=(
                tmp_path
            ),
        )
    )

    manifest = result[
        "run_manifest"
    ]

    manifest_path = Path(
        result[
            "run_manifest_path"
        ]
    )

    assert manifest_path.exists()

    assert (
        manifest["status"]
        == "completed"
    )

    assert (
        manifest[
            "input"
        ]["sha256"]
        == sha256_file(
            EXAMPLE_FASTA
        )
    )

    assert (
        manifest[
            "reference_database"
        ]["version"]
        == "1.0.0"
    )

    assert (
        manifest["error"]
        is None
    )


def test_same_analysis_has_same_fingerprint(
    tmp_path,
) -> None:
    first = (
        analyze_fasta_reproducibly(
            file_path=str(
                EXAMPLE_FASTA
            ),
            manifest_directory=(
                tmp_path / "first"
            ),
        )
    )

    second = (
        analyze_fasta_reproducibly(
            file_path=str(
                EXAMPLE_FASTA
            ),
            manifest_directory=(
                tmp_path / "second"
            ),
        )
    )

    first_manifest = (
        first["run_manifest"]
    )

    second_manifest = (
        second["run_manifest"]
    )

    assert (
        first_manifest["run_id"]
        != second_manifest["run_id"]
    )

    assert (
        first_manifest[
            "run_fingerprint"
        ]
        == second_manifest[
            "run_fingerprint"
        ]
    )

    assert (
        first_manifest[
            "result_sha256"
        ]
        == second_manifest[
            "result_sha256"
        ]
    )