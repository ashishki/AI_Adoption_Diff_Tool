# CODEX_PROMPT.md

Version: 1.5
Date: 2026-04-10
Phase: COMPLETE

<!--
This file is the single source of truth for session state.
Every Codex agent reads this file before starting work.
Every Codex agent updates this file before committing at a phase boundary.
The orchestrator reads this file at the start of every session.

Never delete history from this file. Append; do not replace.
-->

---

## Current State

- **Phase:** COMPLETE (all T01–T17 done)
- **Baseline:** 78 passing tests
- **Ruff:** configured (ruff check passes)
- **Last CI run:** not yet configured
- **Last updated:** 2026-04-10
- **Session tokens (approx):** not yet tracked
- **Cumulative phase tokens (approx):** not yet tracked

---

## Next Task

**ALL TASKS COMPLETE** — T01 through T17 implemented and reviewed. 78/78 tests passing.

---

## Fix Queue

empty (CODE-8..13 resolved 2026-04-10, commit 3fd42b1; CODE-10 deferred — trace_id UUID threaded at T17/cli.py; CODE-16/17 resolved 2026-04-10 commits ac0b90a/fc90e55)

---

## Open Findings

Baseline: 51 passing tests (post-Phase-3 deep review, 2026-04-10)
Next task: T12 — Report Model

| ID | Sev | Description | Files | Status |
|----|-----|-------------|-------|--------|
- **T12 — Report Model** (2026-04-10): Added Pydantic v2 AnalysisReport model aggregating all metric results, window metadata, and confidence data. 55 tests passing. Commits: 20faa6a, 3462f93.
- **T13 — Confidence Scorer** (2026-04-10): Added confidence scorer with score/level/caveats computation, penalty model, and 5-test coverage. 60 tests passing. Commits: 27ec15d, 8e8f20f.
- **T14 — JSON Export** (2026-04-10): Added JSON exporter writing AnalysisReport to output_dir/report.json with auto-dir creation and overwrite. 64 tests passing. Commits: 1c59e47, 4343b98.
- **T15 — Markdown and HTML Report Renderer** (2026-04-10): Added Jinja2-based renderer with 9-metric comparison table, confidence section, footer caveat. 68 tests passing. Commits: 41ca6c9, 6718cc8.

