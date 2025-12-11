"""Tests for Drop Jump CLI."""

from click.testing import CliRunner

from kinemotion.dropjump.cli import dropjump_analyze


def test_dropjump_analyze_help() -> None:
    """Test that the CLI help command works."""
    runner = CliRunner()
    result = runner.invoke(dropjump_analyze, ["--help"])
    assert result.exit_code == 0
    assert "Analyze drop-jump video" in result.output
