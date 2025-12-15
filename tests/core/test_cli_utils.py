"""Tests for shared CLI utilities."""

from pathlib import Path

import click
from click.testing import CliRunner

from kinemotion.core.cli_utils import (
    collect_video_files,
    common_output_options,
    generate_batch_output_paths,
)


def test_collect_video_files_direct_path(tmp_path: Path) -> None:
    """Test collect_video_files with direct file path."""
    video_file = tmp_path / "video.mp4"
    video_file.touch()

    files = collect_video_files((str(video_file),))
    assert len(files) == 1
    assert files[0] == str(video_file)


def test_collect_video_files_glob(tmp_path: Path) -> None:
    """Test collect_video_files with glob pattern."""
    (tmp_path / "video1.mp4").touch()
    (tmp_path / "video2.mp4").touch()
    (tmp_path / "other.txt").touch()

    # Use relative path pattern if possible, or absolute
    pattern = str(tmp_path / "*.mp4")
    files = collect_video_files((pattern,))
    assert len(files) == 2
    assert str(tmp_path / "video1.mp4") in files
    assert str(tmp_path / "video2.mp4") in files


def test_collect_video_files_missing(capsys: object) -> None:
    """Test collect_video_files with missing file."""
    # This prints a warning to stderr via click.echo(err=True)
    # But collect_video_files uses click.echo, so we need a context or capsys
    # Actually click.echo works without context if not using special features,
    # but capturing stderr is tricky without CliRunner or capsys.

    files = collect_video_files(("nonexistent.mp4",))
    assert len(files) == 0
    # We can't easily assert on stderr here without capturing it,
    # but the function behavior (returning empty list) is verified.


def test_generate_batch_output_paths() -> None:
    """Test generate_batch_output_paths logic."""
    video = "path/to/video.mp4"
    out_dir = "out"
    json_dir = "json"

    debug, json_path = generate_batch_output_paths(video, out_dir, json_dir)

    assert debug == "out/video_debug.mp4"
    assert json_path == "json/video.json"


def test_generate_batch_output_paths_none() -> None:
    """Test generate_batch_output_paths with None directories."""
    video = "video.mp4"

    debug, json_path = generate_batch_output_paths(video, None, None)
    assert debug is None
    assert json_path is None


def test_common_output_options() -> None:
    """Test common_output_options decorator."""

    @click.command()
    @common_output_options
    def cli(output: str | None, json_output: str | None) -> None:
        click.echo(f"out: {output}, json: {json_output}")

    runner = CliRunner()
    result = runner.invoke(cli, ["--output", "debug.mp4", "--json-output", "metrics.json"])

    assert result.exit_code == 0
    assert "out: debug.mp4" in result.output
    assert "json: metrics.json" in result.output
