# Task Graph — AI Adoption Diff Tool

Version: 1.0
Last updated: 2026-04-07

<!--
Machine-readable task blocks. Fields are parsed by the Orchestrator.
Schema: templates/tasks_schema.md
-->

---

## Phase 1: Foundation

**Goal:** Working project skeleton with CI and smoke tests. Establishes the baseline before any feature code is written.
**Gate:** All 3 tasks complete, CI green, `pytest` passes, `ruff check` passes, `ai-diff --version` exits 0.

---

## T01: Project Skeleton

Owner:      codex
Phase:      1
Type:       none
Depends-On: none

Objective: |
  Create the complete project directory structure, package entry point, pyproject.toml,
  requirements files, and CLI stub so that `pip install -e .` succeeds and
  `ai-diff --version` exits 0.

Acceptance-Criteria:
  - id: AC-1
    description: "`pip install -e .` exits 0 in a clean virtualenv."
    test: "tests/unit/test_skeleton.py::test_package_installs"
  - id: AC-2
    description: "`ai-diff --version` exits 0 and prints a string matching the version in pyproject.toml."
    test: "tests/unit/test_skeleton.py::test_version_command"
  - id: AC-3
    description: "All directories declared in ARCHITECTURE.md §File Layout exist: `ai_adoption_diff/`, `ai_adoption_diff/ingestion/`, `ai_adoption_diff/analysis/`, `ai_adoption_diff/metrics/`, `ai_adoption_diff/report/`, `ai_adoption_diff/shared/`, `tests/unit/`, `tests/integration/`, `docs/`."
    test: "tests/unit/test_skeleton.py::test_directory_structure"
  - id: AC-4
    description: "`ai_adoption_diff/shared/tracing.py` exports `get_logger()` which returns a structlog BoundLogger with `trace_id` and `operation_name` bindable."
    test: "tests/unit/test_skeleton.py::test_tracing_module_exports_get_logger"

Files:
  - pyproject.toml
  - requirements.txt
  - requirements-dev.txt
  - ai_adoption_diff/__init__.py
  - ai_adoption_diff/cli.py
  - ai_adoption_diff/ingestion/__init__.py
  - ai_adoption_diff/analysis/__init__.py
  - ai_adoption_diff/metrics/__init__.py
  - ai_adoption_diff/report/__init__.py
  - ai_adoption_diff/shared/__init__.py
  - ai_adoption_diff/shared/config.py
  - ai_adoption_diff/shared/tracing.py
  - tests/__init__.py
  - tests/conftest.py
  - tests/unit/__init__.py
  - tests/integration/__init__.py
  - tests/unit/test_skeleton.py

Notes: |
  - CLI stub: `ai-diff analyze` may print "not implemented" and exit 0 — full pipeline is built in later tasks.
  - `shared/config.py` must load `AI_DIFF_LOG_LEVEL` (default: INFO) and `AI_DIFF_OUTPUT_DIR` (default: ./output).
  - `shared/tracing.py` must expose exactly `get_logger(name: str) -> BoundLogger`.
  - Do not add dependencies beyond: click, structlog, pydantic, jinja2, httpx. Dev deps: pytest, ruff.

---

## T02: CI Setup

Owner:      codex
Phase:      1
Type:       none
Depends-On: T01

Objective: |
  Create a GitHub Actions CI workflow that installs dependencies, runs ruff check,
  ruff format check, and pytest on every push and pull request.

Acceptance-Criteria:
  - id: AC-1
    description: "`.github/workflows/ci.yml` exists, is valid YAML, and defines a job named `ci` triggered on `push` and `pull_request`."
    test: "tests/unit/test_ci.py::test_ci_workflow_exists_and_valid"
  - id: AC-2
    description: "The CI workflow contains steps: checkout, python setup (3.11), pip install (`-r requirements-dev.txt -e .`), ruff check, ruff format check, pytest."
    test: "tests/unit/test_ci.py::test_ci_workflow_has_required_steps"
  - id: AC-3
    description: "`ruff check ai_adoption_diff/ tests/` exits 0 on the skeleton codebase."
    test: "tests/unit/test_ci.py::test_ruff_check_passes"
  - id: AC-4
    description: "`ruff format --check ai_adoption_diff/ tests/` exits 0 on the skeleton codebase."
    test: "tests/unit/test_ci.py::test_ruff_format_passes"

