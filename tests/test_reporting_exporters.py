import csv
import json

from src.reporting.exporters import (
    build_export_metadata,
    calculate_file_sha256,
    export_report_json,
    export_report_markdown,
    export_results_csv,
    export_species_summary_csv,
)
from src.reporting.report_service import (
    build_analysis_report,
)


def _build_test_report():
    results = [
        {
            "Identificada": True,
            "Espécie escolhida": "Species alpha",
            "Identidade do alinhamento (%)": 99.5,
            "Cobertura do alinhamento (%)": 100.0,
            "Cache": "hit",
        },
        {
            "Identificada": True,
            "Espécie escolhida": "Species beta",
            "Identidade do alinhamento (%)": 97.0,
            "Cobertura do alinhamento (%)": 95.0,
            "Cache": "miss",
        },
    ]

    return build_analysis_report(
        input_format="fasta",
        search_backend="pairwise",
        results=results,
        total_sequences=2,
        valid_sequences=2,
        identified_sequences=2,
        total_duration_seconds=1.0,
    )


def test_export_report_json(tmp_path):
    report = _build_test_report()

    output = export_report_json(
        report,
        tmp_path / "analysis_report.json",
    )

    assert output.exists()

    data = json.loads(
        output.read_text(
            encoding="utf-8",
        )
    )

    assert data["metadata"]["input_format"] == "fasta"
    assert data["indicators"]["total_sequences"] == 2
    assert data["taxonomy"]["observed_species_count"] == 2
    assert len(data["results"]) == 2


def test_export_results_csv(tmp_path):
    report = _build_test_report()

    output = export_results_csv(
        report,
        tmp_path / "analysis_results.csv",
    )

    assert output.exists()

    with output.open(
        encoding="utf-8",
        newline="",
    ) as file:
        rows = list(
            csv.DictReader(file)
        )

    assert len(rows) == 2

    assert (
        rows[0]["Espécie escolhida"]
        == "Species alpha"
    )


def test_export_species_summary_csv(tmp_path):
    report = _build_test_report()

    output = export_species_summary_csv(
        report,
        tmp_path / "species_summary.csv",
    )

    assert output.exists()

    with output.open(
        encoding="utf-8",
        newline="",
    ) as file:
        rows = list(
            csv.DictReader(file)
        )

    assert len(rows) == 2

    species = {
        row["species"]
        for row in rows
    }

    assert species == {
        "Species alpha",
        "Species beta",
    }


def test_export_report_markdown(tmp_path):
    report = _build_test_report()

    output = export_report_markdown(
        report,
        tmp_path / "analysis_report.md",
    )

    content = output.read_text(
        encoding="utf-8",
    )

    assert "# BioTrace Analysis Report" in content
    assert "## Analysis summary" in content
    assert "## Taxonomy" in content
    assert "## Search" in content
    assert "## Performance" in content

def test_export_empty_results_csv(tmp_path):
    report = build_analysis_report(
        input_format="fasta",
        search_backend="pairwise",
        results=[],
        total_sequences=0,
        valid_sequences=0,
        identified_sequences=0,
        total_duration_seconds=0.0,
    )

    output = export_results_csv(
        report,
        tmp_path / "empty_results.csv",
    )

    assert output.exists()

    assert (
        output.read_text(
            encoding="utf-8",
        )
        == ""
    )


def test_calculate_file_sha256(tmp_path):
    path = tmp_path / "example.txt"

    path.write_text(
        "BioTrace",
        encoding="utf-8",
    )

    digest = calculate_file_sha256(
        path
    )

    assert len(digest) == 64

    assert digest == calculate_file_sha256(
        path
    )


def test_build_export_metadata(tmp_path):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"

    first.write_text(
        "first",
        encoding="utf-8",
    )

    second.write_text(
        "second",
        encoding="utf-8",
    )

    metadata = build_export_metadata(
        [
            first,
            second,
        ]
    )

    assert len(metadata) == 2

    assert metadata[0]["filename"] == "first.txt"
    assert metadata[1]["filename"] == "second.txt"

    assert len(
        str(metadata[0]["sha256"])
    ) == 64

    assert metadata[0]["size_bytes"] > 0
    assert metadata[1]["size_bytes"] > 0
