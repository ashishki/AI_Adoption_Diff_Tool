"""Read commit history from a local git repository."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
from pathlib import Path
from subprocess import CalledProcessError, run
from time import perf_counter

from ai_adoption_diff.ingestion import IngestionError
from ai_adoption_diff.shared.tracing import get_logger


LOGGER = get_logger(__name__)


@dataclass(frozen=True)
class CommitRecord:
    """Normalized commit metadata derived from git log output."""

    sha: str
    author_email_hash: str
    timestamp: datetime
    file_paths: list[str]
    files_changed: int
    insertions: int
    deletions: int
    message: str


def _run_git(repo_path: Path, args: list[str]) -> str:
    operation_name = "git_log"
    logger = LOGGER.bind(operation_name=operation_name, trace_id=str(repo_path))
    started_at = perf_counter()

    try:
        completed = run(
            ["git", "-C", str(repo_path), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except CalledProcessError as exc:
        duration_ms = round((perf_counter() - started_at) * 1000, 3)
        logger.debug(
            "git subprocess failed",
            success=False,
            duration_ms=duration_ms,
            returncode=exc.returncode,
        )
        raise

    duration_ms = round((perf_counter() - started_at) * 1000, 3)
    logger.debug("git subprocess completed", success=True, duration_ms=duration_ms)
    return completed.stdout


def _parse_numstat_value(value: str) -> int:
    if value == "-":
        return 0
    return int(value)


def read_commits(repo_path: str | Path) -> list[CommitRecord]:
    """Return commit records for the given git repository path."""
    path = Path(repo_path)

    try:
        _run_git(path, ["rev-parse", "--is-inside-work-tree"])
    except CalledProcessError as exc:
        raise IngestionError(f"Invalid git repository path: {path}") from exc

    try:
        _run_git(path, ["rev-parse", "--verify", "HEAD"])
    except CalledProcessError:
        return []

    try:
        output = _run_git(
            path,
            ["log", "--format=%H|%ae|%ai|%s", "--numstat", "--no-merges"],
        )
    except CalledProcessError as exc:
        raise IngestionError(f"Failed to read git history for {path}") from exc

    commits: list[CommitRecord] = []
    current_header: tuple[str, str, datetime, str] | None = None
    file_paths: list[str] = []
    insertions = 0
    deletions = 0

    def flush_commit() -> None:
        nonlocal current_header, file_paths, insertions, deletions

        if current_header is None:
            return

        sha, author_email_hash, timestamp, message = current_header
        commits.append(
            CommitRecord(
                sha=sha,
                author_email_hash=author_email_hash,
                timestamp=timestamp,
                file_paths=file_paths.copy(),
                files_changed=len(file_paths),
                insertions=insertions,
                deletions=deletions,
                message=message,
            )
        )
        current_header = None
        file_paths = []
        insertions = 0
        deletions = 0

    for raw_line in output.splitlines():
        if not raw_line.strip():
            continue

        if "|" in raw_line and "\t" not in raw_line:
            flush_commit()
            sha, email, timestamp_raw, message = raw_line.split("|", maxsplit=3)
            current_header = (
                sha,
                hashlib.sha256(email.encode()).hexdigest(),
                datetime.strptime(timestamp_raw, "%Y-%m-%d %H:%M:%S %z"),
                message,
            )
            continue

        inserted_raw, deleted_raw, file_path = raw_line.split("\t", maxsplit=2)
        insertions += _parse_numstat_value(inserted_raw)
        deletions += _parse_numstat_value(deleted_raw)
        file_paths.append(file_path)

    flush_commit()
    return commits