| CODE-7 | P2 | `analyze` stub missing T17 click options | `ai_adoption_diff/cli.py` | **Closed** — T17 commit d5c3206 |
| CODE-10 | P2 | `trace_id` not UUID, uses str(repo_path) | `ai_adoption_diff/ingestion/git_reader.py:35` | Open — deferred, accepted (final phase) |
| CODE-12 | P2 | `heuristic.py` missing median-commit-size signal | `ai_adoption_diff/analysis/heuristic.py` | Open — tracked, accepted (final phase) |
| CODE-15 | P3 | `tmp_git_repo` fixture too small for T17 | `tests/conftest.py` | **Closed** — large_git_repo added, commit 357fff8 |
| CODE-16 | P3 | `GITHUB_TOKEN` absent from `config.py` | `ai_adoption_diff/shared/config.py` | **Closed** — commit ac0b90a; 2026-04-10 |
| CODE-17 | P3 | `requires-python = ">=3.10"` mismatch | `pyproject.toml:10,29` | **Closed** — commit fc90e55; 2026-04-10 |
| CODE-18 | P3 | hot_files bare `None` vs wrapped dataclass | `ai_adoption_diff/metrics/hot_files.py:40,59` | Open — accepted (final phase, no escalation) |
| F-02 | INFO | T16 evidence tests | `ai_adoption_diff/ingestion/github.py` | **Closed** — test_token_not_logged, test_cleanup_on_error |
| F-03 | INFO | ORCHESTRATOR.md unresolved placeholders | `docs/prompts/ORCHESTRATOR.md` | Open — manual action only |

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
- **T08 — Commit Size and Files-Touched Metrics** (2026-04-10): Added deterministic commit-size and files-touched summary metrics with manual p90 interpolation and dedicated unit coverage for fixture arithmetic, empty input, determinism, and known percentile behavior. 36 tests passing. Commits: 4af2283, ee4e798.
- **T09 — Churn and Rework Metrics** (2026-04-10): Added churn rate (deletions/total lines) and revert frequency (regex match fraction) metrics with frozen dataclass results and 5-test unit coverage for known values, edge cases, and regex semantics. 41 tests passing. Commits: b77c174, b127d64.
- **T10 — Test-to-Code Ratio and Boilerplate Metrics** (2026-04-10): Added test-to-code ratio (path-based heuristic) and boilerplate signal (init/conftest/empty-commit fraction) with frozen dataclass results and 4-test unit coverage. 45 tests passing. Commits: 24c041b, 1d43596.
- **T11 — Hot-File Instability and Directory Concentration Metrics** (2026-04-10): Added hot-file count (strict >threshold fraction) and directory concentration (top-3 dirs by line changes) with frozen dataclass results and 4-test unit coverage. 49 tests passing. Commits: 2a87f1b, 854f211.
- **T12 — Report Model** (2026-04-10): Added Pydantic v2 AnalysisReport model aggregating all metric results, window metadata, and confidence data. 55 tests passing. Commits: 20faa6a, 3462f93.
- **T13 — Confidence Scorer** (2026-04-10): Added confidence scorer with score/level/caveats computation, penalty model, and 5-test coverage. 60 tests passing. Commits: 27ec15d, 8e8f20f.
- **T14 — JSON Export** (2026-04-10): Added JSON exporter writing AnalysisReport to output_dir/report.json with auto-dir creation and overwrite. 64 tests passing. Commits: 1c59e47, 4343b98.
- **T15 — Markdown and HTML Report Renderer** (2026-04-10): Added Jinja2-based renderer with 9-metric comparison table, confidence section, footer caveat. 68 tests passing. Commits: 41ca6c9, 6718cc8.
- **T16 — GitHub Remote Repository Support** (2026-04-10): Added GitHub URL detection, token validation, git clone via subprocess (no shell=True), 429 retry with exponential backoff, finally-block cleanup. 73 tests passing. Commits: 19cee72, f089431.
- **T17 — CLI End-to-End Integration** (2026-04-10): Wired full pipeline into analyze command with --repo/--date/--tool/--format/--output flags. 5 integration tests using large_git_repo. 78 tests passing. Commits: d5c3206, 31db3b4.

---

## Phase History

<!--
Append phase summaries here at each phase gate.
-->

### Phase 5 — CLI Integration (T16–T17) — 2026-04-10

Tasks: T16 (GitHub remote support), T17 (CLI end-to-end integration).
Baseline: 68 → 78 tests.
Fixes in cycle: CODE-7 (CLI options resolved), CODE-15 (large_git_repo fixture), F-02 (evidence tests).
Remaining open: CODE-10 (trace_id UUID, deferred), CODE-12 (heuristic signal, tracked), CODE-18 (return-type, accepted).
Phase gate: PASS. Project COMPLETE (T01–T17). Archived: docs/archive/PHASE5_REVIEW.md.

### Phase 4 — Reporting (T12–T15) — 2026-04-10

Tasks: T12 (report model), T13 (confidence scorer), T14 (JSON export), T15 (Markdown/HTML renderer).
Baseline: 51 → 68 tests.
Fixes in cycle: none (all P1/P2 from Phase 3 already resolved).
New open findings: none.
Phase gate: PASS. Archived: docs/archive/PHASE4_REVIEW.md.

### Phase 3 — Metrics (T08–T11) — 2026-04-10

Tasks: T08 (commit size/files-touched), T09 (churn/revert), T10 (test ratio/boilerplate), T11 (hot-files/dir concentration).
Baseline: 36 → 51 tests (post CODE-16 fix tests).
Fixes in cycle: CODE-16 (GITHUB_TOKEN, escalated P1), CODE-17 (requires-python mismatch, escalated P1).
New open findings: CODE-18 (P3, return-type inconsistency in hot_files).
Phase gate: PASS. Archived: docs/archive/PHASE3_REVIEW.md.

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
