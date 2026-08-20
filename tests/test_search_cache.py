from src.search.cache import (
    SearchCache,
    build_search_cache_key,
)
from src.search.contracts import SearchParameters


def test_same_inputs_generate_same_cache_key():
    parameters = SearchParameters(
        top_n=5,
        timeout_seconds=30.0,
    )

    key1 = build_search_cache_key(
        sequence="ATGC",
        database_hash="db123",
        parameters=parameters,
        backend="blast",
        blast_version="2.17.0+",
        biotrace_version="0.8.0-dev",
    )

    key2 = build_search_cache_key(
        sequence="ATGC",
        database_hash="db123",
        parameters=parameters,
        backend="blast",
        blast_version="2.17.0+",
        biotrace_version="0.8.0-dev",
    )

    assert key1 == key2


def test_cache_key_changes_when_backend_changes():
    parameters = SearchParameters()

    pairwise_key = build_search_cache_key(
        sequence="ATGC",
        database_hash="db123",
        parameters=parameters,
        backend="pairwise",
        blast_version=None,
        biotrace_version="0.8.0-dev",
    )

    blast_key = build_search_cache_key(
        sequence="ATGC",
        database_hash="db123",
        parameters=parameters,
        backend="blast",
        blast_version="2.17.0+",
        biotrace_version="0.8.0-dev",
    )

    assert pairwise_key != blast_key


def test_cache_key_changes_when_database_changes():
    parameters = SearchParameters()

    key1 = build_search_cache_key(
        sequence="ATGC",
        database_hash="db123",
        parameters=parameters,
        backend="blast",
        blast_version="2.17.0+",
        biotrace_version="0.8.0-dev",
    )

    key2 = build_search_cache_key(
        sequence="ATGC",
        database_hash="db456",
        parameters=parameters,
        backend="blast",
        blast_version="2.17.0+",
        biotrace_version="0.8.0-dev",
    )

    assert key1 != key2


def test_search_cache_reports_hit_and_miss():
    cache = SearchCache()

    assert cache.contains("abc") is False
    assert cache.get("abc") is None

    cache.set(
        "abc",
        ["cached-result"],
    )

    assert cache.contains("abc") is True
    assert cache.get("abc") == ["cached-result"]


def test_lookup_exposes_hit_state():
    cache = SearchCache()

    miss = cache.lookup(
        "missing"
    )

    assert miss.hit is False
    assert miss.value is None

    cache.set(
        "present",
        ["result"],
    )

    hit = cache.lookup(
        "present"
    )

    assert hit.hit is True
    assert hit.value == ["result"]
