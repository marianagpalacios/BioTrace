from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def verify_database(
    metadata_path: Path,
) -> None:
    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Metadata file not found: {metadata_path}"
        )

    metadata = json.loads(
        metadata_path.read_text(
            encoding="utf-8"
        )
    )

    base_directory = metadata_path.parent

    index_files = metadata.get(
        "index_files",
        [],
    )

    if not index_files:
        raise ValueError(
            "No BLAST index files recorded in metadata."
        )

    for file_info in index_files:
        file_name = file_info["name"]
        expected_sha256 = file_info["sha256"]

        file_path = (
            base_directory
            / file_name
        )

        if not file_path.exists():
            raise FileNotFoundError(
                f"BLAST index file not found: {file_path}"
            )

        actual_sha256 = sha256_file(
            file_path
        )

        if actual_sha256 != expected_sha256:
            raise ValueError(
                "Checksum mismatch for "
                f"{file_name}: "
                f"expected={expected_sha256}, "
                f"actual={actual_sha256}"
            )

    input_fasta = metadata.get(
        "input_fasta"
    )

    if input_fasta:
        fasta_path = Path(
            input_fasta["path"]
        )

        if fasta_path.exists():
            actual_fasta_hash = sha256_file(
                fasta_path
            )

            expected_fasta_hash = (
                input_fasta["sha256"]
            )

            if (
                actual_fasta_hash
                != expected_fasta_hash
            ):
                raise ValueError(
                    "Input FASTA checksum mismatch."
                )

    print(
        "BLAST database verification passed."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Verify a BioTrace BLAST database "
            "against its metadata."
        )
    )

    parser.add_argument(
        "--metadata",
        required=True,
    )

    args = parser.parse_args()

    verify_database(
        Path(args.metadata)
    )


if __name__ == "__main__":
    main()
