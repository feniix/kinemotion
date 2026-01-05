"""Command-line interface for counter movement jump (CMJ) analysis."""

import json
import sys
from dataclasses import dataclass

import click

from ..core.auto_tuning import QualityPreset
from ..core.cli_utils import (
    collect_video_files,
    common_output_options,
    generate_batch_output_paths,
)
from .api import AnalysisOverrides, process_cmj_video
from .kinematics import CMJMetrics


@dataclass
class AnalysisParameters:
    """Expert parameters for CMJ analysis customization."""

    smoothing_window: int | None = None
    velocity_threshold: float | None = None
    countermovement_threshold: float | None = None
    min_contact_frames: int | None = None
    visibility_threshold: float | None = None
    detection_confidence: float | None = None
    tracking_confidence: float | None = None


def _process_batch_videos(
    video_files: list[str],
    output_dir: str | None,
    json_output_dir: str | None,
    quality_preset: QualityPreset,
    verbose: bool,
    expert_params: AnalysisParameters,
    workers: int,
) -> None:
    """Process multiple videos in batch mode."""
    click.echo(
        f"Batch mode: Processing {len(video_files)} video(s) with {workers} workers",
        err=True,
    )
    click.echo("Note: Batch processing not yet fully implemented", err=True)
    click.echo("Processing videos sequentially...", err=True)

    for video in video_files:
        try:
            click.echo(f"\nProcessing: {video}", err=True)
            out_path, json_path = generate_batch_output_paths(video, output_dir, json_output_dir)
            _process_single(video, out_path, json_path, quality_preset, verbose, expert_params)
        except Exception as e:
            click.echo(f"Error processing {video}: {e}", err=True)
            continue


@click.command(name="cmj-analyze")
@click.argument("video_path", nargs=-1, type=click.Path(exists=False), required=True)
@common_output_options
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
    "--smoothing-window",
    type=int,
    default=None,
    help="[EXPERT] Override auto-tuned smoothing window size",
)
@click.option(
    "--velocity-threshold",
    type=float,
    default=None,
    help="[EXPERT] Override auto-tuned velocity threshold for flight detection",
)
@click.option(
    "--countermovement-threshold",
    type=float,
    default=None,
    help="[EXPERT] Override auto-tuned countermovement threshold (negative value)",
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
def cmj_analyze(  # NOSONAR(S107) - Click CLI requires individual parameters
    # for each option
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
    smoothing_window: int | None,
    velocity_threshold: float | None,
    countermovement_threshold: float | None,
    min_contact_frames: int | None,
    visibility_threshold: float | None,
    detection_confidence: float | None,
    tracking_confidence: float | None,
) -> None:
    """
    Analyze counter movement jump (CMJ) video(s) to estimate jump performance
    metrics.

    Uses intelligent auto-tuning to select optimal parameters based on video
    characteristics. Parameters are automatically adjusted for frame rate,
    tracking quality, and analysis preset.

    VIDEO_PATH: Path(s) to video file(s). Supports glob patterns in batch mode.

    Examples:

    \b
    # Basic analysis
    kinemotion cmj-analyze video.mp4

    \b
    # With debug video output
    kinemotion cmj-analyze video.mp4 --output debug.mp4

    \b
    # Batch mode with glob pattern
    kinemotion cmj-analyze videos/*.mp4 --batch --workers 4

    \b
    # Batch with output directories
    kinemotion cmj-analyze videos/*.mp4 --batch \
        --json-output-dir results/ --csv-summary summary.csv
    """
    # Expand glob patterns and collect all video files
    video_files = collect_video_files(video_path)

    if not video_files:
        click.echo("Error: No video files found", err=True)
        sys.exit(1)

    # Determine if batch mode should be used
    use_batch = batch or len(video_files) > 1

    quality_preset = QualityPreset(quality.lower())

    # Group expert parameters
    expert_params = AnalysisParameters(
        smoothing_window=smoothing_window,
        velocity_threshold=velocity_threshold,
        countermovement_threshold=countermovement_threshold,
        min_contact_frames=min_contact_frames,
        visibility_threshold=visibility_threshold,
        detection_confidence=detection_confidence,
        tracking_confidence=tracking_confidence,
    )

    if use_batch:
        _process_batch_videos(
            video_files,
            output_dir,
            json_output_dir,
            quality_preset,
            verbose,
            expert_params,
            workers,
        )
    else:
        # Single video mode
        try:
            _process_single(
                video_files[0],
                output,
                json_output,
                quality_preset,
                verbose,
                expert_params,
            )
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)


def _process_single(
    video_path: str,
    output: str | None,
    json_output: str | None,
    quality_preset: QualityPreset,
    verbose: bool,
    expert_params: AnalysisParameters,
) -> None:
    """Process a single CMJ video by calling the API."""
    try:
        # Create overrides from expert parameters
        overrides = AnalysisOverrides(
            smoothing_window=expert_params.smoothing_window,
            velocity_threshold=expert_params.velocity_threshold,
            min_contact_frames=expert_params.min_contact_frames,
            visibility_threshold=expert_params.visibility_threshold,
        )

        # Call the API function (handles all processing logic)
        metrics = process_cmj_video(
            video_path=video_path,
            quality=quality_preset.value,
            output_video=output,
            json_output=json_output,
            overrides=overrides,
            detection_confidence=expert_params.detection_confidence,
            tracking_confidence=expert_params.tracking_confidence,
            verbose=verbose,
        )

        # Print formatted summary to stdout
        _output_results(metrics, json_output=None)  # Don't write JSON (API already did)

    except Exception as e:
        click.echo(f"Error processing video: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def _output_results(metrics: CMJMetrics, json_output: str | None) -> None:
    """Output analysis results."""
    results = metrics.to_dict()

    # Output JSON
    if json_output:
        with open(json_output, "w") as f:
            json.dump(results, f, indent=2)
        click.echo(f"Metrics saved to: {json_output}", err=True)
    else:
        # Output to stdout
        print(json.dumps(results, indent=2))

    # Print summary
    click.echo("\n" + "=" * 60, err=True)
    click.echo("CMJ ANALYSIS RESULTS", err=True)
    click.echo("=" * 60, err=True)
    click.echo(f"Jump height: {metrics.jump_height:.3f} m", err=True)
    click.echo(f"Flight time: {metrics.flight_time * 1000:.1f} ms", err=True)
    click.echo(f"Countermovement depth: {metrics.countermovement_depth:.3f} m", err=True)
    click.echo(f"Eccentric duration: {metrics.eccentric_duration * 1000:.1f} ms", err=True)
    click.echo(f"Concentric duration: {metrics.concentric_duration * 1000:.1f} ms", err=True)
    click.echo(f"Total movement time: {metrics.total_movement_time * 1000:.1f} ms", err=True)
    click.echo(
        f"Peak eccentric velocity: {abs(metrics.peak_eccentric_velocity):.3f} m/s (downward)",
        err=True,
    )
    click.echo(
        f"Peak concentric velocity: {metrics.peak_concentric_velocity:.3f} m/s (upward)",
        err=True,
    )
    if metrics.transition_time is not None:
        click.echo(f"Transition time: {metrics.transition_time * 1000:.1f} ms", err=True)
    click.echo("=" * 60, err=True)
