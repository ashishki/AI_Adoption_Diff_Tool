# CODEX_PROMPT.md

Version: 1.2
Date: 2026-04-10
Phase: 2

<!--
This file is the single source of truth for session state.
Every Codex agent reads this file before starting work.
Every Codex agent updates this file before committing at a phase boundary.
The orchestrator reads this file at the start of every session.

Never delete history from this file. Append; do not replace.
-->

---

## Current State

- **Phase:** 2
- **Baseline:** 36 passing tests
- **Ruff:** configured (ruff check passes)
- **Last CI run:** not yet configured
- **Last updated:** 2026-04-10
- **Session tokens (approx):** not yet tracked
- **Cumulative phase tokens (approx):** not yet tracked

---

## Next Task

**T09: Churn and Rework Metrics**

Read T09 in `docs/tasks.md` for the full specification, acceptance criteria, and file list.

---

## Fix Queue

empty (CODE-8..13 resolved 2026-04-10, commit 3fd42b1; CODE-10 deferred — trace_id UUID threaded at T17/cli.py)

─── Pre-T16/Pre-Phase-5 Fix Queue (age cap approaching — escalates to P1 at Cycle 3) ─────

🟡 CODE-16 [P3, age 2/3] — GITHUB_TOKEN absent from config.py — resolve before T16
  File: ai_adoption_diff/shared/config.py · Change: add `github_token: str | None = Field(default_factory=lambda: os.getenv("GITHUB_TOKEN"))` to `Config`; ensure field value is never passed to any logger · Test: unit test asserts `Config().github_token` reads from env and is absent from all log output

🟡 CODE-17 [P3, age 2/3] — Python version inconsistency in pyproject.toml — resolve before Phase 5
  File: pyproject.toml:10,29 · Change: set `requires-python = ">=3.11"` to align with ruff `target-version = "py311"` and ARCHITECTURE.md · Test: `pip install -e .` succeeds on Python 3.11; ruff check passes

---

## Open Findings

Baseline: 36 passing tests (post-T08, 2026-04-10)
Next task: T09 — Churn and Rework Metrics

| ID | Sev | Description | Files | Status |
|----|-----|-------------|-------|--------|
| CODE-1 | P2 | `get_logger` return type was `FilteringBoundLogger`; must be `BoundLogger` | `ai_adoption_diff/shared/tracing.py:25` | **Closed** — resolved in T04–T07; verified 2026-04-10 |
| CODE-2 | P2 | `IngestionError` absent from `ingestion/__init__.py` | `ai_adoption_diff/ingestion/__init__.py` | **Closed** — `IngestionError` exported at package level; verified 2026-04-10 |
| CODE-3 | P2 | `AnchorError` and `PartitionError` absent from `analysis/__init__.py` | `ai_adoption_diff/analysis/__init__.py` | **Closed** — both exported at package level; verified 2026-04-10 |
| CODE-6 | P2 | `tracing.py::get_logger` missing inline comment for sole permitted call site | `ai_adoption_diff/shared/tracing.py:28` | **Closed** — inline comment present; verified 2026-04-10 |
| CODE-7 | P2 | `analyze` stub lacks `@click.option` for T17 flags | `ai_adoption_diff/cli.py:17-19` | Watch — deferred to T17 |
| CODE-8 | P2 | Git subprocess calls logged at INFO; spec F1 AC-5 requires DEBUG | `ai_adoption_diff/ingestion/git_reader.py:47,56` | Open — fix before Phase 3 |
| CODE-9 | P2 | `operation_name` is `"git_reader.subprocess"` not spec-required `"git_log"` | `ai_adoption_diff/ingestion/git_reader.py:34` | Open — fix before Phase 3 |
| CODE-10 | P2 | `trace_id` bound to `str(repo_path)` instead of pipeline UUID | `ai_adoption_diff/ingestion/git_reader.py:35` | Open — fix before Phase 3 |
| CODE-11 | P2 | `partition()` does not raise `PartitionError` on empty after-window (spec F4 AC-4) | `ai_adoption_diff/analysis/partitioner.py:26-28` | Open — fix before Phase 3 |
| CODE-12 | P2 | `heuristic.py` missing "median commit size change" signal (spec F3 AC-2) | `ai_adoption_diff/analysis/heuristic.py:131-133` | Open — fix before Phase 3 |
| CODE-13 | P2 | `analysis/` modules import `CommitRecord` from sub-module, bypassing package boundary | `anchor.py:9`, `heuristic.py:10`, `partitioner.py:7` | Open — fix before Phase 3 |
| CODE-14 | P2 | Integration test suite missing invalid-path error propagation test | `tests/integration/test_git_reader.py` | Open — fix before Phase 3 |
| CODE-15 | P3 | `tmp_git_repo` fixture: 5 commits / 5 days; T17 needs ≥20 / ≥6 months | `tests/conftest.py:31-37` | Open — fix before T17 |
| CODE-16 | P3 | `GITHUB_TOKEN` absent from `config.py`; **age cap approaching (2/3)** | `ai_adoption_diff/shared/config.py` | Open — fix before T16; escalates to P1 at Cycle 3 |
| CODE-17 | P3 | `requires-python = ">=3.10"` vs ruff `target-version = "py311"`; **age cap approaching (2/3)** | `pyproject.toml:10,29` | Open — fix before Phase 5; escalates to P1 at Cycle 3 |
| F-01 | INFO | T10/T11 dependency on `CommitRecord.file_paths` | `ai_adoption_diff/ingestion/git_reader.py` | **Closed** — `file_paths` confirmed present; 2026-04-10 |
| F-02 | INFO | T16 token-not-logged and cleanup-on-error are mandatory evidence tests | `ai_adoption_diff/ingestion/github.py` | Deferred — Phase 5 |
| F-03 | INFO | `docs/prompts/ORCHESTRATOR.md` has unresolved `{{PROJECT_ROOT}}` and `{{CODEX_COMMAND}}` placeholders | `docs/prompts/ORCHESTRATOR.md` | Open — manual action required |
| F-04 | INFO | T02 and T03 listed as "pending" in Completed Tasks | `docs/CODEX_PROMPT.md` | **Closed (cosmetic)** — no functional impact; 2026-04-10 |
| F-05 | INFO | T04 provides `CommitRecord.file_paths`; T10/T11 dependency satisfied | `ai_adoption_diff/ingestion/git_reader.py` | **Closed** — 2026-04-10 |