Files:
  - .github/workflows/ci.yml
  - pyproject.toml                  # add [tool.ruff] section
  - tests/unit/test_ci.py

Notes: |
  - CI workflow must not require secrets for the basic test suite (no GITHUB_TOKEN in CI env for unit tests).
  - ruff target-version: py311. Line length: 100.
  - Test CI workflow YAML parsing with PyYAML in the test (load and assert keys).

---

## T03: Smoke Tests

Owner:      codex
Phase:      1
Type:       none
Depends-On: T01, T02

Objective: |
  Establish the initial test baseline with smoke tests that verify the skeleton
  is importable, the CLI entry point is reachable, and the shared modules are
  functional at a surface level.

Acceptance-Criteria:
  - id: AC-1
    description: "`import ai_adoption_diff` succeeds without ImportError."
    test: "tests/unit/test_smoke.py::test_package_importable"
  - id: AC-2
    description: "`from ai_adoption_diff.shared.tracing import get_logger` succeeds; `get_logger('test')` returns an object with a `.info()` method."
    test: "tests/unit/test_smoke.py::test_tracing_get_logger_callable"
  - id: AC-3
    description: "`from ai_adoption_diff.shared.config import Config` succeeds; `Config()` loads without error when no required env vars are missing."
    test: "tests/unit/test_smoke.py::test_config_loads"
  - id: AC-4
    description: "Running `ai-diff --help` via Click's `CliRunner` exits 0 and includes 'analyze' in the output."
    test: "tests/unit/test_smoke.py::test_cli_help_exits_zero"

Files:
  - tests/unit/test_smoke.py

Notes: |
  Use Click's CliRunner for CLI tests — do not invoke subprocess in unit tests.
  Record pytest baseline in CODEX_PROMPT.md after this task completes.

---

## Phase 2: Ingestion and Windowing

**Goal:** The system can read a real git repository and partition its history into before/after windows.
**Gate:** `test_git_reader.py` passes against a real temp git repo; anchor, heuristic, and partitioner unit tests all pass.

---

## T04: Git Log Ingestion

Owner:      codex
Phase:      2
Type:       none
Depends-On: T01, T03

Objective: |
  Implement the git log ingestion module that reads a local git repository's
  commit history and returns a typed list of CommitRecord objects. Author emails
  are hashed before storage.

Acceptance-Criteria:
  - id: AC-1
    description: "`git_reader.read_commits(repo_path)` returns `list[CommitRecord]` with fields `sha`, `author_email_hash`, `timestamp`, `files_changed`, `insertions`, `deletions`, `message`. Raw email is never stored."
    test: "tests/integration/test_git_reader.py::test_read_commits_returns_commit_records"
  - id: AC-2
    description: "Given a repo with 5 known commits (created in a tmp_path fixture), `read_commits()` returns exactly 5 `CommitRecord` objects with correct `insertions` and `deletions` counts."
    test: "tests/integration/test_git_reader.py::test_read_commits_count_and_fields"
  - id: AC-3
    description: "Given a repo with zero commits, `read_commits()` returns an empty list."
    test: "tests/integration/test_git_reader.py::test_read_commits_empty_repo"
  - id: AC-4
    description: "Given a path that is not a git repository, `read_commits()` raises `IngestionError` containing the invalid path string."
    test: "tests/unit/test_git_reader_unit.py::test_read_commits_raises_on_invalid_path"
  - id: AC-5
    description: "`author_email_hash` is the SHA-256 hex digest of the raw author email. Verified by hashing a known email and comparing to the fixture commit's hash."
    test: "tests/integration/test_git_reader.py::test_author_email_is_hashed"

Files:
  - ai_adoption_diff/ingestion/git_reader.py
  - tests/integration/test_git_reader.py
  - tests/unit/test_git_reader_unit.py
  - tests/conftest.py                         # add tmp_git_repo fixture

