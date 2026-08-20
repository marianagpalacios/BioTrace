from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from src.search.contracts import SearchParameters


def sha256_text(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def build_search_cache_key(
    *,
    sequence: str,
    database_hash: str,
    parameters: SearchParameters,
    backend: str,
    blast_version: str | None,
    biotrace_version: str,
) -> str:
    payload = {
        "sequence_sha256": (
            sha256_text(
                sequence.strip().upper()
            )
        ),
        "database_sha256": database_hash,
        "parameters": asdict(parameters),
        "backend": backend,
        "blast_version": blast_version,
        "biotrace_version": biotrace_version,
    }

    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )

    return sha256_text(serialized)


@dataclass(frozen=True)
class CacheLookupResult:
    value: object | None
    hit: bool


class SearchCache:
    """Simple in-memory cache for normalized search results."""

    def __init__(self) -> None:
        self._entries: dict[
            str,
            object,
        ] = {}

    def get(
        self,
        key: str,
    ):
        return self._entries.get(key)

    def lookup(
        self,
        key: str,
    ) -> CacheLookupResult:
        if key not in self._entries:
            return CacheLookupResult(
                value=None,
                hit=False,
            )

        return CacheLookupResult(
            value=self._entries[key],
            hit=True,
        )

    def set(
        self,
        key: str,
        value,
    ) -> None:
        self._entries[key] = value

    def clear(self) -> None:
        self._entries.clear()

    def contains(
        self,
        key: str,
    ) -> bool:
        return key in self._entries