---

## Profile State: RAG

- RAG Status: OFF
- Active corpora: n/a
- Retrieval baseline: n/a
- Open retrieval findings: none
- Index schema version: n/a
- Pending reindex actions: none
- Retrieval-related next tasks: none
- Retrieval-driven tasks: none

---

## Tool-Use State

- Tool-Use Profile: OFF
- Registered tool schemas: n/a
- Unsafe-action guardrails: n/a
- Open tool findings: none

---

## Agentic State

- Agentic Profile: OFF
- Active agent roles: n/a
- Loop termination contract version: n/a
- Cross-iteration state mechanism: n/a
- Open agent findings: none

---

## Planning State

- Planning Profile: OFF
- Plan schema version: n/a
- Plan validation method: n/a
- Open plan findings: none

---

## Compliance State

- Compliance Status: OFF
- Active frameworks: n/a
- Controls implemented: n/a
- Controls partial: n/a
- Controls not started: n/a
- Evidence artifact: n/a
- Open compliance findings: none

---

## NFR Baseline

- API p99 latency: not applicable (CLI tool)
- Error rate: not yet measured
- Throughput: not applicable (CLI tool)
- Last measured: —
- NFR regression open: No

---

## Evaluation State

### Last Evaluation

- Profile: n/a
- Task: n/a
- Date: n/a
- Eval Source: n/a
- Metric(s): n/a
- Score: n/a
- Baseline: n/a
- Delta: n/a
- Regression: n/a

### Open Evaluation Issues

none

### Evaluation History

| Date | Task | Profile | Key metric | Score | Baseline | Delta | Regression? |
|------|------|---------|------------|-------|----------|-------|-------------|

---

## Completed Tasks