Notes: |
  - Use subprocess to invoke `git log --format=... --numstat`. Parse stdout line by line.
  - `CommitRecord` is a frozen dataclass (not mutable after creation).
  - `IngestionError` is a custom exception defined in `ai_adoption_diff/ingestion/__init__.py`.
  - The conftest `tmp_git_repo` fixture creates a real git repo with `git init`, sets
    `user.email` and `user.name` via config, and makes 5 commits with known file changes.
  - Merge commits excluded by default (`--no-merges` flag passed to git log).

---

## T05: Adoption Anchor

Owner:      codex
Phase:      2
Type:       none
Depends-On: T04

Objective: |
  Implement the adoption anchor module that validates a manually provided adoption
  date and computes before/after window bounds from the commit history date range.

Acceptance-Criteria:
  - id: AC-1
    description: "`anchor.compute_window(adoption_date='2024-06-01', commits=commits, window_days=90)` returns `AnalysisWindow(before_start=date(2024,3,3), adoption_date=date(2024,6,1), after_end=date(2024,8,30))`."
    test: "tests/unit/test_anchor.py::test_compute_window_returns_correct_bounds"
  - id: AC-2
    description: "`anchor.compute_window()` with `adoption_date='not-a-date'` raises `ValueError` with message containing 'YYYY-MM-DD'."
    test: "tests/unit/test_anchor.py::test_invalid_date_format_raises_value_error"
  - id: AC-3
    description: "`anchor.compute_window()` where no commits fall in the before window raises `AnchorError('before window is empty')`. Same for after window."
    test: "tests/unit/test_anchor.py::test_empty_before_window_raises_anchor_error"
  - id: AC-4
    description: "`window_days` defaults to 90 when not provided; `window_days=30` produces a 30-day window on each side."
    test: "tests/unit/test_anchor.py::test_custom_window_days"

Files:
  - ai_adoption_diff/analysis/anchor.py
  - tests/unit/test_anchor.py

Notes: |
  `AnchorError` is a custom exception defined in `ai_adoption_diff/analysis/__init__.py`.
  `AnalysisWindow` is a frozen dataclass: `before_start`, `adoption_date`, `after_end` (all `datetime.date`).
  Window bounds are inclusive on both ends.

---

## T06: Heuristic Adoption Window Inference

Owner:      codex
Phase:      2
Type:       none
Depends-On: T04

Objective: |
  Implement the heuristic adoption window inference module that detects adoption
  signals in commit history and returns a suggested adoption date with a confidence
  score when no manual date is provided.

Acceptance-Criteria:
  - id: AC-1
    description: "`heuristic.infer_adoption(commits)` returns `HeuristicResult(suggested_date, confidence_score, signals_detected)` where `confidence_score` is in `[0.0, 1.0]`."
    test: "tests/unit/test_heuristic.py::test_infer_returns_heuristic_result"
  - id: AC-2
    description: "Given commits with a `.cursorrules` file added at a known date, `signals_detected` contains an entry with `signal_name='ai_config_file'` and `detected_date` matching that commit's date."
    test: "tests/unit/test_heuristic.py::test_ai_config_file_signal_detected"
  - id: AC-3
    description: "Given commits with a clear spike in commit frequency (>2x 30-day rolling average) at a known date, `signals_detected` contains `signal_name='commit_frequency_spike'`."
    test: "tests/unit/test_heuristic.py::test_commit_frequency_spike_detected"
  - id: AC-4
    description: "Given a commit list with no detectable signals, `infer_adoption()` returns `HeuristicResult(suggested_date=None, confidence_score=0.0, signals_detected=[])`."
    test: "tests/unit/test_heuristic.py::test_no_signals_returns_none_date"
  - id: AC-5
    description: "The `suggested_date` is the median date of all detected signal dates, not the earliest, when multiple signals are present."
    test: "tests/unit/test_heuristic.py::test_suggested_date_is_median_of_signals"

Files:
  - ai_adoption_diff/analysis/heuristic.py
  - tests/unit/test_heuristic.py

Notes: |
  AI-config file patterns to detect: `.cursorrules`, `.github/copilot-instructions.md`,
  `.claude/`, `AGENTS.md`. These are checked against the file paths in each `CommitRecord`.
  `HeuristicResult` is a frozen dataclass. `signals_detected` is `list[Signal]` where
  `Signal` is a frozen dataclass: `signal_name: str`, `detected_date: date`, `strength: float`.

---

## T07: Window Partitioner

