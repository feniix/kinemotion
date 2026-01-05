"""Command-line interface for drop jump analysis."""

import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import click

from ..core.cli_utils import (
    collect_video_files,
    generate_batch_output_paths,
)
from .api import (
    DropJumpVideoConfig,
    DropJumpVideoResult,
    process_dropjump_video,
    process_dropjump_videos_bulk,
)


@dataclass
class AnalysisParameters:
    """Expert parameters for analysis customization."""

    drop_start_frame: int | None = None
    smoothing_window: int | None = None
    velocity_threshold: float | None = None
    min_contact_frames: int | None = None
    visibility_threshold: float | None = None
    detection_confidence: float | None = None
    tracking_confidence: float | None = None


@click.command(name="dropjump-analyze")
@click.argument("video_path", nargs=-1, type=click.Path(exists=False), required=True)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Path for debug video output (optional)",
)
@click.option(
    "--json-output",
    "-j",
    type=click.Path(),
    help="Path for JSON metrics output (default: stdout)",
)
@click.option(
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
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show auto-selected parameters and analysis details",
)
# Batch processing options
@click.option(
    "--batch",
    is_flag=True,
    help="Enable batch processing mode for multiple videos",
)
@click.option(
    "--workers",
    type=int,
    default=4,
    help="Number of parallel workers for batch processing (default: 4)",
    show_default=True,
)
@click.option(
    "--output-dir",
    type=click.Path(),
    help="Directory for debug video outputs (batch mode only)",
)
@click.option(
    "--json-output-dir",
    type=click.Path(),
    help="Directory for JSON metrics outputs (batch mode only)",
)
@click.option(
    "--csv-summary",
    type=click.Path(),
    help="Path for CSV summary export (batch mode only)",
)
# Expert parameters (hidden in help, but always available for advanced users)
@click.option(
    "--drop-start-frame",
    type=int,
    default=None,
    help="[EXPERT] Manually specify frame where drop begins (overrides auto-detection)",
)
@click.option(
    "--smoothing-window",
    type=int,
    default=None,
    help="[EXPERT] Override auto-tuned smoothing window size",
)
@click.option(
    "--velocity-threshold",
    type=float,
    default=None,
    help="[EXPERT] Override auto-tuned velocity threshold",
)
@click.option(
    "--min-contact-frames",
    type=int,
    default=None,
    help="[EXPERT] Override auto-tuned minimum contact frames",
)
@click.option(
    "--visibility-threshold",
    type=float,
    default=None,
    help="[EXPERT] Override visibility threshold",
)
@click.option(
    "--detection-confidence",
    type=float,
    default=None,
    help="[EXPERT] Override pose detection confidence",
)
@click.option(
    "--tracking-confidence",
    type=float,
    default=None,
    help="[EXPERT] Override pose tracking confidence",
)
def dropjump_analyze(  # NOSONAR(S107) - Click CLI requires individual
    # parameters for each option
    video_path: tuple[str, ...],
    output: str | None,
    json_output: str | None,
    quality: str,
    verbose: bool,
    batch: bool,
    workers: int,
    output_dir: str | None,
    json_output_dir: str | None,
    csv_summary: str | None,
    drop_start_frame: int | None,
    smoothing_window: int | None,
    velocity_threshold: float | None,
    min_contact_frames: int | None,
    visibility_threshold: float | None,
    detection_confidence: float | None,
    tracking_confidence: float | None,
) -> None:
    """
    Analyze drop-jump video(s) to estimate ground contact time, flight time,
    and jump height.

    Uses intelligent auto-tuning to select optimal parameters based on video
    characteristics. Parameters are automatically adjusted for frame rate,
    tracking quality, and analysis preset.

    VIDEO_PATH: Path(s) to video file(s). Supports glob patterns in batch mode
    (e.g., "videos/*.mp4").

    Examples:

    \b
    # Single video
    kinemotion dropjump-analyze video.mp4

    \b
    # Batch mode with glob pattern
    kinemotion dropjump-analyze videos/*.mp4 --batch --workers 4

    \b
    # Batch with output directories
    kinemotion dropjump-analyze videos/*.mp4 --batch \
        --json-output-dir results/ --csv-summary summary.csv
    """
    # Expand glob patterns and collect all video files
    video_files = collect_video_files(video_path)

    if not video_files:
        click.echo("Error: No video files found", err=True)
        sys.exit(1)

    # Determine if batch mode should be used
    use_batch = batch or len(video_files) > 1

    # Group expert parameters
    expert_params = AnalysisParameters(
        drop_start_frame=drop_start_frame,
        smoothing_window=smoothing_window,
        velocity_threshold=velocity_threshold,
        min_contact_frames=min_contact_frames,
        visibility_threshold=visibility_threshold,
        detection_confidence=detection_confidence,
        tracking_confidence=tracking_confidence,
    )

    if use_batch:
        _process_batch(
            video_files,
            quality,
            workers,
            output_dir,
            json_output_dir,
            csv_summary,
            expert_params,
        )
    else:
        # Single video mode (original behavior)
        _process_single(
            video_files[0],
            output,
            json_output,
            quality,
            verbose,
            expert_params,
        )


