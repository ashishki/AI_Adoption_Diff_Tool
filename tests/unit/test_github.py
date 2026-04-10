"""Unit tests for GitHub repository ingestion helpers."""

from __future__ import annotations

from pathlib import Path
import subprocess

import pytest
from structlog.testing import capture_logs

from ai_adoption_diff.ingestion.github import (
    GitHubError,
    clone_repo,
    is_github_url,
    run_with_github_repo,
)


def test_github_url_detected_and_cleanup(monkeypatch) -> None:
    calls: list[tuple[list[str], dict[str, object]]] = []
    observed_clone_path: Path | None = None
    observed_tmp_dir: Path | None = None

    def fake_run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal observed_clone_path
        calls.append((args, kwargs))
        observed_clone_path = Path(args[-1])
        observed_clone_path.mkdir(parents=True)
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    def callback(clone_path: Path) -> str:
        nonlocal observed_tmp_dir
        observed_tmp_dir = clone_path.parent
        assert clone_path.exists()
        return clone_path.name

    result = run_with_github_repo("https://github.com/example/project", "secret-token", callback)

    assert is_github_url("https://github.com/example/project") is True
    assert result == "repo"
    assert len(calls) == 1
    assert calls[0][0] == [
        "git",
        "clone",
        "https://x-access-token:secret-token@github.com/example/project",
        str(observed_clone_path),
    ]
    assert calls[0][1].get("shell") in (None, False)
    assert observed_tmp_dir is not None
    assert observed_tmp_dir.exists() is False


def test_missing_token_exits_with_error() -> None:
    with pytest.raises(GitHubError, match="GITHUB_TOKEN is required"):
        run_with_github_repo("https://github.com/example/project", None, lambda _: None)


def test_rate_limit_retry_and_give_up(monkeypatch, tmp_path: Path) -> None:
    calls: list[list[str]] = []
    sleeps: list[int] = []

    def fake_run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        calls.append(args)
        raise subprocess.CalledProcessError(
            returncode=128,
            cmd=args,
            stderr="fatal: unable to access repository: HTTP 429",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr("ai_adoption_diff.ingestion.github.time.sleep", sleeps.append)

    with pytest.raises(GitHubError, match="rate limit"):
        clone_repo("https://github.com/example/project", "secret-token", tmp_path / "repo")

    assert len(calls) == 4
    assert sleeps == [1, 2, 4]


def test_token_not_logged(monkeypatch, tmp_path: Path) -> None:
    token = "top-secret-token"

    def fake_run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        Path(args[-1]).mkdir(parents=True)
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with capture_logs() as logs:
        clone_repo("https://github.com/example/project", token, tmp_path / "repo")

    assert logs
    for log_record in logs:
        for value in log_record.values():
            assert token not in str(value)


def test_cleanup_on_error(monkeypatch) -> None:
    observed_tmp_dir: Path | None = None

    def fake_run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        Path(args[-1]).mkdir(parents=True)
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    def callback(clone_path: Path) -> None:
        nonlocal observed_tmp_dir
        observed_tmp_dir = clone_path.parent
        raise RuntimeError("analysis failed")

    with pytest.raises(RuntimeError, match="analysis failed"):
        run_with_github_repo("https://github.com/example/project", "secret-token", callback)

    assert observed_tmp_dir is not None
    assert observed_tmp_dir.exists() is False