Owner:      codex
Phase:      2
Type:       none
Depends-On: T04, T05

Objective: |
  Implement the window partitioner that splits a commit list into non-overlapping
  before and after windows based on an AnalysisWindow.

Acceptance-Criteria:
  - id: AC-1
    description: "Given 10 commits spanning 6 months and a window bisecting them, `partitioner.partition(commits, window)` returns `(before, after)` where every commit in `before` has `timestamp.date() < window.adoption_date` and every commit in `after` has `timestamp.date() >= window.adoption_date`."
    test: "tests/unit/test_partitioner.py::test_partition_splits_correctly"
  - id: AC-2
    description: "Commits exactly on `adoption_date` are assigned to `after`, not `before`."
    test: "tests/unit/test_partitioner.py::test_adoption_date_commit_goes_to_after"
  - id: AC-3
    description: "Only commits within `[before_start, after_end]` are included. Commits outside the window are excluded from both lists."
    test: "tests/unit/test_partitioner.py::test_commits_outside_window_excluded"
  - id: AC-4
    description: "The input commit list is not mutated by `partition()`."
    test: "tests/unit/test_partitioner.py::test_partition_does_not_mutate_input"
  - id: AC-5
    description: "`partition()` raises `PartitionError('before window is empty')` when no commits fall in the before window."
    test: "tests/unit/test_partitioner.py::test_empty_before_raises_partition_error"

Files:
  - ai_adoption_diff/analysis/partitioner.py
  - tests/unit/test_partitioner.py

Notes: |
  `PartitionError` is defined in `ai_adoption_diff/analysis/__init__.py`.
  Only commits within `window.before_start` to `window.after_end` are considered.
  Commits before `before_start` or after `after_end` are silently excluded.

---

## Phase 3: Metrics

**Goal:** All metric modules are implemented and tested. Each metric produces a typed before/after result for any commit list.
**Gate:** All metric unit tests pass; each metric function returns identical output for identical input (determinism verified by running twice in tests).

---

## T08: Commit Size and Files-Touched Metrics

Owner:      codex
Phase:      3
Type:       none
Depends-On: T04, T07

Objective: |
  Implement the commit size distribution and files-touched-per-commit metrics,
  computing mean, median, and p90 for both before and after windows.

Acceptance-Criteria:
  - id: AC-1
    description: "`commit_size.compute(commits)` returns `CommitSizeResult(mean_lines, median_lines, p90_lines, mean_files, median_files, p90_files, sample_size)` with values matching the arithmetic computed over the fixture commits."
    test: "tests/unit/test_metrics_commit_size.py::test_compute_known_fixture"
  - id: AC-2
    description: "Given an empty list, `commit_size.compute([])` returns a result with all numeric fields `None` and `sample_size=0` without raising."
    test: "tests/unit/test_metrics_commit_size.py::test_compute_empty_list"
  - id: AC-3
    description: "Calling `commit_size.compute(commits)` twice with the same input returns identical results (determinism)."
    test: "tests/unit/test_metrics_commit_size.py::test_deterministic"
  - id: AC-4
    description: "p90 of `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]` lines is `9.1` (numpy-style interpolation). Verified by fixture test."
    test: "tests/unit/test_metrics_commit_size.py::test_p90_known_value"

Files:
  - ai_adoption_diff/metrics/commit_size.py
  - tests/unit/test_metrics_commit_size.py

Notes: |
  Use `statistics` stdlib for mean/median; use numpy for p90 (already in requirements if needed,
  or implement p90 with sorted list and linear interpolation — keep dependency minimal).
  Prefer stdlib + manual p90 over adding numpy as a dependency.

---

## T09: Churn and Rework Metrics

Owner:      codex
Phase:      3
Type:       none
Depends-On: T04, T07

Objective: |
  Implement churn rate, rework frequency, and revert/fix frequency metrics.

