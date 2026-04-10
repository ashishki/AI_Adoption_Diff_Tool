---
# ARCH_REPORT — Cycle 2
_Date: 2026-04-10_

## Component Verdicts

| Component | Verdict | Note |
|-----------|---------|------|
| `ingestion/git_reader.py` | DRIFT | Subprocess logged at INFO not DEBUG (spec F1 AC5); `operation_name` value is `"git_reader.subprocess"` not `"git_log"` (spec F1 AC5); `trace_id` bound to `str(repo_path)` not a pipeline-level UUID |
| `ingestion/__init__.py` | PASS | `IngestionError` defined and exported; CODE-2 resolved |
| `analysis/anchor.py` | DRIFT | Imports `CommitRecord` directly from `ai_adoption_diff.ingestion.git_reader` sub-module instead of `ai_adoption_diff.ingestion` package boundary |
| `analysis/heuristic.py` | VIOLATION | Missing "sudden change in median commit size" signal required by spec F3 AC2; imports `CommitRecord` from sub-module not package |
| `analysis/partitioner.py` | VIOLATION | Does not raise `PartitionError` when `after_commits` is empty — spec F4 AC4 is unimplemented; imports from sub-modules directly |
| `analysis/__init__.py` | PASS | `AnchorError` and `PartitionError` defined and exported; CODE-3 resolved |
| `metrics/__init__.py` | PASS | Empty stub; ready to receive T08–T11 modules; no premature content |
| `shared/tracing.py` | PASS | CODE-1 resolved: return type is now `BoundLogger`; inline comment marking sole permitted call site present at line 28 |
| `shared/config.py` | DRIFT | `GITHUB_TOKEN` field absent (CODE-4, deferred to T16); PS-4 cannot be fully verified |
| `cli.py` | DRIFT | `analyze` stub has no `@click.option` decorators (CODE-7, deferred to T17); no pipeline-level `trace_id` generated |

## Contract Compliance

| Rule | Verdict | Note |
|------|---------|------|
| SQL Safety | PASS | No database or SQL in scope; rule noted N/A for v1 |
| Authorization (GITHUB_TOKEN pre-call check) | N/A | GitHub module not in cycle scope |
| PII Policy — no raw email in logs or memory | PASS | Email hashed via SHA-256 in `git_reader.py:127` immediately on parse; no raw email in any log field or data structure |
| Credentials and Secrets | PASS | No secrets in source; no `GITHUB_TOKEN` present (CODE-4 deferred) |
| Shared Tracing Module (sole `get_logger` call site) | PASS | CODE-1 resolved; `tracing.py:28` has required inline comment; no inline `structlog.get_logger()` calls in other modules |
| CI Gate | N/A | CI execution state not inspected in this review |
| OBS-1 — Instrumentation (external calls logged with `operation_name` + `trace_id`) | DRIFT | `_run_git` binds both fields but uses wrong `operation_name` value and a path string as `trace_id` instead of a pipeline UUID |
| OBS-2 — Metrics (log `success`, `duration_ms`, `operation_name` at completion) | PASS | Both success and failure paths emit `success`, `duration_ms`, `operation_name` |
| OBS-3 — Health check (`ai-diff --version` exits 0) | PASS | `cli.py` wires `click.version_option` with version sourced from `__version__` |
| PS-1 — Read-only git access | PASS | Only `rev-parse` and `log` commands used; no write operations |
| PS-2 — Subprocess list form | PASS | `_run_git` uses `["git", "-C", str(repo_path), *args]`; `shell=True` absent |
| PS-3 — Determinism (no datetime.now/random inside metric/analysis functions) | PASS | No `datetime.now()` or `random` calls in any scoped file; `perf_counter()` in `_run_git` is for instrumentation only, not metric output |
| PS-4 — GITHUB_TOKEN handling | DRIFT | `GITHUB_TOKEN` absent from `config.py` (CODE-4, deferred to T16); risk of incorrect loading when T16 is implemented |
| PS-5 — Error exposure (no bare tracebacks to user) | PASS | `IngestionError` raised with message strings; no bare `except` without logging found |
| PS-6 — Caveat requirement in reports | N/A | Report modules not yet implemented |

## ADR Compliance

| ADR | Verdict | Note |
|-----|---------|------|
| (no ADRs filed) | N/A | `docs/adr/` directory is empty. No ADR-gated decisions are active. No violations possible. |

## Architecture Findings

### ARCH-1 [P1] — `partition()` Does Not Raise on Empty After-Window

Symptom: `partition()` raises `PartitionError` only when `before` is empty. Spec F4 AC4 and the IMPLEMENTATION_CONTRACT require the same guard for `after`.

