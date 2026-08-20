from pathlib import Path

from src.services.sequence_analysis_service import (
    analyze_sequence_file,
)


BLAST_DATABASE = (
    Path("tests")
    / "data"
    / "blast"
    / "db"
    / "biotrace_test"
)


def test_fasta_can_use_blast_backend(
    tmp_path: Path,
):
    fasta_path = tmp_path / "query.fasta"

    fasta_path.write_text(
        (
            ">query1\n"
            "ATGCAATTCGGTACCGATCG\n"
        ),
        encoding="utf-8",
    )

    result = analyze_sequence_file(
        file_path=str(fasta_path),
        input_format="fasta",
        search_backend="blast",
        blast_database_path=str(
            BLAST_DATABASE
        ),
        search_timeout_seconds=10.0,
    )

    row = result["results"][0]

    assert row["Backend de busca"] == "blast"
    assert row["Espécie escolhida"] == "Species alpha"
    assert row["E-value"] is not None
    assert row["Bit score"] is not None


def test_fastq_can_use_blast_backend(
    tmp_path: Path,
):
    fastq_path = tmp_path / "query.fastq"

    fastq_path.write_text(
        (
            "@query1\n"
            "ATGCAATTCGGTACCGATCG\n"
            "+\n"
            "IIIIIIIIIIIIIIIIIIII\n"
        ),
        encoding="utf-8",
    )

    result = analyze_sequence_file(
        file_path=str(fastq_path),
        input_format="fastq",
        search_backend="blast",
        blast_database_path=str(
            BLAST_DATABASE
        ),
        search_timeout_seconds=10.0,
        min_mean_quality=20.0,
        min_length=1,
        max_length=100,
        trim_ends=False,
        trim_quality_threshold=20,
    )

    row = result["results"][0]

    assert row["Backend de busca"] == "blast"
    assert row["Espécie escolhida"] == "Species alpha"
    assert row["E-value"] is not None
    assert row["Bit score"] is not None
