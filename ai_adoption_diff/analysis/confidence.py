"""Confidence scoring for adoption-anchor reliability."""

from __future__ import annotations

from dataclasses import dataclass

from ai_adoption_diff.ingestion import CommitRecord


@dataclass(frozen=True)
class ConfidenceResult:
    """Confidence score with categorical level and explanatory caveats."""

    score: float
    level: str
    caveats: list[str]


def compute(
    before_commits: list[CommitRecord],
    after_commits: list[CommitRecord],
    anchor_source: str = "manual",
) -> ConfidenceResult:
    """Compute a bounded confidence score from anchor source and window sizes."""
    score = 1.0
    caveats: list[str] = []

    if anchor_source == "heuristic":
        score -= 0.3
        caveats.append("Adoption date was inferred, not provided manually.")

    if len(before_commits) < 10:
        score -= 0.2
        caveats.append("Before window has fewer than 10 commits.")

    if len(after_commits) < 10:
        score -= 0.2
        caveats.append("After window has fewer than 10 commits.")

    score = max(0.0, min(1.0, score))

    if score >= 0.7:
        level = "high"
    elif score >= 0.4:
        level = "medium"
    else:
        level = "low"

    return ConfidenceResult(score=score, level=level, caveats=caveats)
