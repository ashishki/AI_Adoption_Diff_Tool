# Phase 2 Report — Ingestion and Windowing
_Date: 2026-04-10 · Tasks: T04–T07 · Reviewer cycle: 2_

---

## What Was Built and Why

Phase 2 is the first layer of real functionality in the AI Adoption Diff Tool. Before this phase, the project had only a skeleton (CLI stub, shared config, tracing module) and CI. Phase 2 turns it into a system that can actually read a git repository and divide its history into a "before AI" window and an "after AI" window — the foundational split that all later metric comparisons depend on.

Four modules were implemented:

**Git Log Ingestion (T04 — `ingestion/git_reader.py`)**
This module shells out to `git log --numstat` to read a repository's commit history and returns a typed list of `CommitRecord` objects. Each record captures the commit SHA, timestamp, file change counts, insertion and deletion line counts, the commit message, and the list of changed file paths. Author emails are never stored raw — they are SHA-256 hashed immediately on parse, before anything else touches them. This is a hard privacy invariant enforced at the boundary. Repos that do not exist or are not git repositories raise `IngestionError` so the caller always gets a clean typed error rather than a raw subprocess crash.

**Adoption Anchor (T05 — `analysis/anchor.py`)**
When the user already knows when they adopted an AI coding tool, they supply a date. The anchor module validates that date (rejecting anything that is not `YYYY-MM-DD`), then computes a symmetric before/after window of configurable width (default 90 days) around it. The result is an `AnalysisWindow` — a frozen dataclass holding `before_start`, `adoption_date`, and `after_end`. If the commit history has no commits in the before or after window, the module raises `AnchorError` so the caller knows the data is insufficient.

**Heuristic Inference (T06 — `analysis/heuristic.py`)**
When the user does not know their adoption date, the heuristic module tries to infer it from signals in the commit history. Two signals are implemented: detection of AI-configuration files (`.cursorrules`, `.github/copilot-instructions.md`, `.claude/`, `AGENTS.md`) appearing in commit file paths, and a commit-frequency spike detector (a rolling 30-day window rising above 2x its baseline). The module returns a `HeuristicResult` with a suggested date (the median of all detected signal dates), a confidence score between 0.0 and 1.0, and the list of signals that fired. When nothing is detected, it returns `suggested_date=None` and `confidence_score=0.0` rather than guessing.

**Window Partitioner (T07 — `analysis/partitioner.py`)**
Given a commit list and an `AnalysisWindow`, the partitioner splits commits into two non-overlapping groups: commits that fall strictly before the adoption date go into `before`; commits on or after the adoption date go into `after`. Commits outside the window bounds entirely are silently excluded. The input list is never mutated. If the before window is empty, `PartitionError` is raised.

---

## Test Delta

| Milestone | Passing Tests |
|-----------|--------------|
| End of Phase 1 (T01–T03) | 12 |
| End of Phase 2 (T04–T07) | **31** |
| **Delta** | **+19** |

The 19 new tests cover: commit record field correctness, empty repo handling, invalid path error propagation, email hashing, window bounds arithmetic, invalid date rejection, empty window detection, AI-config file signal detection, commit frequency spike detection, no-signal fallback, median date selection, correct before/after splitting, adoption-date boundary routing, out-of-window exclusion, and input immutability.

---

## Open Findings

All findings are P2 (must fix before Phase 3 begins) or lower. There are no P0 or P1 blockers.

### P2 — Fix Before Phase 3

| ID | Where | What Is Wrong | Risk |
|----|-------|---------------|------|
| CODE-8 | `git_reader.py:47,56` | Subprocess calls are logged at `INFO` level; the spec requires `DEBUG`. | Log noise in production runs; users will see git internals they should not. |
| CODE-9 | `git_reader.py:34` | The `operation_name` field is bound as `"git_reader.subprocess"` instead of the spec-required `"git_log"`. | Log correlation tools filtering on `operation_name` will not find git log records. |
| CODE-10 | `git_reader.py:35` | `trace_id` is set to `str(repo_path)` instead of a pipeline-level UUID4. | Every pipeline stage has a different trace ID, making it impossible to correlate a single run's log lines across modules. |
| CODE-11 | `partitioner.py:26-28` | `partition()` does not raise `PartitionError` when the `after` window is empty (spec F4 AC-4 unimplemented). | A caller that receives an empty `after` list will silently compute metrics on zero commits, producing misleading results. |
| CODE-12 | `heuristic.py:131-133` | The "sudden change in median commit size" signal required by spec F3 AC-2 is not implemented. | The heuristic will miss one class of AI adoption evidence, reducing inference quality. |
| CODE-13 | `anchor.py:9`, `heuristic.py:10`, `partitioner.py:7` | All three `analysis/` modules import `CommitRecord` directly from the `ingestion.git_reader` sub-module rather than from the `ingestion` package boundary. | This creates hidden coupling between layers. If `git_reader.py` is refactored, all three analysis modules break at import time even though the public contract has not changed. |
| CODE-14 | `tests/integration/test_git_reader.py` | The integration test suite is missing the invalid-path error propagation test (spec T04 AC-4 integration coverage). | AC-4 coverage exists only at unit level; integration-level confidence that error propagation works end-to-end is absent. |

### P3 — Fix Before Deadline (not blocking Phase 3)

| ID | What | Deadline | Warning |
|----|------|----------|---------|
| CODE-15 | `tmp_git_repo` fixture has only 5 commits / 5 days; T17 needs ≥20 commits spanning ≥6 months. | Before T17 | No action needed now. |
| CODE-16 | `GITHUB_TOKEN` absent from `config.py`; GitHub support (T16) cannot be verified. | Before T16 | **Age 2/3 — escalates to P1 at Cycle 3.** |
| CODE-17 | `requires-python = ">=3.10"` in `pyproject.toml` conflicts with ruff `target-version = "py311"`. | Before Phase 5 | **Age 2/3 — escalates to P1 at Cycle 3.** |

---

## Health Verdict

**OK — Phase 2 is healthy. Phase 3 may proceed after the Fix Queue is cleared.**

Security posture is strong: email hashing is enforced at the parse boundary, subprocess calls use list form with no `shell=True`, and only read-only git commands are invoked. The four carry-forward P2 issues from Phase 1 (CODE-1 through CODE-3 and CODE-6) are all closed. No P0 or P1 findings exist.

The seven open issues (CODE-8 through CODE-14) are real gaps but none of them risk data loss or incorrect metric results at this stage. The two most consequential are CODE-11 (silent empty after-window) and CODE-12 (missing signal), and both have clear, targeted fixes already documented in the Fix Queue.

---

## What Comes Next: Phase 3 — Metrics

Phase 3 (tasks T08–T11) builds the statistical heart of the tool. With the before/after commit lists now reliably produced by Phase 2, Phase 3 computes the measurements that will actually appear in the final report:

- **T08 — Commit Size and Files-Touched Metrics:** mean, median, and p90 of lines changed and files touched per commit, for each window.
- **T09 — Churn and Rework Metrics:** deletion-to-total-lines ratio and revert/fix commit frequency.
- **T10 — Test-to-Code Ratio and Boilerplate Metrics:** fraction of line changes in test files versus non-test files, and a boilerplate signal based on file name patterns.
- **T11 — Hot-File Instability and Directory Concentration:** count of files changed in more than 10% of commits, and the fraction of all changes concentrated in the top three directories.

Before T08 begins, the Fix Queue (CODE-8 through CODE-14) must be resolved. The baseline entering Phase 3 is 31 passing tests.