def _process_single(
    video_path: str,
    output: str | None,
    json_output: str | None,
    quality: str,
    verbose: bool,
    expert_params: AnalysisParameters,
) -> None:
    """Process a single video by calling the API."""
    click.echo(f"Analyzing video: {video_path}", err=True)

    try:
        # Create AnalysisOverrides if any expert parameters are set
        from .api import AnalysisOverrides

        overrides = None
        if any(
            [
                expert_params.smoothing_window is not None,
                expert_params.velocity_threshold is not None,
                expert_params.min_contact_frames is not None,
                expert_params.visibility_threshold is not None,
            ]
        ):
            overrides = AnalysisOverrides(
                smoothing_window=expert_params.smoothing_window,
                velocity_threshold=expert_params.velocity_threshold,
                min_contact_frames=expert_params.min_contact_frames,
                visibility_threshold=expert_params.visibility_threshold,
            )

        # Call the API function (handles all processing logic)
        metrics = process_dropjump_video(
            video_path=video_path,
            quality=quality,
            output_video=output,
            json_output=json_output,
            drop_start_frame=expert_params.drop_start_frame,
            overrides=overrides,
            detection_confidence=expert_params.detection_confidence,
            tracking_confidence=expert_params.tracking_confidence,
            verbose=verbose,
        )

        # Print formatted summary to stdout if no JSON output specified
        if not json_output:
            click.echo(json.dumps(metrics.to_dict(), indent=2))

        click.echo("Analysis complete!", err=True)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def _setup_batch_output_dirs(
    output_dir: str | None,
    json_output_dir: str | None,
) -> None:
    """Create output directories for batch processing.

    Args:
        output_dir: Debug video output directory
        json_output_dir: JSON metrics output directory
    """
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        click.echo(f"Debug videos will be saved to: {output_dir}", err=True)

    if json_output_dir:
        Path(json_output_dir).mkdir(parents=True, exist_ok=True)
        click.echo(f"JSON metrics will be saved to: {json_output_dir}", err=True)


def _create_video_configs(
    video_files: list[str],
    quality: str,
    output_dir: str | None,
    json_output_dir: str | None,
    expert_params: AnalysisParameters,
) -> list[DropJumpVideoConfig]:
    """Build configuration objects for each video.

    Args:
        video_files: List of video file paths
        quality: Quality preset
        output_dir: Debug video output directory
        json_output_dir: JSON metrics output directory
        expert_params: Expert parameter overrides

    Returns:
        List of DropJumpVideoConfig objects
    """
    configs: list[DropJumpVideoConfig] = []
    for video_file in video_files:
        debug_video, json_file = generate_batch_output_paths(
            video_file, output_dir, json_output_dir
        )

        # Create AnalysisOverrides if any expert parameters are set
        from .api import AnalysisOverrides

        overrides = None
        if any(
            [
                expert_params.smoothing_window is not None,
                expert_params.velocity_threshold is not None,
                expert_params.min_contact_frames is not None,
                expert_params.visibility_threshold is not None,
            ]
        ):
            overrides = AnalysisOverrides(
                smoothing_window=expert_params.smoothing_window,
                velocity_threshold=expert_params.velocity_threshold,
                min_contact_frames=expert_params.min_contact_frames,
                visibility_threshold=expert_params.visibility_threshold,
            )

        config = DropJumpVideoConfig(
            video_path=video_file,
            quality=quality,
            output_video=debug_video,
            json_output=json_file,
            drop_start_frame=expert_params.drop_start_frame,
            overrides=overrides,
            detection_confidence=expert_params.detection_confidence,
            tracking_confidence=expert_params.tracking_confidence,
        )
        configs.append(config)

    return configs