Evidence: `ai_adoption_diff/analysis/partitioner.py:26-28` — only `if not before: raise PartitionError("before window is empty")` is present; no after-window guard exists.

Root cause: Incomplete implementation of spec F4 AC4: "Given a window where `after_commits` is empty, the partitioner raises `PartitionError('after window is empty — no commits after adoption date')`."

Impact: A partition producing an empty after-window silently returns `(before, [])`. Every downstream metric will return `MetricResult(value=None, sample_size=0)` for the after window without any error, producing a report that appears valid but carries no after-window data and no user warning.

Fix: Add `if not after: raise PartitionError("after window is empty — no commits after adoption date")` immediately after the `if not before` guard in `partition()`. Add a corresponding test.

---

### ARCH-2 [P1] — `heuristic.py` Missing "Median Commit Size Change" Signal

Symptom: `infer_adoption()` detects only two signal types: `ai_config_file` and `commit_frequency_spike`. Spec F3 AC2 mandates a third: "sudden change in median commit size."

Evidence: `ai_adoption_diff/analysis/heuristic.py:129-140` — `signals` list assembled from `_detect_ai_config_signals()` and `_detect_commit_frequency_spike()` only; no median-commit-size change detector exists anywhere in the file.

Root cause: T06 implementation omitted the median commit size change signal required by spec F3 AC2.

Impact: Heuristic inference is weaker than specified. Repos where AI adoption changed commit size but not frequency will produce zero signals and trigger the "No adoption signals detected" exit path, giving users a false negative.

Fix: Implement `_detect_median_commit_size_change()` that computes rolling median `insertions + deletions` and emits `Signal(signal_name="median_commit_size_change", ...)` when the change exceeds a threshold. Add it to the `signals` aggregation in `infer_adoption()`. Add corresponding tests.

---

### ARCH-3 [P2] — Subprocess Logging Level Is INFO Instead of DEBUG

Symptom: `_run_git()` calls `logger.info(...)` for both success and failure paths. Spec F1 AC5 requires DEBUG level: "All `git` subprocess calls are logged at DEBUG level."

Evidence: `ai_adoption_diff/ingestion/git_reader.py:47` — `logger.info("git subprocess failed", ...)` and `ai_adoption_diff/ingestion/git_reader.py:56` — `logger.info("git subprocess completed", ...)`.

Root cause: Implementation chose INFO; spec mandates DEBUG.

Impact: With default `AI_DIFF_LOG_LEVEL=INFO`, every git invocation produces a visible log line. For large histories this is noisy and violates the spec contract.

Fix: Change both `logger.info(...)` calls in `_run_git()` to `logger.debug(...)`.

---

### ARCH-4 [P2] — `operation_name` Value Mismatch with Spec

Symptom: `_run_git()` binds `operation_name="git_reader.subprocess"`. Spec F1 AC5 specifies the value must be `"git_log"`.

Evidence: `ai_adoption_diff/ingestion/git_reader.py:34`.

Root cause: Implementation chose a descriptive but non-conformant name.

Impact: Any log query filtering by `operation_name="git_log"` (as specified) will miss these events. OBS-1 compliance is nominally broken.

Fix: Change the constant on line 34 from `"git_reader.subprocess"` to `"git_log"`.

---

### ARCH-5 [P2] — `trace_id` Bound to `str(repo_path)` Instead of a Pipeline-Level UUID

Symptom: `_run_git()` binds `trace_id=str(repo_path)`. The architecture and contract specify `trace_id` as a per-pipeline-run identifier correlating all log events within a single CLI invocation.

Evidence: `ai_adoption_diff/ingestion/git_reader.py:35`.

Root cause: No pipeline-level `trace_id` is generated in `cli.py` and propagated down. `git_reader.py` substitutes `repo_path` as a workaround.

Impact: Log correlation across pipeline stages is broken. Events from `anchor.py`, `partitioner.py`, and future metric modules cannot be joined by `trace_id`. Multiple sequential runs against different repos produce changing `trace_id` values mid-run.

Fix: Generate a UUID4 string at the start of each `analyze` invocation in `cli.py` and pass it into the pipeline. `_run_git()` should accept `trace_id` as a parameter or read it from a structlog context variable bound at CLI entry.

---

### ARCH-6 [P2] — Cross-Layer Direct Sub-Module Imports in `analysis/`

Symptom: `anchor.py`, `heuristic.py`, and `partitioner.py` all import `CommitRecord` directly from `ai_adoption_diff.ingestion.git_reader` (implementation sub-module) instead of `ai_adoption_diff.ingestion` (package boundary).

