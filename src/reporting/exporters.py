from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from src.reporting.contracts import AnalysisReport


def export_report_json(
    report: AnalysisReport,
    output_path: str | Path,
) -> Path:
    """Export a complete analysis report as JSON."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            asdict(report),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return path


def export_results_csv(
    report: AnalysisReport,
    output_path: str | Path,
) -> Path:
    """Export individual analysis results as CSV."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not report.results:
        path.write_text(
            "",
            encoding="utf-8",
        )
        return path

    fieldnames: list[str] = []

    for result in report.results:
        for key in result:
            if key not in fieldnames:
                fieldnames.append(key)

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for result in report.results:
            writer.writerow(result)

    return path

def export_species_summary_csv(
    report: AnalysisReport,
    output_path: str | Path,
) -> Path:
    """Export observed species frequencies as CSV."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "species",
                "count",
                "proportion",
            ],
        )

        writer.writeheader()

        for item in (
            report.taxonomy.species_frequencies
        ):
            writer.writerow(
                {
                    "species": item.species,
                    "count": item.count,
                    "proportion": item.proportion,
                }
            )

    return path

def export_report_markdown(
    report: AnalysisReport,
    output_path: str | Path,
) -> Path:
    """Export a human-readable analysis report."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lines = [
        "# BioTrace Analysis Report",
        "",
        f"BioTrace: {report.metadata.biotrace_version}",
        f"Input format: {report.metadata.input_format}",
        f"Search backend: {report.metadata.search_backend}",
        f"Generated at: {report.metadata.generated_at}",
        "",
        "## Analysis summary",
        "",
        f"- Total sequences: {report.indicators.total_sequences}",
        f"- Valid sequences: {report.indicators.valid_sequences}",
        f"- Rejected sequences: {report.indicators.rejected_sequences}",
        f"- Identified sequences: {report.indicators.identified_sequences}",
        f"- Identification rate: {report.indicators.identification_rate:.2f}%",
        "",
        "## Taxonomy",
        "",
        (
            "- Observed species: "
            f"{report.taxonomy.observed_species_count}"
        ),
        (
            "- Most frequent species: "
            f"{report.taxonomy.most_frequent_species or 'None'}"
        ),
        "",
        "## Search",
        "",
        f"- Mean identity: {report.search.mean_identity}",
        f"- Mean coverage: {report.search.mean_coverage}",
        f"- Mean e-value: {report.search.mean_evalue}",
        f"- Mean bit score: {report.search.mean_bit_score}",
        "",
        "## Performance",
        "",
        (
            "- Total duration (s): "
            f"{report.performance.total_duration_seconds}"
        ),
        (
            "- Cache hit rate: "
            f"{report.performance.cache_hit_rate:.2f}%"
        ),
    ]

    if report.warnings:
        lines.extend(
            [
                "",
                "## Warnings",
                "",
            ]
        )

        lines.extend(
            f"- {warning}"
            for warning in report.warnings
        )

    path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    return path


def calculate_file_sha256(
    path: str | Path,
) -> str:
    """Calculate SHA-256 for an exported report file."""

    file_path = Path(path)

    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(8192),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def build_export_metadata(
    paths: list[str | Path],
) -> list[dict[str, object]]:
    """Build reproducibility metadata for exported files."""

    exports: list[dict[str, object]] = []

    for path in paths:
        file_path = Path(path)

        exports.append(
            {
                "filename": file_path.name,
                "sha256": calculate_file_sha256(
                    file_path
                ),
                "size_bytes": file_path.stat().st_size,
            }
        )

    return exports
