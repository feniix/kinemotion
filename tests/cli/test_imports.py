"""Tests for CLI module imports.

These tests ensure that all CLI modules can be imported without errors,
catching issues like missing imports or incorrect import statements that
would only surface when running the CLI commands.
"""

import click


def test_main_cli_imports() -> None:
    """Test that main CLI module can be imported."""
    from kinemotion.cli import cli

    # Verify the CLI group exists and is a Click Group
    assert isinstance(cli, click.Group)


def test_dropjump_cli_imports() -> None:
    """Test that drop jump CLI module can be imported."""
    from kinemotion.dropjump.cli import dropjump_analyze

    # Verify the command exists and is a Click Command
    assert isinstance(dropjump_analyze, click.Command)


def test_cmj_cli_imports() -> None:
    """Test that CMJ CLI module can be imported."""
    from kinemotion.cmj.cli import cmj_analyze

    # Verify the command exists and is a Click Command
    assert isinstance(cmj_analyze, click.Command)


def test_all_cli_commands_registered() -> None:
    """Test that all CLI commands are properly registered with the main CLI."""
    from kinemotion.cli import cli

    # Get list of registered commands
    command_names = list(cli.commands.keys())

    # Verify both commands are registered
    assert "dropjump-analyze" in command_names
    assert "cmj-analyze" in command_names


def test_cli_help_messages() -> None:
    """Test that CLI commands have help messages."""
    from kinemotion.cmj.cli import cmj_analyze
    from kinemotion.dropjump.cli import dropjump_analyze

    # Both commands should have help text as strings
    assert isinstance(dropjump_analyze.help, str)
    assert len(dropjump_analyze.help) > 0

    assert isinstance(cmj_analyze.help, str)
    assert len(cmj_analyze.help) > 0
