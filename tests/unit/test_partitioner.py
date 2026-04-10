"""Unit tests for analysis window partitioning."""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from ai_adoption_diff.analysis import PartitionError
from ai_adoption_diff.analysis.anchor import AnalysisWindow
from ai_adoption_diff.analysis.partitioner import partition
from ai_adoption_diff.ingestion.git_reader import CommitRecord


def _commit(timestamp: datetime, *, sha: str) -> CommitRecord:
    return CommitRecord(
        sha=sha,
        author_email_hash="hash",
        timestamp=timestamp,
        file_paths=["file.py"],
        files_changed=1,
        insertions=1,
        deletions=0,
        message="test commit",
    )


def test_partition_splits_correctly() -> None:
    commits = [
        _commit(datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc), sha="c1"),
        _commit(datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc), sha="c2"),
        _commit(datetime(2024, 2, 1, 12, 0, tzinfo=timezone.utc), sha="c3"),
        _commit(datetime(2024, 2, 15, 12, 0, tzinfo=timezone.utc), sha="c4"),
        _commit(datetime(2024, 2, 29, 12, 0, tzinfo=timezone.utc), sha="c5"),
        _commit(datetime(2024, 3, 1, 12, 0, tzinfo=timezone.utc), sha="c6"),
        _commit(datetime(2024, 3, 15, 12, 0, tzinfo=timezone.utc), sha="c7"),
        _commit(datetime(2024, 4, 1, 12, 0, tzinfo=timezone.utc), sha="c8"),
        _commit(datetime(2024, 5, 1, 12, 0, tzinfo=timezone.utc), sha="c9"),
        _commit(datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc), sha="c10"),
    ]
    window = AnalysisWindow(
        before_start=date(2024, 1, 1),
        adoption_date=date(2024, 3, 1),
        after_end=date(2024, 6, 1),
    )

    before, after = partition(commits, window)

    assert before == commits[:5]
    assert after == commits[5:]
    assert all(commit.timestamp.date() < window.adoption_date for commit in before)
    assert all(commit.timestamp.date() >= window.adoption_date for commit in after)


def test_adoption_date_commit_goes_to_after() -> None:
    commits = [
        _commit(datetime(2024, 2, 29, 12, 0, tzinfo=timezone.utc), sha="before"),
        _commit(datetime(2024, 3, 1, 8, 30, tzinfo=timezone.utc), sha="on-date"),
    ]
    window = AnalysisWindow(
        before_start=date(2024, 2, 1),
        adoption_date=date(2024, 3, 1),
        after_end=date(2024, 4, 1),
    )

    before, after = partition(commits, window)

    assert [commit.sha for commit in before] == ["before"]
    assert [commit.sha for commit in after] == ["on-date"]


def test_commits_outside_window_excluded() -> None:
    commits = [
        _commit(datetime(2024, 1, 31, 12, 0, tzinfo=timezone.utc), sha="too-early"),
        _commit(datetime(2024, 2, 15, 12, 0, tzinfo=timezone.utc), sha="before"),
        _commit(datetime(2024, 3, 1, 12, 0, tzinfo=timezone.utc), sha="after"),
        _commit(datetime(2024, 4, 2, 12, 0, tzinfo=timezone.utc), sha="too-late"),
    ]
    window = AnalysisWindow(
        before_start=date(2024, 2, 1),
        adoption_date=date(2024, 3, 1),
        after_end=date(2024, 4, 1),
    )

    before, after = partition(commits, window)

    assert [commit.sha for commit in before] == ["before"]
    assert [commit.sha for commit in after] == ["after"]


def test_partition_does_not_mutate_input() -> None:
    commits = [
        _commit(datetime(2024, 2, 15, 12, 0, tzinfo=timezone.utc), sha="before"),
        _commit(datetime(2024, 3, 15, 12, 0, tzinfo=timezone.utc), sha="after"),
    ]
    window = AnalysisWindow(
        before_start=date(2024, 2, 1),
        adoption_date=date(2024, 3, 1),
        after_end=date(2024, 4, 1),
    )
    original_commits = commits.copy()

    partition(commits, window)

    assert commits == original_commits


def test_empty_before_raises_partition_error() -> None:
    commits = [
        _commit(datetime(2024, 3, 1, 12, 0, tzinfo=timezone.utc), sha="on-date"),
        _commit(datetime(2024, 3, 15, 12, 0, tzinfo=timezone.utc), sha="after"),
    ]
    window = AnalysisWindow(
        before_start=date(2024, 2, 1),
        adoption_date=date(2024, 3, 1),
        after_end=date(2024, 4, 1),
    )

    with pytest.raises(PartitionError, match="before window is empty"):
        partition(commits, window)


def test_empty_after_raises_partition_error() -> None:
    commits = [
        _commit(datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc), sha="before"),
    ]
    window = AnalysisWindow(
        before_start=date(2024, 1, 1),
        adoption_date=date(2024, 2, 1),
        after_end=date(2024, 3, 1),
    )

    with pytest.raises(PartitionError, match="after window is empty"):
        partition(commits, window)
