"""Tests for CMJ CLI."""

from click.testing import CliRunner

from kinemotion.cmj.cli import cmj_analyze


def test_cmj_analyze_help() -> None:
    """Test that the CLI help command works."""
    runner = CliRunner()
    result = runner.invoke(cmj_analyze, ["--help"])
    assert result.exit_code == 0
    assert "Analyze counter movement jump" in result.output
