# CODEX_PROMPT.md

Version: 1.1
Date: 2026-04-10
Phase: 1

<!--
This file is the single source of truth for session state.
Every Codex agent reads this file before starting work.
Every Codex agent updates this file before committing at a phase boundary.
The orchestrator reads this file at the start of every session.

Never delete history from this file. Append; do not replace.
-->

---

## Current State

- **Phase:** 1
- **Baseline:** 31 passing tests
- **Ruff:** configured (ruff check passes)
- **Last CI run:** not yet configured
- **Last updated:** 2026-04-10
- **Session tokens (approx):** not yet tracked
- **Cumulative phase tokens (approx):** not yet tracked

---

## Next Task

**T08: Commit Size and Files-Touched Metrics**

Read T08 in `docs/tasks.md` for the full specification, acceptance criteria, and file list.

---

## Fix Queue

empty (FIX-1..FIX-4 resolved 2026-04-10, commit 9cfc44f)

---

## Open Findings

Baseline: 21 passing tests (Phase 2 ingest gate, 2026-04-10)
Next task: T06 — Heuristic Adoption Window Inference

| ID | Sev | Description | Files | Status |
|----|-----|-------------|-------|--------|
| CODE-1 | P2 | `get_logger` return type is `FilteringBoundLogger` (internal concrete type); must be `BoundLogger` (public protocol) | `ai_adoption_diff/shared/tracing.py:25` | Open — fix before T04 |
| CODE-2 | P2 | `IngestionError` absent from `ingestion/__init__.py`; layered import contract broken for T04 | `ai_adoption_diff/ingestion/__init__.py:1` | Open — fix before T04 |
| CODE-3 | P2 | `AnchorError` and `PartitionError` absent from `analysis/__init__.py`; layered import contract broken for T05/T07 | `ai_adoption_diff/analysis/__init__.py:1` | Open — fix before T05 |
| CODE-4 | P3 | `GITHUB_TOKEN` field absent from `shared/config.py`; PS-4 requires it to be loaded exclusively there | `ai_adoption_diff/shared/config.py:11-17` | Open — pre-stub before T16 |
| CODE-5 | P3 | `pyproject.toml` `requires-python = ">=3.10"` but ruff `target-version = "py311"`; inconsistent | `pyproject.toml:8,29` | Open — align to `>=3.11` |
| CODE-6 | P2 | `tracing.py::get_logger` calls `structlog.get_logger()` without a comment marking it as the sole permitted call site | `ai_adoption_diff/shared/tracing.py:28` | Open — add inline comment |
| CODE-7 | P2 | `analyze` stub lacks `@click.option` for T17 flags; T17 will need additive signature changes | `ai_adoption_diff/cli.py:17-19` | Watch — deferred to T17 |
| F-01 | INFO | T10/T11 depend on `CommitRecord.file_paths` from T04; if absent Codex must stop and report BLOCKED | `ai_adoption_diff/ingestion/git_reader.py` (T04) | Watch — verify at T04 completion |
| F-02 | INFO | T16 token-not-logged and cleanup-on-error are mandatory evidence tests | `ai_adoption_diff/ingestion/github.py` (T16) | Deferred — Phase 5 |
| F-03 | INFO | `docs/prompts/ORCHESTRATOR.md` has unresolved `{{PROJECT_ROOT}}` and `{{CODEX_COMMAND}}` placeholders | `docs/prompts/ORCHESTRATOR.md` | Open — manual action required |
| F-04 | INFO | T02 and T03 commits listed as "pending" in Completed Tasks despite being complete | `docs/CODEX_PROMPT.md` | Open — cosmetic |
| F-05 | INFO | T04 provides `CommitRecord.file_paths`; T10/T11 dependency satisfied | `ai_adoption_diff/ingestion/git_reader.py` | Resolved — 2026-04-10 |

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
