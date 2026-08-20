import pytest

from src.search.blast_parser import (
    parse_blast_tabular,
    rank_blast_hits,
)
from src.search.contracts import SearchHit


def test_parse_single_blast_hit():
    output = (
        "query1\t"
        "REF001|Species_alpha|ACC001.1\t"
        "100.0\t6\t6\t6\t1e-20\t50.0\t12.0"
    )

    hits = parse_blast_tabular(output)

    assert len(hits) == 1

    hit = hits[0]

    assert hit.species == "Species alpha"
    assert hit.reference_id == "REF001"
    assert hit.accession == "ACC001.1"
    assert hit.identity == 100.0
    assert hit.coverage == 100.0
    assert hit.evalue == 1e-20
    assert hit.bit_score == 50.0
    assert hit.score == 12.0
    assert hit.backend == "blast"


def test_parse_blast_hit_calculates_query_coverage():
    output = (
        "query1\t"
        "REF001|Species_alpha|ACC001.1\t"
        "95.0\t8\t10\t12\t1e-10\t40.0\t10.0"
    )

    hits = parse_blast_tabular(output)

    assert hits[0].coverage == 80.0


def test_empty_output_returns_empty_list():
    assert parse_blast_tabular("") == []


def test_invalid_field_count_is_rejected():
    with pytest.raises(
        ValueError,
        match="Unexpected BLAST output format",
    ):
        parse_blast_tabular(
            "query1\tREF001"
        )


def test_invalid_subject_id_is_rejected():
    output = (
        "query1\tREF001\t100.0\t6\t6\t6\t"
        "1e-20\t50.0\t12.0"
    )

    with pytest.raises(
        ValueError,
        match="Unexpected BLAST subject identifier format",
    ):
        parse_blast_tabular(output)


def test_ranking_prioritizes_identity():
    hits = [
        SearchHit(
            species="Species alpha",
            reference_id="REF001",
            identity=99.0,
            coverage=100.0,
            score=100.0,
            evalue=1e-50,
            bit_score=200.0,
            backend="blast",
        ),
        SearchHit(
            species="Species beta",
            reference_id="REF002",
            identity=100.0,
            coverage=80.0,
            score=80.0,
            evalue=1e-10,
            bit_score=150.0,
            backend="blast",
        ),
    ]

    ranked = rank_blast_hits(
        hits,
        top_n=5,
    )

    assert ranked[0].species == "Species beta"


def test_ranking_uses_coverage_as_second_criterion():
    hits = [
        SearchHit(
            species="Species alpha",
            reference_id="REF001",
            identity=99.0,
            coverage=90.0,
            score=90.0,
            evalue=1e-20,
            bit_score=100.0,
            backend="blast",
        ),
        SearchHit(
            species="Species beta",
            reference_id="REF002",
            identity=99.0,
            coverage=95.0,
            score=90.0,
            evalue=1e-20,
            bit_score=100.0,
            backend="blast",
        ),
    ]

    ranked = rank_blast_hits(
        hits,
        top_n=5,
    )

    assert ranked[0].species == "Species beta"


def test_ranking_uses_bit_score_before_evalue():
    hits = [
        SearchHit(
            species="Species alpha",
            reference_id="REF001",
            identity=99.0,
            coverage=95.0,
            score=90.0,
            evalue=1e-100,
            bit_score=100.0,
            backend="blast",
        ),
        SearchHit(
            species="Species beta",
            reference_id="REF002",
            identity=99.0,
            coverage=95.0,
            score=90.0,
            evalue=1e-20,
            bit_score=120.0,
            backend="blast",
        ),
    ]

    ranked = rank_blast_hits(
        hits,
        top_n=5,
    )

    assert ranked[0].species == "Species beta"


def test_ranking_uses_lower_evalue_as_final_criterion():
    hits = [
        SearchHit(
            species="Species alpha",
            reference_id="REF001",
            identity=99.0,
            coverage=95.0,
            score=90.0,
            evalue=1e-20,
            bit_score=120.0,
            backend="blast",
        ),
        SearchHit(
            species="Species beta",
            reference_id="REF002",
            identity=99.0,
            coverage=95.0,
            score=90.0,
            evalue=1e-50,
            bit_score=120.0,
            backend="blast",
        ),
    ]

    ranked = rank_blast_hits(
        hits,
        top_n=5,
    )

    assert ranked[0].species == "Species beta"


def test_ranking_keeps_best_hit_per_species():
    hits = [
        SearchHit(
            species="Species alpha",
            reference_id="REF001",
            identity=95.0,
            coverage=90.0,
            score=80.0,
            evalue=1e-10,
            bit_score=80.0,
            backend="blast",
        ),
        SearchHit(
            species="Species alpha",
            reference_id="REF002",
            identity=99.0,
            coverage=100.0,
            score=100.0,
            evalue=1e-30,
            bit_score=120.0,
            backend="blast",
        ),
    ]

    ranked = rank_blast_hits(
        hits,
        top_n=5,
    )

    assert len(ranked) == 1
    assert ranked[0].reference_id == "REF002"
