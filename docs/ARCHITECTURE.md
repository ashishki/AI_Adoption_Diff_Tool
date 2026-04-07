# Architecture — AI Adoption Diff Tool

Version: 1.0
Last updated: 2026-04-07
Status: Draft

---

## System Overview

AI Adoption Diff Tool is a local CLI analytics tool that reads a Git repository's commit history and produces a structured before/after comparison of repository evolution metrics, calibrated around a declared or inferred AI coding-tool adoption date. It serves solo developers, tech leads, engineering managers, developer productivity engineers, and AI tooling researchers who need evidence-based analysis of how tools like Cursor, Copilot, or Claude Code affected development patterns. The system is stateless at the application layer — all persistent state is in the repository being analyzed and in the output report files — and the analytical core is entirely deterministic.

---

## Solution Shape

| Decision | Selection | Justification |
|----------|-----------|---------------|
| Primary shape | Deterministic subsystem | All v1 metric computation is formalizable: commit parsing, window partitioning, ratio calculations, distribution statistics. No LLM reasoning is needed or justified for the analytical core. |
| Governance level | Lean | Single developer or small team, no compliance requirements, read-only tool with low blast radius, no persistent workers or privileged actions. |
| Runtime tier | T0 | Local CLI with no persistent worker state, no mutable runtime, no privileged actions. Inputs: read-only git history. Outputs: local report files. |

### Rejected Lower-Complexity Options

| Rejected option | Why it is insufficient |
|-----------------|------------------------|
| Purely deterministic forever (no future LLM layer) | Sufficient for v1. An optional LLM explanation layer is anticipated but deferred — it will not affect the deterministic core and will require an ADR before activation. Deterministic is the correct choice now. |
| Workflow or human-in-the-loop assistant | The analytical pipeline has a fixed stage graph (ingest → anchor → partition → compute → report). Human-in-the-loop adds no value to metric computation; interpretation is the user's responsibility. |
| Higher-autonomy agent | Explicitly rejected. The brief states: "this project should start as a deterministic analytics system, not an autonomous agent." No task in v1 requires open-ended iteration or delegation. |

### Minimum Viable Control Surface

- GitHub token from environment variable only; never from source code or CLI argument
- Read-only git operations enforced; no write calls to any repository
- Network egress limited to GitHub API (optional; only when remote repo flag is set)

### Human Approval Boundaries

| Boundary | Human approval required? | Why |
|----------|--------------------------|-----|
| Metric computation and report generation | No | Fully deterministic; reversible (output is a local file) |
| Publishing or sharing the report externally | Yes (out of scope in v1) | Export produces a local file; distribution is the user's decision |
| Adding an LLM explanation layer in a future phase | Yes — ADR required | Changes solution shape from deterministic to hybrid; governance change requiring explicit sign-off |

### Deterministic vs LLM-Owned Subproblems

| Subproblem | Owner | Reason |
|------------|-------|--------|
| Git log ingestion and commit parsing | Deterministic | Structured data extraction; reproducibility required |
| Adoption anchor validation and window computation | Deterministic | Date arithmetic; must be auditable |
| Heuristic adoption window inference | Deterministic | Rule-based signal detection on commit metadata |
| All metric calculations | Deterministic | Arithmetic on commit history; same input must always produce same output |
| Confidence scoring | Deterministic | Rule-based formula; user must be able to inspect the scoring logic |
| Report rendering | Deterministic | Template-based; LLM narrative explicitly deferred to a future phase |

### Runtime and Isolation Model

| Property | Decision |
|----------|----------|
| Isolation boundary | Managed — local process boundary; no container required |
| Persistence model | Stateless — no persistent state between runs; output is written at end of run |
| Network model | Optional egress to GitHub API only; no ingress; all other egress denied by default |
| Secrets model | `GITHUB_TOKEN` from env var only; never logged, never written to output files |
| Runtime mutation boundary | None — no shell mutation, no package installs, no service management at runtime |
| Rollback / recovery model | N/A — re-run the CLI to regenerate; no state to roll back |

---

## Capability Profiles

