"""Generate a small deterministic FASTQ example for BioTrace QC."""

from pathlib import Path
import sys

import pandas as pd

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from src.config import (  # noqa: E402
    DEFAULT_REFERENCE_DATABASE_PATH,
)


OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "examples"
    / "example_reads.fastq"
)


def _reference_sequence(
    dataframe: pd.DataFrame,
    accession: str,
) -> str:
    matches = dataframe[
        dataframe["accession"]
        == accession
    ]

    if len(matches) != 1:
        raise SystemExit(
            "A referência "
            f"{accession} não foi "
            "encontrada exatamente "
            "uma vez."
        )

    return str(
        matches.iloc[0]["sequence"]
    ).strip().upper()


def _record(
    record_id: str,
    sequence: str,
    qualities: list[int],
) -> SeqRecord:
    record = SeqRecord(
        Seq(sequence),
        id=record_id,
        description="",
    )

    record.letter_annotations[
        "phred_quality"
    ] = qualities

    return record


def main() -> None:
    database = pd.read_csv(
        DEFAULT_REFERENCE_DATABASE_PATH,
        dtype=str,
    )

    dre001 = _reference_sequence(
        database,
        "HQ141077.1",
    )

    dre002 = _reference_sequence(
        database,
        "HQ141079.1",
    )

    pass_qualities = (
        [10] * 4
        + [35] * (
            len(dre001) - 8
        )
        + [10] * 4
    )

    low_mean_qualities = (
        [35]
        + [18] * (
            len(dre002) - 2
        )
        + [35]
    )

    short_sequence = dre001[:400]

    records = [
        _record(
            "read_pass_trimmed",
            dre001,
            pass_qualities,
        ),
        _record(
            "read_reject_quality",
            dre002,
            low_mean_qualities,
        ),
        _record(
            "read_reject_length",
            short_sequence,
            [35] * len(short_sequence),
        ),
    ]

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    count = SeqIO.write(
        records,
        OUTPUT_PATH,
        "fastq",
    )

    print(
        "FASTQ de exemplo "
        f"gerado em: {OUTPUT_PATH}"
    )

    print(
        f"Registros: {count}"
    )


if __name__ == "__main__":
    main()