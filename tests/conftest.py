"""Shared pytest fixtures for the test suite."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess

import pytest


def _run_git(repo_path: Path, args: list[str], env: dict[str, str] | None = None) -> None:
    subprocess.run(
        ["git", "-C", str(repo_path), *args],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )


@pytest.fixture(scope="function")
def tmp_git_repo(tmp_path: Path) -> Path:
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    _run_git(repo_path, ["init"])
    _run_git(repo_path, ["config", "user.name", "Example Dev"])
    _run_git(repo_path, ["config", "user.email", "dev@example.com"])

    commit_specs = [
        ("2024-01-01T09:00:00+0000", "initial commit"),
        ("2024-01-02T09:00:00+0000", "second commit"),
        ("2024-01-03T09:00:00+0000", "third commit"),
        ("2024-01-04T09:00:00+0000", "fourth commit"),
        ("2024-01-05T09:00:00+0000", "fifth commit"),
    ]

    (repo_path / "app.py").write_text("line one\n")
    _commit_all(repo_path, *commit_specs[0])

    (repo_path / "app.py").write_text("line one\nline two\n")
    _commit_all(repo_path, *commit_specs[1])

    (repo_path / "app.py").write_text("line one updated\nline two\n")
    _commit_all(repo_path, *commit_specs[2])

    (repo_path / "docs.md").write_text("alpha\nbeta\n")
    _commit_all(repo_path, *commit_specs[3])

    (repo_path / "docs.md").write_text("alpha\n")
    (repo_path / "notes.txt").write_text("note\n")
    _commit_all(repo_path, *commit_specs[4])

    return repo_path


@pytest.fixture(scope="function")
def large_git_repo(tmp_path: Path) -> Path:
    """Git repo with ≥20 commits spanning ≥6 months — required by T17 integration tests.

    24 commits: Jan–Mar 2024 (before window), Apr–Jul 2024 (after window).
    Adoption date mid-point: 2024-04-01.
    """
    repo_path = tmp_path / "large_repo"
    repo_path.mkdir()

    _run_git(repo_path, ["init"])
    _run_git(repo_path, ["config", "user.name", "Example Dev"])
    _run_git(repo_path, ["config", "user.email", "dev@example.com"])

    # 24 commits spanning 2024-01-01 to 2024-07-15 (6.5 months)
    commit_specs = [
        ("2024-01-05T09:00:00+0000", "feat: init app"),
        ("2024-01-15T09:00:00+0000", "feat: add config"),
        ("2024-01-25T09:00:00+0000", "fix: config typo"),
        ("2024-02-05T09:00:00+0000", "feat: add models"),
        ("2024-02-12T09:00:00+0000", "refactor: clean models"),
        ("2024-02-20T09:00:00+0000", "test: add model tests"),
        ("2024-02-28T09:00:00+0000", "fix: model validation"),
        ("2024-03-05T09:00:00+0000", "feat: add api"),
        ("2024-03-12T09:00:00+0000", "feat: api auth"),
        ("2024-03-20T09:00:00+0000", "test: api tests"),
        ("2024-03-28T09:00:00+0000", "fix: auth edge case"),
        ("2024-04-01T09:00:00+0000", "chore: add .cursorrules"),  # adoption signal
        ("2024-04-08T09:00:00+0000", "feat: ai-assisted endpoint"),
        ("2024-04-15T09:00:00+0000", "feat: ai-assisted models"),
        ("2024-04-22T09:00:00+0000", "feat: ai-assisted tests"),
        ("2024-04-30T09:00:00+0000", "fix: ai endpoint bug"),
        ("2024-05-07T09:00:00+0000", "feat: new module"),
        ("2024-05-15T09:00:00+0000", "refactor: module cleanup"),
        ("2024-05-22T09:00:00+0000", "test: new module tests"),
        ("2024-06-01T09:00:00+0000", "feat: reporting"),
        ("2024-06-10T09:00:00+0000", "fix: report formatting"),
        ("2024-06-20T09:00:00+0000", "feat: export json"),
        ("2024-07-01T09:00:00+0000", "feat: export html"),
        ("2024-07-15T09:00:00+0000", "chore: cleanup"),
    ]

    (repo_path / "app.py").write_text("# app\n")
    _commit_all(repo_path, *commit_specs[0])

    for i, (commit_time, message) in enumerate(commit_specs[1:], start=1):
        (repo_path / "app.py").write_text(f"# app v{i}\n")
        if "cursorrules" in message:
            (repo_path / ".cursorrules").write_text("# cursor rules\n")
        _commit_all(repo_path, commit_time, message)

    return repo_path


def _commit_all(repo_path: Path, commit_time: str, message: str) -> None:
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = commit_time
    env["GIT_COMMITTER_DATE"] = commit_time
    _run_git(repo_path, ["add", "."], env=env)
    _run_git(repo_path, ["commit", "-m", message], env=env)
