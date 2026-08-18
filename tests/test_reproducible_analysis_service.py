import json
from pathlib import Path

import pytest

from src.config import (
    PROJECT_ROOT,
)
from src.reproducibility.hashing import (
    sha256_file,
)
from src.services.analysis_service import (
    AnalysisError,
)
from src.services.reproducible_analysis_service import (
    analyze_fasta_reproducibly,
    analyze_sequence_file_reproducibly,
)


EXAMPLE_FASTA = (
    PROJECT_ROOT
    / "data"
    / "examples"
    / "example_query.fasta"
)

EXAMPLE_FASTQ = (
    PROJECT_ROOT
    / "data"
    / "examples"
    / "example_reads.fastq"
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


def test_failed_analysis_writes_failed_manifest(
    tmp_path,
) -> None:
    runs_directory = (
        tmp_path
        / "runs"
    )

    missing_database = (
        tmp_path
        / "missing.csv"
    )

    with pytest.raises(
        AnalysisError
    ):
        analyze_fasta_reproducibly(
            file_path=str(
                EXAMPLE_FASTA
            ),
            reference_database_path=(
                missing_database
            ),
            manifest_directory=(
                runs_directory
            ),
        )

    manifests = list(
        runs_directory.glob(
            "*.json"
        )
    )

    assert len(manifests) == 1

    payload = json.loads(
        manifests[0].read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["status"]
        == "failed"
    )

    assert (
        payload["error"]
        is not None
    )


def test_reproducible_fastq_records_qc_parameters(
    tmp_path,
) -> None:
    result = analyze_sequence_file_reproducibly(
        file_path=str(EXAMPLE_FASTQ),
        input_format="fastq",
        manifest_directory=tmp_path,
    )

    manifest = result["run_manifest"]
    parameters = manifest["parameters"]

    assert parameters["input_format"] == "fastq"
    assert parameters["min_mean_quality"] == 20.0
    assert parameters["min_length"] == 500
    assert parameters["max_length"] == 800
    assert parameters["trim_ends"] is True
    assert parameters["trim_quality_threshold"] == 20
    assert (
        parameters[
            "alignment_mode"
        ]
        == "global"
    )
    assert (
        parameters[
            "alignment_match_score"
        ]
        == 2.0
    )
    assert (
        parameters[
            "alignment_mismatch_score"
        ]
        == -1.0
    )
    assert (
        parameters[
            "alignment_open_gap_score"
        ]
        == -2.0
    )
    assert (
        parameters[
            "alignment_extend_gap_score"
        ]
        == -0.5
    )
    assert result["quality_summary"]["passed_records"] == 1
