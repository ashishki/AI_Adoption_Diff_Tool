"""Hot-file instability and directory concentration metrics."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from ai_adoption_diff.ingestion import CommitRecord


@dataclass(frozen=True)
class HotFileResult:
    """Count of files that recur across more than a threshold of commits."""

    hot_file_count: int | None
    sample_size: int


@dataclass(frozen=True)
class DirConcentrationResult:
    """Fraction of changed lines attributable to the top three directories."""

    dir_concentration: float | None
    sample_size: int


def _directory_for_path(file_path: str) -> str:
    first_segment, separator, _ = file_path.partition("/")
    if separator:
        return first_segment
    return "."


def compute_hot_file_count(
    commits: list[CommitRecord],
    threshold: float = 0.1,
) -> HotFileResult | None:
    """Count files appearing in more than threshold * commit_count distinct commits."""
    if not commits:
        return None

    file_commit_counts: Counter[str] = Counter()
    for commit in commits:
        file_commit_counts.update(set(commit.file_paths))

    minimum_commit_count = threshold * len(commits)
    hot_file_count = sum(
        1
        for distinct_commit_count in file_commit_counts.values()
        if distinct_commit_count > minimum_commit_count
    )

    return HotFileResult(hot_file_count=hot_file_count, sample_size=len(commits))


def compute_dir_concentration(commits: list[CommitRecord]) -> DirConcentrationResult | None:
    """Return the share of changed lines concentrated in the top three directories."""
    if not commits:
        return None

    total_lines_changed = sum(commit.insertions + commit.deletions for commit in commits)
    if total_lines_changed == 0:
        return DirConcentrationResult(dir_concentration=0.0, sample_size=len(commits))

    directory_totals: Counter[str] = Counter()
    for commit in commits:
        lines_changed = commit.insertions + commit.deletions
        if lines_changed == 0 or not commit.file_paths:
            continue

        # Commit records only expose commit-level line totals, not per-file numstat
        # data, so distribute a commit's changed lines evenly across the distinct
        # directories touched by that commit.
        directories = {_directory_for_path(file_path) for file_path in commit.file_paths}
        lines_per_directory = lines_changed / len(directories)
        for directory in directories:
            directory_totals[directory] += lines_per_directory

    top_three_total = sum(changed_lines for _, changed_lines in directory_totals.most_common(3))
    return DirConcentrationResult(
        dir_concentration=top_three_total / total_lines_changed,
        sample_size=len(commits),
    )
