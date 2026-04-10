---
# ARCH_REPORT — Cycle 1
_Date: 2026-04-09_

## Component Verdicts

| Component | Verdict | Note |
|-----------|---------|------|
| CLI Entry Point (`cli.py`) | PASS | Layer boundary respected; imports only `__version__` and `click`; no cross-layer violations; stub correctly wired to `cli` group via `project.scripts` |
| Shared Config (`shared/config.py`) | PASS | Loads `AI_DIFF_LOG_LEVEL` and `AI_DIFF_OUTPUT_DIR` from env; no cross-layer imports; Pydantic BaseModel correctly used |
| Shared Tracing (`shared/tracing.py`) | DRIFT | `get_logger` return type annotation is `FilteringBoundLogger`, not `BoundLogger`; META_ANALYSIS PROMPT_2 scope requires signature `get_logger(name: str) -> BoundLogger`; actual type differs from stated contract (see ARCH-1) |
| Ingestion `__init__.py` | DRIFT | Empty stub; `IngestionError` not yet defined; META_ANALYSIS PROMPT_2 scope item 1 flags this as required before T04 implementation begins (see ARCH-2) |
| Analysis `__init__.py` | DRIFT | Empty stub; `AnchorError` and `PartitionError` not yet defined; META_ANALYSIS PROMPT_2 scope item 2 flags this as required before T05/T07 (see ARCH-2) |
| Metrics `__init__.py` | PASS | Empty stub acceptable at Phase 1; no metric modules exist yet; no violations introduced |
| Report `__init__.py` | PASS | Empty stub acceptable at Phase 1; no report modules exist yet; no violations introduced |
| Git Ingestion (`ingestion/git_reader.py`) | N/A | Not yet implemented; planned for T04 |
| GitHub Remote (`ingestion/github.py`) | N/A | Not yet implemented; planned for T16 |
| Adoption Anchor (`analysis/anchor.py`) | N/A | Not yet implemented; planned for T05 |
| Heuristic Inference (`analysis/heuristic.py`) | N/A | Not yet implemented; planned for T06 |
| Window Partitioner (`analysis/partitioner.py`) | N/A | Not yet implemented; planned for T07 |
| Confidence Scorer (`analysis/confidence.py`) | N/A | Not yet implemented; planned for T07 area |
| Commit Size Metrics (`metrics/commit_size.py`) | N/A | Not yet implemented; planned for T08 |
| Churn Metrics (`metrics/churn.py`) | N/A | Not yet implemented; planned for T09 |
| Test Ratio Metrics (`metrics/test_ratio.py`) | N/A | Not yet implemented; planned for T10 |
| Hot-File Metrics (`metrics/hot_files.py`) | N/A | Not yet implemented; planned for T11 |
| Report Model (`report/model.py`) | N/A | Not yet implemented; planned for T12 |
| JSON Exporter (`report/json_export.py`) | N/A | Not yet implemented; planned for T13 |
| Report Renderer (`report/renderer.py`) | N/A | Not yet implemented; planned for T14/T15 |

---

## Contract Compliance

| Rule | Verdict | Note |
|------|---------|------|
| SQL Safety | PASS | No SQL in project; rule noted as N/A for v1 by contract |
| Multi-Tenant | PASS | Single-tenant; rule not active |
| Authorization (GITHUB_TOKEN validation before API calls) | PASS | No GitHub API calls yet; `GITHUB_TOKEN` handling not implemented; no violation introduced |
| PII Policy (no author_email/author_name in logs at INFO+) | PASS | No PII-handling code exists yet; no violation introduced |
| Credentials and Secrets (no secrets in source) | PASS | No credentials, tokens, or secrets found in any source file |
| Shared Tracing Module (all logging via `get_logger`) | PASS | `tracing.py` defines `get_logger`; `cli.py` does not emit structured logs (stub only); no inline `structlog.get_logger()` calls found in individual modules |
| CI Gate | PASS | `.github/workflows/ci.yml` verified by `test_ci.py`; test confirms checkout, Python 3.11 setup, `ruff check`, `ruff format --check`, and `pytest -q` steps are present |
| OBS-1 (instrument every external call with operation_name, trace_id) | N/A | No external calls yet; rule will apply at T04 and T16 |
| OBS-2 (log duration_ms and success per external call) | N/A | No external calls yet; rule will apply at T04 and T16 |
| OBS-3 (`ai-diff --version` exits 0, prints version) | PASS | `test_version_command` in `test_skeleton.py` verifies exit 0 and version string match against `pyproject.toml` |
| PS-1: Read-Only Repository Access | PASS | No git calls yet; no write operations introduced |
| PS-2: Subprocess Safety (list form only) | PASS | `test_skeleton.py` and `test_ci.py` use `subprocess.run` with list form; no `shell=True` found |
| PS-3: Determinism (no datetime.now(), no random in metric functions) | PASS | No metric functions exist yet; no violations introduced |
| PS-4: GitHub Token Handling (loaded once in config.py) | DRIFT | `shared/config.py` does not yet load or expose `GITHUB_TOKEN`; this is not a violation now (T16 deferred) but the contract requires it be loaded exclusively in `config.py`; the field is absent (see ARCH-3) |
| PS-5: Error Exposure (no bare tracebacks to user) | PASS | `cli.py` stub does not expose tracebacks; no error paths exist yet |
| PS-6: Caveat Requirement (static caveat in every report) | N/A | No report modules exist yet; must be enforced at T12/T13/T14 |
| Commit Granularity (one logical change per commit) | PASS | Phase 1 commits are split by task per available history |
| Sandbox Isolation (tests use tmp_path, no shared mutable state) | PASS | `conftest.py` is an empty stub; no shared mutable fixtures introduced; `tmp_path` usage deferred to T04 fixture |

