# Implementation Contract — AI Adoption Diff Tool

Status: **IMMUTABLE** — changes to this document require an Architectural Decision Record filed in `docs/adr/`.
Version: 1.0
Effective date: 2026-04-07

Any agent (Codex or review) may cite this document as the authority on implementation rules. Any finding that this contract was violated is automatically P1.

---

## Universal Rules

These rules apply to every project using the AI Workflow Playbook. They are not negotiable and are not changed without an ADR.

### SQL Safety

- All SQL is parameterized. Use `text()` with named parameters: `text("SELECT ... WHERE id = :id")` with `{"id": value}`.
- Never interpolate variables into SQL strings. This includes f-strings, `%` formatting, and `+` concatenation.
- Violation: automatic P1.

_Note: AI Adoption Diff Tool has no database in v1. This rule is present for future phases that may introduce persistence._

### Multi-Tenant Systems

_This is a single-tenant system. This section is not active._

### Authorization

- Every external-facing operation must validate credentials before accessing remote resources.
- For GitHub API access: validate `GITHUB_TOKEN` is present before making any API call.
- Violation: automatic P1.

### PII Policy

- No `author_email` or `author_name` values in log messages at INFO level or above.
- No PII in error messages returned to the user.
- `author_email` is hashed (SHA-256) immediately upon ingestion; raw email is never stored in memory beyond the parsing step.
- Fields classified as Internal: `author_email`, `author_name`.
- Violation: automatic P1.

### Credentials and Secrets

- No credentials, API keys, tokens, passwords, or secrets in source code.
- No credentials in comments.
- No credentials in test fixtures (use placeholder strings; real values come from environment variables).
- All secrets come from environment variables. Required env vars documented in `docs/ARCHITECTURE.md §Runtime Contract`.
- `.env` files are in `.gitignore` and are never committed.
- `GITHUB_TOKEN` must never be interpolated into a shell command string or logged at any level.
- Violation: automatic P1 (and a security incident).

### Shared Tracing Module

- One shared tracing module: `ai_adoption_diff/shared/tracing.py` with a single `get_logger()` function.
- All code that emits structured log entries imports `get_logger` from this module.
- No inline `structlog.get_logger()` calls in individual modules.
- Violation: P2 (accumulates; becomes P1 at age cap).

### CI Gate

- CI must pass before any PR is merged.
- A PR with failing CI is never merged, regardless of deadline pressure.
- Violation: automatic P1.

### Observability

**OBS-1 — Instrumentation.** Every external call (git subprocess, GitHub API) must be logged via the shared tracing module with `operation_name` and `trace_id` bound. Violation: P2.

**OBS-2 — Metrics.** For each external call, log a structured entry at completion with `success`, `duration_ms`, and `operation_name`. Violation: P2.

**OBS-3 — Health check.** `ai-diff --version` exits 0 and prints the version string. Violation: P1.

---

## Project-Specific Rules

### PS-1: Read-Only Repository Access

All git operations are read-only. No code path may call `git commit`, `git push`, `git checkout` (mutating), `git reset`, `git rm`, or any command that modifies repository state.

Violation: automatic P1.

### PS-2: Subprocess Safety

All subprocess calls must use the list form (`subprocess.run(["git", "log", ...])`) — never the shell string form (`subprocess.run("git log ...", shell=True)`).

Violation: automatic P1.

### PS-3: Determinism Requirement

All metric computation functions must be pure and deterministic: same input → same output always. No random number generation, no `datetime.now()` calls, no external state reads inside metric functions.

`datetime.now(UTC)` is permitted only in `report/model.py` for the `generated_at` field.

Violation: P1.

### PS-4: GitHub Token Handling

`GITHUB_TOKEN` must be loaded from the environment exactly once, in `ai_adoption_diff/shared/config.py`. It must not be passed as a CLI argument, stored in a config file, or logged at any level. When constructing git clone URLs that embed the token, the token must be in the subprocess args list (not a shell string), and the log entry must never include the URL with the token embedded.

Violation: automatic P1.

### PS-5: Error Exposure

Internal stack traces must not be exposed to the end user. All user-facing errors go to stderr as plain English messages. Full tracebacks are shown only when `--debug` flag is set. Bare `except Exception:` blocks without logging are forbidden.

Violation: P2.

### PS-6: Caveat Requirement

