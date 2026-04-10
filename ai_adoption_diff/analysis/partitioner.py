"""Partition commit history into before and after analysis windows."""

from __future__ import annotations

from ai_adoption_diff.analysis import PartitionError
from ai_adoption_diff.analysis.anchor import AnalysisWindow
from ai_adoption_diff.ingestion.git_reader import CommitRecord


def partition(
    commits: list[CommitRecord],
    window: AnalysisWindow,
) -> tuple[list[CommitRecord], list[CommitRecord]]:
    """Split commits into non-overlapping before and after windows."""
    before = [
        commit
        for commit in commits
        if window.before_start <= commit.timestamp.date() < window.adoption_date
    ]
    after = [
        commit
        for commit in commits
        if window.adoption_date <= commit.timestamp.date() <= window.after_end
    ]

    if not before:
        raise PartitionError("before window is empty")

    return before, after
