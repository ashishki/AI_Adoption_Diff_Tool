"""Churn and revert-frequency metrics."""

from __future__ import annotations

from dataclasses import dataclass
import re

from ai_adoption_diff.ingestion import CommitRecord


REVERT_PATTERN = re.compile(r"^(revert|fix|fixup|hotfix)\b", re.IGNORECASE)


@dataclass(frozen=True)
class ChurnRateResult:
    """Computed churn-rate summary."""

    churn_rate: float | None
    sample_size: int


@dataclass(frozen=True)
class RevertFrequencyResult:
    """Computed revert/fix frequency summary."""

    revert_frequency: float | None
    sample_size: int


def compute_churn_rate(commits: list[CommitRecord]) -> ChurnRateResult:
    """Return deletions divided by total changed lines across commits."""
    if not commits:
        return ChurnRateResult(churn_rate=None, sample_size=0)

    total_insertions = sum(commit.insertions for commit in commits)
    total_deletions = sum(commit.deletions for commit in commits)
    total_changed_lines = total_insertions + total_deletions

    if total_changed_lines == 0:
        churn_rate = 0.0
    else:
        churn_rate = round(total_deletions / total_changed_lines, 3)

    return ChurnRateResult(churn_rate=churn_rate, sample_size=len(commits))


def compute_revert_frequency(commits: list[CommitRecord]) -> RevertFrequencyResult:
    """Return the fraction of commits whose message looks like revert/fix work."""
    if not commits:
        return RevertFrequencyResult(revert_frequency=None, sample_size=0)

    matching_commits = sum(
        1 for commit in commits if REVERT_PATTERN.search(commit.message) is not None
    )
    revert_frequency = matching_commits / len(commits)
    return RevertFrequencyResult(
        revert_frequency=revert_frequency,
        sample_size=len(commits),
    )
