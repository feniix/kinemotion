"""Command-line interface for counter movement jump (CMJ) analysis."""

import glob
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click
import numpy as np

from ..core.auto_tuning import (
    QualityPreset,
    analyze_video_sample,
    auto_tune_parameters,
)
from ..core.cli_utils import (
    apply_expert_param_overrides,
    common_output_options,
    determine_initial_confidence,
    print_auto_tuned_params,
    smooth_landmark_sequence,
    track_all_frames,
)
from ..core.pose import PoseTracker
from ..core.video_io import VideoProcessor
from .analysis import detect_cmj_phases
from .debug_overlay import CMJDebugOverlayRenderer
from .kinematics import CMJMetrics, calculate_cmj_metrics


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


def _collect_video_files(video_path: tuple[str, ...]) -> list[str]:
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


def _generate_output_paths(
    video: str, output_dir: str | None, json_output_dir: str | None
) -> tuple[str | None, str | None]:
    """Generate output paths for debug video and JSON."""
    out_path = None
    json_path = None
    if output_dir:
        out_path = str(Path(output_dir) / f"{Path(video).stem}_debug.mp4")
    if json_output_dir:
        json_path = str(Path(json_output_dir) / f"{Path(video).stem}.json")
    return out_path, json_path


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
            out_path, json_path = _generate_output_paths(
                video, output_dir, json_output_dir
            )
            _process_single(
                video, out_path, json_path, quality_preset, verbose, expert_params
            )
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
def cmj_analyze(  # NOSONAR(S107) - Click CLI requires individual parameters for each option
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
    Analyze counter movement jump (CMJ) video(s) to estimate jump performance metrics.

    Uses intelligent auto-tuning to select optimal parameters based on video characteristics.
    Parameters are automatically adjusted for frame rate, tracking quality, and analysis preset.

    VIDEO_PATH: Path(s) to video file(s). Supports glob patterns in batch mode.

    Examples:

    \\b
    # Basic analysis
    kinemotion cmj-analyze video.mp4

    \\b
    # With debug video output
    kinemotion cmj-analyze video.mp4 --output debug.mp4

    \\b
    # Batch mode with glob pattern
    kinemotion cmj-analyze videos/*.mp4 --batch --workers 4

    \\b
    # Batch with output directories
    kinemotion cmj-analyze videos/*.mp4 --batch \\
        --json-output-dir results/ --csv-summary summary.csv
    """
    # Expand glob patterns and collect all video files
    video_files = _collect_video_files(video_path)

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


def _get_foot_position(frame_landmarks: dict | None, last_position: float) -> float:
    """Extract average foot position from frame landmarks."""
    if not frame_landmarks:
        return last_position

    # Average foot position (ankles and heels)
    foot_y_values = []
    for key in ["left_ankle", "right_ankle", "left_heel", "right_heel"]:
        if key in frame_landmarks:
            foot_y_values.append(frame_landmarks[key][1])

    if foot_y_values:
        return float(np.mean(foot_y_values))
    return last_position


def _extract_positions_from_landmarks(
    smoothed_landmarks: list,
) -> tuple[np.ndarray, str]:
    """Extract vertical foot positions from landmarks.

    Args:
        smoothed_landmarks: Smoothed landmark sequence

    Returns:
        Tuple of (positions array, tracking method name)
    """
    click.echo("Extracting foot positions...", err=True)
    position_list: list[float] = []

    for frame_landmarks in smoothed_landmarks:
        last_pos = position_list[-1] if position_list else 0.5
        position = _get_foot_position(frame_landmarks, last_pos)
        position_list.append(position)

    return np.array(position_list), "foot"


def _process_single(
    video_path: str,
    output: str | None,
    json_output: str | None,
    quality_preset: QualityPreset,
    verbose: bool,
    expert_params: AnalysisParameters,
) -> None:
    """Process a single CMJ video."""
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

            # Calculate countermovement threshold (FPS-adjusted)
            # Base: +0.015 at 30fps (POSITIVE for downward motion in normalized coords)
            countermovement_threshold = 0.015 * (30.0 / video.fps)
            if expert_params.countermovement_threshold is not None:
                countermovement_threshold = expert_params.countermovement_threshold

            # Show parameters if verbose
            if verbose:
                print_auto_tuned_params(
                    video,
                    quality_preset,
                    params,
                    extra_params={
                        "countermovement_threshold": countermovement_threshold
                    },
                )

            # Apply smoothing
            smoothed_landmarks = smooth_landmark_sequence(landmarks_sequence, params)

            # Extract foot positions
            vertical_positions, tracking_method = _extract_positions_from_landmarks(
                smoothed_landmarks
            )

            # Detect CMJ phases
            click.echo("Detecting CMJ phases...", err=True)
            phases = detect_cmj_phases(
                vertical_positions,
                video.fps,
                window_length=params.smoothing_window,
                polyorder=params.polyorder,
            )

            if phases is None:
                click.echo("Error: Could not detect CMJ phases", err=True)
                sys.exit(1)

            standing_end, lowest_point, takeoff_frame, landing_frame = phases

            # Calculate metrics
            click.echo("Calculating metrics...", err=True)

            # Compute SIGNED velocities for CMJ metrics (need direction info)
            from .analysis import compute_signed_velocity

            velocities = compute_signed_velocity(
                vertical_positions,
                window_length=params.smoothing_window,
                polyorder=params.polyorder,
            )

            metrics = calculate_cmj_metrics(
                vertical_positions,
                velocities,
                standing_end,
                lowest_point,
                takeoff_frame,
                landing_frame,
                video.fps,
                tracking_method=tracking_method,
            )

            # Output results
            _output_results(metrics, json_output)

            # Generate debug video if requested
            if output:
                _create_debug_video(output, video, frames, smoothed_landmarks, metrics)

    except Exception as e:
        click.echo(f"Error processing video: {e}", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)


def _create_debug_video(
    output: str,
    video: VideoProcessor,
    frames: list,
    smoothed_landmarks: list,
    metrics: CMJMetrics,
) -> None:
    """Generate debug video with overlays.

    Args:
        output: Output video path
        video: Video processor
        frames: Video frames
        smoothed_landmarks: Smoothed landmarks
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

    with CMJDebugOverlayRenderer(
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
                    frame, smoothed_landmarks[i], i, metrics
                )
                renderer.write_frame(annotated)
                render_bar.update(1)

    click.echo(f"Debug video saved: {output}", err=True)


def _output_results(metrics: Any, json_output: str | None) -> None:
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
    click.echo(
        f"Countermovement depth: {metrics.countermovement_depth:.3f} m", err=True
    )
    click.echo(
        f"Eccentric duration: {metrics.eccentric_duration * 1000:.1f} ms", err=True
    )
    click.echo(
        f"Concentric duration: {metrics.concentric_duration * 1000:.1f} ms", err=True
    )
    click.echo(
        f"Total movement time: {metrics.total_movement_time * 1000:.1f} ms", err=True
    )
    click.echo(
        f"Peak eccentric velocity: {abs(metrics.peak_eccentric_velocity):.3f} m/s (downward)",
        err=True,
    )
    click.echo(
        f"Peak concentric velocity: {metrics.peak_concentric_velocity:.3f} m/s (upward)",
        err=True,
    )
    if metrics.transition_time is not None:
        click.echo(
            f"Transition time: {metrics.transition_time * 1000:.1f} ms", err=True
        )
    click.echo("=" * 60, err=True)
