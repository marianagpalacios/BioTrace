"""Dispatch BioTrace analyses according to the input sequence format."""

from pathlib import Path

from src.config import (
    DEFAULT_ALLOW_N,
    DEFAULT_FASTQ_MAX_LENGTH,
    DEFAULT_FASTQ_MIN_LENGTH,
    DEFAULT_FASTQ_MIN_MEAN_QUALITY,
    DEFAULT_FASTQ_TRIM_ENDS,
    DEFAULT_FASTQ_TRIM_QUALITY,
    DEFAULT_MIN_SIMILARITY,
    DEFAULT_REFERENCE_DATABASE_PATH,
    DEFAULT_REFERENCE_METADATA_PATH,
    DEFAULT_TOP_N,
)
from src.contracts import (
    AnalysisResult,
    InputFormat,
)
from src.search.cache import SearchCache
from src.services.analysis_service import (
    ProgressCallback,
    analyze_fasta_file,
)
from src.services.fastq_analysis_service import (
    analyze_fastq_file,
)


def analyze_sequence_file(
    file_path: str,
    *,
    input_format: InputFormat,
    reference_database_path: str | Path = (
        DEFAULT_REFERENCE_DATABASE_PATH
    ),
    min_similarity: float = DEFAULT_MIN_SIMILARITY,
    allow_n: bool = DEFAULT_ALLOW_N,
    top_n: int = DEFAULT_TOP_N,
    progress_callback: ProgressCallback | None = None,
    reference_metadata_path: str | Path = (
        DEFAULT_REFERENCE_METADATA_PATH
    ),
    min_mean_quality: float = (
        DEFAULT_FASTQ_MIN_MEAN_QUALITY
    ),
    min_length: int = DEFAULT_FASTQ_MIN_LENGTH,
    max_length: int = DEFAULT_FASTQ_MAX_LENGTH,
    trim_ends: bool = DEFAULT_FASTQ_TRIM_ENDS,
    trim_quality_threshold: int = (
        DEFAULT_FASTQ_TRIM_QUALITY
    ),
    search_backend: str = "pairwise",
    blast_database_path: str | None = None,
    search_timeout_seconds: float = 30.0,
    search_database_hash: str = "",
    blast_version: str | None = None,
    search_cache: SearchCache | None = None,
) -> AnalysisResult:
    """Dispatch FASTA or FASTQ to the appropriate service."""

    if input_format == "fasta":
        return analyze_fasta_file(
            file_path=file_path,
            reference_database_path=(
                reference_database_path
            ),
            min_similarity=min_similarity,
            allow_n=allow_n,
            top_n=top_n,
            progress_callback=progress_callback,
            reference_metadata_path=(
                reference_metadata_path
            ),
            search_backend=search_backend,
            blast_database_path=blast_database_path,
            search_timeout_seconds=search_timeout_seconds,
            search_database_hash=search_database_hash,
            blast_version=blast_version,
            search_cache=search_cache,
        )

    if input_format == "fastq":
        return analyze_fastq_file(
            file_path=file_path,
            reference_database_path=(
                reference_database_path
            ),
            min_similarity=min_similarity,
            allow_n=allow_n,
            top_n=top_n,
            progress_callback=progress_callback,
            reference_metadata_path=(
                reference_metadata_path
            ),
            min_mean_quality=min_mean_quality,
            min_length=min_length,
            max_length=max_length,
            trim_ends=trim_ends,
            trim_quality_threshold=(
                trim_quality_threshold
            ),
            search_backend=search_backend,
            blast_database_path=blast_database_path,
            search_timeout_seconds=search_timeout_seconds,
            search_database_hash=search_database_hash,
            blast_version=blast_version,
            search_cache=search_cache,
        )

    raise ValueError(
        "Formato de entrada não "
        f"suportado: {input_format}."
    )
