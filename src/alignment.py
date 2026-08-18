from dataclasses import dataclass
from typing import Literal

from Bio.Align import PairwiseAligner

from src.config import (
    DEFAULT_ALIGNMENT_EXTEND_GAP_SCORE,
    DEFAULT_ALIGNMENT_MATCH_SCORE,
    DEFAULT_ALIGNMENT_MISMATCH_SCORE,
    DEFAULT_ALIGNMENT_MODE,
    DEFAULT_ALIGNMENT_OPEN_GAP_SCORE,
)


AlignmentMode = Literal["global", "local"]


@dataclass(frozen=True)
class AlignmentResult:
    """Result of a pairwise nucleotide sequence alignment."""

    score: float
    identity: float
    coverage: float
    aligned_length: int
    matches: int


def align_sequences(
    candidate_sequence: str,
    reference_sequence: str,
    *,
    mode: AlignmentMode = DEFAULT_ALIGNMENT_MODE,
    match_score: float = DEFAULT_ALIGNMENT_MATCH_SCORE,
    mismatch_score: float = DEFAULT_ALIGNMENT_MISMATCH_SCORE,
    open_gap_score: float = DEFAULT_ALIGNMENT_OPEN_GAP_SCORE,
    extend_gap_score: float = DEFAULT_ALIGNMENT_EXTEND_GAP_SCORE,
) -> AlignmentResult:
    """Align a candidate sequence against a reference sequence."""

    candidate = candidate_sequence.strip().upper()
    reference = reference_sequence.strip().upper()

    if not candidate:
        raise ValueError("Candidate sequence cannot be empty.")

    if not reference:
        raise ValueError("Reference sequence cannot be empty.")

    if mode not in {"global", "local"}:
        raise ValueError(
            "Alignment mode must be 'global' or 'local'."
        )

    aligner = PairwiseAligner()

    aligner.mode = mode
    aligner.match_score = match_score
    aligner.mismatch_score = mismatch_score
    aligner.open_gap_score = open_gap_score
    aligner.extend_gap_score = extend_gap_score

    alignment = aligner.align(
        reference,
        candidate,
    )[0]

    aligned_reference = str(alignment[0])
    aligned_candidate = str(alignment[1])

    paired_bases = [
        (reference_base, candidate_base)
        for reference_base, candidate_base in zip(
            aligned_reference,
            aligned_candidate,
        )
        if reference_base != "-"
        and candidate_base != "-"
    ]

    matches = sum(
        reference_base == candidate_base
        for reference_base, candidate_base in paired_bases
    )

    aligned_length = len(paired_bases)

    identity = (
        matches / aligned_length * 100.0
        if aligned_length
        else 0.0
    )

    covered_candidate_bases = sum(
        base != "-"
        for base in aligned_candidate
    )

    coverage = (
        covered_candidate_bases
        / len(candidate)
        * 100.0
    )

    return AlignmentResult(
        score=float(alignment.score),
        identity=identity,
        coverage=coverage,
        aligned_length=aligned_length,
        matches=matches,
    )
