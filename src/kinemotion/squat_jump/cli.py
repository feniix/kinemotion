"""Command-line interface for squat jump (SJ) analysis."""

import json
import sys
from dataclasses import dataclass

import click

from ..core.auto_tuning import QualityPreset
from ..core.cli_utils import (
    batch_processing_options,
    collect_video_files,
    common_output_options,
    generate_batch_output_paths,
    quality_option,
    verbose_option,
)
from .api import AnalysisOverrides, process_sj_video
from .kinematics import SJMetrics


@dataclass
class AnalysisParameters:
    """Expert parameters for SJ analysis customization."""

    smoothing_window: int | None = None
    velocity_threshold: float | None = None
    squat_hold_threshold: float | None = None
    min_contact_frames: int | None = None
    visibility_threshold: float | None = None
    detection_confidence: float | None = None
    tracking_confidence: float | None = None
    mass_kg: float | None = None  # For power calculations


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


@click.command(name="sj-analyze")
@click.argument("video_path", nargs=-1, type=click.Path(exists=False), required=True)
@common_output_options
@quality_option
@verbose_option
@batch_processing_options
@click.option(
    "--mass",
    type=float,
    required=True,
    help="Athlete mass in kilograms (required for power calculations)",
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
    "--squat-hold-threshold",
    type=float,
    default=None,
    help="[EXPERT] Override auto-tuned squat hold threshold",
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
def sj_analyze(  # NOSONAR(S107) - Click CLI requires individual parameters
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
    mass: float,
    smoothing_window: int | None,
    velocity_threshold: float | None,
    squat_hold_threshold: float | None,
    min_contact_frames: int | None,
    visibility_threshold: float | None,
    detection_confidence: float | None,
    tracking_confidence: float | None,
) -> None:
    """
    Analyze squat jump (SJ) video(s) to estimate jump performance metrics.

    ⚠️ EXPERIMENTAL: Squat Jump analysis is new and awaiting validation studies.
    Power/force calculations use validated Sayers regression but SJ-specific
    phase detection may need refinement based on real-world data.

    Squat Jump starts from a static squat position and focuses on explosive
    upward movement without countermovement. Power calculations require
    athlete mass for force and power metrics.

    Uses intelligent auto-tuning to select optimal parameters based on video
    characteristics. Parameters are automatically adjusted for frame rate,
    tracking quality, and analysis preset.

    VIDEO_PATH: Path(s) to video file(s). Supports glob patterns in batch mode.

    Examples:

    \b
    # Basic analysis
    kinemotion sj-analyze video.mp4 --mass 75.0

    \b
    # With debug video output
    kinemotion sj-analyze video.mp4 --mass 75.0 --output debug.mp4

    \b
    # Batch mode with glob pattern
    kinemotion sj-analyze videos/*.mp4 --batch --workers 4 --mass 75.0

    \b
    # Batch with output directories
    kinemotion sj-analyze videos/*.mp4 --batch --mass 75.0 \\
        --json-output-dir results/ --csv-summary summary.csv
    """
    # Warn user that SJ is experimental
    click.echo(
        "⚠️  WARNING: Squat Jump analysis is experimental (since v0.74.0)",
        err=True,
    )
    click.echo(
        "   Power/force calculations use validated Sayers regression, but",
        err=True,
    )
    click.echo(
        "   SJ-specific phase detection may need refinement based on real-world data.",
        err=True,
    )
    click.echo(err=True)
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
        squat_hold_threshold=squat_hold_threshold,
        min_contact_frames=min_contact_frames,
        visibility_threshold=visibility_threshold,
        detection_confidence=detection_confidence,
        tracking_confidence=tracking_confidence,
        mass_kg=mass,
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
    """Process a single SJ video by calling the API."""
    try:
        # Create overrides from expert parameters
        overrides = AnalysisOverrides(
            smoothing_window=expert_params.smoothing_window,
            velocity_threshold=expert_params.velocity_threshold,
            min_contact_frames=expert_params.min_contact_frames,
            visibility_threshold=expert_params.visibility_threshold,
        )

        # Call the API function (handles all processing logic)
        metrics = process_sj_video(
            video_path=video_path,
            quality=quality_preset.value,
            output_video=output,
            json_output=json_output,
            overrides=overrides,
            detection_confidence=expert_params.detection_confidence,
            tracking_confidence=expert_params.tracking_confidence,
            mass_kg=expert_params.mass_kg,
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


def _output_results(metrics: SJMetrics, json_output: str | None) -> None:
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
    click.echo("SJ ANALYSIS RESULTS", err=True)
    click.echo("=" * 60, err=True)
    click.echo(f"Jump height: {metrics.jump_height:.3f} m", err=True)
    click.echo(f"Flight time: {metrics.flight_time * 1000:.1f} ms", err=True)
    click.echo(f"Squat hold duration: {metrics.squat_hold_duration * 1000:.1f} ms", err=True)
    click.echo(f"Concentric duration: {metrics.concentric_duration * 1000:.1f} ms", err=True)
    click.echo(f"Peak concentric velocity: {metrics.peak_concentric_velocity:.3f} m/s", err=True)
    if metrics.peak_power is not None:
        click.echo(f"Peak power: {metrics.peak_power:.0f} W", err=True)
        click.echo(f"Mean power: {metrics.mean_power:.0f} W", err=True)
    if metrics.peak_force is not None:
        click.echo(f"Peak force: {metrics.peak_force:.0f} N", err=True)
    click.echo("=" * 60, err=True)