Every exported report (JSON and Markdown) must include the static caveat: `"Metrics show correlation only. Causality cannot be inferred."`. This must appear in the Markdown footer and as a top-level field in the JSON output.

Violation: P2.

---

## Control Surface and Runtime Boundaries

| Boundary | Rule |
|----------|------|
| Secrets scope | `GITHUB_TOKEN` only; loaded once in `shared/config.py`; scoped to GitHub API calls |
| Network egress | GitHub API (`api.github.com`) only; only when `--repo` is a GitHub URL |
| Privileged actions | None — all git operations are read-only subprocess calls |
| Runtime mutation | None — no shell mutation, no package installs, no service management at runtime |
| Persistence | Stateless — reports written to local output files; no database or persistent worker state |
| Auditability | Structured JSON logs with `trace_id` and `operation_name` per run |

### Runtime Tier Guardrails

- This is a T0 project. It must not silently acquire T1/T2/T3 behaviors.
- No long-lived background workers. No privileged shell mutation. No persistent runtime state beyond the output directory.
- Any addition of a database, message queue, or background service requires an ADR and runtime tier re-evaluation.

---

## Mandatory Pre-Task Protocol

Every Codex agent must execute these steps before writing any implementation code. No exceptions.

1. Read `docs/IMPLEMENTATION_CONTRACT.md` (this file) from top to bottom.
2. Read the full task in `docs/tasks.md`, including all acceptance criteria, the Depends-On list, and the Notes section.
3. Read all Depends-On tasks to understand the interface contracts your implementation must satisfy.
4. Run `pytest -q`. Record: `{N} passing, {M} failed`. If M > 0, stop and report.
5. Run `ruff check`. Must exit 0. If not, fix ruff issues first in a separate commit, then restart.
6. Confirm every acceptance criterion will have a corresponding test before implementation is considered complete.

Skipping any step is a P1 finding in the next review cycle.

---

## Forbidden Actions

| Forbidden Action | Reason |
|-----------------|--------|
| Shell-form subprocess (`shell=True`) | Command injection risk |
| Writing to the analyzed repository | The tool is read-only |
| Logging `GITHUB_TOKEN` at any level | Credential exposure |
| Embedding token in a shell command string | Token appears in shell history and process table |
| Calling `datetime.now()` inside metric functions | Breaks determinism (PS-3) |
| Bare `except Exception: pass` without logging | Silent failure |
| Skipping the pre-task baseline capture | Cannot verify no regression |
| Self-closing a review finding without code verification | Findings are verified by reading code |
| Modifying this document without an ADR | The contract is immutable by design |
| Deferring CI setup past Phase 1 | Every commit must be CI-verified |
| Merging a PR with failing CI | The CI gate is non-negotiable |
| Committing credentials or secrets | Irreversible exposure |
| Adding a TODO without a task reference | Orphaned TODOs accumulate |
| Leaving commented-out code in a commit | Degrades readability |
| Activating LLM inference without an ADR | Changes solution shape; requires governance approval |

---

## Quality Process Rules

### P2 Age Cap

Any P2 finding open for more than 3 consecutive review cycles must be:
- Closed (resolved with a code change and a passing test), OR
- Escalated to P1 (resolved before the next phase gate), OR
- Formally deferred to v2 (with an ADR in `docs/adr/`)

### Commit Granularity

One logical change per commit. Module implementation and tests are at minimum two commits. Never bundle unrelated changes.

### Sandbox Isolation

Tests do not share mutable state. Integration tests use `tmp_path` for filesystem isolation. Tests must not depend on files created by other tests or execution order.

---

## Governing Documents

| Document | Path | Role |
|----------|------|------|
| Architecture | `docs/ARCHITECTURE.md` | System design authority |
| Specification | `docs/spec.md` | Feature authority |
| Task graph | `docs/tasks.md` | Implementation authority |
| Session handoff | `docs/CODEX_PROMPT.md` | State authority |
| This document | `docs/IMPLEMENTATION_CONTRACT.md` | Rule authority — immutable |
| Review reports | `docs/audit/CYCLE{N}_REVIEW.md` | Finding authority |
| ADRs | `docs/adr/ADR{NNN}.md` | Decision authority |

Precedence (highest to lowest): IMPLEMENTATION_CONTRACT → ADRs → ARCHITECTURE → spec → tasks → CODEX_PROMPT.