Evidence:
- `ai_adoption_diff/analysis/anchor.py:9`: `from ai_adoption_diff.ingestion.git_reader import CommitRecord`
- `ai_adoption_diff/analysis/heuristic.py:10`: `from ai_adoption_diff.ingestion.git_reader import CommitRecord`
- `ai_adoption_diff/analysis/partitioner.py:7`: `from ai_adoption_diff.ingestion.git_reader import CommitRecord`

Root cause: `CommitRecord` is not re-exported from `ai_adoption_diff/ingestion/__init__.py`, so consumers reach through to the implementation module.

Impact: If `CommitRecord` moves or the ingestion module is split, all three analysis files break simultaneously. The ingestion package boundary is bypassed, violating the layered import contract that callers import from the package `__init__`, not from internal modules.

Fix: Add `from ai_adoption_diff.ingestion.git_reader import CommitRecord` to `ai_adoption_diff/ingestion/__init__.py` as a re-export. Update all three analysis files to `from ai_adoption_diff.ingestion import CommitRecord`. This mirrors the existing `IngestionError` pattern.

---

### ARCH-7 [P3] — CODE-4 Still Open: `GITHUB_TOKEN` Absent from `config.py`

Symptom: `shared/config.py` `Config` model has `log_level` and `output_dir` only. No `github_token` field.

Evidence: `ai_adoption_diff/shared/config.py:11-17`.

Root cause: Deferred to T16 per META_ANALYSIS. Carried from Cycle 1.

Impact: PS-4 cannot be verified as satisfied. Risk: when T16 is implemented, the token may be loaded outside `config.py`, violating the single-load-site contract.

Fix: Add `github_token: str | None = Field(default_factory=lambda: os.getenv("GITHUB_TOKEN"))` to `Config` before T16 begins. Ensure the field value is never passed to any logger.

---

### ARCH-8 [P3] — CODE-5 Still Open: Python Version Inconsistency

Symptom: `pyproject.toml` declares `requires-python = ">=3.10"` but ruff uses `target-version = "py311"`. Architecture specifies Python 3.11.

Evidence: `pyproject.toml:10` and `pyproject.toml:29`.

Root cause: Carried from Cycle 1; not resolved during Phase 2.

Impact: Users on Python 3.10 can install the package, but ruff permits 3.11-only syntax that will fail on such installations. False compatibility signal.

Fix: Change `requires-python` to `">=3.11"` to align with ARCHITECTURE.md tech stack choice and ruff target.

## Right-Sizing / Runtime Checks

| Check | Verdict | Note |
|-------|---------|------|
| Solution shape still Deterministic subsystem | PASS | No LLM calls, no external model inference, no agent loops introduced in T04–T07 |
| Metric functions are pure/deterministic | PASS | No metric functions implemented yet; all analysis code uses standard library, date arithmetic, sorted inputs, and statistics — no `datetime.now()`, `random`, or external state reads |
| T0 runtime preserved (no DB/worker/mutable state) | PASS | No database, no background workers, no persistent runtime state; outputs are local files only |
| Read-only git enforcement holds | PASS | `_run_git()` called only with `rev-parse` and `log`; no write-capable git commands present |
| Subprocess list-form used everywhere | PASS | `subprocess.run(["git", "-C", str(repo_path), *args], ...)` — list form; `shell=True` absent |
| No LLM calls without ADR | CLEAN | No LLM calls, tool schemas, or agent loops in any scoped file; all Capability Profiles remain OFF |

## Doc Patches Needed

| File | Section | Change |
|------|---------|--------|
| `docs/ARCHITECTURE.md` | Component Table | Add note that `CommitRecord` must be re-exported from `ingestion/__init__.py` to enforce the package boundary (prerequisite for closing ARCH-6) |
| `docs/ARCHITECTURE.md` | Observability Invariants | Add: "All git subprocess calls logged at DEBUG level with `operation_name='git_log'`" (currently implied by spec F1 AC5 but not stated in ARCHITECTURE.md) |
| `docs/adr/` | (new file needed) | No ADRs have been filed. Any approved deviation from the IMPLEMENTATION_CONTRACT (e.g., deferred `CommitRecord` re-export) must be recorded as `ADR-001` before it can be accepted as a formal exception rather than an open finding. |
| `docs/CODEX_PROMPT.md` | Open findings table | Close CODE-1, CODE-2, CODE-3 as resolved. Update CODE-6 status to resolved (inline comment now present). Keep CODE-4, CODE-5, CODE-7 as open. |

---
