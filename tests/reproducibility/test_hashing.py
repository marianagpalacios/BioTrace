from src.reproducibility.hashing import (
    sha256_bytes,
    sha256_file,
    sha256_json,
)


def test_sha256_bytes_is_deterministic() -> None:
    content = b"BioTrace"

    first = sha256_bytes(content)
    second = sha256_bytes(content)

    assert first == second
    assert len(first) == 64


def test_sha256_file_matches_bytes(
    tmp_path,
) -> None:
    path = (
        tmp_path
        / "example.fasta"
    )

    content = (
        b">example\n"
        b"ACGTACGT\n"
    )

    path.write_bytes(content)

    assert sha256_file(path) == (
        sha256_bytes(content)
    )


def test_canonical_json_ignores_key_order() -> None:
    first = {
        "a": 1,
        "b": 2,
    }

    second = {
        "b": 2,
        "a": 1,
    }

    assert sha256_json(first) == (
        sha256_json(second)
    )


def test_json_hash_changes_with_content() -> None:
    assert sha256_json(
        {"top_n": 5}
    ) != sha256_json(
        {"top_n": 6}
    )
