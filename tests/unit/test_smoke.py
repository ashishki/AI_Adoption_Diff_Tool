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


def test_config_github_token_reads_env(monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "test-secret-token")

    from importlib import reload
    import ai_adoption_diff.shared.config as cfg_module

    reload(cfg_module)
    config = cfg_module.Config()

    assert config.github_token == "test-secret-token"


def test_config_github_token_absent_from_logs(monkeypatch, caplog) -> None:
    import logging

    monkeypatch.setenv("GITHUB_TOKEN", "should-not-appear-in-logs")

    from importlib import reload
    import ai_adoption_diff.shared.config as cfg_module

    reload(cfg_module)

    with caplog.at_level(logging.DEBUG):
        cfg_module.Config()

    for record in caplog.records:
        assert "should-not-appear-in-logs" not in record.getMessage()


def test_cli_help_exits_zero() -> None:
    runner = CliRunner()

    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "analyze" in result.output
