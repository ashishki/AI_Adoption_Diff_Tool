"""GitHub repository cloning helpers."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from time import perf_counter
from typing import TypeVar
from urllib.parse import urlparse

from ai_adoption_diff.shared.tracing import get_logger


LOGGER = get_logger(__name__)
T = TypeVar("T")
_GITHUB_URL_PREFIX = "https://github.com/"
_RATE_LIMIT_BACKOFF_SECONDS = (1, 2, 4)


class GitHubError(Exception):
    """Raised when GitHub repository access fails."""


def is_github_url(url: str) -> bool:
    """Return True when the URL targets a GitHub repository."""
    return url.startswith(_GITHUB_URL_PREFIX)


def _extract_owner_repo(url: str) -> tuple[str, str]:
    if not is_github_url(url):
        raise GitHubError("GitHub repository URL is required.")

    parsed = urlparse(url)
    path_parts = [part for part in parsed.path.split("/") if part]
    if len(path_parts) < 2:
        raise GitHubError("Invalid GitHub repository URL.")

    owner = path_parts[0]
    repo = path_parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]

    if not owner or not repo:
        raise GitHubError("Invalid GitHub repository URL.")

    return owner, repo


def _is_rate_limited(exc: subprocess.CalledProcessError) -> bool:
    stderr = exc.stderr or ""
    stdout = exc.stdout or ""
    return "429" in stderr or "429" in stdout


def clone_repo(url: str, token: str, dest: Path) -> None:
    """Clone a GitHub repository into the destination path."""
    owner, repo = _extract_owner_repo(url)
    clone_url = f"https://x-access-token:{token}@github.com/{owner}/{repo}"
    command = ["git", "clone", clone_url, str(dest)]
    logger = LOGGER.bind(operation_name="git_clone", trace_id=str(dest))

    for attempt in range(len(_RATE_LIMIT_BACKOFF_SECONDS) + 1):
        started_at = perf_counter()
        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            duration_ms = round((perf_counter() - started_at) * 1000, 3)
            if _is_rate_limited(exc):
                if attempt < len(_RATE_LIMIT_BACKOFF_SECONDS):
                    backoff_seconds = _RATE_LIMIT_BACKOFF_SECONDS[attempt]
                    logger.warning(
                        "git clone rate limited",
                        success=False,
                        duration_ms=duration_ms,
                        retry_in_seconds=backoff_seconds,
                        attempt=attempt + 1,
                    )
                    time.sleep(backoff_seconds)
                    continue

                logger.error(
                    "git clone failed due to rate limit",
                    success=False,
                    duration_ms=duration_ms,
                    attempts=attempt + 1,
                )
                raise GitHubError(
                    "GitHub rate limit encountered while cloning repository."
                ) from exc

            logger.error(
                "git clone failed",
                success=False,
                duration_ms=duration_ms,
                returncode=exc.returncode,
            )
            raise GitHubError("Failed to clone GitHub repository.") from exc

        duration_ms = round((perf_counter() - started_at) * 1000, 3)
        logger.debug("git clone completed", success=True, duration_ms=duration_ms)
        return


def run_with_github_repo(url: str, token: str | None, callback: Callable[[Path], T]) -> T:
    """Clone a GitHub repository, run a callback against it, and clean up."""
    if token is None:
        raise GitHubError("GITHUB_TOKEN is required for GitHub repositories.")

    temp_dir = Path(tempfile.mkdtemp(prefix="ai-diff-github-"))
    clone_path = temp_dir / "repo"

    try:
        clone_repo(url, token, clone_path)
        return callback(clone_path)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
