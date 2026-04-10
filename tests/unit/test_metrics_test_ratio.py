"""Unit tests for test-ratio and boilerplate metrics."""

from __future__ import annotations

from datetime import datetime, timezone

from ai_adoption_diff.ingestion import CommitRecord
from ai_adoption_diff.metrics.test_ratio import (
    BoilerplateSignalResult,
    RatioMetricResult,
    compute_boilerplate_signal,
    compute_test_ratio,
)


def _commit(
    *,
    sha: str,
    file_paths: list[str],
    insertions: int,
    deletions: int,
) -> CommitRecord:
    return CommitRecord(
        sha=sha,
        author_email_hash="hash",
        timestamp=datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
        file_paths=file_paths,
        files_changed=len(file_paths),
        insertions=insertions,
        deletions=deletions,
        message="test commit",
    )


def test_ratio_known_value() -> None:
    commits = [
        _commit(
            sha="c1",
            file_paths=["src/tests/test_widget.py"],
            insertions=30,
            deletions=10,
        ),
        _commit(
            sha="c2",
            file_paths=["src/widget.py"],
            insertions=70,
            deletions=30,
        ),
    ]

    assert compute_test_ratio(commits) == RatioMetricResult(test_ratio=0.4, sample_size=2)


def test_ratio_edge_cases() -> None:
    no_test_file_commits = [
        _commit(sha="c1", file_paths=["src/app.py"], insertions=20, deletions=5),
    ]
    all_test_file_commits = [
        _commit(sha="c2", file_paths=["pkg/tests/test_app.py"], insertions=15, deletions=5),
        _commit(sha="c3", file_paths=["pkg/module_test.py"], insertions=7, deletions=3),
    ]

    assert compute_test_ratio(no_test_file_commits) == RatioMetricResult(
        test_ratio=0.0,
        sample_size=1,
    )
    assert compute_test_ratio(all_test_file_commits) == RatioMetricResult(
        test_ratio=None,
        sample_size=2,
    )


def test_boilerplate_signal_known_value() -> None:
    commits = [
        _commit(sha="c1", file_paths=["pkg/__init__.py"], insertions=1, deletions=0),
        _commit(sha="c2", file_paths=["pkg/module.py"], insertions=10, deletions=2),
        _commit(sha="c3", file_paths=["tests/conftest.py"], insertions=5, deletions=0),
        _commit(sha="c4", file_paths=["docs/README.md"], insertions=0, deletions=0),
    ]

    assert compute_boilerplate_signal(commits) == BoilerplateSignalResult(
        boilerplate_signal=0.75,
        sample_size=4,
    )


def test_empty_list() -> None:
    assert compute_test_ratio([]) == RatioMetricResult(test_ratio=None, sample_size=0)
    assert compute_boilerplate_signal([]) == BoilerplateSignalResult(
        boilerplate_signal=None,
        sample_size=0,
    )
