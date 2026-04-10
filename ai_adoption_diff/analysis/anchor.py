"""Adoption date anchoring utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from ai_adoption_diff.analysis import AnchorError
from ai_adoption_diff.ingestion import CommitRecord


@dataclass(frozen=True)
class AnalysisWindow:
    """Inclusive analysis window around a validated adoption date."""

    before_start: date
    adoption_date: date
    after_end: date


def _parse_adoption_date(adoption_date: str) -> date:
    try:
        return date.fromisoformat(adoption_date)
    except ValueError as exc:
        raise ValueError("adoption_date must use YYYY-MM-DD format") from exc


def compute_window(
    adoption_date: str,
    commits: list[CommitRecord],
    window_days: int = 90,
) -> AnalysisWindow:
    """Return an inclusive before/after window around the adoption date."""
    parsed_adoption_date = _parse_adoption_date(adoption_date)
    before_start = parsed_adoption_date - timedelta(days=window_days)
    after_end = parsed_adoption_date + timedelta(days=window_days)

    has_before_commit = any(
        before_start <= commit.timestamp.date() <= parsed_adoption_date for commit in commits
    )
    if not has_before_commit:
        raise AnchorError("before window is empty")

    has_after_commit = any(
        parsed_adoption_date <= commit.timestamp.date() <= after_end for commit in commits
    )
    if not has_after_commit:
        raise AnchorError("after window is empty")

    return AnalysisWindow(
        before_start=before_start,
        adoption_date=parsed_adoption_date,
        after_end=after_end,
    )
