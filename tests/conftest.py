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


def _commit_all(repo_path: Path, commit_time: str, message: str) -> None:
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = commit_time
    env["GIT_COMMITTER_DATE"] = commit_time
    _run_git(repo_path, ["add", "."], env=env)
    _run_git(repo_path, ["commit", "-m", message], env=env)
