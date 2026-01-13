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


def quality_option(func: Callable) -> Callable:  # type: ignore[type-arg]
    """Add quality preset option to CLI command."""
    return click.option(
        "--quality",
        type=click.Choice(["fast", "balanced", "accurate"], case_sensitive=False),
        default="balanced",
        help=(
            "Analysis quality preset: "
            "fast (quick, less precise), "
            "balanced (default, good for most cases), "
            "accurate (research-grade, slower)"
        ),
        show_default=True,
    )(func)


def verbose_option(func: Callable) -> Callable:  # type: ignore[type-arg]
    """Add verbose flag to CLI command."""
    return click.option(
        "--verbose",
        "-v",
        is_flag=True,
        help="Show auto-selected parameters and analysis details",
    )(func)


def batch_processing_options(func: Callable) -> Callable:  # type: ignore[type-arg]
    """Add batch processing options to CLI command."""
    func = click.option(
        "--batch",
        is_flag=True,
        help="Enable batch processing mode for multiple videos",
    )(func)
    func = click.option(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers for batch processing (default: 4)",
        show_default=True,
    )(func)
    func = click.option(
        "--output-dir",
        type=click.Path(),
        help="Directory for debug video outputs (batch mode only)",
    )(func)
    func = click.option(
        "--json-output-dir",
        type=click.Path(),
        help="Directory for JSON metrics outputs (batch mode only)",
    )(func)
    func = click.option(
        "--csv-summary",
        type=click.Path(),
        help="Path for CSV summary export (batch mode only)",
    )(func)
    return func


def common_analysis_options(func: Callable) -> Callable:  # type: ignore[type-arg]
    """Add all common analysis options (output, quality, verbose, batch).

    Combines:
    - common_output_options (--output, --json-output)
    - quality_option (--quality)
    - verbose_option (--verbose)
    - batch_processing_options (--batch, --workers, --output-dir, etc.)
    """
    func = common_output_options(func)
    func = quality_option(func)
    func = verbose_option(func)
    func = batch_processing_options(func)
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
