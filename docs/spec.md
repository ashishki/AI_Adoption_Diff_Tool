# Specification — AI Adoption Diff Tool

Version: 1.0
Last updated: 2026-04-07

---

## Overview

AI Adoption Diff Tool is a CLI analytics tool that reads a Git repository's commit history and produces a structured before/after comparison of development patterns, calibrated around a declared or inferred AI coding-tool adoption date. The system answers the question: "Did adopting this AI coding tool change how our repository evolves?" All analysis is deterministic; the system presents measured signals and confidence levels, never causal claims.

---

## User Roles

| Role | Description | What they do |
|------|-------------|-------------|
| Developer / Tech lead | Primary operator | Runs analysis on their own or their team's repo; interprets the report |
| Engineering manager | Consumer of reports | Reviews exported reports for productivity signals |
| Developer productivity engineer | Power user | Compares multiple repos or tools; exports JSON for further analysis |
| AI tooling researcher | Advanced operator | Uses JSON export for offline statistical analysis |

All roles interact through the CLI. There are no user accounts or permissions in v1.

---

## Feature Areas

### F1: Git History Ingestion

**Description:** The system reads a local Git repository's commit history and converts it into a structured, typed internal representation suitable for metric computation.

**Acceptance Criteria:**

1. Given a valid local repo path, `git_reader.py` returns a list of `CommitRecord` objects with fields: `sha`, `author_email_hash`, `timestamp`, `files_changed`, `insertions`, `deletions`, `message`. Raw `author_email` is hashed (SHA-256) before storage in memory.
2. Given a repo with zero commits, `git_reader.py` returns an empty list without error.
3. Given a repo path that does not exist or is not a git repository, the ingestion module raises `IngestionError` with a message containing the invalid path. No traceback is exposed to the user.
4. `git log` is called with `--no-merges` by default; an explicit flag `--include-merges` enables merge commits.
5. All `git` subprocess calls are logged at DEBUG level with `operation_name="git_log"` and `trace_id` bound.

**Out of scope for v1:**

- Shallow clone or partial history ingestion
- Submodule traversal
- Binary file diff analysis

---

### F2: Adoption Anchor

**Description:** The system accepts a manual adoption date (or infers one heuristically) and uses it to partition commit history into before and after analysis windows.

**Acceptance Criteria:**

1. Given `--date 2024-06-01`, the anchor module produces a `Window(before_start, adoption_date, after_end)` where `before_start = adoption_date - window_size` and `after_end = adoption_date + window_size` (default window_size: 90 days).
2. Given `--date` with a value that is not a valid ISO 8601 date (YYYY-MM-DD), the CLI exits 1 with a message: `"Invalid adoption date '{value}'. Expected format: YYYY-MM-DD."`.
3. Given `--date` that falls outside the repository's commit history range (no commits in before or after window), the CLI exits 1 with a message identifying which window has zero commits.
4. `--window-days N` overrides the default 90-day window size for both before and after periods.
5. Without `--date`, heuristic inference runs automatically (see F3).

**Out of scope for v1:**

- Multiple adoption dates (phased rollout modeling)
- Time-zone-aware anchor dates

---

### F3: Heuristic Adoption Window Inference

**Description:** When no manual date is provided, the system applies rule-based signal detection to suggest an adoption window and confidence score.

**Acceptance Criteria:**

1. Given a commit history with no `--date` argument, `heuristic.py` returns a `HeuristicResult(suggested_date, confidence_score, signals_detected)` where `confidence_score` is in `[0.0, 1.0]`.
2. Signals detected include at minimum: spike in commit frequency, sudden change in median commit size, and appearance of AI-tool-related file patterns (`.cursorrules`, `.github/copilot-instructions.md`, `.claude/`).
3. When zero signals are detected, `heuristic.py` returns `HeuristicResult(suggested_date=None, confidence_score=0.0, signals_detected=[])` and the CLI prints: `"No adoption signals detected. Provide --date to run a manual analysis."` and exits 0.
4. The `signals_detected` list contains one entry per detected signal: `{signal_name, detected_date, strength}`.
5. The suggested date is the median date of all signal detections, not the earliest.

**Out of scope for v1:**

- ML-based date inference
- Multiple tool attribution (detecting which specific tool was adopted)

---

### F4: Before/After Window Partitioning

**Description:** The system splits the ingested commit list into two non-overlapping windows for metric computation.

**Acceptance Criteria:**

1. Given a commit list and a `Window`, `partitioner.py` returns `(before_commits, after_commits)` where every commit in `before_commits` has `timestamp < adoption_date` and every commit in `after_commits` has `timestamp >= adoption_date`.
2. Commits on exactly the adoption date are assigned to the after window.
3. Given a window where `before_commits` is empty, the partitioner raises `PartitionError("before window is empty — no commits before adoption date")`.
4. Given a window where `after_commits` is empty, the partitioner raises `PartitionError("after window is empty — no commits after adoption date")`.
5. The partitioner does not mutate the input commit list.

**Out of scope for v1:**

- Multi-window partitioning (e.g., "1 month before" vs "1 month after" vs "3 months after")

---

### F5: Metric Computation

**Description:** The system computes a fixed set of deterministic metrics over each window independently and returns typed result objects.

**Metric set for v1:**

