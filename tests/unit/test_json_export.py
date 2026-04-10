"""Unit tests for JSON report export."""

from __future__ import annotations

import json

from ai_adoption_diff.report.json_export import write
from ai_adoption_diff.report.model import AnalysisReport


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
            "caveats": ["Metrics show correlation only. Causality cannot be inferred."],
        }
    )


def test_write_creates_valid_json_file(tmp_path) -> None:
    report_path = write(_build_report(), tmp_path)

    assert report_path.exists()
    assert json.loads(report_path.read_text(encoding="utf-8"))["repo_path"] == "/tmp/example-repo"


def test_write_creates_output_dir(tmp_path) -> None:
    output_dir = tmp_path / "nested" / "reports"

    report_path = write(_build_report(), output_dir)

    assert output_dir.is_dir()
    assert report_path == output_dir / "report.json"


def test_write_overwrites_existing(tmp_path) -> None:
    report_path = tmp_path / "report.json"
    report_path.write_text("not-json", encoding="utf-8")

    write(_build_report(), tmp_path)

    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert payload["tool_label"] == "cursor"


def test_json_contains_required_keys(tmp_path) -> None:
    report_path = write(_build_report(), tmp_path)

    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert set(payload) == {
        "repo_path",
        "tool_label",
        "adoption_date",
        "window_days",
        "confidence",
        "metrics",
        "generated_at",
        "caveats",
    }
