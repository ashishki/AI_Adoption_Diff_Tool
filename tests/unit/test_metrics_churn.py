"""Unit tests for churn and revert-frequency metrics."""

from __future__ import annotations

from datetime import datetime, timezone

from ai_adoption_diff.ingestion import CommitRecord
from ai_adoption_diff.metrics.churn import (
    ChurnRateResult,
    RevertFrequencyResult,
    compute_churn_rate,
    compute_revert_frequency,
)


def _commit(
    *,
    sha: str,
    insertions: int,
    deletions: int,
    message: str,
) -> CommitRecord:
    return CommitRecord(
        sha=sha,
        author_email_hash="hash",
        timestamp=datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
        file_paths=["file.py"],
        files_changed=1,
        insertions=insertions,
        deletions=deletions,
        message=message,
    )


def test_churn_rate_known_value() -> None:
    result = compute_churn_rate([_commit(sha="c1", insertions=10, deletions=5, message="feature")])

    assert result == ChurnRateResult(churn_rate=0.333, sample_size=1)


def test_churn_rate_no_lines_changed() -> None:
    result = compute_churn_rate(
        [
            _commit(sha="c1", insertions=0, deletions=0, message="docs"),
            _commit(sha="c2", insertions=0, deletions=0, message="chore"),
        ]
    )

    assert result == ChurnRateResult(churn_rate=0.0, sample_size=2)


def test_revert_frequency_known_value() -> None:
    commits = [
        _commit(sha="c1", insertions=1, deletions=1, message="feature"),
        _commit(sha="c2", insertions=1, deletions=1, message="refactor"),
        _commit(sha="c3", insertions=1, deletions=1, message="docs"),
        _commit(sha="c4", insertions=1, deletions=1, message="cleanup"),
        _commit(sha="c5", insertions=1, deletions=1, message="feature 2"),
        _commit(sha="c6", insertions=1, deletions=1, message="Fix typo"),
        _commit(sha="c7", insertions=1, deletions=1, message="test"),
        _commit(sha="c8", insertions=1, deletions=1, message="style"),
        _commit(sha="c9", insertions=1, deletions=1, message="REVERT commit"),
        _commit(sha="c10", insertions=1, deletions=1, message="chore"),
    ]

    result = compute_revert_frequency(commits)

    assert result == RevertFrequencyResult(revert_frequency=0.2, sample_size=10)


def test_empty_list_returns_none() -> None:
    assert compute_churn_rate([]) == ChurnRateResult(churn_rate=None, sample_size=0)
    assert compute_revert_frequency([]) == RevertFrequencyResult(
        revert_frequency=None,
        sample_size=0,
    )


def test_revert_frequency_regex_cases() -> None:
    commits = [
        _commit(sha="c1", insertions=1, deletions=0, message="Fix: typo"),
        _commit(sha="c2", insertions=1, deletions=0, message="REVERT commit"),
        _commit(sha="c3", insertions=1, deletions=0, message="fixed bug"),
    ]

    result = compute_revert_frequency(commits)

    assert result == RevertFrequencyResult(
        revert_frequency=2 / 3,
        sample_size=3,
    )
