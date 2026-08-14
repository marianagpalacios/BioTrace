import json

from src.reproducibility.manifest import (
    build_run_manifest,
    load_run_manifest,
    write_run_manifest,
)


def create_files(
    tmp_path,
):
    input_path = (
        tmp_path
        / "query.fasta"
    )

    input_path.write_text(
        ">query\nACGTACGT\n",
        encoding="utf-8",
    )

    database_path = (
        tmp_path
        / "species_database.csv"
    )

    database_path.write_text(
        "species,id,sequence\n"
        "Danio rerio,DRE001,ACGT\n",
        encoding="utf-8",
    )

    metadata_path = (
        tmp_path
        / "database_metadata.json"
    )

    metadata_path.write_text(
        json.dumps(
            {
                "version": "1.0.0",
                "marker": "COI-5P",
                "source": (
                    "NCBI GenBank"
                ),
            }
        ),
        encoding="utf-8",
    )

    return (
        input_path,
        database_path,
        metadata_path,
    )


def build_example_manifest(
    tmp_path,
    *,
    run_id: str,
    top_n: int = 5,
):
    (
        input_path,
        database_path,
        metadata_path,
    ) = create_files(tmp_path)

    return build_run_manifest(
        run_id=run_id,
        status="completed",
        started_at_utc=(
            "2026-08-12T12:00:00Z"
        ),
        finished_at_utc=(
            "2026-08-12T12:00:01Z"
        ),
        duration_seconds=1.0,
        input_path=input_path,
        reference_database_path=(
            database_path
        ),
        reference_metadata_path=(
            metadata_path
        ),
        parameters={
            "input_format": "fasta",
            "min_similarity": 95.0,
            "allow_n": True,
            "top_n": top_n,
            "min_mean_quality": None,
            "min_length": None,
            "max_length": None,
            "trim_ends": None,
            "trim_quality_threshold": None,
        },
        result={
            "total_sequences": 1,
            "valid_count": 1,
            "invalid_count": 0,
            "results": [
                {
                    "species": (
                        "Danio rerio"
                    )
                }
            ],
        },
    )


def test_manifest_has_required_provenance(
    tmp_path,
) -> None:
    manifest = build_example_manifest(
        tmp_path,
        run_id="run-a",
    )

    assert (
        manifest["schema_version"]
        == "1.1"
    )

    assert (
        len(
            manifest[
                "input"
            ]["sha256"]
        )
        == 64
    )

    assert (
        manifest[
            "reference_database"
        ]["version"]
        == "1.0.0"
    )

    assert (
        len(
            manifest[
                "run_fingerprint"
            ]
        )
        == 64
    )


def test_same_conditions_have_same_fingerprint(
    tmp_path,
) -> None:
    first = build_example_manifest(
        tmp_path,
        run_id="run-a",
    )

    second = build_example_manifest(
        tmp_path,
        run_id="run-b",
    )

    assert (
        first["run_id"]
        != second["run_id"]
    )

    assert (
        first["run_fingerprint"]
        == second["run_fingerprint"]
    )


def test_parameter_change_changes_fingerprint(
    tmp_path,
) -> None:
    first = build_example_manifest(
        tmp_path,
        run_id="run-a",
        top_n=5,
    )

    second = build_example_manifest(
        tmp_path,
        run_id="run-b",
        top_n=6,
    )

    assert (
        first["run_fingerprint"]
        != second["run_fingerprint"]
    )


def test_manifest_can_be_written_and_loaded(
    tmp_path,
) -> None:
    manifest = build_example_manifest(
        tmp_path,
        run_id="run-a",
    )

    path = write_run_manifest(
        manifest,
        directory=(
            tmp_path
            / "runs"
        ),
    )

    loaded = load_run_manifest(
        path
    )

    assert loaded == manifest
