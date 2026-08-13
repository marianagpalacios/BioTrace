"""Generate a reproducible example FASTA from the curated database."""

from pathlib import Path
import textwrap

import pandas as pd

from src.config import (
    DEFAULT_REFERENCE_DATABASE_PATH,
    PROJECT_ROOT,
)


OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "examples"
    / "example_query.fasta"
)

EXAMPLE_ACCESSION = "HQ141077.1"


def main() -> None:
    database = pd.read_csv(
        DEFAULT_REFERENCE_DATABASE_PATH,
        dtype=str,
    )

    matches = database[
        database["accession"]
        == EXAMPLE_ACCESSION
    ]

    if len(matches) != 1:
        raise SystemExit(
            "A referência usada no exemplo "
            "não foi encontrada exatamente uma vez."
        )

    row = matches.iloc[0]

    sequence = str(
        row["sequence"]
    ).strip().upper()

    wrapped = "\n".join(
        textwrap.wrap(
            sequence,
            width=70,
        )
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        (
            ">example_query"
            f"|reference={row['id']}"
            f"|accession={row['accession']}"
            "\n"
            f"{wrapped}\n"
        ),
        encoding="utf-8",
        newline="\n",
    )

    print(
        f"FASTA de exemplo gerado em: "
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
