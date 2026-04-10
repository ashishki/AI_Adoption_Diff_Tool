# Phase 3 Deep Review — Cycle 3

Date: 2026-04-10
Phase: 3 (T08–T11, plus T08 from prior phase)
Reviewers: META, ARCH, CODE
Baseline post-phase: 51 tests passing (49 + 2 CODE-16 evidence tests)

---

## META Review

**Summary: WARN**

- [P1→RESOLVED] CODE-16 (age 3/3, escalated): GITHUB_TOKEN absent from config.py — **fixed this cycle** (commit ac0b90a). Tests added (commit 550573b).
- [P1→RESOLVED] CODE-17 (age 3/3, escalated): requires-python ">=3.10" vs ruff py311 — **fixed this cycle** (commit fc90e55).
- [P2] CODE-15: tmp_git_repo fixture has 5 commits/5 days; T17 needs ≥20/≥6 months. Non-blocking for Phase 4.
- [INFO] All Phase 3 tasks complete (T08–T11). Test baseline advancing: 36→41→45→49→51.
- [INFO] All Phase 4 dependencies satisfied; T12 ready.

---

## ARCH Review

**Summary: PASS**

- All Phase 3 metrics modules (churn.py, test_ratio.py, hot_files.py) follow the architecture.
- Deterministic and pure: no side effects, no external IO, no datetime.now(), no random.
- Frozen dataclasses for all result types.
- CommitRecord imported from package boundary (ai_adoption_diff.ingestion) in all three modules.
- Package structure matches ARCHITECTURE.md file tree.
- No circular import risks.
- All algorithmic choices correct: churn formula, regex pattern, test-file heuristic, strict > threshold, directory extraction.

---

## CODE Review

**Summary: WARN**

Ruff: PASS
Tests: 13/13 Phase 3 unit tests passing (49 total pre-fix)

Findings:

- [P3] CODE-18: Return-type inconsistency — T09/T10 return frozen dataclass instances with `None` metric fields for empty input; T11 returns bare `None`; T08 follows T09/T10 convention. The AC language "return None" is ambiguous. The wrapped-result convention (T08/T09/T10) is preferable for type consistency; T11 is the outlier. Standardize T11 return type to match T09/T10 before Phase 5 (non-blocking for Phase 4).
  Files: ai_adoption_diff/metrics/hot_files.py (lines 39-40, 58-59)

- [INFO] T10 test-file path detection: `"/tests/"` pattern misses `"tests/file.py"` (no leading slash). All existing tests use explicit paths with separators — not currently a bug but worth noting. No AC violation detected.

---

## Consolidated

| ID | Sev | Description | Status |
|----|-----|-------------|--------|
| CODE-16 | P1 (escalated) | GITHUB_TOKEN absent from config.py | **Resolved** — commit ac0b90a, tests 550573b |
| CODE-17 | P1 (escalated) | requires-python >=3.10 vs py311 | **Resolved** — commit fc90e55 |
| CODE-18 | P3 | Return-type inconsistency: hot_files returns bare None vs wrapped dataclass | Open — fix before Phase 5 |
| CODE-15 | P2 | tmp_git_repo fixture too small for T17 | Open — fix before T17 |

---

## Phase Gate Decision

**PROCEED to Phase 4 (T12–T15)**

All P1/P2 blockers resolved. Fix queue cleared. Baseline 51 tests passing. Ruff PASS.
