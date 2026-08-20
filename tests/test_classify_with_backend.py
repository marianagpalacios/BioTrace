from src.search.contracts import (
    SearchHit,
    SearchParameters,
)
from src.taxonomy import classify_with_backend


class FakeBackend:
    @property
    def name(self):
        return "fake"

    def search(
        self,
        sequence: str,
        parameters: SearchParameters,
    ):
        return [
            SearchHit(
                species="Species alpha",
                reference_id="REF001",
                identity=99.5,
                coverage=98.0,
                score=150.0,
                evalue=1e-40,
                bit_score=120.0,
                accession="ACC001.1",
                gene="COI",
                source="NCBI",
                backend="fake",
            )
        ]


def test_classify_with_backend_identifies_species():
    result = classify_with_backend(
        "ATGC",
        backend=FakeBackend(),
        min_similarity=95.0,
        top_n=5,
    )

    assert result["species"] == "Species alpha"
    assert result["identified"] is True
    assert result["backend"] == "fake"
    assert result["similarity"] == 99.5
    assert result["alignment_identity"] == 99.5
    assert result["alignment_coverage"] == 98.0
    assert result["evalue"] == 1e-40
    assert result["bit_score"] == 120.0


def test_classify_with_backend_respects_threshold():
    result = classify_with_backend(
        "ATGC",
        backend=FakeBackend(),
        min_similarity=100.0,
    )

    assert result["species"] is None
    assert result["identified"] is False
    assert result["similarity"] == 99.5


def test_classify_with_backend_builds_ranking():
    result = classify_with_backend(
        "ATGC",
        backend=FakeBackend(),
        min_similarity=95.0,
    )

    assert len(result["ranking"]) == 1

    ranking_hit = result["ranking"][0]

    assert ranking_hit["species"] == "Species alpha"
    assert ranking_hit["evalue"] == 1e-40
    assert ranking_hit["bit_score"] == 120.0
    assert ranking_hit["backend"] == "fake"


class EmptyBackend:
    @property
    def name(self):
        return "empty"

    def search(
        self,
        sequence: str,
        parameters: SearchParameters,
    ):
        return []


def test_classify_with_backend_handles_no_hits():
    result = classify_with_backend(
        "ATGC",
        backend=EmptyBackend(),
        min_similarity=95.0,
    )

    assert result["species"] is None
    assert result["identified"] is False
    assert result["similarity"] == 0.0
    assert result["ranking"] == []
    assert result["backend"] == "empty"