from pathlib import Path
from typing import cast

import pytest

from src.contracts import InputFormat
from src.services.analysis_service import (
    AnalysisError,
    analyze_fasta_file,
)
from src.services.fastq_analysis_service import analyze_fastq_file
from src.services.sequence_analysis_service import analyze_sequence_file


def test_unsupported_input_format_has_clear_error(tmp_path: Path) -> None:
    input_path = tmp_path / "input.txt"
    input_path.write_text("ATGC", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="Formato de entrada não suportado: txt",
    ):
        analyze_sequence_file(
            str(input_path),
            input_format=cast(InputFormat, "txt"),
        )


def test_empty_fasta_has_clear_error(tmp_path: Path) -> None:
    input_path = tmp_path / "empty.fasta"
    input_path.write_text("", encoding="utf-8")

    with pytest.raises(
        AnalysisError,
        match="Nenhuma sequência foi encontrada no arquivo FASTA",
    ):
        analyze_fasta_file(str(input_path))


def test_empty_fastq_has_clear_error(tmp_path: Path) -> None:
    input_path = tmp_path / "empty.fastq"
    input_path.write_text("", encoding="utf-8")

    with pytest.raises(
        AnalysisError,
        match="Nenhum registro foi encontrado no arquivo FASTQ",
    ):
        analyze_fastq_file(str(input_path))
