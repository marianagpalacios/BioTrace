from src.search.contracts import SearchHit


def _parse_subject_id(
    subject_id: str,
) -> tuple[str, str, str]:
    parts = subject_id.split("|")

    if len(parts) != 3:
        raise ValueError(
            "Unexpected BLAST subject identifier format."
        )

    reference_id, species_token, accession = parts

    species = species_token.replace(
        "_",
        " ",
    )

    return (
        reference_id,
        species,
        accession,
    )


def parse_blast_tabular(
    output: str,
) -> list[SearchHit]:
    """Parse BioTrace BLAST tabular output."""

    hits: list[SearchHit] = []

    for raw_line in output.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        fields = line.split("\t")

        if len(fields) != 9:
            raise ValueError(
                "Unexpected BLAST output format."
            )

        (
            query_id,
            subject_id,
            identity,
            alignment_length,
            query_length,
            subject_length,
            evalue,
            bit_score,
            score,
        ) = fields

        (
            reference_id,
            species,
            accession,
        ) = _parse_subject_id(
            subject_id
        )

        query_length_value = int(
            query_length
        )

        alignment_length_value = int(
            alignment_length
        )

        coverage = (
            alignment_length_value
            / query_length_value
            * 100.0
            if query_length_value
            else 0.0
        )

        hits.append(
            SearchHit(
                species=species,
                reference_id=reference_id,
                identity=float(identity),
                coverage=coverage,
                score=float(score),
                evalue=float(evalue),
                bit_score=float(bit_score),
                accession=accession,
                backend="blast",
            )
        )

    return hits


def rank_blast_hits(
    hits: list[SearchHit],
    *,
    top_n: int,
) -> list[SearchHit]:
    """Rank BLAST hits using the BioTrace v0.8 rules."""

    best_by_species: dict[
        str,
        SearchHit,
    ] = {}

    for hit in hits:
        current = best_by_species.get(
            hit.species
        )

        if (
            current is None
            or _blast_sort_key(hit)
            > _blast_sort_key(current)
        ):
            best_by_species[
                hit.species
            ] = hit

    ranked = sorted(
        best_by_species.values(),
        key=_blast_sort_key,
        reverse=True,
    )

    return ranked[:top_n]


def _blast_sort_key(
    hit: SearchHit,
) -> tuple[float, float, float, float]:
    bit_score = (
        hit.bit_score
        if hit.bit_score is not None
        else float("-inf")
    )

    evalue = (
        hit.evalue
        if hit.evalue is not None
        else float("inf")
    )

    return (
        hit.identity,
        hit.coverage,
        bit_score,
        -evalue,
    )
