from src.fasta import SequenceRecord


DEFAULT_VALID_BASES = {"A", "T", "C", "G", "N"}
STRICT_VALID_BASES = {"A", "T", "C", "G"}


def get_valid_bases(allow_n: bool = True) -> set[str]:
    """Return the set of accepted DNA bases for the current validation mode."""
    return DEFAULT_VALID_BASES if allow_n else STRICT_VALID_BASES


def find_invalid_bases(sequence: str, allow_n: bool = True) -> list[str]:
    """Return invalid bases found in a sequence, preserving a readable order."""
    valid_bases = get_valid_bases(allow_n)
    invalid_bases = {base for base in sequence.upper() if base not in valid_bases}
    return sorted(invalid_bases)


def validate_sequences(
    sequences: list[SequenceRecord],
    allow_n: bool = True,
) -> tuple[list[SequenceRecord], list[dict[str, object]]]:
    """Split FASTA records into valid and invalid sequence groups."""
    valid_sequences: list[SequenceRecord] = []
    invalid_sequences: list[dict[str, object]] = []

    for item in sequences:
        sequence_id = item.get("id", "Sem ID")
        sequence = item.get("sequence", "").upper().strip()

        if not sequence:
            invalid_sequences.append(
                {
                    "id": sequence_id,
                    "invalid_bases": [],
                    "reason": "Sequência vazia.",
                }
            )
            continue

        invalid_bases = find_invalid_bases(sequence, allow_n=allow_n)

        if invalid_bases:
            invalid_sequences.append(
                {
                    "id": sequence_id,
                    "invalid_bases": invalid_bases,
                    "reason": "Bases inválidas encontradas.",
                }
            )
            continue

        valid_sequences.append({"id": sequence_id, "sequence": sequence})

    return valid_sequences, invalid_sequences