from pathlib import Path
import shutil
import subprocess
import tempfile

from src.search.blast_parser import (
    parse_blast_tabular,
    rank_blast_hits,
)
from src.search.contracts import (
    SearchHit,
    SearchParameters,
)


class BlastNotInstalledError(RuntimeError):
    """Raised when the blastn executable cannot be found."""


class BlastTimeoutError(RuntimeError):
    """Raised when a BLAST search exceeds its timeout."""


class BlastExecutionError(RuntimeError):
    """Raised when blastn finishes with an execution error."""


class LocalBlastBackend:
    """Sequence-search backend using local NCBI BLAST+."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        blastn_executable: str = "blastn",
    ) -> None:
        self.database_path = Path(database_path)
        self.blastn_executable = blastn_executable

    @property
    def name(self) -> str:
        return "blast"

    def _resolve_executable(self) -> str:
        executable = shutil.which(
            self.blastn_executable
        )

        if executable is None:
            raise BlastNotInstalledError(
                "BLAST+ was not found. "
                "Install NCBI BLAST+ and ensure "
                "'blastn' is available in PATH."
            )

        return executable

    def search(
        self,
        sequence: str,
        parameters: SearchParameters,
    ) -> list[SearchHit]:
        candidate = sequence.strip().upper()

        if not candidate:
            raise ValueError(
                "Sequence cannot be empty."
            )

        executable = self._resolve_executable()

        with tempfile.TemporaryDirectory() as temp_dir:
            query_path = (
                Path(temp_dir)
                / "query.fasta"
            )

            query_path.write_text(
                f">query\n{candidate}\n",
                encoding="utf-8",
            )

            command = self._build_command(
                executable=executable,
                query_path=query_path,
                sequence_length=len(candidate),
            )

            try:
                completed = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=parameters.timeout_seconds,
                )
            except subprocess.TimeoutExpired as exc:
                raise BlastTimeoutError(
                    "BLAST search exceeded "
                    f"{parameters.timeout_seconds} seconds."
                ) from exc

            if completed.returncode != 0:
                error_message = (
                    completed.stderr.strip()
                    or "Unknown BLAST execution error."
                )

                raise BlastExecutionError(
                    error_message
                )

            hits = parse_blast_tabular(
                completed.stdout
            )

            return rank_blast_hits(
                hits,
                top_n=parameters.top_n,
            )

    def _build_command(
        self,
        *,
        executable: str,
        query_path: Path,
        sequence_length: int | None = None,
    ) -> list[str]:
        """Build the blastn command without shell interpolation."""

        output_format = (
            "6 "
            "qseqid "
            "sseqid "
            "pident "
            "length "
            "qlen "
            "slen "
            "evalue "
            "bitscore "
            "score"
        )

        command = [
            executable,
            "-query",
            str(query_path),
            "-db",
            str(self.database_path),
            "-outfmt",
            output_format,
        ]

        if (
            sequence_length is not None
            and sequence_length < 50
        ):
            command.extend(
                ["-task", "blastn-short"]
            )

        return command
