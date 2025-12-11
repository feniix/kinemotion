"""Shared CLI utilities for drop jump and CMJ analysis."""

import glob
from collections.abc import Callable
from pathlib import Path

import click


def common_output_options(func: Callable) -> Callable:  # type: ignore[type-arg]
    """Add common output options to CLI command."""
    func = click.option(
        "--output",
        "-o",
        type=click.Path(),
        help="Path for debug video output (optional)",
    )(func)
    func = click.option(
        "--json-output",
        "-j",
        type=click.Path(),
        help="Path for JSON metrics output (default: stdout)",
    )(func)
    return func


def collect_video_files(video_path: tuple[str, ...]) -> list[str]:
    """Expand glob patterns and collect all video files."""
    video_files: list[str] = []
    for pattern in video_path:
        expanded = glob.glob(pattern)
        if expanded:
            video_files.extend(expanded)
        elif Path(pattern).exists():
            video_files.append(pattern)
        else:
            click.echo(f"Warning: No files found for pattern: {pattern}", err=True)
    return video_files


def generate_batch_output_paths(
    video_path: str, output_dir: str | None, json_output_dir: str | None
) -> tuple[str | None, str | None]:
    """Generate output paths for debug video and JSON in batch mode.

    Args:
        video_path: Path to source video
        output_dir: Directory for debug video output (optional)
        json_output_dir: Directory for JSON metrics output (optional)

    Returns:
        Tuple of (debug_video_path, json_output_path)
    """
    out_path = None
    json_path = None
    if output_dir:
        out_path = str(Path(output_dir) / f"{Path(video_path).stem}_debug.mp4")
    if json_output_dir:
        json_path = str(Path(json_output_dir) / f"{Path(video_path).stem}.json")
    return out_path, json_path
