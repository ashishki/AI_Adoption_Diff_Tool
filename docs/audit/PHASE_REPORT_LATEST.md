# Phase 1 Report — Foundation
_Date: 2026-04-10 · Tasks: T01, T02, T03 · Reviewed: Cycle 1_

---

## What Was Built and Why

Phase 1 is the foundation layer. Before any analysis logic, metrics, or reporting can be written, the project needs a place to live: a proper Python package structure, a working entry point, a lint configuration, a CI pipeline, and a baseline of smoke tests. That is exactly what Phase 1 delivers.

### T01 — Project Skeleton

The first task created the entire directory tree from scratch. The package `ai_adoption_diff` and its sub-packages (`ingestion`, `analysis`, `metrics`, `report`, `shared`) were all stubbed out with `__init__.py` files. Two shared modules were implemented for real:

- `shared/config.py` — loads environment variables (`AI_DIFF_LOG_LEVEL`, `AI_DIFF_OUTPUT_DIR`) via Pydantic, giving every future module a single, validated source of configuration truth.
- `shared/tracing.py` — wraps structlog to expose a single `get_logger(name)` function. All logging in the project must go through this function rather than calling structlog directly.

A Click-based CLI stub was wired up so that `ai-diff --version` exits 0 and `ai-diff analyze` acknowledges the command without crashing. The `pyproject.toml` was written with all declared dependencies (click, structlog, pydantic, jinja2, httpx) and dev dependencies (pytest, ruff).

Why does the skeleton matter? Because every later task builds on an assumption that the package installs cleanly, the sub-package layout matches the architecture plan, and shared infrastructure is already in place. Getting this right early prevents painful retrofits later.

T01 brought the test count from 0 to 4.

### T02 — CI Setup

The second task added a GitHub Actions workflow (`.github/workflows/ci.yml`) that triggers on every push and pull request. The workflow: checks out the code, sets up Python 3.11, installs both runtime and dev dependencies, runs `ruff check`, runs `ruff format --check`, and finally runs `pytest`. Ruff was configured in `pyproject.toml` with `target-version = "py311"` and a line length of 100 characters.

The tests for T02 validate the CI configuration itself: they load the YAML file, assert the job name and trigger events, and verify that ruff passes against the current codebase. This means CI is not just a file that exists — it is a file that is tested.

T02 brought the test count from 4 to 8.

### T03 — Smoke Tests

The third task established the formal test baseline by adding smoke tests that cover the most critical surface areas of the skeleton:

