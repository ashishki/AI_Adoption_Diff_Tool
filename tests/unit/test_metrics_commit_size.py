"""Unit tests for commit size metrics."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from ai_adoption_diff.ingestion import CommitRecord
from ai_adoption_diff.metrics.commit_size import CommitSizeResult, compute


def _commit(
    *,
    sha: str,
    insertions: int,
    deletions: int,
    files_changed: int,
) -> CommitRecord:
    return CommitRecord(
        sha=sha,
        author_email_hash="hash",
        timestamp=datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
        file_paths=[f"file_{index}.py" for index in range(files_changed)],
        files_changed=files_changed,
        insertions=insertions,
        deletions=deletions,
        message="test commit",
    )


def test_compute_known_fixture() -> None:
    commits = [
        _commit(sha="c1", insertions=10, deletions=5, files_changed=2),
        _commit(sha="c2", insertions=3, deletions=1, files_changed=1),
        _commit(sha="c3", insertions=8, deletions=4, files_changed=3),
        _commit(sha="c4", insertions=0, deletions=2, files_changed=1),
    ]

    result = compute(commits)

    assert result.sample_size == 4
    assert result.mean_lines == 8.25
    assert result.median_lines == 8.0
    assert result.p90_lines == pytest.approx(14.1)
    assert result.mean_files == 1.75
    assert result.median_files == 1.5
    assert result.p90_files == pytest.approx(2.7)
    assert result == CommitSizeResult(
        mean_lines=8.25,
        median_lines=8.0,
        p90_lines=pytest.approx(14.1),
        mean_files=1.75,
        median_files=1.5,
        p90_files=pytest.approx(2.7),
        sample_size=4,
    )


def test_compute_empty_list() -> None:
    assert compute([]) == CommitSizeResult(
        mean_lines=None,
        median_lines=None,
        p90_lines=None,
        mean_files=None,
        median_files=None,
        p90_files=None,
        sample_size=0,
    )


def test_deterministic() -> None:
    commits = [
        _commit(sha="c1", insertions=5, deletions=2, files_changed=1),
        _commit(sha="c2", insertions=7, deletions=3, files_changed=4),
        _commit(sha="c3", insertions=1, deletions=0, files_changed=2),
    ]

    assert compute(commits) == compute(commits)


def test_p90_known_value() -> None:
    commits = [
        _commit(sha=f"c{index}", insertions=index, deletions=0, files_changed=1)
        for index in range(1, 11)
    ]

    result = compute(commits)

    assert result.p90_lines == 9.1
