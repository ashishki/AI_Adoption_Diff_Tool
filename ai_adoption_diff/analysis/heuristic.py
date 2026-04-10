"""Heuristic adoption date inference from commit history."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date, timedelta
from statistics import mean, median

from ai_adoption_diff.ingestion import CommitRecord


AI_CONFIG_FILE_PATHS = {
    ".cursorrules",
    ".github/copilot-instructions.md",
    "AGENTS.md",
}
AI_CONFIG_DIRECTORY_PREFIXES = (".claude/",)


@dataclass(frozen=True)
class Signal:
    """A heuristic signal indicating possible AI adoption."""

    signal_name: str
    detected_date: date
    strength: float


@dataclass(frozen=True)
class HeuristicResult:
    """Suggested adoption date with supporting heuristic evidence."""

    suggested_date: date | None
    confidence_score: float
    signals_detected: list[Signal]


def _is_ai_config_path(file_path: str) -> bool:
    return file_path in AI_CONFIG_FILE_PATHS or file_path.startswith(AI_CONFIG_DIRECTORY_PREFIXES)


def _detect_ai_config_signals(commits: list[CommitRecord]) -> list[Signal]:
    signals: list[Signal] = []

    for commit in commits:
        if any(_is_ai_config_path(file_path) for file_path in commit.file_paths):
            signals.append(
                Signal(
                    signal_name="ai_config_file",
                    detected_date=commit.timestamp.date(),
                    strength=0.7,
                )
            )

    return signals


def _rolling_window_counts(
    commits: list[CommitRecord], window_days: int = 30
) -> list[tuple[date, int]]:
    if not commits:
        return []

    commit_dates = sorted(commit.timestamp.date() for commit in commits)
    counts_by_day = Counter(commit_dates)
    min_day = commit_dates[0]
    max_day = commit_dates[-1]

    window_dates: list[date] = []
    current_day = min_day
    while current_day <= max_day:
        window_dates.append(current_day)
        current_day += timedelta(days=1)

    counts: list[tuple[date, int]] = []
    window_start_offset = window_days - 1
    for window_end in window_dates:
        window_start = window_end - timedelta(days=window_start_offset)
        count = sum(
            daily_count
            for day, daily_count in counts_by_day.items()
            if window_start <= day <= window_end
        )
        counts.append((window_end, count))

    return counts


def _detect_commit_frequency_spike(commits: list[CommitRecord]) -> list[Signal]:
    window_counts = _rolling_window_counts(commits)
    if not window_counts:
        return []

    average_count = mean(count for _, count in window_counts)
    if average_count == 0:
        return []

    strongest_window_end, strongest_count = max(window_counts, key=lambda item: item[1])
    if strongest_count <= average_count * 2:
        return []

    strength = min(1.0, strongest_count / average_count / 3)
    return [
        Signal(
            signal_name="commit_frequency_spike",
            detected_date=strongest_window_end,
            strength=strength,
        )
    ]


def _suggested_date_from_signals(signals: list[Signal]) -> date | None:
    if not signals:
        return None

    median_ordinal = int(median(signal.detected_date.toordinal() for signal in signals))
    return date.fromordinal(median_ordinal)


def _confidence_score(signals: list[Signal]) -> float:
    if not signals:
        return 0.0

    base_confidence = mean(signal.strength for signal in signals) * 0.1
    return max(0.0, min(1.0, len(signals) * 0.3 + base_confidence))


def infer_adoption(commits: list[CommitRecord]) -> HeuristicResult:
    """Infer a likely adoption date from commit-history signals."""
    signals = [
        *_detect_ai_config_signals(commits),
        *_detect_commit_frequency_spike(commits),
    ]

    return HeuristicResult(
        suggested_date=_suggested_date_from_signals(signals),
        confidence_score=_confidence_score(signals),
        signals_detected=signals,
    )
