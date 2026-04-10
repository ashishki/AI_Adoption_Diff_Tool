"""Unit tests for heuristic adoption inference."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from ai_adoption_diff.analysis.heuristic import HeuristicResult, infer_adoption
from ai_adoption_diff.ingestion.git_reader import CommitRecord


def _commit(
    timestamp: datetime,
    *,
    file_paths: list[str] | None = None,
    sha: str = "abc123",
) -> CommitRecord:
    paths = ["file.py"] if file_paths is None else file_paths
    return CommitRecord(
        sha=sha,
        author_email_hash="hash",
        timestamp=timestamp,
        file_paths=paths,
        files_changed=len(paths),
        insertions=1,
        deletions=0,
        message="test commit",
    )


def test_infer_returns_heuristic_result() -> None:
    commits = [
        _commit(
            datetime(2024, 4, 10, 12, 0, tzinfo=timezone.utc),
            file_paths=[".cursorrules"],
        )
    ]

    result = infer_adoption(commits)

    assert isinstance(result, HeuristicResult)
    assert 0.0 <= result.confidence_score <= 1.0


def test_ai_config_file_signal_detected() -> None:
    detected_at = datetime(2024, 4, 10, 12, 0, tzinfo=timezone.utc)
    commits = [
        _commit(datetime(2024, 4, 1, 12, 0, tzinfo=timezone.utc)),
        _commit(detected_at, file_paths=[".cursorrules"]),
    ]

    result = infer_adoption(commits)

    assert any(
        signal.signal_name == "ai_config_file" and signal.detected_date == detected_at.date()
        for signal in result.signals_detected
    )


def test_commit_frequency_spike_detected() -> None:
    commits = [
        _commit(
            datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc) + timedelta(days=offset),
            sha=f"baseline-{offset}",
        )
        for offset in (0, 40, 80)
    ]
    commits.extend(
        _commit(
            datetime(2024, 5, 1, 12, 0, tzinfo=timezone.utc) + timedelta(days=offset),
            sha=f"spike-{offset}",
        )
        for offset in range(10)
    )

    result = infer_adoption(commits)

    assert any(
        signal.signal_name == "commit_frequency_spike" and signal.detected_date == date(2024, 5, 10)
        for signal in result.signals_detected
    )


def test_no_signals_returns_none_date() -> None:
    commits = [
        _commit(datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)),
        _commit(datetime(2024, 2, 1, 12, 0, tzinfo=timezone.utc)),
        _commit(datetime(2024, 3, 1, 12, 0, tzinfo=timezone.utc)),
    ]

    result = infer_adoption(commits)

    assert result == HeuristicResult(
        suggested_date=None,
        confidence_score=0.0,
        signals_detected=[],
    )


def test_suggested_date_is_median_of_signals() -> None:
    commits = [
        _commit(
            datetime(2024, 4, 10, 12, 0, tzinfo=timezone.utc),
            file_paths=[".cursorrules"],
            sha="first-signal",
        ),
        _commit(
            datetime(2024, 4, 15, 12, 0, tzinfo=timezone.utc),
            file_paths=["AGENTS.md"],
            sha="middle-signal",
        ),
    ]
    commits.extend(
        _commit(
            datetime(2024, 4, 15, 13, 0, tzinfo=timezone.utc) + timedelta(days=offset),
            sha=f"spike-{offset}",
        )
        for offset in range(10)
    )

    result = infer_adoption(commits)

    assert result.suggested_date == date(2024, 4, 15)
