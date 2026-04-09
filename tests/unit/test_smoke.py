"""Smoke tests for the package, shared modules, and CLI surface."""

from __future__ import annotations

import importlib

from click.testing import CliRunner

from ai_adoption_diff.cli import cli


def test_package_importable() -> None:
    package = importlib.import_module("ai_adoption_diff")

    assert package is not None


def test_tracing_get_logger_callable() -> None:
    from ai_adoption_diff.shared.tracing import get_logger

    logger = get_logger("test")

    assert hasattr(logger, "info")


def test_config_loads(monkeypatch) -> None:
    monkeypatch.delenv("AI_DIFF_LOG_LEVEL", raising=False)
    monkeypatch.delenv("AI_DIFF_OUTPUT_DIR", raising=False)

    from ai_adoption_diff.shared.config import Config

    config = Config()

    assert config is not None


def test_cli_help_exits_zero() -> None:
    runner = CliRunner()

    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "analyze" in result.output
