"""Tests for the initial project skeleton."""

from __future__ import annotations

import importlib.metadata
import re
import shutil
import subprocess
from pathlib import Path

from click.testing import CliRunner

from ai_adoption_diff.cli import cli
from ai_adoption_diff.shared.tracing import get_logger


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_package_installs() -> None:
    assert importlib.metadata.version("ai-adoption-diff-tool")


def test_version_command() -> None:
    pyproject_text = (PROJECT_ROOT / "pyproject.toml").read_text()
    match = re.search(r'^version = "([^"]+)"$', pyproject_text, re.MULTILINE)
    assert match is not None
    expected_version = match.group(1)

    # Try the installed entry point if available on PATH
    ai_diff_bin = shutil.which("ai-diff")
    if ai_diff_bin:
        result = subprocess.run(
            [ai_diff_bin, "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        assert expected_version in result.stdout

    # Always verify via CliRunner (works regardless of PATH)
    runner = CliRunner()
    cli_result = runner.invoke(cli, ["--version"])
    assert cli_result.exit_code == 0
    assert expected_version in cli_result.output


def test_directory_structure() -> None:
    expected_dirs = [
        PROJECT_ROOT / "ai_adoption_diff",
        PROJECT_ROOT / "ai_adoption_diff" / "ingestion",
        PROJECT_ROOT / "ai_adoption_diff" / "analysis",
        PROJECT_ROOT / "ai_adoption_diff" / "metrics",
        PROJECT_ROOT / "ai_adoption_diff" / "report",
        PROJECT_ROOT / "ai_adoption_diff" / "shared",
        PROJECT_ROOT / "tests" / "unit",
        PROJECT_ROOT / "tests" / "integration",
        PROJECT_ROOT / "docs",
    ]

    for expected_dir in expected_dirs:
        assert expected_dir.is_dir(), f"missing directory: {expected_dir}"


def test_tracing_module_exports_get_logger() -> None:
    logger = get_logger("test")
    # Verify the logger supports bind() with trace_id and operation_name
    rebound_logger = logger.bind(trace_id="trace-1", operation_name="op-1")

    assert hasattr(logger, "info"), "Logger must expose .info()"
    assert hasattr(logger, "bind"), "Logger must expose .bind()"
    assert rebound_logger is not None
