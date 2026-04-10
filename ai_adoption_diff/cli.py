"""CLI entry point for AI Adoption Diff Tool."""

from __future__ import annotations

from pathlib import Path
import subprocess

import click

from ai_adoption_diff import __version__
from ai_adoption_diff.analysis import AnchorError, PartitionError
from ai_adoption_diff.analysis.anchor import AnalysisWindow, compute_window
from ai_adoption_diff.analysis.confidence import compute as compute_confidence
from ai_adoption_diff.analysis.heuristic import infer_adoption
from ai_adoption_diff.analysis.partitioner import partition
from ai_adoption_diff.ingestion import IngestionError
from ai_adoption_diff.ingestion.git_reader import CommitRecord, read_commits
from ai_adoption_diff.ingestion.github import GitHubError, is_github_url, run_with_github_repo
from ai_adoption_diff.metrics.commit_size import compute as compute_commit_size
from ai_adoption_diff.metrics.churn import compute_churn_rate, compute_revert_frequency
from ai_adoption_diff.metrics.hot_files import compute_dir_concentration, compute_hot_file_count
from ai_adoption_diff.metrics.test_ratio import compute_boilerplate_signal, compute_test_ratio
from ai_adoption_diff.report import json_export, renderer
from ai_adoption_diff.report.model import (
    AnalysisReport,
    ConfidenceSummary,
    MetricWindowResults,
    MetricsSummary,
)
from ai_adoption_diff.shared.config import Config


CORRELATION_CAVEAT = "Metrics show correlation only. Causality cannot be inferred."


@click.group()
@click.version_option(version=__version__, prog_name="ai-diff")
def cli() -> None:
    """Analyze repository changes around AI tool adoption."""


def _ensure_local_repo(repo: str) -> Path:
    repo_path = Path(repo)
    if not repo_path.exists():
        raise click.ClickException(f"{repo_path} does not exist")

    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "--is-inside-work-tree"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise click.ClickException(f"{repo_path} is not a git repository") from exc

    if completed.stdout.strip() != "true":
        raise click.ClickException(f"{repo_path} is not a git repository")

    return repo_path


def _build_window_from_date(adoption_date: str, commits: list[CommitRecord]) -> AnalysisWindow:
    try:
        return compute_window(adoption_date, commits)
    except (AnchorError, ValueError) as exc:
        raise click.ClickException(
            f"No commits found in the analysis windows for adoption date {adoption_date}."
        ) from exc


def _build_window_from_heuristic(commits: list[CommitRecord]) -> tuple[AnalysisWindow | None, str]:
    heuristic_result = infer_adoption(commits)
    if not heuristic_result.signals_detected or heuristic_result.suggested_date is None:
        click.echo("No adoption signals detected.")
        return None, "heuristic"

    try:
        return compute_window(heuristic_result.suggested_date.isoformat(), commits), "heuristic"
    except AnchorError as exc:
        raise click.ClickException(
            "No commits found in the inferred analysis windows for the detected adoption date."
        ) from exc


def _build_metric_window(commits: list[CommitRecord]) -> MetricWindowResults:
    commit_size = compute_commit_size(commits)
    churn_rate = compute_churn_rate(commits)
    revert_frequency = compute_revert_frequency(commits)
    test_ratio = compute_test_ratio(commits)
    boilerplate_signal = compute_boilerplate_signal(commits)
    hot_file_count = compute_hot_file_count(commits)
    dir_concentration = compute_dir_concentration(commits)

    return MetricWindowResults(
        mean_lines=commit_size.mean_lines,
        median_lines=commit_size.median_lines,
        p90_lines=commit_size.p90_lines,
        mean_files=commit_size.mean_files,
        median_files=commit_size.median_files,
        p90_files=commit_size.p90_files,
        churn_rate=churn_rate.churn_rate,
        rework_frequency=None,
        revert_frequency=revert_frequency.revert_frequency,
        test_ratio=test_ratio.test_ratio,
        boilerplate_signal=boilerplate_signal.boilerplate_signal,
        hot_file_count=None if hot_file_count is None else hot_file_count.hot_file_count,
        dir_concentration=(
            None if dir_concentration is None else dir_concentration.dir_concentration
        ),
        sample_size=len(commits),
    )


