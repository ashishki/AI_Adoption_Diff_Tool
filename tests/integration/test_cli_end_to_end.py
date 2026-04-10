"""Integration tests for the end-to-end CLI analysis pipeline."""

from __future__ import annotations

import json

from click.testing import CliRunner

from ai_adoption_diff.cli import cli
from ai_adoption_diff.report.model import AnalysisReport


def test_analyze_full_pipeline_exits_zero(large_git_repo, tmp_path) -> None:
    runner = CliRunner(mix_stderr=False)
    output_dir = tmp_path / "output"

    result = runner.invoke(
        cli,
        [
            "analyze",
            "--repo",
            str(large_git_repo),
            "--date",
            "2024-04-01",
            "--tool",
            "cursor",
            "--output",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert (output_dir / "report.json").exists()
    assert (output_dir / "report.md").exists()
    assert "Analysis complete:" in result.stdout
    assert result.stderr == ""


def test_report_json_validates_against_model(large_git_repo, tmp_path) -> None:
    runner = CliRunner(mix_stderr=False)
    output_dir = tmp_path / "output"

    result = runner.invoke(
        cli,
        [
            "analyze",
            "--repo",
            str(large_git_repo),
            "--date",
            "2024-04-01",
            "--tool",
            "cursor",
            "--output",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
    report = AnalysisReport.model_validate(payload)

    assert report.repo_path == str(large_git_repo)
    assert report.tool_label == "cursor"


def test_heuristic_mode_no_crash(large_git_repo, tmp_path) -> None:
    runner = CliRunner(mix_stderr=False)
    output_dir = tmp_path / "output"

    result = runner.invoke(
        cli,
        [
            "analyze",
            "--repo",
            str(large_git_repo),
            "--output",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert result.stderr == ""
    assert "Analysis complete:" in result.stdout or "No adoption signals detected." in result.stdout


def test_invalid_repo_exits_one(tmp_path) -> None:
    runner = CliRunner(mix_stderr=False)
    missing_repo = tmp_path / "missing-repo"

    result = runner.invoke(cli, ["analyze", "--repo", str(missing_repo)])

    assert result.exit_code == 1
    assert "does not exist" in result.stderr or "not a git repository" in result.stderr


def test_html_format_flag_produces_html(large_git_repo, tmp_path) -> None:
    runner = CliRunner(mix_stderr=False)
    output_dir = tmp_path / "output"

    result = runner.invoke(
        cli,
        [
            "analyze",
            "--repo",
            str(large_git_repo),
            "--date",
            "2024-04-01",
            "--tool",
            "cursor",
            "--format",
            "html",
            "--output",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert (output_dir / "report.json").exists()
    assert (output_dir / "report.md").exists()
    assert (output_dir / "report.html").exists()
