"""Unit tests for hot-file and directory concentration metrics."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from ai_adoption_diff.ingestion import CommitRecord
from ai_adoption_diff.metrics.hot_files import (
    DirConcentrationResult,
    HotFileResult,
    compute_dir_concentration,
    compute_hot_file_count,
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


def test_hot_file_count_known_value() -> None:
    commits = [
        _commit(
            sha="c1",
            file_paths=["src/core.py", "src/shared.py", "src/unique_1.py"],
            insertions=10,
            deletions=2,
        ),
        _commit(
            sha="c2",
            file_paths=["src/core.py", "docs/readme.md"],
            insertions=8,
            deletions=1,
        ),
        _commit(
            sha="c3",
            file_paths=["src/core.py", "tests/test_core.py"],
            insertions=6,
            deletions=3,
        ),
        _commit(
            sha="c4",
            file_paths=["src/shared.py", "src/helpers.py"],
            insertions=4,
            deletions=1,
        ),
        _commit(
            sha="c5",
            file_paths=["src/unique_5.py"],
            insertions=4,
            deletions=1,
        ),
        _commit(
            sha="c6",
            file_paths=["src/unique_6.py"],
            insertions=4,
            deletions=1,
        ),
        _commit(
            sha="c7",
            file_paths=["src/unique_7.py"],
            insertions=4,
            deletions=1,
        ),
        _commit(
            sha="c8",
            file_paths=["src/unique_8.py"],
            insertions=4,
            deletions=1,
        ),
        _commit(
            sha="c9",
            file_paths=["src/unique_9.py"],
            insertions=4,
            deletions=1,
        ),
        _commit(
            sha="c10",
            file_paths=["src/unique_10.py"],
            insertions=4,
            deletions=1,
        ),
    ]

    result = compute_hot_file_count(commits)

    assert result == HotFileResult(hot_file_count=2, sample_size=10)


def test_threshold_boundary() -> None:
    commits = [
        _commit(sha="c1", file_paths=["src/hot.py", "src/boundary.py"], insertions=1, deletions=0),
        _commit(sha="c2", file_paths=["src/hot.py"], insertions=1, deletions=0),
        _commit(sha="c3", file_paths=["src/unique_3.py"], insertions=1, deletions=0),
        _commit(sha="c4", file_paths=["src/unique_4.py"], insertions=1, deletions=0),
        _commit(sha="c5", file_paths=["src/unique_5.py"], insertions=1, deletions=0),
        _commit(sha="c6", file_paths=["src/unique_6.py"], insertions=1, deletions=0),
        _commit(sha="c7", file_paths=["src/unique_7.py"], insertions=1, deletions=0),
        _commit(sha="c8", file_paths=["src/unique_8.py"], insertions=1, deletions=0),
        _commit(sha="c9", file_paths=["src/unique_9.py"], insertions=1, deletions=0),
        _commit(sha="c10", file_paths=["src/unique_10.py"], insertions=1, deletions=0),
    ]

    result = compute_hot_file_count(commits)

    assert result == HotFileResult(hot_file_count=1, sample_size=10)


def test_dir_concentration_single_dir() -> None:
    commits = [
        _commit(sha="c1", file_paths=["src/app.py"], insertions=10, deletions=5),
        _commit(sha="c2", file_paths=["src/utils.py", "src/helpers.py"], insertions=7, deletions=3),
        _commit(sha="c3", file_paths=["src/models.py"], insertions=4, deletions=1),
    ]

    result = compute_dir_concentration(commits)

    assert result == DirConcentrationResult(
        dir_concentration=pytest.approx(1.0),
        sample_size=3,
    )


def test_empty_list() -> None:
    assert compute_hot_file_count([]) is None
    assert compute_dir_concentration([]) is None
