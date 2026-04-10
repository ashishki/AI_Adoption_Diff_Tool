"""Unit tests for the AnalysisReport model."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from ai_adoption_diff.report.model import AnalysisReport


def _complete_report_dict() -> dict[str, object]:
    return {
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


def test_model_validates_complete_dict() -> None:
    report = AnalysisReport.model_validate(_complete_report_dict())

    assert report.repo_path == "/tmp/example-repo"
    assert report.tool_label == "cursor"
    assert report.metrics.before.mean_lines == 12.5
    assert report.metrics.after.mean_lines is None


def test_model_rejects_incomplete_dict() -> None:
    incomplete = _complete_report_dict()
    incomplete.pop("tool_label")

    with pytest.raises(ValidationError):
        AnalysisReport.model_validate(incomplete)


def test_model_dump_json_valid() -> None:
    report = AnalysisReport.model_validate(_complete_report_dict())

    payload = json.loads(report.model_dump_json())

    assert payload["repo_path"] == "/tmp/example-repo"
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


def test_generated_at_is_utc_iso8601() -> None:
    before = datetime.now(timezone.utc)
    report = AnalysisReport.model_validate(_complete_report_dict())
    after = datetime.now(timezone.utc)

    generated_at = datetime.fromisoformat(report.generated_at)

    assert generated_at.tzinfo == timezone.utc
    assert before <= generated_at <= after
    assert abs((after - generated_at).total_seconds()) < 5