| Profile    | Status | Declared in Phase | Notes |
|------------|--------|-------------------|-------|
| RAG        | OFF    | 1                 | No document corpus; all knowledge is in structured git history. Retrieval not applicable. |
| Tool-Use   | OFF    | 1                 | No LLM-directed tool calls in v1. GitHub API and git are called deterministically by the application. |
| Agentic    | OFF    | 1                 | No multi-step decision loop. Single-pass pipeline. |
| Planning   | OFF    | 1                 | Primary deliverable is an analysis report, not a structured plan for downstream execution. |
| Compliance | OFF    | 1                 | No named regulatory framework. No regulated data. Standard security practices apply. |

**RAG Profile: OFF**
Justification: All data is structured commit metadata from git history. No unstructured document corpus. No citation requirement. No knowledge base too large for a prompt. Retrieval is not applicable in v1.

**Tool-Use Profile: OFF**
Justification: No LLM calls in v1. GitHub API and git CLI calls are deterministic application code paths, not LLM-directed tool invocations. When an optional LLM explanation layer is added in a future phase, this profile will be re-evaluated — an ADR will be required.

**Agentic Profile: OFF**
Justification: The system executes a fixed pipeline — ingest, anchor, partition, compute, score, report — without any decision loop or agent roles.

**Planning Profile: OFF**
Justification: The system's deliverable is a before/after diff report. It is not a structured plan consumed by a downstream executor or human workflow.

**Compliance Profile: OFF**
Justification: No named compliance framework applies. Commit metadata (author names, emails) is classified as Internal. Standard security practices (SEC-1..4 in IMPLEMENTATION_CONTRACT.md) are sufficient.

---

## Inference / Model Strategy

Not applicable in v1. All computation is deterministic. A future optional LLM explanation layer will require an ADR and a new model strategy section in this document.

---

## Component Table

| Component | File / Directory | Responsibility |
|-----------|-----------------|----------------|
| CLI Entry Point | `ai_adoption_diff/cli.py` | Click-based CLI; parses input, orchestrates pipeline, writes output |
| Git Ingestion | `ai_adoption_diff/ingestion/git_reader.py` | Reads git log → list of `CommitRecord` dataclasses |
| GitHub Remote | `ai_adoption_diff/ingestion/github.py` | Fetches remote GitHub repository metadata (optional) |
| Adoption Anchor | `ai_adoption_diff/analysis/anchor.py` | Validates manual adoption date; computes window bounds |
| Heuristic Inference | `ai_adoption_diff/analysis/heuristic.py` | Infers adoption window from commit signals without a manual date |
| Window Partitioner | `ai_adoption_diff/analysis/partitioner.py` | Splits commit list into before/after windows |
| Confidence Scorer | `ai_adoption_diff/analysis/confidence.py` | Computes confidence score for the adoption anchor; generates caveats |
| Commit Size Metrics | `ai_adoption_diff/metrics/commit_size.py` | Commit size distribution, files-touched-per-commit |
| Churn Metrics | `ai_adoption_diff/metrics/churn.py` | Churn, rework, revert/fix frequency |
| Test Ratio Metrics | `ai_adoption_diff/metrics/test_ratio.py` | Test-to-code ratio trend, boilerplate/repetition signals |
| Hot-File Metrics | `ai_adoption_diff/metrics/hot_files.py` | Hot-file instability, directory-level change concentration |
| Report Model | `ai_adoption_diff/report/model.py` | Pydantic `AnalysisReport` model for structured output |
| JSON Exporter | `ai_adoption_diff/report/json_export.py` | Serializes report model to JSON |
| Report Renderer | `ai_adoption_diff/report/renderer.py` | Renders report to Markdown and HTML via Jinja2 |
| Shared Config | `ai_adoption_diff/shared/config.py` | Env var loading and validation; fails fast on missing required vars |
| Shared Tracing | `ai_adoption_diff/shared/tracing.py` | Structured logging context (trace_id, operation_name) via structlog |

---

## Data Flow — Primary Request Path

The following steps describe the end-to-end path for a standard single-repo analysis run:

