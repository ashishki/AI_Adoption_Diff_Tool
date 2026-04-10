"""Test-to-code ratio and boilerplate metrics.

The path-based heuristics in this module are intentionally simple so the metrics
stay deterministic and easy to reason about.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_adoption_diff.ingestion import CommitRecord


@dataclass(frozen=True)
class RatioMetricResult:
    """Computed ratio of test-file line changes to non-test-file line changes."""

    test_ratio: float | None
    sample_size: int


@dataclass(frozen=True)
class BoilerplateSignalResult:
    """Computed fraction of commits matching the boilerplate heuristic."""

    boilerplate_signal: float | None
    sample_size: int


def _is_test_file(file_path: str) -> bool:
    return "/test_" in file_path or "/tests/" in file_path or file_path.endswith("_test.py")


def compute_test_ratio(commits: list[CommitRecord]) -> RatioMetricResult:
    """Return test-file changed lines divided by non-test-file changed lines."""
    if not commits:
        return RatioMetricResult(test_ratio=None, sample_size=0)

    test_lines = 0
    non_test_lines = 0

    for commit in commits:
        lines_changed = commit.insertions + commit.deletions
        if any(_is_test_file(file_path) for file_path in commit.file_paths):
            test_lines += lines_changed
        else:
            non_test_lines += lines_changed

    if test_lines == 0:
        ratio = 0.0
    elif non_test_lines == 0:
        ratio = None
    else:
        ratio = test_lines / non_test_lines

    return RatioMetricResult(test_ratio=ratio, sample_size=len(commits))


def compute_boilerplate_signal(commits: list[CommitRecord]) -> BoilerplateSignalResult:
    """Return the fraction of commits that add at least one boilerplate-style file."""
    if not commits:
        return BoilerplateSignalResult(boilerplate_signal=None, sample_size=0)

    boilerplate_commits = 0
    for commit in commits:
        has_boilerplate_path = any(
            file_path.endswith("__init__.py") or file_path.endswith("conftest.py")
            for file_path in commit.file_paths
        )
        has_no_content_change = commit.insertions == 0 and commit.deletions == 0
        if has_boilerplate_path or has_no_content_change:
            boilerplate_commits += 1

    return BoilerplateSignalResult(
        boilerplate_signal=boilerplate_commits / len(commits),
        sample_size=len(commits),
    )
