"""Integration tests for git log ingestion."""

from __future__ import annotations

from datetime import datetime
import hashlib
from pathlib import Path
import subprocess

from ai_adoption_diff.ingestion.git_reader import CommitRecord, read_commits


def test_read_commits_returns_commit_records(tmp_git_repo: Path) -> None:
    commits = read_commits(tmp_git_repo)

    assert commits
    assert all(isinstance(commit, CommitRecord) for commit in commits)
    assert all(not hasattr(commit, "author_email") for commit in commits)

    commit = commits[0]
    assert commit.sha
    assert isinstance(commit.timestamp, datetime)
    assert isinstance(commit.file_paths, list)
    assert commit.files_changed == len(commit.file_paths)
    assert isinstance(commit.insertions, int)
    assert isinstance(commit.deletions, int)
    assert isinstance(commit.message, str)


def test_read_commits_count_and_fields(tmp_git_repo: Path) -> None:
    commits = read_commits(tmp_git_repo)

    assert len(commits) == 5

    expected = [
        ("fifth commit", 2, 1, 1),
        ("fourth commit", 1, 2, 0),
        ("third commit", 1, 1, 1),
        ("second commit", 1, 1, 0),
        ("initial commit", 1, 1, 0),
    ]

    actual = [
        (commit.message, commit.files_changed, commit.insertions, commit.deletions)
        for commit in commits
    ]

    assert actual == expected


def test_read_commits_empty_repo(tmp_path: Path) -> None:
    repo_path = tmp_path / "empty-repo"
    repo_path.mkdir()
    subprocess.run(["git", "init", str(repo_path)], check=True, capture_output=True, text=True)

    assert read_commits(repo_path) == []


def test_author_email_is_hashed(tmp_git_repo: Path) -> None:
    commits = read_commits(tmp_git_repo)
    expected_hash = hashlib.sha256("dev@example.com".encode()).hexdigest()

    assert commits
    assert all(commit.author_email_hash == expected_hash for commit in commits)