1. User invokes `ai-diff analyze --repo /path/to/repo --date 2024-06-01 --tool cursor`.
2. CLI (`cli.py`) parses arguments, loads and validates config from environment via `shared/config.py`. Missing required vars → exit 1 with clear message.
3. `ingestion/git_reader.py` invokes `git log --format=...` via subprocess, parses stdout into a list of `CommitRecord` objects.
4. `analysis/anchor.py` validates the adoption date and computes `before_window` and `after_window` date bounds using the configurable analysis window size (default: 90 days each side).
5. `analysis/partitioner.py` splits the commit list into `before` and `after` windows.
6. Each metric module (`metrics/*.py`) computes statistics independently over each window and returns a typed result object.
7. `analysis/confidence.py` computes a confidence score for the adoption anchor and generates human-readable caveat strings.
8. `report/model.py` assembles the `AnalysisReport` Pydantic object from metric results, window metadata, confidence data, and tool label.
9. `report/json_export.py` writes `report.json`; `report/renderer.py` writes `report.md` (and optionally `report.html`) to the output directory.
10. CLI prints a short summary to stdout and exits 0.

**Heuristic mode path (no manual date):**
After step 3, if no adoption date is provided, `analysis/heuristic.py` runs signal detection over the full commit history and returns a `HeuristicResult` containing a suggested window and confidence score. Execution resumes at step 4 with the inferred date.

---

## Tech Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.11 | Preferred language per brief; strong ecosystem for data analysis and CLI tooling; stable type annotations enforced by ruff |
| CLI framework | Click | Clean decorator-based CLI; better UX than argparse for multi-option commands; natural extension path for future subcommands |
| Git access | subprocess → `git log` | Direct git invocation is dependency-free and produces exactly the log format needed; avoids GitPython's heavyweight dependency graph |
| Data validation | Pydantic v2 | Report model needs strong type validation and JSON serialization; Pydantic v2 is fast and produces a clean JSON schema |
| Report rendering | Jinja2 | Template-based rendering for Markdown and HTML; avoids string concatenation in rendering logic |
| HTTP client | httpx | Used for GitHub API calls; async-capable for future use; well-typed |
| Logging | structlog | Structured JSON logging with bound `trace_id` and `operation_name`; fulfills shared tracing requirement without OpenTelemetry overhead |
| Lint / format | ruff | Unified linter and formatter; zero configuration drift |
| Test framework | pytest | Industry standard; rich fixture system; supports tmp_path for integration tests |
| CI | GitHub Actions | Standard; free for public repos; appropriate for the project scale |
| Distribution | pip install (local) | v1 is a local tool installed via `pip install -e .`; no container or cloud deployment in scope |

---

## Security Boundaries

### Authentication

The system has no user authentication. It is a local CLI tool. The only credential in scope is the optional `GITHUB_TOKEN` environment variable used for GitHub API access when a remote repository URL is provided. This token is:
- Loaded from env var only; never accepted as a CLI argument (avoids shell history and log exposure)
- Never written to output files, log messages, or span attributes
- Scoped to read-only GitHub API operations

### Tenant Isolation

This is a single-tenant system. Tenant isolation is not applicable.

### PII Policy

Commit metadata contains author names and email addresses. These are not regulated under any active compliance framework, but must be handled with care:
- `author_email` and `author_name` are classified as **Internal** in this project.
- These fields must not appear in log messages or error output except when debug-level logging is explicitly enabled by the operator.
- Exported reports may include aggregate author-level commit counts but must not include raw email addresses in default output (omitted or hashed with SHA-256).
- Fields classified as Internal: `author_email`, `author_name`.

---

## Observability

| Dimension | Choice | Notes |
|-----------|--------|-------|
| Tracing | structlog context vars | Shared module: `ai_adoption_diff/shared/tracing.py`; provides `get_logger()` with `trace_id` and `operation_name` bound per pipeline run |
| Metrics | CLI stdout summary + structured log | No external metrics sink in v1; timing data goes to structured log |
| Logging | structlog JSON | Required fields: `trace_id`, `operation_name`, `level` |
| Dashboards | N/A | CLI tool; no dashboard in v1 |
| Alerting | N/A | Failures surface as exit code 1 + stderr |

### Observability Invariants

- No `author_email` or `author_name` in log messages at INFO or above (see §PII Policy).
- Installation check: `ai-diff --version` exits 0 and prints version — used by CI.
- All git subprocess calls wrapped in structlog spans with `operation_name`.