- The top-level package is importable without errors.
- `get_logger('test')` from `shared/tracing.py` returns an object with a `.info()` method.
- `Config()` from `shared/config.py` instantiates without errors.
- `ai-diff --help` (via Click's `CliRunner`) exits 0 and mentions the `analyze` command.

These tests exist to catch any silent breakage in the shared modules — the kind of breakage that would otherwise only surface when a later task tried to actually use logging or configuration.

T03 brought the test count from 8 to 12.

---

## Test Delta

| Milestone | Passing Tests |
|-----------|--------------|
| Before Phase 1 (no code) | 0 |
| After T01 | 4 |
| After T02 | 8 |
| After T03 (Phase 1 gate) | **12** |

All 12 tests pass. No failures. `ruff check` exits 0. `ai-diff --version` exits 0. The Phase 1 gate conditions are fully satisfied.

---

## Open Findings

The deep review identified 5 P2 findings, 2 P3 findings, and 4 informational carry-forwards. There are no P0 or P1 issues. A P2 issue means "must fix before the next task begins." A P3 means "deferred to a scheduled future task." INFO means "watch and verify later."

### P2 — Must Fix Before T04

| ID | File | What Is Wrong | Why It Matters |
|----|------|---------------|----------------|
| CODE-1 | `shared/tracing.py:25` | `get_logger` return type is annotated as `FilteringBoundLogger`, which is an internal structlog concrete type, not the public protocol. | Any module that imports `get_logger` and annotates its logger variable as `BoundLogger` (the public interface) will get a type-checker error. This is a contract-correctness issue, not a runtime bug, but it will break mypy/pyright for all future tasks. Fix: change the annotation to `structlog.stdlib.BoundLogger`. |
| CODE-2 | `ingestion/__init__.py:1` | `IngestionError` is not exported from the `ingestion` package. | T04 (Git Log Ingestion) requires callers to catch `IngestionError` via `from ai_adoption_diff.ingestion import IngestionError`. If the exception is defined directly in `git_reader.py` instead, the import path breaks and the layered architecture is violated. Fix: add `class IngestionError(Exception): pass` to `ingestion/__init__.py`. |
| CODE-3 | `analysis/__init__.py:1` | `AnchorError` and `PartitionError` are not exported from the `analysis` package. | Same layered import problem as CODE-2, affecting T05 (anchor) and T07 (partitioner). Fix: add both exception stubs to `analysis/__init__.py`. |
| CODE-6 | `shared/tracing.py:28` | The `structlog.get_logger()` call inside `get_logger()` has no comment explaining that this is the only place in the codebase where direct structlog calls are permitted. | Without this marker, a future developer may add direct `structlog.get_logger()` calls elsewhere, bypassing the shared tracing setup (trace IDs, log level, format). Fix: add one inline comment. No structural change required. |
| CODE-7 | `cli.py:17-19` | The `analyze` CLI stub has no `@click.option` declarations for `--repo`, `--date`, `--tool`, `--format`. | T17 (CLI End-to-End Integration) will need to add these options. Doing so against a bare stub is fine, but this finding is being tracked to ensure T17 remembers to add all four options and does not silently omit any. Status: Watch — deferred to T17. |

### P3 — Deferred, Lower Risk

| ID | File | What Is Wrong | When to Fix |
|----|------|---------------|-------------|
| CODE-4 | `shared/config.py:11-17` | `GITHUB_TOKEN` is not declared in `Config`. The architecture requires that `shared/config.py` be the exclusive place where this env var is loaded. | Pre-stub before T16 (GitHub Remote Support). |
| CODE-5 | `pyproject.toml:8,29` | `requires-python = ">=3.10"` but `ruff target-version = "py311"`. These two settings are inconsistent — the package claims to support Python 3.10 but is linted as if it only needs to work on 3.11+. | Align to `>=3.11` at any convenient point. Low risk; cosmetic inconsistency. |

### INFO — Carry-Forwards to Watch

| ID | Description | Action Required |
|----|-------------|-----------------|
| F-01 | T10 and T11 (test-ratio and hot-files metrics) both need `CommitRecord.file_paths` to be present. That field is defined in T04. | At T04 completion, verify `file_paths` is a real field on `CommitRecord`. If missing, T10/T11 are BLOCKED. |
| F-02 | T16 has two mandatory "heavy" evidence tests: token-not-logged and cleanup-on-error. These need real structlog capture fixtures. | Deferred to Phase 5. |
| F-03 | `docs/prompts/ORCHESTRATOR.md` contains two unresolved template placeholders: `{{PROJECT_ROOT}}` and `{{CODEX_COMMAND}}`. | Manual action required before the first orchestrator loop runs. |
| F-04 | In `CODEX_PROMPT.md`, the Completed Tasks entries for T02 and T03 show commit hashes as "pending" even though both tasks are done. | Cosmetic; update the commit hashes when convenient. No functional impact. |

---

## Health Verdict

**OK — Phase 1 gate passed. No stop-ship conditions.**

The structural baseline is sound. Twelve tests pass, linting is clean, and the CLI entry point is functional. The five P2 findings are real and must be resolved before T04 begins, but they are all small, targeted fixes (two exception class stubs, one return type annotation, one inline comment, one watch item). None of them require rearchitecting anything. The two P3 findings are minor cosmetic inconsistencies with no runtime risk.

The project is in a healthy state to proceed to Phase 2.

---

## What Comes Next

**Resolve the Fix Queue first (before writing any T04 code):**

1. FIX-1: Change `get_logger` return annotation in `tracing.py` to `structlog.stdlib.BoundLogger`.
2. FIX-2: Add `class IngestionError(Exception): pass` to `ingestion/__init__.py`.
3. FIX-3: Add `class AnchorError(Exception): pass` and `class PartitionError(Exception): pass` to `analysis/__init__.py`.
4. FIX-4: Add the inline comment to `tracing.py:28` marking the sole permitted `structlog.get_logger()` call site.

**Then begin Phase 2 — Ingestion and Windowing:**

- **T04 — Git Log Ingestion:** Implement `git_reader.read_commits()` using subprocess + git log. Parse commit records into a frozen `CommitRecord` dataclass. Hash author emails with SHA-256. Raise `IngestionError` on invalid repo paths. Add `tmp_git_repo` fixture to conftest.
- **T05 — Adoption Anchor:** Implement `anchor.compute_window()` to validate a manual adoption date and compute before/after window bounds.
- **T06 — Heuristic Adoption Window Inference:** Detect AI adoption signals (config files, commit frequency spikes) in the commit history and return a suggested adoption date with confidence score.
- **T07 — Window Partitioner:** Split a commit list into before/after lists based on an `AnalysisWindow`. Raise `PartitionError` if the before window is empty.

Phase 2 gate: integration tests against a real temp git repo pass; anchor, heuristic, and partitioner unit tests all pass.
