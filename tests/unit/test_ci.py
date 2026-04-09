"""Tests for the GitHub Actions CI workflow and ruff configuration."""

from __future__ import annotations

import subprocess
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"


def load_ci_workflow() -> dict:
    with CI_WORKFLOW_PATH.open(encoding="utf-8") as workflow_file:
        workflow = yaml.safe_load(workflow_file)

    assert isinstance(workflow, dict)
    return workflow


def test_ci_workflow_exists_and_valid() -> None:
    assert CI_WORKFLOW_PATH.is_file()

    workflow = load_ci_workflow()

    assert workflow["name"] == "ci"
    assert "on" in workflow
    assert "push" in workflow["on"]
    assert "pull_request" in workflow["on"]
    assert "jobs" in workflow
    assert "ci" in workflow["jobs"]


def test_ci_workflow_has_required_steps() -> None:
    workflow = load_ci_workflow()

    steps = workflow["jobs"]["ci"]["steps"]
    step_names = [step.get("name", "") for step in steps]
    step_uses = [step.get("uses", "") for step in steps]
    step_runs = [step.get("run", "") for step in steps]

    assert "actions/checkout@v4" in step_uses
    assert "Setup Python" in step_names
    assert any(
        step_use == "actions/setup-python@v5"
        and step.get("with", {}).get("python-version") == "3.11"
        for step, step_use in zip(steps, step_uses, strict=True)
    )
    assert "Install dependencies" in step_names
    assert "pip install -r requirements-dev.txt -e ." in step_runs
    assert "Ruff check" in step_names
    assert "ruff check ai_adoption_diff/ tests/" in step_runs
    assert "Ruff format check" in step_names
    assert "ruff format --check ai_adoption_diff/ tests/" in step_runs
    assert "Pytest" in step_names
    assert "pytest -q" in step_runs


def test_ruff_check_passes() -> None:
    result = subprocess.run(
        ["ruff", "check", "ai_adoption_diff/", "tests/"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_ruff_format_passes() -> None:
    result = subprocess.run(
        ["ruff", "format", "--check", "ai_adoption_diff/", "tests/"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
