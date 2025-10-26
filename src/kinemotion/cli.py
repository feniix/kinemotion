"""Command-line interface for kinemotion analysis."""

import click

from .dropjump.cli import dropjump_analyze


@click.group()
@click.version_option(package_name="dropjump-analyze")
def cli() -> None:
    """Kinemotion: Video-based kinematic analysis for athletic performance."""
    pass


# Register commands from submodules
cli.add_command(dropjump_analyze)


if __name__ == "__main__":
    cli()
