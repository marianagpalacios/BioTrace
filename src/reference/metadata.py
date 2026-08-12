"""Reference database provenance metadata and integrity checks."""

from dataclasses import asdict, dataclass
from datetime import date
import hashlib
import json
from pathlib import Path
import re

import pandas as pd


_METADATA_REQUIRED_FIELDS = frozenset(
    {
        "name",
        "version",
        "marker",
        "taxonomic_scope",
        "source",
        "created_at",
        "record_count",
        "species_count",
        "csv_sha256",
    }
)

_VERSION_PATTERN = re.compile(
    r"^\d+\.\d+\.\d+$"
)

_SHA256_PATTERN = re.compile(
    r"^[a-f0-9]{64}$"
)


@dataclass(frozen=True)
class ReferenceDatabaseMetadata:
    """Provenance information for one database version."""

    name: str
    version: str
    marker: str
    taxonomic_scope: str
    source: str
    created_at: str
    record_count: int
    species_count: int
    csv_sha256: str

    def to_dict(
        self,
    ) -> dict[str, str | int]:
        return asdict(self)


class ReferenceMetadataError(Exception):
    """Raised when metadata are invalid or inconsistent."""


def calculate_sha256(
    file_path: str | Path,
) -> str:
    """Calculate the SHA-256 digest of a file."""
    path = Path(file_path)
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(65_536),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def load_reference_metadata(
    file_path: str | Path,
) -> ReferenceDatabaseMetadata:
    """Load and structurally validate metadata."""
    path = Path(file_path)

    if not path.exists():
        raise ReferenceMetadataError(
            f"Metadados do banco não encontrados: {path}."
        )

    if not path.is_file():
        raise ReferenceMetadataError(
            f"O caminho dos metadados não é um arquivo: {path}."
        )

    try:
        payload = json.loads(
            path.read_text(encoding="utf-8")
        )

    except json.JSONDecodeError as error:
        raise ReferenceMetadataError(
            "O arquivo de metadados contém JSON inválido."
        ) from error

    except OSError as error:
        raise ReferenceMetadataError(
            f"Não foi possível ler os metadados: {error}."
        ) from error

    if not isinstance(payload, dict):
        raise ReferenceMetadataError(
            "Os metadados devem ser um objeto JSON."
        )

    missing_fields = (
        _METADATA_REQUIRED_FIELDS.difference(
            payload
        )
    )

    if missing_fields:
        raise ReferenceMetadataError(
            "Campos obrigatórios ausentes: "
            + ", ".join(sorted(missing_fields))
            + "."
        )

    try:
        metadata = ReferenceDatabaseMetadata(
            name=str(payload["name"]).strip(),
            version=str(
                payload["version"]
            ).strip(),
            marker=str(payload["marker"]).strip(),
            taxonomic_scope=str(
                payload["taxonomic_scope"]
            ).strip(),
            source=str(
                payload["source"]
            ).strip(),
            created_at=str(
                payload["created_at"]
            ).strip(),
            record_count=int(
                payload["record_count"]
            ),
            species_count=int(
                payload["species_count"]
            ),
            csv_sha256=str(
                payload["csv_sha256"]
            ).strip().lower(),
        )

    except (TypeError, ValueError) as error:
        raise ReferenceMetadataError(
            "Os tipos dos campos de metadados são inválidos."
        ) from error

    errors: list[str] = []

    if not _VERSION_PATTERN.fullmatch(
        metadata.version
    ):
        errors.append(
            "A versão deve seguir o formato X.Y.Z."
        )

    try:
        created_at = date.fromisoformat(
            metadata.created_at
        )

        if created_at > date.today():
            errors.append(
                "A data dos metadados não pode estar no futuro."
            )

    except ValueError:
        errors.append(
            "A data deve seguir o formato YYYY-MM-DD."
        )

    if metadata.record_count < 1:
        errors.append(
            "A quantidade de registros deve ser positiva."
        )

    if metadata.species_count < 1:
        errors.append(
            "A quantidade de espécies deve ser positiva."
        )

    if not _SHA256_PATTERN.fullmatch(
        metadata.csv_sha256
    ):
        errors.append(
            "O checksum deve ser um SHA-256 "
            "hexadecimal de 64 caracteres."
        )

    if errors:
        raise ReferenceMetadataError(
            "\n".join(errors)
        )

    return metadata


def validate_reference_metadata(
    metadata: ReferenceDatabaseMetadata,
    database_path: str | Path,
    dataframe: pd.DataFrame,
) -> None:
    """Compare metadata with the current CSV."""
    errors: list[str] = []

    actual_hash = calculate_sha256(
        database_path
    )

    actual_record_count = len(dataframe)

    actual_species_count = (
        dataframe["species"].nunique()
    )

    if metadata.csv_sha256 != actual_hash:
        errors.append(
            "O checksum do CSV não corresponde "
            "aos metadados."
        )

    if (
        metadata.record_count
        != actual_record_count
    ):
        errors.append(
            "A quantidade de registros dos "
            "metadados não corresponde ao CSV."
        )

    if (
        metadata.species_count
        != actual_species_count
    ):
        errors.append(
            "A quantidade de espécies dos "
            "metadados não corresponde ao CSV."
        )

    actual_markers = set(
        dataframe["marker_region"].unique()
    )

    if actual_markers != {metadata.marker}:
        errors.append(
            "O marcador dos metadados não "
            "corresponde ao CSV."
        )

    actual_sources = set(
        dataframe["source"].unique()
    )

    if actual_sources != {metadata.source}:
        errors.append(
            "A fonte dos metadados não "
            "corresponde ao CSV."
        )

    if errors:
        raise ReferenceMetadataError(
            "\n".join(errors)
        )