| Metric | Module | Description |
|--------|--------|-------------|
| Commit size distribution | `metrics/commit_size.py` | Mean, median, p90 of `insertions + deletions` per commit |
| Files touched per commit | `metrics/commit_size.py` | Mean, median, p90 of `files_changed` per commit |
| Churn rate | `metrics/churn.py` | Ratio of `deletions / (insertions + deletions)` |
| Rework frequency | `metrics/churn.py` | Fraction of commits modifying a file changed in the previous 7 days |
| Revert/fix frequency | `metrics/churn.py` | Fraction of commits whose message matches `^(revert|fix|fixup|hotfix)` (case-insensitive) |
| Test-to-code ratio | `metrics/test_ratio.py` | Ratio of test file changes to non-test file changes (by line count) |
| Boilerplate signal | `metrics/test_ratio.py` | Fraction of commits adding files that are identical or near-identical in structure |
| Hot-file instability | `metrics/hot_files.py` | Count of files changed in >10% of commits in the window |
| Directory concentration | `metrics/hot_files.py` | Fraction of changes concentrated in the top-3 directories |

**Acceptance Criteria:**

1. Each metric function accepts `list[CommitRecord]` and returns a typed dataclass with `before: MetricResult` and `after: MetricResult`. It never raises on an empty list — it returns `MetricResult(value=None, sample_size=0)`.
2. Given identical input, each metric function returns identical output (determinism property).
3. Churn rate is `0.0` when `insertions + deletions == 0` (no divide-by-zero).
4. Revert/fix frequency pattern matches are case-insensitive and match only the start of the commit message (anchored regex).
5. Each metric module has at least one test with a known fixture input and asserted output value.

**Out of scope for v1:**

- Code complexity metrics (cyclomatic complexity, cognitive complexity)
- Language-specific metrics
- Semantic similarity between before/after commits

---

### F6: Confidence Scoring

**Description:** The system computes a confidence score for the adoption anchor (manual or heuristic) and generates human-readable caveats for the report.

**Acceptance Criteria:**

1. `confidence.py` accepts `(before_commits, after_commits, anchor_source)` and returns `ConfidenceResult(score: float, level: str, caveats: list[str])`.
2. `score` is in `[0.0, 1.0]`. `level` is one of `"high"` (score ≥ 0.7), `"medium"` (0.4 ≤ score < 0.7), or `"low"` (score < 0.4).
3. `caveats` always includes at minimum one entry when `anchor_source == "heuristic"`: `"Adoption date was inferred, not provided manually. Results may be less reliable."`.
4. When `before_commits` has fewer than 10 commits, `caveats` includes: `"Before window has fewer than 10 commits. Statistical reliability is limited."`.
5. When `after_commits` has fewer than 10 commits, `caveats` includes: `"After window has fewer than 10 commits. Statistical reliability is limited."`.

**Out of scope for v1:**

- Bayesian confidence intervals
- Per-metric confidence scores

---

### F7: Structured Report Output

**Description:** The system assembles all analysis results into a structured `AnalysisReport` object and exports it as JSON and Markdown (optionally HTML).

**Acceptance Criteria:**

1. `AnalysisReport` is a Pydantic v2 model. `model.model_validate(data)` raises `ValidationError` for any missing required field.
2. `json_export.py` writes `report.json` to the output directory. The file is valid JSON parseable by `json.loads()`. It includes: `repo_path`, `tool_label`, `adoption_date`, `window_days`, `confidence`, `metrics` (before/after for each metric), `generated_at` (ISO 8601 UTC timestamp), `caveats`.
3. `renderer.py` writes `report.md` containing: a header section with repo and adoption metadata, a confidence section with score and caveats, a metrics comparison table (before vs after, with delta), and a footer noting the tool version and generation timestamp.
4. When `--format html` is passed, `renderer.py` also writes `report.html` using the same data rendered via Jinja2 template.
5. When the output directory does not exist, the CLI creates it automatically. When it exists, existing files are overwritten.

**Out of scope for v1:**

- PDF export
- Interactive HTML with charts
- Report versioning or history

---

### F8: CLI Interface

**Description:** The system exposes a `ai-diff` CLI command with subcommands for analysis and version reporting.

**Acceptance Criteria:**

1. `ai-diff --version` exits 0 and prints the version string matching `pyproject.toml`.
2. `ai-diff analyze --help` exits 0 and lists all flags: `--repo`, `--date`, `--tool`, `--window-days`, `--format`, `--output-dir`, `--include-merges`.
3. `ai-diff analyze --repo <path> --date <date>` runs the full pipeline and exits 0 on success.
4. `ai-diff analyze` with no `--repo` argument exits 1 with: `"Missing required argument: --repo"`.
5. All user-facing error messages go to stderr. The summary report path goes to stdout.

**Out of scope for v1:**

- `ai-diff compare` (multi-repo comparison) — planned for v2
- Interactive TUI

---

### F9: GitHub Remote Repository Support

**Description:** When `--repo` is a GitHub URL, the system uses the GitHub API to fetch repository metadata and clones the repo locally for git history analysis.

**Acceptance Criteria:**

1. `--repo https://github.com/owner/repo` triggers GitHub mode: the system validates the URL format, clones the repo to a temp directory, and runs standard analysis on the clone.
2. When `GITHUB_TOKEN` is not set in the environment and `--repo` is a GitHub URL, the CLI exits 1 with: `"GITHUB_TOKEN is required for GitHub repository access."`.
3. The cloned repo is cleaned up (temp directory deleted) after analysis completes, including on error.
4. On GitHub API rate limit (HTTP 429), the system retries with exponential backoff up to 3 times before exiting 1 with a rate-limit message.
5. `GITHUB_TOKEN` is never logged at any log level.

**Out of scope for v1:**

- GitLab, Bitbucket, or other git hosts
- SSH-based cloning
- Private repo support beyond `GITHUB_TOKEN`
