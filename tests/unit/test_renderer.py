"""Unit tests for Markdown and HTML report rendering."""

from __future__ import annotations

from ai_adoption_diff import __version__
from ai_adoption_diff.report.model import AnalysisReport
from ai_adoption_diff.report.renderer import render_html, render_markdown


def _build_report() -> AnalysisReport:
    return AnalysisReport.model_validate(
        {
            "repo_path": "/tmp/example-repo",
            "tool_label": "cursor",
            "adoption_date": "2024-06-01",
            "window_days": 90,
            "confidence": {
                "score": 0.82,
                "level": "high",
                "anchor_source": "manual",
                "rationale": "Manual adoption date supplied by the operator.",
            },
            "metrics": {
                "before": {
                    "mean_lines": 12.5,
                    "median_lines": 10.0,
                    "p90_lines": 25.0,
                    "mean_files": 2.0,
                    "median_files": 2.0,
                    "p90_files": 4.0,
                    "churn_rate": 0.2,
                    "rework_frequency": None,
                    "revert_frequency": 0.1,
                    "test_ratio": 0.4,
                    "boilerplate_signal": 0.05,
                    "hot_file_count": 3,
                    "dir_concentration": 0.6,
                    "sample_size": 20,
                },
                "after": {
                    "mean_lines": None,
                    "median_lines": 9.0,
                    "p90_lines": 18.0,
                    "mean_files": 1.5,
                    "median_files": 1.0,
                    "p90_files": 3.0,
                    "churn_rate": 0.15,
                    "rework_frequency": 0.08,
                    "revert_frequency": None,
                    "test_ratio": 0.5,
                    "boilerplate_signal": 0.04,
                    "hot_file_count": None,
                    "dir_concentration": 0.55,
                    "sample_size": 22,
                },
            },
            "generated_at": "2026-04-10T08:30:00+00:00",
            "caveats": [
                "Metrics show correlation only. Causality cannot be inferred.",
                "Before window has fewer than 10 commits. Statistical reliability is limited.",
            ],
        }
    )


def test_render_markdown_creates_file_with_sections(tmp_path) -> None:
    report_path = render_markdown(_build_report(), tmp_path)
    content = report_path.read_text(encoding="utf-8")

    assert report_path == tmp_path / "report.md"
    assert "# Analysis Report" in content
    assert "Repo Path: `/tmp/example-repo`" in content
    assert "Tool Label: `cursor`" in content
    assert "Adoption Date: `2024-06-01`" in content
    assert "## Confidence" in content
    assert "Score: 0.82" in content
    assert "Level: high" in content
    assert "Metrics show correlation only. Causality cannot be inferred." in content
    assert "| Metric | Before | After | Delta |" in content


def test_markdown_table_has_all_metrics(tmp_path) -> None:
    content = render_markdown(_build_report(), tmp_path).read_text(encoding="utf-8")

    metric_labels = [
        "Commit size distribution",
        "Files touched per commit",
        "Churn rate",
        "Rework frequency",
        "Revert/fix frequency",
        "Test-to-code ratio",
        "Boilerplate signal",
        "Hot-file instability",
        "Directory concentration",
    ]

    for label in metric_labels:
        assert f"| {label} |" in content

    assert len([line for line in content.splitlines() if line.startswith("| ")]) == 11
    assert "| Commit size distribution | 12.5 | N/A | N/A |" in content
    assert "| Rework frequency | N/A | 0.08 | N/A |" in content
    assert "| Hot-file instability | 3 | N/A | N/A |" in content


def test_render_html_creates_file_with_table(tmp_path) -> None:
    report_path = render_html(_build_report(), tmp_path)
    content = report_path.read_text(encoding="utf-8")

    assert report_path == tmp_path / "report.html"
    assert "<!DOCTYPE html>" in content
    assert "<table>" in content
    assert "<th>Metric</th>" in content
    assert "<td>Commit size distribution</td>" in content
    assert "<td>12.5</td>" in content
    assert "<td>N/A</td>" in content


def test_markdown_footer_contains_caveat(tmp_path) -> None:
    content = render_markdown(_build_report(), tmp_path).read_text(encoding="utf-8")

    assert f"Tool Version: {__version__}" in content
    assert "Generated At: 2026-04-10T08:30:00+00:00" in content
    assert "Caveat: Metrics show correlation only. Causality cannot be inferred." in content