def _compute_batch_statistics(results: list[DropJumpVideoResult]) -> None:
    """Compute and display batch processing statistics.

    Args:
        results: List of video processing results
    """
    click.echo("\n" + "=" * 70, err=True)
    click.echo("BATCH PROCESSING SUMMARY", err=True)
    click.echo("=" * 70, err=True)

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    click.echo(f"Total videos: {len(results)}", err=True)
    click.echo(f"Successful: {len(successful)}", err=True)
    click.echo(f"Failed: {len(failed)}", err=True)

    if successful:
        # Calculate average metrics
        with_gct = [
            r for r in successful if r.metrics and r.metrics.ground_contact_time is not None
        ]
        with_flight = [r for r in successful if r.metrics and r.metrics.flight_time is not None]
        with_jump = [r for r in successful if r.metrics and r.metrics.jump_height is not None]

        if with_gct:
            avg_gct = sum(
                r.metrics.ground_contact_time * 1000
                for r in with_gct
                if r.metrics and r.metrics.ground_contact_time is not None
            ) / len(with_gct)
            click.echo(f"\nAverage ground contact time: {avg_gct:.1f} ms", err=True)

        if with_flight:
            avg_flight = sum(
                r.metrics.flight_time * 1000
                for r in with_flight
                if r.metrics and r.metrics.flight_time is not None
            ) / len(with_flight)
            click.echo(f"Average flight time: {avg_flight:.1f} ms", err=True)

        if with_jump:
            avg_jump = sum(
                r.metrics.jump_height
                for r in with_jump
                if r.metrics and r.metrics.jump_height is not None
            ) / len(with_jump)
            click.echo(
                f"Average jump height: {avg_jump:.3f} m ({avg_jump * 100:.1f} cm)",
                err=True,
            )


def _format_time_metric(value: float | None, multiplier: float = 1000.0) -> str:
    """Format time metric for CSV output.

    Args:
        value: Time value in seconds
        multiplier: Multiplier to convert to milliseconds (default: 1000.0)

    Returns:
        Formatted string or "N/A" if value is None
    """
    return f"{value * multiplier:.1f}" if value is not None else "N/A"


def _format_distance_metric(value: float | None) -> str:
    """Format distance metric for CSV output.

    Args:
        value: Distance value in meters

    Returns:
        Formatted string or "N/A" if value is None
    """
    return f"{value:.3f}" if value is not None else "N/A"


def _create_csv_row_from_result(result: DropJumpVideoResult) -> list[str]:
    """Create CSV row from video processing result.

    Args:
        result: Video processing result

    Returns:
        List of formatted values for CSV row
    """
    video_name = Path(result.video_path).name
    processing_time = f"{result.processing_time:.2f}"

    if result.success and result.metrics:
        return [
            video_name,
            _format_time_metric(result.metrics.ground_contact_time),
            _format_time_metric(result.metrics.flight_time),
            _format_distance_metric(result.metrics.jump_height),
            processing_time,
            "Success",
        ]
    else:
        return [
            video_name,
            "N/A",
            "N/A",
            "N/A",
            processing_time,
            f"Failed: {result.error}",
        ]


def _write_csv_summary(
    csv_summary: str | None,
    results: list[DropJumpVideoResult],
    successful: list[DropJumpVideoResult],
) -> None:
    """Write CSV summary of batch processing results.

    Args:
        csv_summary: Path to CSV output file
        results: All processing results
        successful: Successful processing results
    """
    if not csv_summary or not successful:
        return

    click.echo(f"\nExporting CSV summary to: {csv_summary}", err=True)
    Path(csv_summary).parent.mkdir(parents=True, exist_ok=True)

    with open(csv_summary, "w", newline="") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow(
            [
                "Video",
                "Ground Contact Time (ms)",
                "Flight Time (ms)",
                "Jump Height (m)",
                "Processing Time (s)",
                "Status",
            ]
        )

        # Data rows
        for result in results:
            writer.writerow(_create_csv_row_from_result(result))

    click.echo("CSV summary written successfully", err=True)


def _process_batch(
    video_files: list[str],
    quality: str,
    workers: int,
    output_dir: str | None,
    json_output_dir: str | None,
    csv_summary: str | None,
    expert_params: AnalysisParameters,
) -> None:
    """Process multiple videos in batch mode using parallel processing."""
    click.echo(f"\nBatch processing {len(video_files)} videos with {workers} workers", err=True)
    click.echo("=" * 70, err=True)

    # Setup output directories
    _setup_batch_output_dirs(output_dir, json_output_dir)

    # Create video configurations
    configs = _create_video_configs(
        video_files, quality, output_dir, json_output_dir, expert_params
    )

    # Progress callback
    completed = 0

    def show_progress(result: DropJumpVideoResult) -> None:
        nonlocal completed
        completed += 1
        status = "✓" if result.success else "✗"
        video_name = Path(result.video_path).name
        click.echo(
            f"[{completed}/{len(configs)}] {status} {video_name} ({result.processing_time:.1f}s)",
            err=True,
        )
        if not result.success:
            click.echo(f"    Error: {result.error}", err=True)

    # Process all videos
    click.echo("\nProcessing videos...", err=True)
    results = process_dropjump_videos_bulk(
        configs, max_workers=workers, progress_callback=show_progress
    )

    # Display statistics
    _compute_batch_statistics(results)

    # Export CSV summary if requested
    successful = [r for r in results if r.success]
    _write_csv_summary(csv_summary, results, successful)

    click.echo("\nBatch processing complete!", err=True)
