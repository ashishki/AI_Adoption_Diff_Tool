"""Markdown and HTML renderers for analysis reports."""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Real
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ai_adoption_diff import __version__
from ai_adoption_diff.report.model import AnalysisReport

TEMPLATES_DIR = Path(__file__).parent / "templates"
CORRELATION_CAVEAT = "Metrics show correlation only. Causality cannot be inferred."


@dataclass(frozen=True)
class MetricRow:
    """Display data for a single report metric row."""

    label: str
    before: float | int | None
    after: float | int | None


def _build_metrics(report: AnalysisReport) -> list[MetricRow]:
    before = report.metrics.before
    after = report.metrics.after

    return [
        MetricRow("Commit size distribution", before.mean_lines, after.mean_lines),
        MetricRow("Files touched per commit", before.mean_files, after.mean_files),
        MetricRow("Churn rate", before.churn_rate, after.churn_rate),
        MetricRow("Rework frequency", before.rework_frequency, after.rework_frequency),
        MetricRow("Revert/fix frequency", before.revert_frequency, after.revert_frequency),
        MetricRow("Test-to-code ratio", before.test_ratio, after.test_ratio),
        MetricRow("Boilerplate signal", before.boilerplate_signal, after.boilerplate_signal),
        MetricRow("Hot-file instability", before.hot_file_count, after.hot_file_count),
        MetricRow("Directory concentration", before.dir_concentration, after.dir_concentration),
    ]


def _format_number(value: float | int) -> str:
    if isinstance(value, int):
        return str(value)
    formatted = f"{value:.3f}".rstrip("0").rstrip(".")
    return formatted if formatted != "-0" else "0"


def _format_value(value: object) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, Real) and not isinstance(value, bool):
        return _format_number(float(value) if not isinstance(value, int) else value)
    return str(value)


def _format_delta(before: float | int | None, after: float | int | None) -> str:
    if before is None or after is None:
        return "N/A"
    delta = after - before
    return _format_number(delta)


def _environment() -> Environment:
    environment = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    environment.globals.update(
        format_value=_format_value,
        format_delta=_format_delta,
        tool_version=__version__,
        correlation_caveat=CORRELATION_CAVEAT,
    )
    return environment


def _render_to_path(
    report: AnalysisReport, output_dir: Path | str, template_name: str, filename: str
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    template = _environment().get_template(template_name)
    rendered = template.render(report=report, metrics=_build_metrics(report))

    report_path = output_path / filename
    report_path.write_text(rendered, encoding="utf-8")
    return report_path


def render_markdown(report: AnalysisReport, output_dir: Path | str) -> Path:
    """Write a Markdown report to ``output_dir/report.md`` and return the file path."""

    return _render_to_path(report, output_dir, "report.md.j2", "report.md")


def render_html(report: AnalysisReport, output_dir: Path | str) -> Path:
    """Write an HTML report to ``output_dir/report.html`` and return the file path."""

    return _render_to_path(report, output_dir, "report.html.j2", "report.html")
