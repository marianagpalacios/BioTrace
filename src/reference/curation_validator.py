"""Scientific validation rules for the curated reference database."""

from dataclasses import dataclass
from datetime import date
import re

import pandas as pd

from src.config import (
    CURATED_REFERENCE_REQUIRED_COLUMNS,
    CURATED_REFERENCE_VALID_BASES,
    REFERENCE_EXPECTED_GENE,
    REFERENCE_EXPECTED_MARKER_REGION,
    REFERENCE_EXPECTED_SOURCE,
    REFERENCE_MAX_LENGTH_SPREAD,
    REFERENCE_MAX_SEQUENCE_LENGTH,
    REFERENCE_MIN_RECORDS_PER_SPECIES,
    REFERENCE_MIN_SEQUENCE_LENGTH,
)


_SPECIES_PATTERN = re.compile(
    r"^[A-Z][a-z]+ [a-z][a-z-]+$"
)

_ACCESSION_VERSION_PATTERN = re.compile(
    r"^[A-Za-z0-9_]+\.\d+$"
)


@dataclass(frozen=True)
class CuratedReferenceValidationResult:
    """Validated curated data and non-blocking warnings."""

    dataframe: pd.DataFrame
    warnings: tuple[str, ...]


class CuratedReferenceValidationError(Exception):
    """Raised when scientific curation rules are violated."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = tuple(errors)

        details = "\n".join(
            f"- {message}"
            for message in errors
        )

        super().__init__(
            "Banco de referência curado inválido:\n"
            f"{details}"
        )


def _csv_rows(indexes: pd.Index) -> str:
    """Convert DataFrame indexes to CSV line numbers."""

    return ", ".join(
        str(int(index) + 2)
        for index in indexes
    )


def validate_curated_reference_dataframe(
    database: pd.DataFrame,
    *,
    today: date | None = None,
) -> CuratedReferenceValidationResult:
    """Validate scientific rules for the curated database."""

    missing_columns = (
        CURATED_REFERENCE_REQUIRED_COLUMNS.difference(
            database.columns
        )
    )

    if missing_columns:
        missing = ", ".join(
            sorted(missing_columns)
        )

        raise CuratedReferenceValidationError(
            [
                "Colunas obrigatórias da base curada "
                f"ausentes: {missing}."
            ]
        )

    current_date = today or date.today()

    normalized = database.copy()

    errors: list[str] = []
    warnings: list[str] = []

    # -------------------------------------------------
    # Normalizações seguras
    # -------------------------------------------------

    for column in (
        "species",
        "id",
        "gene",
        "marker_region",
        "accession",
        "source",
        "retrieved_at",
    ):
        normalized[column] = (
            normalized[column]
            .astype(str)
            .str.strip()
        )

    normalized["sequence"] = (
        normalized["sequence"]
        .astype(str)
        .str.replace(
            r"\s+",
            "",
            regex=True,
        )
        .str.upper()
    )

    # -------------------------------------------------
    # Nome científico binomial
    # -------------------------------------------------

    invalid_species = ~normalized[
        "species"
    ].str.fullmatch(
        _SPECIES_PATTERN
    )

    if invalid_species.any():
        errors.append(
            "Nomes científicos fora do formato "
            "binomial nas linhas "
            f"{_csv_rows(normalized.index[invalid_species])}."
        )

    # -------------------------------------------------
    # Accession com versão
    # -------------------------------------------------

    invalid_accessions = ~normalized[
        "accession"
    ].str.fullmatch(
        _ACCESSION_VERSION_PATTERN
    )

    if invalid_accessions.any():
        errors.append(
            "Accessions sem versão válida nas linhas "
            f"{_csv_rows(normalized.index[invalid_accessions])}."
        )

    # -------------------------------------------------
    # Accessions únicos
    # -------------------------------------------------

    duplicate_accessions = normalized[
        "accession"
    ].duplicated(
        keep=False
    )

    if duplicate_accessions.any():
        errors.append(
            "Accessions duplicados nas linhas "
            f"{_csv_rows(normalized.index[duplicate_accessions])}."
        )

    # -------------------------------------------------
    # Gene esperado
    # -------------------------------------------------

    invalid_gene = (
        normalized["gene"]
        != REFERENCE_EXPECTED_GENE
    )

    if invalid_gene.any():
        errors.append(
            f"Gene diferente de "
            f"'{REFERENCE_EXPECTED_GENE}' nas linhas "
            f"{_csv_rows(normalized.index[invalid_gene])}."
        )

    # -------------------------------------------------
    # Região do marcador
    # -------------------------------------------------

    invalid_marker = (
        normalized["marker_region"]
        != REFERENCE_EXPECTED_MARKER_REGION
    )

    if invalid_marker.any():
        errors.append(
            "Marcador diferente de "
            f"'{REFERENCE_EXPECTED_MARKER_REGION}' "
            "nas linhas "
            f"{_csv_rows(normalized.index[invalid_marker])}."
        )

    # -------------------------------------------------
    # Fonte
    # -------------------------------------------------

    invalid_source = (
        normalized["source"]
        != REFERENCE_EXPECTED_SOURCE
    )

    if invalid_source.any():
        errors.append(
            "Fonte diferente de "
            f"'{REFERENCE_EXPECTED_SOURCE}' nas linhas "
            f"{_csv_rows(normalized.index[invalid_source])}."
        )

    # -------------------------------------------------
    # retrieved_at
    # -------------------------------------------------

    for index, raw_date in normalized[
        "retrieved_at"
    ].items():
        try:
            retrieved_at = date.fromisoformat(
                raw_date
            )

        except ValueError:
            errors.append(
                "Data retrieved_at inválida na linha "
                f"{int(index) + 2}: '{raw_date}'. "
                "Use YYYY-MM-DD."
            )
            continue

        if retrieved_at > current_date:
            errors.append(
                "retrieved_at não pode estar no futuro "
                f"na linha {int(index) + 2}."
            )

    # -------------------------------------------------
    # Bases permitidas
    # -------------------------------------------------

    invalid_sequence_rows: list[str] = []

    for index, sequence in normalized[
        "sequence"
    ].items():
        invalid_bases = sorted(
            set(sequence).difference(
                CURATED_REFERENCE_VALID_BASES
            )
        )

        if invalid_bases:
            invalid_sequence_rows.append(
                f"linha {int(index) + 2} "
                f"({', '.join(invalid_bases)})"
            )

    if invalid_sequence_rows:
        errors.append(
            "Bases inválidas na base curada: "
            + "; ".join(invalid_sequence_rows)
            + "."
        )

    # -------------------------------------------------
    # Comprimento
    # -------------------------------------------------

    lengths = normalized[
        "sequence"
    ].str.len()

    invalid_lengths = ~lengths.between(
        REFERENCE_MIN_SEQUENCE_LENGTH,
        REFERENCE_MAX_SEQUENCE_LENGTH,
    )

    if invalid_lengths.any():
        errors.append(
            "Sequências fora do intervalo "
            f"{REFERENCE_MIN_SEQUENCE_LENGTH}-"
            f"{REFERENCE_MAX_SEQUENCE_LENGTH} bp "
            "nas linhas "
            f"{_csv_rows(normalized.index[invalid_lengths])}."
        )

    # -------------------------------------------------
    # Mínimo de referências por espécie
    # -------------------------------------------------

    species_counts = normalized.groupby(
        "species"
    ).size()

    for species, count in species_counts.items():
        if count < REFERENCE_MIN_RECORDS_PER_SPECIES:
            errors.append(
                f"A espécie '{species}' possui "
                f"{count} referência(s); mínimo esperado: "
                f"{REFERENCE_MIN_RECORDS_PER_SPECIES}."
            )

    # -------------------------------------------------
    # Sequências idênticas
    # -------------------------------------------------

    sequence_groups = normalized.groupby(
        "sequence",
        sort=False,
    )

    for sequence, group in sequence_groups:
        if not sequence or len(group) < 2:
            continue

        species = sorted(
            group["species"].unique()
        )

        accessions = sorted(
            group["accession"].tolist()
        )

        formatted_accessions = ", ".join(
            accessions
        )

        if len(species) > 1:
            errors.append(
                "Sequência idêntica encontrada em "
                "espécies diferentes: "
                f"{', '.join(species)}; accessions: "
                f"{formatted_accessions}."
            )

        else:
            warnings.append(
                "Sequência idêntica dentro da espécie "
                f"'{species[0]}' nos accessions "
                f"{formatted_accessions}."
            )

    # -------------------------------------------------
    # Variação excessiva de comprimento
    # -------------------------------------------------

    working = normalized.copy()
    working["_sequence_length"] = lengths

    for species, group in working.groupby(
        "species"
    ):
        spread = (
            group["_sequence_length"].max()
            - group["_sequence_length"].min()
        )

        if spread > REFERENCE_MAX_LENGTH_SPREAD:
            warnings.append(
                f"A espécie '{species}' apresenta "
                f"variação de {spread} bp entre "
                "suas referências."
            )

    # -------------------------------------------------
    # Resultado
    # -------------------------------------------------

    if errors:
        raise CuratedReferenceValidationError(
            errors
        )

    return CuratedReferenceValidationResult(
        dataframe=normalized.reset_index(
            drop=True
        ),
        warnings=tuple(warnings),
    )