"""Unit tests for adoption anchor window computation."""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from ai_adoption_diff.analysis import AnchorError
from ai_adoption_diff.analysis.anchor import AnalysisWindow, compute_window
from ai_adoption_diff.ingestion.git_reader import CommitRecord


def _commit(timestamp: datetime) -> CommitRecord:
    return CommitRecord(
        sha="abc123",
        author_email_hash="hash",
        timestamp=timestamp,
        file_paths=["file.py"],
        files_changed=1,
        insertions=1,
        deletions=0,
        message="test commit",
    )


def test_compute_window_returns_correct_bounds() -> None:
    commits = [
        _commit(datetime(2024, 3, 3, 12, 0, tzinfo=timezone.utc)),
        _commit(datetime(2024, 6, 1, 9, 0, tzinfo=timezone.utc)),
        _commit(datetime(2024, 8, 30, 18, 0, tzinfo=timezone.utc)),
    ]

    window = compute_window(
        adoption_date="2024-06-01",
        commits=commits,
        window_days=90,
    )

    assert window == AnalysisWindow(
        before_start=date(2024, 3, 3),
        adoption_date=date(2024, 6, 1),
        after_end=date(2024, 8, 30),
    )


def test_invalid_date_format_raises_value_error() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        compute_window(adoption_date="not-a-date", commits=[])


def test_empty_before_window_raises_anchor_error() -> None:
    after_only_commits = [
        _commit(datetime(2024, 6, 2, 12, 0, tzinfo=timezone.utc)),
        _commit(datetime(2024, 8, 15, 12, 0, tzinfo=timezone.utc)),
    ]
    with pytest.raises(AnchorError, match="before window is empty"):
        compute_window(adoption_date="2024-06-01", commits=after_only_commits)

    before_only_commits = [
        _commit(datetime(2024, 3, 15, 12, 0, tzinfo=timezone.utc)),
        _commit(datetime(2024, 5, 31, 12, 0, tzinfo=timezone.utc)),
    ]
    with pytest.raises(AnchorError, match="after window is empty"):
        compute_window(adoption_date="2024-06-01", commits=before_only_commits)


def test_custom_window_days() -> None:
    commits = [
        _commit(datetime(2024, 3, 3, 12, 0, tzinfo=timezone.utc)),
        _commit(datetime(2024, 5, 2, 12, 0, tzinfo=timezone.utc)),
        _commit(datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc)),
    ]

    default_window = compute_window(adoption_date="2024-06-01", commits=commits)
    custom_window = compute_window(
        adoption_date="2024-06-01",
        commits=commits,
        window_days=30,
    )

    assert default_window == AnalysisWindow(
        before_start=date(2024, 3, 3),
        adoption_date=date(2024, 6, 1),
        after_end=date(2024, 8, 30),
    )
    assert custom_window == AnalysisWindow(
        before_start=date(2024, 5, 2),
        adoption_date=date(2024, 6, 1),
        after_end=date(2024, 7, 1),
    )