---

## ADR Compliance

| ADR | Verdict | Note |
|-----|---------|------|
| (none) | N/A | No ADRs have been filed in `docs/adr/`. Directory exists but is empty. No decisions have been formalized yet. No violations possible; no ADR-gated features are active. |

---

## Architecture Findings

### ARCH-1 [P2] — `get_logger` return type does not match PROMPT_2 contract

Symptom: `shared/tracing.py` declares `get_logger(name: str) -> FilteringBoundLogger`. META_ANALYSIS PROMPT_2 scope item 4 requires the signature to be exactly `get_logger(name: str) -> BoundLogger`. Downstream T04+ tasks will rely on this signature; a type mismatch may cause type-checker failures when those tasks import and annotate against the function.

Evidence: `ai_adoption_diff/shared/tracing.py:25`

Root cause: `FilteringBoundLogger` is the structlog internal type returned by `structlog.make_filtering_bound_logger()`; `BoundLogger` is the public protocol type. The implementation chose the concrete internal type rather than the public protocol type.

Impact: Type annotations in T04+ modules that declare `logger: BoundLogger` will be incompatible with the returned `FilteringBoundLogger` unless callers use the concrete type. Static analysis (mypy/pyright) may flag this as a type error across the codebase.

Fix: Change the return annotation to `structlog.stdlib.BoundLogger` or the appropriate public protocol. Verify with `mypy` before closing.

---

### ARCH-2 [P2] — `IngestionError`, `AnchorError`, `PartitionError` absent from package `__init__.py` files

Symptom: `ai_adoption_diff/ingestion/__init__.py` and `ai_adoption_diff/analysis/__init__.py` are empty stubs. They do not declare `IngestionError`, `AnchorError`, or `PartitionError`. META_ANALYSIS PROMPT_2 scope items 1 and 2 require these exception classes to be present before T04, T05, and T07 implementation begins.

Evidence: `ai_adoption_diff/ingestion/__init__.py:1`, `ai_adoption_diff/analysis/__init__.py:1`

Root cause: Phase 1 tasks (T01–T03) established the directory skeleton but did not include exception class stubs in the `__init__.py` files. The spec (F1 AC-3, F4 AC-3/AC-4) defines these exceptions as the public interface of their respective packages.

Impact: When Codex begins T04, it will need to define `IngestionError` somewhere. Without it pre-declared in `__init__.py`, there is a risk the exception is placed in `git_reader.py` itself and not re-exported from the package root, breaking the layered import contract (callers should import `from ai_adoption_diff.ingestion import IngestionError`, not from the implementation file).

Fix: Add `class IngestionError(Exception): pass` to `ingestion/__init__.py`; add `class AnchorError(Exception): pass` and `class PartitionError(Exception): pass` to `analysis/__init__.py`. These are Phase 2 pre-conditions and should be resolved before T04 starts.

---

### ARCH-3 [P3] — `GITHUB_TOKEN` not yet represented in `shared/config.py`

Symptom: `shared/config.py` defines `Config` with `log_level` and `output_dir` fields but has no `github_token` field. PS-4 requires `GITHUB_TOKEN` to be loaded exactly once in `shared/config.py`.

Evidence: `ai_adoption_diff/shared/config.py:11-17`

Root cause: T16 (GitHub remote support) is deferred to Phase 5. The `Config` model was not pre-stubbed with the `GITHUB_TOKEN` field.

