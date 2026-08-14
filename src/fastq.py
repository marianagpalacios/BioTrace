from pathlib import Path
from typing import TypedDict

from Bio import SeqIO


class FastqReadError(ValueError):
    """Erro levantado quando um arquivo FASTQ não pode ser interpretado."""


class FastqRecord(TypedDict):
    """Representação simplificada de uma leitura FASTQ."""

    id: str
    sequence: str
    qualities: list[int]


def read_fastq(file_path: str | Path) -> list[FastqRecord]:
    """
    Lê um arquivo FASTQ e retorna suas leituras.

    Cada leitura contém:

    - identificador;
    - sequência;
    - escores de qualidade Phred.
    """

    path = Path(file_path)

    records: list[FastqRecord] = []

    try:
        for record in SeqIO.parse(str(path), "fastq"):
            sequence = str(record.seq).upper()

            qualities = record.letter_annotations.get("phred_quality")

            if qualities is None:
                raise FastqReadError(
                    f"A leitura '{record.id}' não possui escores Phred."
                )

            qualities = list(qualities)

            if len(sequence) != len(qualities):
                raise FastqReadError(
                    f"A leitura '{record.id}' possui quantidade de escores "
                    "Phred diferente do comprimento da sequência."
                )

            records.append(
                {
                    "id": record.id,
                    "sequence": sequence,
                    "qualities": qualities,
                }
            )

    except FastqReadError:
        raise

    except Exception as exc:
        raise FastqReadError(
            f"Não foi possível ler o arquivo FASTQ: {path}"
        ) from exc

    return records