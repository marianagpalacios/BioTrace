"""Deterministic hashing helpers."""

import hashlib
import json
from pathlib import Path
from typing import Any


HASH_CHUNK_SIZE = 1024 * 1024


def sha256_bytes(
    content: bytes,
) -> str:
    """Return the SHA-256 of raw bytes."""

    return hashlib.sha256(
        content
    ).hexdigest()


def sha256_file(
    file_path: str | Path,
) -> str:
    """Calculate SHA-256 without loading the whole file."""

    path = Path(file_path)

    digest = hashlib.sha256()

    with path.open("rb") as file:
        while chunk := file.read(
            HASH_CHUNK_SIZE
        ):
            digest.update(chunk)

    return digest.hexdigest()


def _json_default(
    value: Any,
) -> Any:
    """Normalize scalar-like objects for JSON serialization."""

    if hasattr(value, "item"):
        return value.item()

    raise TypeError(
        f"Objeto não serializável: "
        f"{type(value).__name__}"
    )


def canonical_json_bytes(
    value: Any,
) -> bytes:
    """Serialize JSON deterministically."""

    serialized = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        default=_json_default,
    )

    return serialized.encode(
        "utf-8"
    )


def sha256_json(
    value: Any,
) -> str:
    """Return SHA-256 for a canonical JSON representation."""

    return sha256_bytes(
        canonical_json_bytes(value)
    )