from pathlib import Path

import pytest

from scripts.build_blast_database import (
    build_database,
)
from scripts.verify_blast_database import (
    verify_database,
)


def test_build_blast_database_creates_metadata(
    tmp_path: Path,
):
    fasta_path = tmp_path / "references.fasta"

    fasta_path.write_text(
        (
            ">REF001\n"
            "ATGCAATTCGGTACCGATCG\n"
            ">REF002\n"
            "GGCTAACCGTTAGGCTACGA\n"
        ),
        encoding="utf-8",
    )

    output_prefix = (
        tmp_path
        / "db"
        / "test_database"
    )

    metadata = build_database(
        fasta_path=fasta_path,
        output_prefix=output_prefix,
        source="controlled test",
        marker="COI",
        database_version="test-1",
    )

    assert metadata["sequence_count"] == 2
    assert metadata["source"] == "controlled test"
    assert metadata["marker"] == "COI"
    assert metadata["database_version"] == "test-1"

    metadata_path = (
        output_prefix.parent
        / "test_database.metadata.json"
    )

    assert metadata_path.exists()
    assert metadata["index_files"]


def test_built_database_passes_verification(
    tmp_path: Path,
):
    fasta_path = tmp_path / "references.fasta"

    fasta_path.write_text(
        ">REF001\nATGCAATTCGGTACCGATCG\n",
        encoding="utf-8",
    )

    output_prefix = (
        tmp_path
        / "db"
        / "test_database"
    )

    build_database(
        fasta_path=fasta_path,
        output_prefix=output_prefix,
        source="controlled test",
        marker="COI",
        database_version="test-1",
    )

    metadata_path = (
        output_prefix.parent
        / "test_database.metadata.json"
    )

    verify_database(
        metadata_path
    )


def test_modified_index_file_is_rejected(
    tmp_path: Path,
):
    fasta_path = tmp_path / "references.fasta"

    fasta_path.write_text(
        ">REF001\nATGCAATTCGGTACCGATCG\n",
        encoding="utf-8",
    )

    output_prefix = (
        tmp_path
        / "db"
        / "test_database"
    )

    metadata = build_database(
        fasta_path=fasta_path,
        output_prefix=output_prefix,
        source="controlled test",
        marker="COI",
        database_version="test-1",
    )

    index_name = metadata["index_files"][0]["name"]

    index_path = (
        output_prefix.parent
        / index_name
    )

    with index_path.open("ab") as file:
        file.write(b"corruption")

    metadata_path = (
        output_prefix.parent
        / "test_database.metadata.json"
    )

    with pytest.raises(
        ValueError,
        match="Checksum mismatch",
    ):
        verify_database(
            metadata_path
        )