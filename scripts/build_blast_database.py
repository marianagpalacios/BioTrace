from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def count_fasta_sequences(path: Path) -> int:
    count = 0

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line in file:
            if line.startswith(">"):
                count += 1

    return count


def get_blast_version(
    executable: str,
) -> str:
    completed = subprocess.run(
        [executable, "-version"],
        capture_output=True,
        text=True,
        check=True,
    )

    first_line = (
        completed.stdout
        .strip()
        .splitlines()[0]
    )

    return first_line


def build_database(
    *,
    fasta_path: Path,
    output_prefix: Path,
    source: str,
    marker: str,
    database_version: str,
    makeblastdb_executable: str = "makeblastdb",
) -> dict[str, object]:
    output_prefix.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
        makeblastdb_executable,
        "-in",
        str(fasta_path),
        "-dbtype",
        "nucl",
        "-parse_seqids",
        "-title",
        "BioTrace BLAST database",
        "-out",
        str(output_prefix),
    ]

    with tempfile.TemporaryDirectory(
        prefix="biotrace-blast-",
    ) as temp_dir:
        build_directory = Path(temp_dir)
        build_fasta = (
            build_directory
            / "references.fasta"
        )

        shutil.copy2(
            fasta_path,
            build_fasta,
        )

        build_command = [
            makeblastdb_executable,
            "-in",
            build_fasta.name,
            "-dbtype",
            "nucl",
            "-parse_seqids",
            "-title",
            "BioTrace BLAST database",
            "-out",
            output_prefix.name,
        ]

        subprocess.run(
            build_command,
            check=True,
            cwd=build_directory,
        )

        for generated_path in sorted(
            build_directory.glob(
                f"{output_prefix.name}.*"
            )
        ):
            shutil.copy2(
                generated_path,
                output_prefix.parent
                / generated_path.name,
            )

    database_files = sorted(
        output_prefix.parent.glob(
            f"{output_prefix.name}.*"
        )
    )

    files_metadata = []

    for path in database_files:
        files_metadata.append(
            {
                "name": path.name,
                "sha256": sha256_file(
                    path
                ),
                "size_bytes": (
                    path.stat().st_size
                ),
            }
        )

    metadata = {
        "database_version": (
            database_version
        ),
        "source": source,
        "marker": marker,
        "created_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "blast_version": (
            get_blast_version(
                makeblastdb_executable
            )
        ),
        "command": command,
        "input_fasta": {
            "path": str(fasta_path),
            "sha256": sha256_file(
                fasta_path
            ),
        },
        "sequence_count": (
            count_fasta_sequences(
                fasta_path
            )
        ),
        "index_files": files_metadata,
    }

    metadata_path = (
        output_prefix.parent
        / f"{output_prefix.name}.metadata.json"
    )

    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build a BioTrace local BLAST database."
        )
    )

    parser.add_argument(
        "--fasta",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    parser.add_argument(
        "--source",
        required=True,
    )

    parser.add_argument(
        "--marker",
        required=True,
    )

    parser.add_argument(
        "--database-version",
        required=True,
    )

    args = parser.parse_args()

    build_database(
        fasta_path=Path(args.fasta),
        output_prefix=Path(args.output),
        source=args.source,
        marker=args.marker,
        database_version=(
            args.database_version
        ),
    )


if __name__ == "__main__":
    main()
