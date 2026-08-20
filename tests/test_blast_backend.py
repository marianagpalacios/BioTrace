from pathlib import Path
import subprocess

import pytest

from src.search.blast_backend import (
    BlastExecutionError,
    BlastNotInstalledError,
    BlastTimeoutError,
    LocalBlastBackend,
)
from src.search.contracts import SearchParameters


def test_blast_backend_name():
    backend = LocalBlastBackend(
        "database/test_db"
    )

    assert backend.name == "blast"


def test_build_command_contains_expected_arguments():
    backend = LocalBlastBackend(
        "database/test_db"
    )

    command = backend._build_command(
        executable="blastn",
        query_path=Path("query.fasta"),
    )

    assert command[0] == "blastn"
    assert "-query" in command
    assert "-db" in command
    assert "-outfmt" in command

    database_argument = command[
        command.index("-db") + 1
    ]

    assert (
        Path(database_argument)
        == Path("database/test_db")
    )


def test_build_command_uses_short_task_for_short_sequences():
    backend = LocalBlastBackend(
        "database/test_db"
    )

    command = backend._build_command(
        executable="blastn",
        query_path=Path("query.fasta"),
        sequence_length=20,
    )

    assert "-task" in command
    assert (
        command[command.index("-task") + 1]
        == "blastn-short"
    )


def test_missing_blast_is_rejected(
    monkeypatch,
):
    backend = LocalBlastBackend(
        "database/test_db"
    )

    monkeypatch.setattr(
        "src.search.blast_backend.shutil.which",
        lambda executable: None,
    )

    with pytest.raises(
        BlastNotInstalledError,
        match="BLAST\\+ was not found",
    ):
        backend.search(
            "ATGC",
            SearchParameters(),
        )


def test_timeout_is_converted_to_domain_error(
    monkeypatch,
):
    backend = LocalBlastBackend(
        "database/test_db"
    )

    monkeypatch.setattr(
        backend,
        "_resolve_executable",
        lambda: "blastn",
    )

    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd="blastn",
            timeout=1,
        )

    monkeypatch.setattr(
        "src.search.blast_backend.subprocess.run",
        fake_run,
    )

    with pytest.raises(
        BlastTimeoutError,
        match="BLAST search exceeded",
    ):
        backend.search(
            "ATGC",
            SearchParameters(
                timeout_seconds=1,
            ),
        )


def test_nonzero_return_code_is_rejected(
    monkeypatch,
):
    backend = LocalBlastBackend(
        "database/test_db"
    )

    monkeypatch.setattr(
        backend,
        "_resolve_executable",
        lambda: "blastn",
    )

    completed = subprocess.CompletedProcess(
        args=["blastn"],
        returncode=2,
        stdout="",
        stderr="BLAST database error",
    )

    monkeypatch.setattr(
        "src.search.blast_backend.subprocess.run",
        lambda *args, **kwargs: completed,
    )

    with pytest.raises(
        BlastExecutionError,
        match="BLAST database error",
    ):
        backend.search(
            "ATGC",
            SearchParameters(),
        )
