import pytest

from src.fastq import FastqReadError, read_fastq


def test_read_fastq_reads_sequence_and_phred_scores(tmp_path):
    fastq_file = tmp_path / "example.fastq"

    fastq_file.write_text(
        "@read1\n"
        "ACGT\n"
        "+\n"
        "IIII\n",
        encoding="utf-8",
    )

    records = read_fastq(fastq_file)

    assert len(records) == 1

    assert records[0]["id"] == "read1"
    assert records[0]["sequence"] == "ACGT"

    assert records[0]["qualities"] == [40, 40, 40, 40]


def test_read_fastq_reads_multiple_records(tmp_path):
    fastq_file = tmp_path / "example.fastq"

    fastq_file.write_text(
        "@read1\n"
        "ACGT\n"
        "+\n"
        "IIII\n"
        "@read2\n"
        "TGCA\n"
        "+\n"
        "5555\n",
        encoding="utf-8",
    )

    records = read_fastq(fastq_file)

    assert len(records) == 2

    assert records[0]["id"] == "read1"
    assert records[1]["id"] == "read2"


def test_read_fastq_raises_error_for_invalid_fastq(tmp_path):
    fastq_file = tmp_path / "invalid.fastq"

    fastq_file.write_text(
        "@read1\n"
        "ACGT\n"
        "+\n"
        "III\n",
        encoding="utf-8",
    )

    with pytest.raises(FastqReadError):
        read_fastq(fastq_file)