Acceptance-Criteria:
  - id: AC-1
    description: "`churn.compute_churn_rate(commits)` returns the ratio `sum(deletions) / sum(insertions + deletions)`. Given `[CommitRecord(insertions=10, deletions=5, ...)]`, result is `0.333...` (rounded to 3 decimal places in the result object)."
    test: "tests/unit/test_metrics_churn.py::test_churn_rate_known_value"
  - id: AC-2
    description: "When `insertions + deletions == 0` across all commits, `churn_rate` is `0.0` (no divide-by-zero)."
    test: "tests/unit/test_metrics_churn.py::test_churn_rate_no_lines_changed"
  - id: AC-3
    description: "`churn.compute_revert_frequency(commits)` returns the fraction of commits whose message matches `^(revert|fix|fixup|hotfix)\\b` (case-insensitive, word boundary). Given 2 matching out of 10, result is `0.2`."
    test: "tests/unit/test_metrics_churn.py::test_revert_frequency_known_value"
  - id: AC-4
    description: "Given an empty commit list, all churn metrics return `None` without raising."
    test: "tests/unit/test_metrics_churn.py::test_empty_list_returns_none"
  - id: AC-5
    description: "Revert frequency regex matches are case-insensitive: 'Fix: typo' matches, 'REVERT commit' matches, 'fixed bug' does not match (requires word boundary)."
    test: "tests/unit/test_metrics_churn.py::test_revert_frequency_regex_cases"

Files:
  - ai_adoption_diff/metrics/churn.py
  - tests/unit/test_metrics_churn.py

---

## T10: Test-to-Code Ratio and Boilerplate Metrics

Owner:      codex
Phase:      3
Type:       none
Depends-On: T04, T07

Objective: |
  Implement the test-to-code ratio trend metric and a boilerplate/repetition
  signal based on file path patterns.

Acceptance-Criteria:
  - id: AC-1
    description: "`test_ratio.compute_test_ratio(commits)` returns the ratio of lines changed in test files to lines changed in non-test files. Test files are identified by path containing `/test_` or `/tests/` or ending in `_test.py`. Given 40 test lines and 100 non-test lines, result is `0.4`."
    test: "tests/unit/test_metrics_test_ratio.py::test_ratio_known_value"
  - id: AC-2
    description: "When no test file changes exist, `test_ratio` is `0.0`. When all changes are in test files, `test_ratio` is `None` (no non-test denominator)."
    test: "tests/unit/test_metrics_test_ratio.py::test_ratio_edge_cases"
  - id: AC-3
    description: "`test_ratio.compute_boilerplate_signal(commits)` returns the fraction of commits that add at least one file whose name matches a boilerplate pattern: `__init__.py`, `conftest.py`, files with no content change (`insertions == 0 and deletions == 0`)."
    test: "tests/unit/test_metrics_test_ratio.py::test_boilerplate_signal_known_value"
  - id: AC-4
    description: "Given an empty commit list, all metrics return `None` without raising."
    test: "tests/unit/test_metrics_test_ratio.py::test_empty_list"

Files:
  - ai_adoption_diff/metrics/test_ratio.py
  - tests/unit/test_metrics_test_ratio.py

Notes: |
  Test file identification is path-based only (no AST parsing). The heuristics are intentionally
  simple and documented as such in code comments. `CommitRecord` must expose a `file_paths`
  field listing changed file paths — verify this is available from T04's implementation.
  If `file_paths` is missing from T04, stop and report BLOCKED with interface_mismatch type.

---

## T11: Hot-File Instability and Directory Concentration Metrics

Owner:      codex
Phase:      3
Type:       none
Depends-On: T04, T07

Objective: |
  Implement hot-file instability (files changed in >10% of commits) and
  directory-level change concentration (fraction of changes in top-3 directories).

Acceptance-Criteria:
  - id: AC-1
    description: "`hot_files.compute_hot_file_count(commits, threshold=0.1)` returns the count of unique file paths that appear in more than `threshold * len(commits)` distinct commits."
    test: "tests/unit/test_metrics_hot_files.py::test_hot_file_count_known_value"
  - id: AC-2
    description: "Given 10 commits and one file appearing in 2 of them (20%), with default threshold 0.1, that file is counted as hot. A file appearing in only 1 commit (10%) is exactly at threshold and must NOT be counted (strict greater-than)."
    test: "tests/unit/test_metrics_hot_files.py::test_threshold_boundary"
  - id: AC-3
    description: "`hot_files.compute_dir_concentration(commits)` returns the fraction of total line changes (insertions + deletions) attributable to the top-3 directories (by first path segment). Given all changes in one directory, result is `1.0`."
    test: "tests/unit/test_metrics_hot_files.py::test_dir_concentration_single_dir"
  - id: AC-4
    description: "Given an empty commit list, both functions return `None` without raising."
    test: "tests/unit/test_metrics_hot_files.py::test_empty_list"

