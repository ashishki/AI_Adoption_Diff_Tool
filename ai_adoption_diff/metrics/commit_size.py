"""Commit size and files-touched metrics."""

from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import mean, median

from ai_adoption_diff.ingestion import CommitRecord


@dataclass(frozen=True)
class CommitSizeResult:
    """Aggregate statistics for commit size and files touched."""

    mean_lines: float | None
    median_lines: float | None
    p90_lines: float | None
    mean_files: float | None
    median_files: float | None
    p90_files: float | None
    sample_size: int


def _compute_p90(values: list[int]) -> float | None:
    if not values:
        return None

    ordered_values = sorted(values)
    percentile_index = 0.9 * (len(ordered_values) - 1)
    lower_index = math.floor(percentile_index)
    upper_index = math.ceil(percentile_index)

    if lower_index == upper_index:
        return float(ordered_values[lower_index])

    lower_value = ordered_values[lower_index]
    upper_value = ordered_values[upper_index]
    interpolation = percentile_index - lower_index
    return float(lower_value + interpolation * (upper_value - lower_value))


def compute(commits: list[CommitRecord]) -> CommitSizeResult:
    """Compute commit size and files-touched summary statistics."""
    if not commits:
        return CommitSizeResult(
            mean_lines=None,
            median_lines=None,
            p90_lines=None,
            mean_files=None,
            median_files=None,
            p90_files=None,
            sample_size=0,
        )

    total_lines = [commit.insertions + commit.deletions for commit in commits]
    files_touched = [commit.files_changed for commit in commits]

    return CommitSizeResult(
        mean_lines=float(mean(total_lines)),
        median_lines=float(median(total_lines)),
        p90_lines=_compute_p90(total_lines),
        mean_files=float(mean(files_touched)),
        median_files=float(median(files_touched)),
        p90_files=_compute_p90(files_touched),
        sample_size=len(commits),
    )