---

## External Integrations

| Integration | Purpose | Auth method | Rate limit / SLA |
|-------------|---------|-------------|-----------------|
| GitHub REST API v3 | Fetch repository metadata for remote repos | `GITHUB_TOKEN` Bearer token from env | 5,000 req/hr authenticated; exponential backoff required on 429 |
| Local git CLI (`git`) | Parse commit history from local repositories | None (local filesystem access) | N/A |

---

## File Layout

```
ai_adoption_diff/
├── __init__.py
├── cli.py                          # Click CLI entry point
├── ingestion/
│   ├── __init__.py
│   ├── git_reader.py               # git log parsing → CommitRecord list
│   └── github.py                   # GitHub remote support
├── analysis/
│   ├── __init__.py
│   ├── anchor.py                   # Manual adoption date anchor + window bounds
│   ├── heuristic.py                # Heuristic adoption window inference
│   ├── partitioner.py              # Before/after window partitioning
│   └── confidence.py               # Confidence scoring and caveat generation
├── metrics/
│   ├── __init__.py
│   ├── commit_size.py              # Commit size distribution, files-touched
│   ├── churn.py                    # Churn, rework, revert/fix frequency
│   ├── test_ratio.py               # Test-to-code ratio, boilerplate signals
│   └── hot_files.py                # Hot-file instability, dir concentration
├── report/
│   ├── __init__.py
│   ├── model.py                    # Pydantic AnalysisReport model
│   ├── json_export.py              # JSON serialization
│   └── renderer.py                 # Markdown + HTML rendering (Jinja2)
└── shared/
    ├── __init__.py
    ├── config.py                   # Env var loading; fail-fast on missing vars
    └── tracing.py                  # Shared structlog logger factory
tests/
├── conftest.py                     # Shared fixtures (sample commits, tmp dirs)
├── unit/
│   ├── test_anchor.py
│   ├── test_partitioner.py
│   ├── test_heuristic.py
│   ├── test_metrics_commit_size.py
│   ├── test_metrics_churn.py
│   ├── test_metrics_test_ratio.py
│   ├── test_metrics_hot_files.py
│   ├── test_confidence.py
│   └── test_report_model.py
└── integration/
    ├── test_git_reader.py
    └── test_cli_end_to_end.py
docs/
├── ARCHITECTURE.md
├── spec.md
├── tasks.md
├── CODEX_PROMPT.md
├── IMPLEMENTATION_CONTRACT.md
├── audit/
│   ├── AUDIT_INDEX.md
│   ├── PROMPT_0_META.md
│   ├── PROMPT_1_ARCH.md
│   ├── PROMPT_2_CODE.md
│   └── PROMPT_3_CONSOLIDATED.md
├── adr/
└── prompts/
    ├── ORCHESTRATOR.md
    └── PROMPT_S_STRATEGY.md
.github/
└── workflows/
    └── ci.yml
pyproject.toml
requirements.txt
requirements-dev.txt
README.md
```

---

## Runtime Contract

| Variable | Description | Example value | Required |
|----------|-------------|---------------|----------|
| `GITHUB_TOKEN` | GitHub personal access token for remote repo access | `ghp_xxxxxxxxxxxx` | No — required only when `--repo` is a GitHub URL |
| `AI_DIFF_LOG_LEVEL` | Logging verbosity | `INFO` | No (default: `INFO`) |
| `AI_DIFF_OUTPUT_DIR` | Default output directory for reports | `/tmp/ai_diff_output` | No (default: `./output`) |

---

## Non-Goals (v1)

- No LLM-based narrative generation or explanation — deferred; requires ADR when added
- No causal claims in output — correlation only, with explicit caveats in every report
- No cross-repo leaderboard or comparative ranking across organizations
- No write access to any repository under any circumstance
- No web UI or API server — CLI only in v1
- No multi-tenant SaaS deployment
- No automatic judgment of which AI tool performed "best"
- No T2/T3 runtime behavior — no persistent workers, no privileged shell mutation
- No RAG, Agentic, Planning, or Compliance profiles in v1 — all require ADRs before activation