Impact: Low at this phase. Risk: when T16 is implemented, `GITHUB_TOKEN` might be loaded in `ingestion/github.py` directly, violating PS-4. Having the field pre-declared in `Config` is the correct control surface.

Fix: Add `github_token: str | None = Field(default_factory=lambda: os.getenv("GITHUB_TOKEN"))` to `Config`. Ensure the field value is never logged. Resolve before T16 begins.

---

### ARCH-4 [P2] — `analyze` command stub lacks required flags; extension path not structurally verified

Symptom: `cli.py` defines `analyze()` with no parameters. META_ANALYSIS PROMPT_2 scope item 5 requires the stub to "support extension to `ai-diff analyze` with `--repo`, `--date`, `--tool`, `--format` flags in T17 without rewrite." The current stub has no `@click.option` decorators and no parameter signature.

Evidence: `ai_adoption_diff/cli.py:17-19`

Root cause: Phase 1 stub was intentionally minimal. However, without at least the Click parameter declarations in place, T17 will require structural changes to the function signature rather than additive decoration, which increases regression risk.

Impact: T17 implementation will need to modify the function signature and add decorators. This is normal extension but the stub's complete absence of parameters means no contract exists to validate against during the Phase 2–4 cycles.

Fix: This is a deferred concern for T17. No structural violation has occurred yet. Mark as watch item; verify at T17 that the stub was extended additively without rewriting existing tests.

---

### ARCH-5 [P3] — `pyproject.toml` targets Python 3.11 in ruff but `requires-python = ">=3.10"`

Symptom: `pyproject.toml` sets `requires-python = ">=3.10"` but `[tool.ruff] target-version = "py311"`. This mismatch means ruff will lint for Python 3.11 syntax features but the package declares support for 3.10+.

Evidence: `pyproject.toml:8` (`requires-python = ">=3.10"`), `pyproject.toml:29` (`target-version = "py311"`)

Root cause: ARCHITECTURE.md §Tech Stack specifies Python 3.11 as the language choice; `requires-python` was set conservatively to 3.10. The two settings are inconsistent.

Impact: Low; no current code uses 3.11-only syntax. Risk: as T04+ code is written, ruff may permit 3.11-only syntax that will fail on 3.10 installations.

Fix: Align to `requires-python = ">=3.11"` to match ARCHITECTURE.md and ruff config, or change `target-version` to `py310`. Recommended: align to `>=3.11` to match the architecture specification.

---

## Right-Sizing / Runtime Checks

| Check | Verdict | Note |
|-------|---------|------|
| Solution shape still Deterministic subsystem | PASS | No LLM calls, no agent loops, no ML inference introduced; pipeline is fixed-stage (ingest → anchor → partition → compute → report) as specified |
| Metric functions are pure/deterministic | PASS | No metric modules exist yet; no `datetime.now()`, `random`, or external state reads found in any existing code |
| T0 runtime preserved (no DB/worker/mutable state) | PASS | No database, no background worker, no persistent state beyond output files; `Config.output_dir` is a local path only |
| Read-only git enforcement holds | PASS | No git subprocess calls exist yet; no write-mode git operations introduced |
| Subprocess list-form used everywhere | PASS | All subprocess calls in test files use list form (`["ruff", "check", ...]`, `[ai_diff_bin, "--version"]`); no `shell=True` found |
| No LLM calls without ADR | CLEAN | No LLM calls anywhere in the codebase; Capability Profiles remain all OFF |

---

## Doc Patches Needed

| File | Section | Change |
|------|---------|--------|
| `docs/ARCHITECTURE.md` | §Component Table | `Confidence Scorer` is listed as `ai_adoption_diff/analysis/confidence.py` but is absent from the file layout diagram — layout shows only `anchor.py`, `heuristic.py`, `partitioner.py`. Add `confidence.py` to the layout tree. |
| `docs/ARCHITECTURE.md` | §File Layout | `docs/adr/` is shown as an empty directory in the layout — this is accurate but should include a placeholder note that ADRs will live here as `ADR{NNN}.md` per IMPLEMENTATION_CONTRACT.md governance. |
| `docs/CODEX_PROMPT.md` | Pending commits section | META_ANALYSIS F-04: T02 and T03 are listed as "pending" despite being complete. Update to reflect Phase 1 completion state. Cosmetic; no functional impact. |
| `docs/prompts/ORCHESTRATOR.md` | Entire file | META_ANALYSIS F-03: `{{PROJECT_ROOT}}` and `{{CODEX_COMMAND}}` placeholders remain unresolved. Must be filled before the first orchestrator loop is started. |

---
