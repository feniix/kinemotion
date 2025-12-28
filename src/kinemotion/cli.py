"""Command-line interface for kinemotion analysis."""

import click

from .cmj.cli import cmj_analyze
from .dropjump.cli import dropjump_analyze


@click.group()
@click.version_option(package_name="dropjump-analyze")
def cli() -> None:  # type: ignore[return]
    """Kinemotion: Video-based kinematic analysis for athletic performance."""
    pass


# Register commands from submodules
# Type ignore needed because @click.group() transforms cli into a click.Group
cli.add_command(dropjump_analyze)  # type: ignore[attr-defined]
cli.add_command(cmj_analyze)  # type: ignore[attr-defined]


if __name__ == "__main__":
    cli()
