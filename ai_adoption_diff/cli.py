"""CLI entry point for AI Adoption Diff Tool."""

from __future__ import annotations

import click

from ai_adoption_diff import __version__


@click.group()
@click.version_option(version=__version__, prog_name="ai-diff")
def cli() -> None:
    """Analyze repository changes around AI tool adoption."""


@cli.command()
def analyze() -> None:
    """Stub analysis command for the initial project skeleton."""
    click.echo("not implemented")


if __name__ == "__main__":
    cli()
