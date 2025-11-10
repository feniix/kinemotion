"""Command-line interface for drop jump analysis."""

import csv
import glob
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click
import numpy as np

from ..api import (
    DropJumpVideoConfig,
    DropJumpVideoResult,
    process_dropjump_videos_bulk,
)
from ..core.auto_tuning import (
    QualityPreset,
    analyze_video_sample,
    auto_tune_parameters,
)
from ..core.cli_utils import (
    apply_expert_param_overrides,
    determine_initial_confidence,
    print_auto_tuned_params,
    smooth_landmark_sequence,
    track_all_frames,
)
from ..core.pose import PoseTracker
from ..core.video_io import VideoProcessor
from .analysis import (
    ContactState,
    detect_ground_contact,
    extract_foot_positions_and_visibilities,
)
from .debug_overlay import DebugOverlayRenderer
from .kinematics import DropJumpMetrics, calculate_drop_jump_metrics


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
def dropjump_analyze(  # NOSONAR(S107) - Click CLI requires individual parameters for each option
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
    Analyze drop-jump video(s) to estimate ground contact time, flight time, and jump height.

    Uses intelligent auto-tuning to select optimal parameters based on video characteristics.
    Parameters are automatically adjusted for frame rate, tracking quality, and analysis preset.

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
    kinemotion dropjump-analyze videos/*.mp4 --batch \\
        --json-output-dir results/ --csv-summary summary.csv
    """
    # Expand glob patterns and collect all video files
    video_files: list[str] = []
    for pattern in video_path:
        expanded = glob.glob(pattern)
        if expanded:
            video_files.extend(expanded)
        elif Path(pattern).exists():
            # Direct path (not a glob pattern)
            video_files.append(pattern)
        else:
            click.echo(f"Warning: No files found for pattern: {pattern}", err=True)

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


def _extract_positions_and_visibilities(
    smoothed_landmarks: list,
) -> tuple[np.ndarray, np.ndarray]:
    """Extract vertical positions and visibilities from landmarks.

    Args:
        smoothed_landmarks: Smoothed landmark sequence

    Returns:
        Tuple of (vertical_positions, visibilities)
    """
    click.echo("Extracting foot positions...", err=True)
    return extract_foot_positions_and_visibilities(smoothed_landmarks)


def _create_debug_video(
    output: str,
    video: VideoProcessor,
    frames: list,
    smoothed_landmarks: list,
    contact_states: list[ContactState],
    metrics: DropJumpMetrics,
) -> None:
    """Generate debug video with overlays.

    Args:
        output: Output video path
        video: Video processor
        frames: Video frames
        smoothed_landmarks: Smoothed landmarks
        contact_states: Contact states
        metrics: Calculated metrics
    """
    click.echo(f"Generating debug video: {output}", err=True)
    if video.display_width != video.width or video.display_height != video.height:
        click.echo(f"Source video encoded: {video.width}x{video.height}", err=True)
        click.echo(
            f"Output dimensions: {video.display_width}x{video.display_height} "
            f"(respecting display aspect ratio)",
            err=True,
        )
    else:
        click.echo(
            f"Output dimensions: {video.width}x{video.height} "
            f"(matching source video aspect ratio)",
            err=True,
        )

    with DebugOverlayRenderer(
        output,
        video.width,
        video.height,
        video.display_width,
        video.display_height,
        video.fps,
    ) as renderer:
        render_bar: Any
        with click.progressbar(
            length=len(frames), label="Rendering frames"
        ) as render_bar:
            for i, frame in enumerate(frames):
                annotated = renderer.render_frame(
                    frame,
                    smoothed_landmarks[i],
                    contact_states[i],
                    i,
                    metrics,
                    use_com=False,
                )
                renderer.write_frame(annotated)
                render_bar.update(1)

    click.echo(f"Debug video saved: {output}", err=True)


def _process_single(
    video_path: str,
    output: str | None,
    json_output: str | None,
    quality: str,
    verbose: bool,
    expert_params: AnalysisParameters,
) -> None:
    """Process a single video (original CLI behavior)."""
    click.echo(f"Analyzing video: {video_path}", err=True)

    quality_preset = QualityPreset(quality.lower())

    try:
        with VideoProcessor(video_path) as video:
            click.echo(
                f"Video: {video.width}x{video.height} @ {video.fps:.2f} fps, "
                f"{video.frame_count} frames",
                err=True,
            )

            # Determine confidence levels
            detection_conf, tracking_conf = determine_initial_confidence(
                quality_preset, expert_params
            )

            # Track all frames
            tracker = PoseTracker(
                min_detection_confidence=detection_conf,
                min_tracking_confidence=tracking_conf,
            )
            frames, landmarks_sequence = track_all_frames(video, tracker)

            if not landmarks_sequence:
                click.echo("Error: No frames processed", err=True)
                sys.exit(1)

            # Auto-tune parameters
            characteristics = analyze_video_sample(
                landmarks_sequence, video.fps, video.frame_count
            )
            params = auto_tune_parameters(characteristics, quality_preset)
            params = apply_expert_param_overrides(params, expert_params)

            # Show parameters if verbose
            if verbose:
                print_auto_tuned_params(video, quality_preset, params, characteristics)

            # Apply smoothing
            smoothed_landmarks = smooth_landmark_sequence(landmarks_sequence, params)

            # Extract positions
            vertical_positions, visibilities = _extract_positions_and_visibilities(
                smoothed_landmarks
            )

            # Detect ground contact
            contact_states = detect_ground_contact(
                vertical_positions,
                velocity_threshold=params.velocity_threshold,
                min_contact_frames=params.min_contact_frames,
                visibility_threshold=params.visibility_threshold,
                visibilities=visibilities,
                window_length=params.smoothing_window,
                polyorder=params.polyorder,
            )

            # Calculate metrics
            click.echo("Calculating metrics...", err=True)
            metrics = calculate_drop_jump_metrics(
                contact_states,
                vertical_positions,
                video.fps,
                drop_start_frame=expert_params.drop_start_frame,
                velocity_threshold=params.velocity_threshold,
                smoothing_window=params.smoothing_window,
                polyorder=params.polyorder,
                use_curvature=params.use_curvature,
            )

            # Output metrics
            metrics_json = json.dumps(metrics.to_dict(), indent=2)
            if json_output:
                Path(json_output).write_text(metrics_json)
                click.echo(f"Metrics written to: {json_output}", err=True)
            else:
                click.echo(metrics_json)

            # Generate debug video if requested
            if output:
                _create_debug_video(
                    output, video, frames, smoothed_landmarks, contact_states, metrics
                )

            click.echo("Analysis complete!", err=True)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


def _setup_batch_output_dirs(
    output_dir: str | None, json_output_dir: str | None
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
        video_name = Path(video_file).stem

        debug_video = None
        if output_dir:
            debug_video = str(Path(output_dir) / f"{video_name}_debug.mp4")

        json_file = None
        if json_output_dir:
            json_file = str(Path(json_output_dir) / f"{video_name}.json")

        config = DropJumpVideoConfig(
            video_path=video_file,
            quality=quality,
            output_video=debug_video,
            json_output=json_file,
            drop_start_frame=expert_params.drop_start_frame,
            smoothing_window=expert_params.smoothing_window,
            velocity_threshold=expert_params.velocity_threshold,
            min_contact_frames=expert_params.min_contact_frames,
            visibility_threshold=expert_params.visibility_threshold,
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
            r
            for r in successful
            if r.metrics and r.metrics.ground_contact_time is not None
        ]
        with_flight = [
            r for r in successful if r.metrics and r.metrics.flight_time is not None
        ]
        with_jump = [
            r for r in successful if r.metrics and r.metrics.jump_height is not None
        ]

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
    click.echo(
        f"\nBatch processing {len(video_files)} videos with {workers} workers", err=True
    )
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
            f"[{completed}/{len(configs)}] {status} {video_name} "
            f"({result.processing_time:.1f}s)",
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