Files:
  - ai_adoption_diff/metrics/hot_files.py
  - tests/unit/test_metrics_hot_files.py

Notes: |
  Directory is the first path segment of the file path (e.g., `src/` from `src/app/main.py`).
  If the path has no directory component (root-level file), assign it to `"."` as the directory.
  Requires `file_paths` on `CommitRecord` — same dependency note as T10.

---

## Phase 4: Reporting

**Goal:** The system can assemble all metric results into a typed report and export it as JSON and Markdown. Confidence scoring is complete.
**Gate:** `report/model.py` validates correctly; JSON and Markdown output match expected structure; confidence scorer returns correct levels for known inputs.

---

## T12: Report Model

Owner:      codex
Phase:      4
Type:       none
Depends-On: T08, T09, T10, T11

Objective: |
  Implement the Pydantic v2 AnalysisReport model that aggregates all metric
  results, window metadata, and confidence data into a single validated structure.

Acceptance-Criteria:
  - id: AC-1
    description: "`AnalysisReport.model_validate(complete_dict)` succeeds and produces a valid instance when all required fields are present."
    test: "tests/unit/test_report_model.py::test_model_validates_complete_dict"
  - id: AC-2
    description: "`AnalysisReport.model_validate(incomplete_dict)` raises `ValidationError` when required fields are missing."
    test: "tests/unit/test_report_model.py::test_model_rejects_incomplete_dict"
  - id: AC-3
    description: "`report.model_dump_json()` produces valid JSON parseable by `json.loads()` containing fields: `repo_path`, `tool_label`, `adoption_date`, `window_days`, `confidence`, `metrics`, `generated_at`, `caveats`."
    test: "tests/unit/test_report_model.py::test_model_dump_json_valid"
  - id: AC-4
    description: "`generated_at` is an ISO 8601 UTC timestamp string. When constructed by the factory, it reflects the current UTC time (within 5 seconds of `datetime.now(UTC)`)."
    test: "tests/unit/test_report_model.py::test_generated_at_is_utc_iso8601"

Files:
  - ai_adoption_diff/report/model.py
  - tests/unit/test_report_model.py

Notes: |
  All metric result fields in `AnalysisReport` are `Optional` — a metric may return `None`
  when the window has insufficient data. The model must accept and preserve `None` values.
  `tool_label` must be one of `Literal["cursor", "copilot", "claude_code", "unknown"]`.

---

## T13: Confidence Scorer

Owner:      codex
Phase:      4
Type:       none
Depends-On: T05, T06, T07

Objective: |
  Implement the confidence scorer that evaluates the reliability of the adoption
  anchor and produces a score, level, and human-readable caveats list.

Acceptance-Criteria:
  - id: AC-1
    description: "`confidence.compute(before_commits, after_commits, anchor_source='manual')` returns `ConfidenceResult(score: float, level: str, caveats: list[str])` with `score in [0.0, 1.0]` and `level in ['high', 'medium', 'low']`."
    test: "tests/unit/test_confidence.py::test_compute_returns_confidence_result"
  - id: AC-2
    description: "`level == 'high'` when `score >= 0.7`, `level == 'medium'` when `0.4 <= score < 0.7`, `level == 'low'` when `score < 0.4`."
    test: "tests/unit/test_confidence.py::test_level_thresholds"
  - id: AC-3
    description: "When `anchor_source == 'heuristic'`, `caveats` always includes the string 'Adoption date was inferred, not provided manually.'."
    test: "tests/unit/test_confidence.py::test_heuristic_anchor_caveat_present"
  - id: AC-4
    description: "When `len(before_commits) < 10`, `caveats` includes 'Before window has fewer than 10 commits.'."
    test: "tests/unit/test_confidence.py::test_small_before_window_caveat"
  - id: AC-5
    description: "When `len(after_commits) < 10`, `caveats` includes 'After window has fewer than 10 commits.'."
    test: "tests/unit/test_confidence.py::test_small_after_window_caveat"

