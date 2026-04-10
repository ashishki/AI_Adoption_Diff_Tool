"""Unit tests for confidence scoring."""

from __future__ import annotations

from datetime import datetime, timezone

from ai_adoption_diff.analysis.confidence import ConfidenceResult, compute
from ai_adoption_diff.ingestion import CommitRecord


def _commit(index: int) -> CommitRecord:
    return CommitRecord(
        sha=f"sha-{index}",
        author_email_hash="hash",
        timestamp=datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
        file_paths=["file.py"],
        files_changed=1,
        insertions=1,
        deletions=0,
        message="test commit",
    )


def _commits(count: int) -> list[CommitRecord]:
    return [_commit(index) for index in range(count)]


def test_compute_returns_confidence_result() -> None:
    result = compute(before_commits=_commits(10), after_commits=_commits(10))

    assert isinstance(result, ConfidenceResult)
    assert result.score == 1.0
    assert result.level in {"high", "medium", "low"}
    assert result.caveats == []


def test_level_thresholds() -> None:
    assert compute(before_commits=_commits(10), after_commits=_commits(10)).level == "high"
    assert (
        compute(
            before_commits=_commits(9),
            after_commits=_commits(10),
            anchor_source="heuristic",
        ).level
        == "medium"
    )
    assert (
        compute(
            before_commits=_commits(9),
            after_commits=_commits(9),
            anchor_source="heuristic",
        ).level
        == "low"
    )


def test_heuristic_anchor_caveat_present() -> None:
    result = compute(
        before_commits=_commits(10),
        after_commits=_commits(10),
        anchor_source="heuristic",
    )

    assert "Adoption date was inferred, not provided manually." in result.caveats


def test_small_before_window_caveat() -> None:
    result = compute(before_commits=_commits(9), after_commits=_commits(10))

    assert "Before window has fewer than 10 commits." in result.caveats


def test_small_after_window_caveat() -> None:
    result = compute(before_commits=_commits(10), after_commits=_commits(9))

    assert "After window has fewer than 10 commits." in result.caveats
