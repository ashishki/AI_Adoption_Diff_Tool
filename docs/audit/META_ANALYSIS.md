---
# META_ANALYSIS — Cycle 2
_Date: 2026-04-10 · Type: full_

## Project State

Phase 2 (T04–T07) complete. Next: T08 — Commit Size and Files-Touched Metrics.
Baseline: 31 pass, 0 skip. Previous cycle (Cycle 1): 12 pass — delta +19 tests across T04–T07.

## Open Findings

| ID | Sev | Description | Files | Status |
|----|-----|-------------|-------|--------|
| CODE-1 | P2 | `get_logger` return type is `FilteringBoundLogger` (internal concrete type); must be `BoundLogger` (public protocol) | `ai_adoption_diff/shared/tracing.py:25` | Open — carried from Cycle 1; required before T04; verify resolution at T08 pre-task |
| CODE-2 | P2 | `IngestionError` absent from `ingestion/__init__.py`; layered import contract broken | `ai_adoption_diff/ingestion/__init__.py` | Open — carried from Cycle 1; T04 required it; verify resolved by PROMPT_2 inspection |
| CODE-3 | P2 | `AnchorError` and `PartitionError` absent from `analysis/__init__.py`; layered import contract broken | `ai_adoption_diff/analysis/__init__.py` | Open — carried from Cycle 1; T05/T07 required them; verify resolved by PROMPT_2 inspection |
| CODE-4 | P3 | `GITHUB_TOKEN` field absent from `shared/config.py`; must be loaded exclusively there per T16 spec | `ai_adoption_diff/shared/config.py` | Open — deferred pre-stub to T16 |
| CODE-5 | P3 | `pyproject.toml` `requires-python = ">=3.10"` but ruff `target-version = "py311"`; inconsistent | `pyproject.toml` | Open — align to `>=3.11` before Phase 5 |
| CODE-6 | P2 | `tracing.py::get_logger` calls `structlog.get_logger()` without a comment marking it as the sole permitted call site | `ai_adoption_diff/shared/tracing.py:28` | Open — add inline comment; no structural change required |
| CODE-7 | P2 | `analyze` stub lacks `@click.option` for T17 flags (`--repo`, `--date`, `--tool`, `--format`) | `ai_adoption_diff/cli.py` | Watch — deferred to T17 |
| F-01 | INFO | T10/T11 depend on `CommitRecord.file_paths` from T04 | `ai_adoption_diff/ingestion/git_reader.py` | Resolved — CODEX_PROMPT F-05 confirms file_paths present (closed 2026-04-10) |
| F-02 | INFO | T16 token-not-logged and cleanup-on-error are mandatory evidence tests | `ai_adoption_diff/ingestion/github.py` | Deferred — Phase 5 |
| F-03 | INFO | `docs/prompts/ORCHESTRATOR.md` has unresolved `{{PROJECT_ROOT}}` and `{{CODEX_COMMAND}}` placeholders | `docs/prompts/ORCHESTRATOR.md` | Open — manual action required |
| F-04 | INFO | T02 and T03 commits listed as "pending" in CODEX_PROMPT.md despite being complete | `docs/CODEX_PROMPT.md` | Open — cosmetic; recommend closing in REVIEW_REPORT without action |

## PROMPT_1 Scope (architecture)

- `ai_adoption_diff/ingestion/git_reader.py`: new T04 — `CommitRecord` frozen dataclass, `read_commits()` with SHA-256 email hashing and subprocess `git log --numstat`; verify `IngestionError` placement relative to `__init__.py` contract
- `ai_adoption_diff/analysis/anchor.py`: new T05 — `AnalysisWindow` frozen dataclass, `compute_window()` with inclusive before/after bounds; verify `AnchorError` placement and window boundary logic
- `ai_adoption_diff/analysis/heuristic.py`: new T06 — `HeuristicResult` and `Signal` frozen dataclasses; AI-config file signal detection; commit-frequency spike detection; median date inference; confidence score range `[0.0, 1.0]`
- `ai_adoption_diff/analysis/partitioner.py`: new T07 — `partition()` determinism and immutability guarantees; `PartitionError` placement; adoption-date boundary routing (on-date commits go to `after`)
- `ai_adoption_diff/ingestion/__init__.py`: verify `IngestionError` exported at package level (CODE-2 resolution check)
- `ai_adoption_diff/analysis/__init__.py`: verify `AnchorError` and `PartitionError` exported at package level (CODE-3 resolution check)
- `ai_adoption_diff/metrics/__init__.py`: currently empty — confirm interface is ready to receive T08–T11 metric modules

## PROMPT_2 Scope (code, priority order)

1. `ai_adoption_diff/ingestion/git_reader.py` (new — T04; security-critical: email hashing, subprocess invocation)
2. `ai_adoption_diff/ingestion/__init__.py` (new content expected — CODE-2 resolution check: `IngestionError` export)
3. `ai_adoption_diff/analysis/__init__.py` (new content expected — CODE-3 resolution check: `AnchorError`, `PartitionError` exports)
4. `ai_adoption_diff/analysis/anchor.py` (new — T05; boundary correctness, error contract)
5. `ai_adoption_diff/analysis/heuristic.py` (new — T06; signal detection correctness, median logic, confidence score range enforcement)
6. `ai_adoption_diff/analysis/partitioner.py` (new — T07; immutability contract, adoption-date boundary routing)
7. `ai_adoption_diff/shared/tracing.py` (regression check — CODE-1, CODE-6 still open)
8. `ai_adoption_diff/shared/config.py` (regression check — CODE-4 pre-stub status)
9. `pyproject.toml` (regression check — CODE-5 python version inconsistency)
10. `tests/integration/test_git_reader.py` (new — verify email hashing test adequacy and tmp_git_repo fixture robustness for T17 extension)
11. `tests/unit/test_heuristic.py` (new — verify median and spike signal edge cases)
12. `tests/unit/test_partitioner.py` (new — verify immutability and boundary tests)

## Cycle Type

Full — Phase 2 (T04–T07) is complete with all 4 tasks implemented and 31 tests passing (+19 from Cycle 1 baseline of 12). This constitutes a phase-gate boundary review before Phase 3 metrics work begins.

## Notes for PROMPT_3

- Priority consolidation focus: verify CODE-1, CODE-2, CODE-3 resolution status. CODEX_PROMPT.md still lists them as "Open" but T04–T07 required these interfaces — they may have been implicitly resolved without the Open Findings table being updated. PROMPT_2 findings will clarify.
- Security emphasis: `git_reader.py` subprocess call surface and author email hashing correctness are the highest-risk new code this cycle. PROMPT_3 must confirm no raw email leaks into any data structure or log output.
- The metrics module (`ai_adoption_diff/metrics/`) is empty — T08 is the immediate next task. PROMPT_3 should note if any preparatory stubs or shared interfaces are needed before T08 can begin cleanly.
- `CommitRecord.file_paths` availability is confirmed resolved (F-05/F-01); close F-01 in REVIEW_REPORT.
- F-04 (pending commit labels for T02/T03) remains cosmetic; recommend closing in REVIEW_REPORT without requiring any code action.
- The `tmp_git_repo` fixture in `tests/conftest.py` currently provides 5 commits; T17 notes require at least 20 commits spanning 6 months. Flag this as a pre-T17 extension requirement if PROMPT_2 confirms the current fixture count.

---