Files:
  - ai_adoption_diff/analysis/confidence.py
  - tests/unit/test_confidence.py

---

## T14: JSON Export

Owner:      codex
Phase:      4
Type:       none
Depends-On: T12

Objective: |
  Implement the JSON exporter that writes an AnalysisReport to a file in the
  output directory.

Acceptance-Criteria:
  - id: AC-1
    description: "`json_export.write(report, output_dir)` creates `output_dir/report.json` containing valid JSON. `json.loads(path.read_text())` succeeds."
    test: "tests/unit/test_json_export.py::test_write_creates_valid_json_file"
  - id: AC-2
    description: "When `output_dir` does not exist, `write()` creates it automatically."
    test: "tests/unit/test_json_export.py::test_write_creates_output_dir"
  - id: AC-3
    description: "When `report.json` already exists, `write()` overwrites it without error."
    test: "tests/unit/test_json_export.py::test_write_overwrites_existing"
  - id: AC-4
    description: "The written JSON file contains all top-level keys: `repo_path`, `tool_label`, `adoption_date`, `window_days`, `confidence`, `metrics`, `generated_at`, `caveats`."
    test: "tests/unit/test_json_export.py::test_json_contains_required_keys"

Files:
  - ai_adoption_diff/report/json_export.py
  - tests/unit/test_json_export.py

---

## T15: Markdown and HTML Report Renderer

Owner:      codex
Phase:      4
Type:       none
Depends-On: T12, T14

Objective: |
  Implement the Jinja2-based report renderer that writes AnalysisReport to
  Markdown (always) and optionally to HTML.

Acceptance-Criteria:
  - id: AC-1
    description: "`renderer.render_markdown(report, output_dir)` creates `output_dir/report.md` containing: a header section with repo path, tool label, and adoption date; a confidence section with score, level, and all caveats; a metrics comparison table with before/after/delta columns."
    test: "tests/unit/test_renderer.py::test_render_markdown_creates_file_with_sections"
  - id: AC-2
    description: "The metrics comparison table in `report.md` has a row for each of the 9 metric categories defined in spec.md §F5. Rows with `None` values show 'N/A' in the before or after column."
    test: "tests/unit/test_renderer.py::test_markdown_table_has_all_metrics"
  - id: AC-3
    description: "`renderer.render_html(report, output_dir)` creates `output_dir/report.html` containing a `<table>` element with the same metrics data as the Markdown table."
    test: "tests/unit/test_renderer.py::test_render_html_creates_file_with_table"
  - id: AC-4
    description: "The Markdown report footer includes: tool version, generation timestamp from `report.generated_at`, and the caveat: 'Metrics show correlation only. Causality cannot be inferred.'."
    test: "tests/unit/test_renderer.py::test_markdown_footer_contains_caveat"

Files:
  - ai_adoption_diff/report/renderer.py
  - ai_adoption_diff/report/templates/report.md.j2
  - ai_adoption_diff/report/templates/report.html.j2
  - tests/unit/test_renderer.py

Notes: |
  Jinja2 templates live in `ai_adoption_diff/report/templates/`. Use `importlib.resources`
  or `pathlib` relative to `__file__` to locate templates — do not hardcode absolute paths.
  The HTML template is minimal: valid HTML5, one `<table>` with metrics, no external CSS.

---

## Phase 5: CLI Integration and Remote Support

**Goal:** Full end-to-end pipeline runs via CLI on both local and GitHub repos. Multi-repo comparison produces consistent output format.
**Gate:** End-to-end integration test passes on a real local repo; GitHub remote path tested with mocked API; `ai-diff --version` passes in CI.

---

## T16: GitHub Remote Repository Support

Owner:      codex
Phase:      5
Type:       none
Depends-On: T04

Objective: |
  Implement GitHub remote repository support: detect GitHub URLs, validate the token,
  clone the repo to a temp directory, run analysis, and clean up on exit.

