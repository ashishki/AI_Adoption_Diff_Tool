---
# REVIEW_REPORT — Cycle 2
_Date: 2026-04-10 · Scope: T04–T07_

## Executive Summary

- **Stop-Ship: No** — No P0 or P1 blockers exist. Phase 3 (T08) may begin after Fix Queue items are resolved.
- Phase 2 (T04–T07) is complete. Baseline is 31 passing tests, up from 12 in Cycle 1 (+19 tests).
- CODE-1, CODE-2, CODE-3, and CODE-6 are **Closed** — all four P2 carry-forwards from Cycle 1 resolved during T04–T07 implementation.
- Two functional gaps remain in Phase 2 code: `partition()` does not guard the empty `after` window (CODE-11), and `heuristic.py` is missing the mandatory median-commit-size-change signal (CODE-12). Both are P2 and must be resolved before Phase 3 metrics depend on them.
- Security posture is **PASS**: author emails are SHA-256 hashed immediately on parse; no raw email appears in any log field or data structure.
- Subprocess security invariants are **PASS**: list form used throughout; `shell=True` is absent; only read-only git commands (`rev-parse`, `log`) are invoked.
- Cross-layer import hygiene is broken in all three `analysis/` modules: `CommitRecord` is imported directly from `ingestion.git_reader` sub-module instead of the `ingestion` package boundary (CODE-13).
- Two P3 items (CODE-16 / CODE-17) are entering their second cycle open. Age cap is 3 cycles; they must be resolved before T16/T17 respectively and are now flagged **age cap approaching (2/3)**.

---

## P0 Issues

_None._

---

## P1 Issues

_None._

---

## P2 Issues

| ID | Description | Files | Status |
|----|-------------|-------|--------|
| CODE-8 | Git subprocess calls logged at INFO; spec F1 AC-5 requires DEBUG level | `ai_adoption_diff/ingestion/git_reader.py:47,56` | Open |
| CODE-9 | `operation_name` bound as `"git_reader.subprocess"` instead of spec-required `"git_log"` | `ai_adoption_diff/ingestion/git_reader.py:34` | Open |
| CODE-10 | `trace_id` bound to `str(repo_path)` instead of a pipeline-level UUID; log correlation broken across pipeline stages | `ai_adoption_diff/ingestion/git_reader.py:35` | Open |
| CODE-11 | `partition()` does not raise `PartitionError` when `after_commits` is empty — spec F4 AC-4 unimplemented | `ai_adoption_diff/analysis/partitioner.py:26-28` | Open |
| CODE-12 | `heuristic.py` missing "sudden change in median commit size" signal required by spec F3 AC-2 | `ai_adoption_diff/analysis/heuristic.py:131-133` | Open |
| CODE-13 | `analysis/` modules import `CommitRecord` from `ingestion.git_reader` sub-module, bypassing `ingestion` package boundary | `ai_adoption_diff/analysis/anchor.py:9`, `heuristic.py:10`, `partitioner.py:7` | Open |
| CODE-14 | Integration test suite missing invalid-path error propagation test (spec T04 AC-4 integration coverage) | `tests/integration/test_git_reader.py` | Open |

---

## P3 Issues

| ID | Description | Files | Age | Deadline |
|----|-------------|-------|-----|----------|
| CODE-15 | `tmp_git_repo` fixture: 5 commits / 5 days; T17 requires ≥20 commits spanning ≥6 months | `tests/conftest.py:31-37` | 1 | Before T17 |
| CODE-16 | `GITHUB_TOKEN` absent from `config.py`; PS-4 cannot be verified; **age cap approaching (2/3) — escalates to P1 at age 3** | `ai_adoption_diff/shared/config.py` | 2 | Before T16 |
| CODE-17 | `pyproject.toml` `requires-python = ">=3.10"` conflicts with ruff `target-version = "py311"`; **age cap approaching (2/3) — escalates to P1 at age 3** | `pyproject.toml:10,29` | 2 | Before Phase 5 |

---

## Carry-Forward Status

| ID | Sev | Description | Status | Change |
|----|-----|-------------|--------|--------|
| CODE-1 | P2 | `get_logger` return type was `FilteringBoundLogger`; must be `BoundLogger` | **Closed** — `tracing.py:25` now returns `BoundLogger`; verified by ARCH_REPORT 2026-04-10 | Closed this cycle |
| CODE-2 | P2 | `IngestionError` absent from `ingestion/__init__.py` | **Closed** — `IngestionError` defined and exported at package level; verified by ARCH_REPORT 2026-04-10 | Closed this cycle |
| CODE-3 | P2 | `AnchorError` and `PartitionError` absent from `analysis/__init__.py` | **Closed** — both exported at package level; verified by ARCH_REPORT 2026-04-10 | Closed this cycle |
| CODE-6 | P2 | `tracing.py::get_logger` missing inline comment marking sole permitted call site | **Closed** — inline comment present at `tracing.py:28`; verified by ARCH_REPORT 2026-04-10 | Closed this cycle |
| CODE-4 → CODE-16 | P3 | `GITHUB_TOKEN` absent from `config.py` | Open — renumbered CODE-16; age 2/3; age cap approaching; must fix before T16 | Renumbered; age incremented |
| CODE-5 → CODE-17 | P3 | Python version inconsistency in `pyproject.toml` | Open — renumbered CODE-17; age 2/3; age cap approaching; must fix before Phase 5 | Renumbered; age incremented |
| CODE-7 | P2 | `analyze` stub lacks `@click.option` decorators for T17 flags | Watch — deferred to T17; no change | No change |
| F-01 | INFO | T10/T11 dependency on `CommitRecord.file_paths` | **Closed** — `file_paths` confirmed present in T04 implementation; CODEX_PROMPT F-05 closed 2026-04-10 | Already closed |
| F-04 | INFO | T02/T03 listed as "pending" in Completed Tasks | **Closed (cosmetic)** — no code action required; updated in CODEX_PROMPT | Closed cosmetically |

---

## Stop-Ship Decision

**No** — Zero P0 or P1 findings. Phase 3 (T08: Commit Size and Files-Touched Metrics) may proceed after the six P2 Fix Queue items (CODE-8 through CODE-13) are resolved before Phase 3 begins. CODE-14 (missing integration test) must also be addressed in the same window. CODE-16 and CODE-17 must be resolved before T16 and Phase 5 begin respectively; failure to resolve in Cycle 3 triggers automatic escalation to P1.

---
