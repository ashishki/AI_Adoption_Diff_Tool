Project Brief
1. Project
Project name: AI Adoption Diff Tool
One-sentence summary: A tool that analyzes repository history and produces an evidence-based before/after view of how AI coding tool adoption changed development patterns.
Why this project exists: Teams are already using tools like Cursor, Copilot, and Claude Code, but they usually do not have a practical way to measure how those tools actually changed repository evolution, commit behavior, boilerplate patterns, churn, and engineering quality signals.
What success looks like in v1: A user can point the system at a repository, provide either an adoption date or an inferred-adoption mode, and receive a clear report with interpretable metrics, confidence notes, and exportable results.
2. Users and Workflows
Primary users / operators: solo developers, tech leads, engineering managers, developer productivity engineers, platform teams, AI tooling researchers
Main workflow 1: A user selects a local repository or GitHub repository, provides a tool label and adoption date, runs analysis, and receives a before/after report.
Main workflow 2: A user runs heuristic mode without a precise adoption date and receives a suggested adoption window with confidence scoring.
Main workflow 3: A user compares multiple repositories or multiple AI tools across projects using the same metric set and reporting format.
Main workflow 4: A user exports a report as JSON and human-readable Markdown or HTML for internal discussion, portfolio use, or technical review.
3. Problem and Value
Current pain point: There is no practical, developer-facing tool that helps teams inspect what changed in a repository after adopting AI coding tools.
Why existing approaches are not enough: Most current analysis is manual, academic, or ad hoc. Teams may look at commit history or anecdotal experience, but they do not have a consistent analytical layer for comparing pre- and post-adoption behavior.
Value delivered: The project turns repository history into structured evidence. It helps teams reason about AI tool adoption with actual signals instead of intuition alone.
What makes this useful: It answers a real operational question for engineering teams: did AI tooling improve speed, increase noise, change code shape, or shift maintenance patterns?
4. Scope
In scope for v1:
Git history ingestion from local repositories
Optional GitHub repository support
Manual adoption anchor date input
Heuristic adoption-window inference
Before/after comparison windows
Deterministic metric computation
Confidence-aware reporting
JSON plus Markdown or HTML export
Out of scope for v1:
Strong causal claims
Automatic judgment of which AI tool is “best”
Full cross-repo benchmarking leaderboard
Direct evaluation of .cursorrules quality
Write access to repositories
Enterprise multi-tenant SaaS deployment
5. Inputs and Outputs
Main inputs:
Local repo path or GitHub repository URL
Optional tool label: Cursor, Copilot, Claude Code, Unknown
Optional known adoption date
Optional analysis window settings
Main outputs:
Before/after comparison report
Adoption confidence score
Interpretable repository metrics
Structured export for downstream analysis
Human-readable summary with caveats
6. Core Signals and Metrics
Initial metric categories:
Commit size distribution
Files touched per commit
Churn and rework
Boilerplate or repetition signals
Test-to-code ratio trend
Revert or fix frequency
Hot-file instability
Directory-level change concentration
Metric philosophy: Metrics must be interpretable, deterministic, and presented with caveats. The system should not imply causality where only correlation exists.
7. Constraints and Design Principles
Primary design principle: The analytical core must remain deterministic.
LLM usage policy: LLMs may be used later for optional explanation, summarization, or clustering support, but not for primary metric computation.
Trust model: Raw evidence and deterministic outputs must remain the source of truth. Narrative interpretation must never override measured results.
Security posture: Read-only by default. No repository mutation. Bounded external calls. Explicit handling of tokens and secrets.
Operational posture: Start with a minimum viable analytical pipeline, not a high-autonomy agent.
8. Risks and Unknowns
Main risk 1: False causality. A repository may change for many reasons unrelated to AI tool adoption.
Main risk 2: Adoption date ambiguity. Teams often do not have one clean rollout moment.
Main risk 3: Weak metrics. Some metrics may look interesting but fail to say anything meaningful about engineering outcomes.
Main risk 4: Repository heterogeneity. Different repo types and team practices may make naive comparisons misleading.
Main risk 5: Data access variance. Some useful metadata may not be available in all repos or hosting environments.
9. Quality Bar for v1
The tool must produce stable results on the same repository and settings.
The report must clearly separate measured signals from interpretation.
The system must expose confidence and caveats instead of pretending to know more than it does.
The analysis must remain useful even when adoption detection is imperfect.
The outputs must be usable by a technical reviewer, not just visually attractive.
10. Suggested Initial Version
Recommended first version: local CLI plus report generator
Why this version first: It keeps the project simple, testable, deterministic, and aligned with an evaluation-first workflow.
Possible later extensions:
Web UI
GitHub app integration
Cross-repo comparative analysis
Rules-registry layer built on top of collected evidence
Optional LLM explanation layer
Private team dashboards
11. Notes for Architecture Phase
This project should start as a deterministic analytics system, not an autonomous agent.
The likely solution shape is Hybrid, with a deterministic core and optional LLM explanation layer later.
Likely active capability profiles for early phases:
Tool-Use: yes
Planning: possibly yes
RAG: no for v1
Agentic: no for v1
Compliance: no unless private-enterprise requirements appear
The project should prioritize evidence quality, baseline evaluation, and metric defensibility over feature breadth.