Acceptance-Criteria:
  - id: AC-1
    description: "When `--repo https://github.com/owner/repo` is passed and `GITHUB_TOKEN` is set, the system clones the repo to a temp directory and runs analysis on the clone. The temp directory is deleted after the run."
    test: "tests/unit/test_github.py::test_github_url_detected_and_cleanup"
  - id: AC-2
    description: "When `--repo` is a GitHub URL and `GITHUB_TOKEN` is not set, the CLI exits 1 with message containing 'GITHUB_TOKEN is required'."
    test: "tests/unit/test_github.py::test_missing_token_exits_with_error"
  - id: AC-3
    description: "On HTTP 429 from GitHub API, `github.py` retries up to 3 times with exponential backoff (1s, 2s, 4s). After 3 retries, raises `GitHubError` with message containing 'rate limit'."
    test: "tests/unit/test_github.py::test_rate_limit_retry_and_give_up"
  - id: AC-4
    description: "`GITHUB_TOKEN` value is never present in any log message at any log level. Verified by capturing structlog output during a GitHub operation and asserting the token string is absent."
    test: "tests/unit/test_github.py::test_token_not_logged"
  - id: AC-5
    description: "On any exception during clone or analysis, the temp directory is deleted (verified by asserting `tmp_dir.exists() == False` in the except branch of the test)."
    test: "tests/unit/test_github.py::test_cleanup_on_error"

Execution-Mode: heavy
Evidence:
  - Token-not-logged test passes with a real structlog capture fixture
  - Cleanup-on-error test verifies temp directory is deleted even when analysis raises
Verifier-Focus: |
  Verify that GITHUB_TOKEN is never interpolated into any log call, error message,
  or subprocess command string. Read github.py top to bottom and grep for any string
  concatenation or f-string that includes the token variable.

Files:
  - ai_adoption_diff/ingestion/github.py
  - tests/unit/test_github.py

Notes: |
  Clone via `subprocess` calling `git clone`. Pass token as part of the URL
  (`https://x-access-token:{token}@github.com/owner/repo`) — the token is in the
  subprocess args list (not a shell string), so it does not appear in shell history.
  Never log the clone URL with the token embedded.
  Use `tempfile.mkdtemp()` and clean up in a `finally` block.

---

## T17: CLI End-to-End Integration

Owner:      codex
Phase:      5
Type:       none
Depends-On: T01, T04, T05, T06, T07, T08, T09, T10, T11, T12, T13, T14, T15

Objective: |
  Wire the full pipeline into the CLI and validate end-to-end behavior on a real
  local git repository. The `ai-diff analyze` command must run the complete pipeline
  and produce report.json and report.md.

Acceptance-Criteria:
  - id: AC-1
    description: "`ai-diff analyze --repo <tmp_git_repo> --date <known_date> --tool cursor` exits 0, creates `output/report.json` and `output/report.md`, and prints a summary line to stdout."
    test: "tests/integration/test_cli_end_to_end.py::test_analyze_full_pipeline_exits_zero"
  - id: AC-2
    description: "The generated `report.json` passes `AnalysisReport.model_validate(json.loads(path.read_text()))` without error."
    test: "tests/integration/test_cli_end_to_end.py::test_report_json_validates_against_model"
  - id: AC-3
    description: "`ai-diff analyze --repo <path>` with no `--date` runs heuristic mode and exits 0 or exits 0 with 'No adoption signals detected.' when the fixture repo has no signals."
    test: "tests/integration/test_cli_end_to_end.py::test_heuristic_mode_no_crash"
  - id: AC-4
    description: "`ai-diff analyze --repo /nonexistent` exits 1 with a message on stderr containing 'not a git repository' or 'does not exist'."
    test: "tests/integration/test_cli_end_to_end.py::test_invalid_repo_exits_one"
  - id: AC-5
    description: "`ai-diff analyze --format html ...` produces `output/report.html` in addition to `report.json` and `report.md`."
    test: "tests/integration/test_cli_end_to_end.py::test_html_format_flag_produces_html"

Files:
  - ai_adoption_diff/cli.py                         # complete implementation
  - tests/integration/test_cli_end_to_end.py

Notes: |
  The integration tests use the `tmp_git_repo` fixture from conftest.py (T04).
  The fixture must have at least 20 commits spanning at least 6 months for the
  adoption window tests to have sufficient data. Extend the fixture in conftest.py
  as part of this task if needed.
  Use Click's CliRunner with `mix_stderr=False` for integration tests.