- **T01 — Project Skeleton** (2026-04-09): Package structure, CLI stub, shared config and tracing modules. 4 tests passing. Commit: d08cc4b.
- **T02 — CI Setup** (2026-04-09): GitHub Actions workflow, Ruff configuration, and CI validation tests. 8 tests passing. Commit: pending.
- **T03 — Smoke Tests** (2026-04-09): Added smoke coverage for package importability, shared tracing/config surfaces, and CLI help output. 12 tests passing. Commit: pending.
- **T04 — Git Log Ingestion** (2026-04-10): Added `CommitRecord`, git log parsing, deterministic temp git repo fixture, and ingestion coverage for commit counts, empty repos, invalid paths, and hashed author emails. 17 tests passing. Commit: pending.
- **T05 — Adoption Anchor** (2026-04-10): Added `AnalysisWindow`, manual adoption-date validation, inclusive before/after window computation, and anchor coverage for bounds, invalid dates, empty windows, and custom window sizes. 21 tests passing. Commit: pending.
- **T06 — Heuristic Adoption Window Inference** (2026-04-10): Added heuristic AI-config and commit-frequency signal detection, median-date inference, and confidence scoring with dedicated unit coverage. 26 tests passing. Commit: pending.
- **T07 — Window Partitioner** (2026-04-10): Added deterministic before/after commit partitioning against `AnalysisWindow`, exclusion of out-of-window commits, adoption-date routing to `after`, and dedicated unit coverage for empty-before validation and input immutability. 31 tests passing. Commit: pending.
- **T08 — Commit Size and Files-Touched Metrics** (2026-04-10): Added deterministic commit-size and files-touched summary metrics with manual p90 interpolation and dedicated unit coverage for fixture arithmetic, empty input, determinism, and known percentile behavior. 36 tests passing. Commit: pending.

---

## Phase History

<!--
Append phase summaries here at each phase gate.
-->

---

## Compaction Protocol

Compact when EITHER condition is true:
- `## Completed Tasks` contains more than 20 entries, OR
- `## Phase History` contains more than 5 phase summaries

---

## Instructions for Codex

Read these instructions every time you pick up a task. Do not skip steps.

### Pre-Task Protocol (mandatory — do not skip)

1. **Read `docs/IMPLEMENTATION_CONTRACT.md`** — before anything else. Know the rules before touching code.
2. **Read the full task in `docs/tasks.md`** — including all acceptance criteria, file lists, and notes.
3. **Read all Depends-On tasks** — understand the interface contracts your task must satisfy.
4. **Run `pytest -q`** — capture the current baseline. Record: `N passing, M failed`. If M > 0, stop and report: you cannot add failures to an already-failing baseline.
5. **Run `ruff check`** — must exit 0. If not, fix ruff issues first. Commit the ruff fix separately with message `chore(lint): resolve ruff issues`. Then re-run the pre-task protocol.
6. **Write tests before or alongside implementation.** Every acceptance criterion has exactly one corresponding test (or more, never zero).

### During Implementation

- Work on one task at a time.
- Read only the files you need. Use `grep` to find relevant sections first.
- Do not modify files outside the task's scope without documenting why.
- If you discover an interface mismatch or missing dependency, stop and report it. Do not silently patch adjacent tasks.

### Post-Task Protocol

1. Run `pytest -q` — baseline must be ≥ pre-task baseline. If lower, something broke; fix it before committing.
2. Run `ruff check ai_adoption_diff/ tests/` — must exit 0.
3. Run `ruff format --check ai_adoption_diff/ tests/` — must exit 0.
4. Update this file (`docs/CODEX_PROMPT.md`):
   - New baseline (number of passing tests)
   - Move this task to "Completed Tasks"
   - Set "Next Task" to the next task
   - Add any new open findings discovered during this task
5. Commit with format: `type(scope): description` — one logical change per commit.
6. If the task produced multiple logical changes (e.g., ingestion module + tests), use multiple commits.

### Return Format

When done, return exactly:

```
IMPLEMENTATION_RESULT: DONE
New baseline: {N} passing tests
Commits: {list of commit hashes and messages}
Notes: {anything the orchestrator should know — surprises, deviations, decisions made}
```

When blocked, return exactly:

```
IMPLEMENTATION_RESULT: BLOCKED
Blocker: {exact description of what is blocking progress}
Type: dependency | interface_mismatch | environment | ambiguity
Recommended action: {what the orchestrator or human should do}
Progress made: {what was completed before hitting the blocker}
```

### Commit Message Format

```
type(scope): short description (imperative mood, ≤72 chars)

Optional body: explain why, not what. The diff shows the what.
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `security`

Do not include:
- `Co-Authored-By` lines
- Credentials or secrets
- TODO comments without a task reference (`# TODO: see T{NN}`)
- Commented-out code
- `print()` debugging statements