def _build_report(
    repo_path: str,
    tool_label: str,
    window: AnalysisWindow,
    before_commits: list[CommitRecord],
    after_commits: list[CommitRecord],
    anchor_source: str,
) -> AnalysisReport:
    confidence = compute_confidence(before_commits, after_commits, anchor_source=anchor_source)
    caveats = [*confidence.caveats, CORRELATION_CAVEAT]
    rationale = (
        "Manual adoption date supplied by the operator."
        if anchor_source == "manual"
        else "Adoption date inferred from commit-history signals."
    )

    return AnalysisReport(
        repo_path=repo_path,
        tool_label=tool_label,
        adoption_date=window.adoption_date.isoformat(),
        window_days=(window.adoption_date - window.before_start).days,
        confidence=ConfidenceSummary(
            score=confidence.score,
            level=confidence.level,
            anchor_source=anchor_source,
            rationale=rationale,
        ),
        metrics=MetricsSummary(
            before=_build_metric_window(before_commits),
            after=_build_metric_window(after_commits),
        ),
        caveats=caveats,
    )


def _run_analysis(repo_path: Path, date: str | None, tool: str, output: Path, fmt: str) -> int:
    try:
        commits = read_commits(repo_path)
    except IngestionError as exc:
        raise click.ClickException(str(exc)) from exc

    if date is not None:
        window = _build_window_from_date(date, commits)
        anchor_source = "manual"
    else:
        heuristic_window, anchor_source = _build_window_from_heuristic(commits)
        if heuristic_window is None:
            return 0
        window = heuristic_window

    try:
        before_commits, after_commits = partition(commits, window)
    except PartitionError as exc:
        raise click.ClickException(
            f"No commits found in the analysis windows for adoption date {window.adoption_date}."
        ) from exc

    report = _build_report(
        repo_path=str(repo_path),
        tool_label=tool,
        window=window,
        before_commits=before_commits,
        after_commits=after_commits,
        anchor_source=anchor_source,
    )

    json_path = json_export.write(report, output)
    markdown_path = renderer.render_markdown(report, output)

    html_path: Path | None = None
    if fmt in {"html", "both"}:
        html_path = renderer.render_html(report, output)

    summary = (
        f"Analysis complete: adoption_date={report.adoption_date} "
        f"before_commits={len(before_commits)} after_commits={len(after_commits)} "
        f"json={json_path} markdown={markdown_path}"
    )
    if html_path is not None:
        summary += f" html={html_path}"

    click.echo(summary)
    return 0


def _run_for_repo_input(
    repo: str, date: str | None, tool: str, output: Path, fmt: str, config: Config
) -> int:
    def runner(local_repo_path: Path) -> int:
        return _run_analysis(local_repo_path, date, tool, output, fmt)

    if is_github_url(repo):
        try:
            return run_with_github_repo(repo, config.github_token, runner)
        except GitHubError as exc:
            raise click.ClickException(str(exc)) from exc

    repo_path = _ensure_local_repo(repo)
    return runner(repo_path)


@cli.command()
@click.option("--repo", required=True, type=str)
@click.option("--date", type=str)
@click.option(
    "--tool",
    type=click.Choice(["cursor", "copilot", "claude_code", "unknown"]),
    default="unknown",
    show_default=True,
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["json", "html", "both"]),
    default="json",
    show_default=True,
)
@click.option(
    "--output",
    type=click.Path(path_type=Path, file_okay=False, dir_okay=True, writable=True),
    default=Path("./output"),
    show_default=True,
)
def analyze(repo: str, date: str | None, tool: str, fmt: str, output: Path) -> None:
    """Run the full repository analysis pipeline."""
    config = Config()
    exit_code = _run_for_repo_input(repo, date, tool, output, fmt, config)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    cli()
