from dataclasses import dataclass
import re

import pandas as pd

from src.config import (
    REFERENCE_OPTIONAL_COLUMNS,
    REFERENCE_REQUIRED_COLUMNS,
    REFERENCE_VALID_BASES,
)

_TEXT_COLUMNS = (
    "species",
    "id",
    "gene",
    "marker_region",
    "accession",
    "source",
    "retrieved_at",
)

_WHITESPACE_PATTERN = re.compile(r"\s+")


@dataclass(frozen=True)
class ReferenceValidationResult:
    """Normalized reference data and non-blocking warnings."""

    dataframe: pd.DataFrame
    warnings: tuple[str, ...]


class ReferenceDatabaseValidationError(Exception):
    """Raised when blocking data-quality errors are found."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = tuple(errors)
        details = "\n".join(
            f"- {message}"
            for message in errors
        )
        super().__init__(
            f"Banco de referência inválido:\n{details}"
        )


def _csv_rows(indexes: pd.Index) -> str:
    """Convert DataFrame indexes to CSV line numbers."""
    return ", ".join(
        str(int(index) + 2)
        for index in indexes
    )


def validate_reference_dataframe(
    database: pd.DataFrame,
) -> ReferenceValidationResult:
    """Validate required fields and apply safe normalizations."""
    missing_columns = REFERENCE_REQUIRED_COLUMNS.difference(
        database.columns
    )

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))

        raise ReferenceDatabaseValidationError(
            [f"Colunas obrigatórias ausentes: {missing}."]
        )

    normalized = database.copy()
    errors: list[str] = []
    warnings: list[str] = []

    empty_rows = normalized[
        list(REFERENCE_REQUIRED_COLUMNS)
    ].apply(
        lambda column: column.astype(str).str.strip().eq("")
    ).all(axis=1)

    if empty_rows.any():
        errors.append(
            "Linhas completamente vazias nos campos obrigatórios: "
            f"{_csv_rows(normalized.index[empty_rows])}."
        )

    for column in _TEXT_COLUMNS:
        if column not in normalized.columns:
            continue

        original = normalized[column].astype(str)
        stripped = original.str.strip()
        changed = original.ne(stripped)

        if changed.any():
            warnings.append(
                f"Espaços externos removidos da coluna "
                f"'{column}' nas linhas "
                f"{_csv_rows(normalized.index[changed])}."
            )

        normalized[column] = stripped

    original_sequences = normalized["sequence"].astype(str)

    compact_sequences = original_sequences.str.replace(
        _WHITESPACE_PATTERN,
        "",
        regex=True,
    )

    whitespace_changed = original_sequences.ne(
        compact_sequences
    )

    if whitespace_changed.any():
        warnings.append(
            "Espaços removidos das sequências nas linhas "
            f"{_csv_rows(normalized.index[whitespace_changed])}."
        )

    lowercase_rows = compact_sequences.str.contains(
        r"[a-z]",
        regex=True,
    )

    if lowercase_rows.any():
        warnings.append(
            "Sequências convertidas para maiúsculas nas linhas "
            f"{_csv_rows(normalized.index[lowercase_rows])}."
        )

    normalized["sequence"] = compact_sequences.str.upper()

    required_messages = {
        "species": "Espécies sem nome",
        "id": "Referências sem ID",
        "sequence": "Sequências vazias",
    }

    for column, label in required_messages.items():
        blank_rows = (
            normalized[column]
            .astype(str)
            .str.strip()
            .eq("")
        )

        if blank_rows.any():
            errors.append(
                f"{label} nas linhas "
                f"{_csv_rows(normalized.index[blank_rows])}."
            )

    nonempty_ids = normalized.loc[
        normalized["id"].astype(str).str.strip().ne(""),
        "id",
    ]

    duplicate_ids = nonempty_ids.duplicated(
        keep=False
    )

    if duplicate_ids.any():
        errors.append(
            "IDs duplicados nas linhas "
            f"{_csv_rows(nonempty_ids.index[duplicate_ids])}."
        )

    invalid_rows: list[str] = []

    for index, sequence in normalized["sequence"].items():
        if not sequence:
            continue

        invalid_bases = sorted(
            set(sequence).difference(
                REFERENCE_VALID_BASES
            )
        )

        if invalid_bases:
            invalid_rows.append(
                f"linha {int(index) + 2} "
                f"({', '.join(invalid_bases)})"
            )

    if invalid_rows:
        errors.append(
            "Caracteres inválidos nas sequências: "
            + "; ".join(invalid_rows)
            + "."
        )

    missing_optional = REFERENCE_OPTIONAL_COLUMNS.difference(
        normalized.columns
    )

    if missing_optional:
        warnings.append(
            "Colunas opcionais ausentes: "
            + ", ".join(sorted(missing_optional))
            + "."
        )

    species_variants: dict[str, set[str]] = {}

    for species in normalized["species"].astype(str):
        if species:
            species_variants.setdefault(
                species.casefold(),
                set(),
            ).add(species)

    inconsistent_names = [
        sorted(variants)
        for variants in species_variants.values()
        if len(variants) > 1
    ]

    if inconsistent_names:
        formatted = "; ".join(
            " / ".join(group)
            for group in inconsistent_names
        )

        warnings.append(
            "Possíveis inconsistências de capitalização "
            f"em espécies: {formatted}."
        )

    if errors:
        raise ReferenceDatabaseValidationError(errors)

    return ReferenceValidationResult(
        dataframe=normalized.reset_index(drop=True),
        warnings=tuple(warnings),
    )