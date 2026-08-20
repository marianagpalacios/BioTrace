from Bio import SeqIO


SequenceRecord = dict[str, str]


def read_fasta(file_path: str) -> list[SequenceRecord]:
    """Read sequence identifiers and nucleotide strings from a FASTA file."""

    sequences: list[SequenceRecord] = []

    for record in SeqIO.parse(file_path, "fasta"):
        sequences.append(
            {
                "id": str(record.id),
                "sequence": str(record.seq).replace("\n", "").replace(" ", ""),
            }
        )

    return sequences
