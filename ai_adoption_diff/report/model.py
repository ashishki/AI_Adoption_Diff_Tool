"""Pydantic report model for structured analysis output."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# PS-3 exception: the implementation contract explicitly permits datetime.now()
# in this module for the report generation timestamp.
def _utc_now_iso8601() -> str:
    return datetime.now(timezone.utc).isoformat()


class ConfidenceSummary(BaseModel):
    """Confidence payload for the report."""

    model_config = ConfigDict(extra="allow")

    score: float | None = None
    level: str | None = None
    anchor_source: str | None = None
    rationale: str | None = None


class MetricWindowResults(BaseModel):
    """Metric values for a single analysis window."""

    model_config = ConfigDict(extra="allow")

    mean_lines: float | None = None
    median_lines: float | None = None
    p90_lines: float | None = None
    mean_files: float | None = None
    median_files: float | None = None
    p90_files: float | None = None
    churn_rate: float | None = None
    rework_frequency: float | None = None
    revert_frequency: float | None = None
    test_ratio: float | None = None
    boilerplate_signal: float | None = None
    hot_file_count: int | None = None
    dir_concentration: float | None = None
    sample_size: int | None = None


class MetricsSummary(BaseModel):
    """Before/after metric buckets for the report."""

    model_config = ConfigDict(extra="allow")

    before: MetricWindowResults
    after: MetricWindowResults


class AnalysisReport(BaseModel):
    """Validated report envelope for exported analysis results."""

    repo_path: str
    tool_label: Literal["cursor", "copilot", "claude_code", "unknown"]
    adoption_date: str
    window_days: int
    confidence: ConfidenceSummary
    metrics: MetricsSummary
    generated_at: str = Field(default_factory=_utc_now_iso8601)
    caveats: list[str]
