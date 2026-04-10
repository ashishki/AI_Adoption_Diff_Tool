"""JSON export for analysis reports."""

from __future__ import annotations

from pathlib import Path

from ai_adoption_diff.report.model import AnalysisReport


def write(report: AnalysisReport, output_dir: Path | str) -> Path:
    """Write a report to ``output_dir/report.json`` and return the file path."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report_path = output_path / "report.json"
    report_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    return report_path
