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

from ..api import VideoConfig, VideoResult, process_videos_bulk
from ..core.auto_tuning import (
    AnalysisParameters as AutoTunedParams,
)
from ..core.auto_tuning import (
    QualityPreset,
    VideoCharacteristics,
    analyze_video_sample,
    auto_tune_parameters,
)
from ..core.pose import PoseTracker
from ..core.smoothing import smooth_landmarks, smooth_landmarks_advanced
from ..core.video_io import VideoProcessor
from .analysis import (
    ContactState,
    compute_average_foot_position,
    detect_ground_contact,
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
    "--drop-height",
    type=float,
    required=True,
    help=(
        "Height of drop box/platform in meters (e.g., 0.40 for 40cm box) - "
        "REQUIRED for accurate calibration"
    ),
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
def dropjump_analyze(
    video_path: tuple[str, ...],
    output: str | None,
    json_output: str | None,
    drop_height: float,
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
    kinemotion dropjump-analyze video.mp4 --drop-height 0.40

    \b
    # Batch mode with glob pattern
    kinemotion dropjump-analyze videos/*.mp4 --batch --drop-height 0.40 --workers 4

    \b
    # Batch with output directories
    kinemotion dropjump-analyze videos/*.mp4 --batch --drop-height 0.40 \\
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
    params = AnalysisParameters(
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
            drop_height,
            quality,
            workers,
            output_dir,
            json_output_dir,
            csv_summary,
            params,
        )
    else:
        # Single video mode (original behavior)
        _process_single(
            video_files[0],
            output,
            json_output,
            drop_height,
            quality,
            verbose,
            params,
        )


def _determine_initial_confidence(
    quality_preset: QualityPreset,
    expert_params: AnalysisParameters,
) -> tuple[float, float]:
    """Determine initial detection and tracking confidence levels.

    Args:
        quality_preset: Quality preset enum
        expert_params: Expert parameter overrides

    Returns:
        Tuple of (detection_confidence, tracking_confidence)
    """
    initial_detection_conf = 0.5
    initial_tracking_conf = 0.5

    if quality_preset == QualityPreset.FAST:
        initial_detection_conf = 0.3
        initial_tracking_conf = 0.3
    elif quality_preset == QualityPreset.ACCURATE:
        initial_detection_conf = 0.6
        initial_tracking_conf = 0.6

    # Override with expert values if provided
    if expert_params.detection_confidence is not None:
        initial_detection_conf = expert_params.detection_confidence
    if expert_params.tracking_confidence is not None:
        initial_tracking_conf = expert_params.tracking_confidence

    return initial_detection_conf, initial_tracking_conf


def _track_all_frames(video: VideoProcessor, tracker: PoseTracker) -> tuple[list, list]:
    """Track pose landmarks in all video frames.

    Args:
        video: Video processor
        tracker: Pose tracker

    Returns:
        Tuple of (frames, landmarks_sequence)
    """
    click.echo("Tracking pose landmarks...", err=True)
    landmarks_sequence = []
    frames = []

    bar: Any
    with click.progressbar(length=video.frame_count, label="Processing frames") as bar:
        while True:
            frame = video.read_frame()
            if frame is None:
                break

            frames.append(frame)
            landmarks = tracker.process_frame(frame)
            landmarks_sequence.append(landmarks)

            bar.update(1)

    tracker.close()
    return frames, landmarks_sequence


def _apply_expert_param_overrides(
    params: AutoTunedParams, expert_params: AnalysisParameters
) -> AutoTunedParams:
    """Apply expert parameter overrides to auto-tuned parameters.

    Args:
        params: Auto-tuned parameters
        expert_params: Expert overrides

    Returns:
        Modified params object (mutated in place)
    """
    if expert_params.smoothing_window is not None:
        params.smoothing_window = expert_params.smoothing_window
    if expert_params.velocity_threshold is not None:
        params.velocity_threshold = expert_params.velocity_threshold
    if expert_params.min_contact_frames is not None:
        params.min_contact_frames = expert_params.min_contact_frames
    if expert_params.visibility_threshold is not None:
        params.visibility_threshold = expert_params.visibility_threshold
    return params


def _print_auto_tuned_params(
    video: VideoProcessor,
    characteristics: VideoCharacteristics,
    quality_preset: QualityPreset,
    params: AutoTunedParams,
) -> None:
    """Print auto-tuned parameters in verbose mode.

    Args:
        video: Video processor
        characteristics: Video characteristics
        quality_preset: Quality preset
        params: Auto-tuned parameters
    """
    click.echo("\n" + "=" * 60, err=True)
    click.echo("AUTO-TUNED PARAMETERS", err=True)
    click.echo("=" * 60, err=True)
    click.echo(f"Video FPS: {video.fps:.2f}", err=True)
    click.echo(
        f"Tracking quality: {characteristics.tracking_quality} "
        f"(avg visibility: {characteristics.avg_visibility:.2f})",
        err=True,
    )
    click.echo(f"Quality preset: {quality_preset.value}", err=True)
    click.echo("\nSelected parameters:", err=True)
    click.echo(f"  smoothing_window: {params.smoothing_window}", err=True)
    click.echo(f"  polyorder: {params.polyorder}", err=True)
    click.echo(f"  velocity_threshold: {params.velocity_threshold:.4f}", err=True)
    click.echo(f"  min_contact_frames: {params.min_contact_frames}", err=True)
    click.echo(f"  visibility_threshold: {params.visibility_threshold}", err=True)
    click.echo(f"  detection_confidence: {params.detection_confidence}", err=True)
    click.echo(f"  tracking_confidence: {params.tracking_confidence}", err=True)
    click.echo(f"  outlier_rejection: {params.outlier_rejection}", err=True)
    click.echo(f"  bilateral_filter: {params.bilateral_filter}", err=True)
    click.echo(f"  use_curvature: {params.use_curvature}", err=True)
    click.echo("=" * 60 + "\n", err=True)


def _smooth_landmark_sequence(
    landmarks_sequence: list, params: AutoTunedParams
) -> list:
    """Apply smoothing to landmark sequence.

    Args:
        landmarks_sequence: Raw landmark sequence
        params: Auto-tuned parameters

    Returns:
        Smoothed landmarks
    """
    if params.outlier_rejection or params.bilateral_filter:
        if params.outlier_rejection:
            click.echo("Smoothing landmarks with outlier rejection...", err=True)
        if params.bilateral_filter:
            click.echo(
                "Using bilateral temporal filter for edge-preserving smoothing...",
                err=True,
            )
        return smooth_landmarks_advanced(
            landmarks_sequence,
            window_length=params.smoothing_window,
            polyorder=params.polyorder,
            use_outlier_rejection=params.outlier_rejection,
            use_bilateral=params.bilateral_filter,
        )
    else:
        click.echo("Smoothing landmarks...", err=True)
        return smooth_landmarks(
            landmarks_sequence,
            window_length=params.smoothing_window,
            polyorder=params.polyorder,
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

    position_list: list[float] = []
    visibilities_list: list[float] = []

    for frame_landmarks in smoothed_landmarks:
        if frame_landmarks:
            _, foot_y = compute_average_foot_position(frame_landmarks)
            position_list.append(foot_y)

            # Average visibility of foot landmarks
            foot_vis = []
            for key in ["left_ankle", "right_ankle", "left_heel", "right_heel"]:
                if key in frame_landmarks:
                    foot_vis.append(frame_landmarks[key][2])
            visibilities_list.append(float(np.mean(foot_vis)) if foot_vis else 0.0)
        else:
            position_list.append(position_list[-1] if position_list else 0.5)
            visibilities_list.append(0.0)

    return np.array(position_list), np.array(visibilities_list)


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
    drop_height: float,
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
            detection_conf, tracking_conf = _determine_initial_confidence(
                quality_preset, expert_params
            )

            # Track all frames
            tracker = PoseTracker(
                min_detection_confidence=detection_conf,
                min_tracking_confidence=tracking_conf,
            )
            frames, landmarks_sequence = _track_all_frames(video, tracker)

            if not landmarks_sequence:
                click.echo("Error: No frames processed", err=True)
                sys.exit(1)

            # Auto-tune parameters
            characteristics = analyze_video_sample(
                landmarks_sequence, video.fps, video.frame_count
            )
            params = auto_tune_parameters(characteristics, quality_preset)
            params = _apply_expert_param_overrides(params, expert_params)

            # Show parameters if verbose
            if verbose:
                _print_auto_tuned_params(video, characteristics, quality_preset, params)

            # Apply smoothing
            smoothed_landmarks = _smooth_landmark_sequence(landmarks_sequence, params)

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
            click.echo(
                f"Using drop height calibration: {drop_height}m ({drop_height*100:.0f}cm)",
                err=True,
            )
            metrics = calculate_drop_jump_metrics(
                contact_states,
                vertical_positions,
                video.fps,
                drop_height_m=drop_height,
                drop_start_frame=expert_params.drop_start_frame,
                velocity_threshold=params.velocity_threshold,
                smoothing_window=params.smoothing_window,
                polyorder=params.polyorder,
                use_curvature=params.use_curvature,
                kinematic_correction_factor=1.0,
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
    drop_height: float,
    quality: str,
    output_dir: str | None,
    json_output_dir: str | None,
    expert_params: AnalysisParameters,
) -> list[VideoConfig]:
    """Build configuration objects for each video.

    Args:
        video_files: List of video file paths
        drop_height: Drop height in meters
        quality: Quality preset
        output_dir: Debug video output directory
        json_output_dir: JSON metrics output directory
        expert_params: Expert parameter overrides

    Returns:
        List of VideoConfig objects
    """
    configs: list[VideoConfig] = []
    for video_file in video_files:
        video_name = Path(video_file).stem

        debug_video = None
        if output_dir:
            debug_video = str(Path(output_dir) / f"{video_name}_debug.mp4")

        json_file = None
        if json_output_dir:
            json_file = str(Path(json_output_dir) / f"{video_name}.json")

        config = VideoConfig(
            video_path=video_file,
            drop_height=drop_height,
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


def _compute_batch_statistics(results: list[VideoResult]) -> None:
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


def _write_csv_summary(
    csv_summary: str | None, results: list[VideoResult], successful: list[VideoResult]
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
            if result.success and result.metrics:
                writer.writerow(
                    [
                        Path(result.video_path).name,
                        (
                            f"{result.metrics.ground_contact_time * 1000:.1f}"
                            if result.metrics.ground_contact_time
                            else "N/A"
                        ),
                        (
                            f"{result.metrics.flight_time * 1000:.1f}"
                            if result.metrics.flight_time
                            else "N/A"
                        ),
                        (
                            f"{result.metrics.jump_height:.3f}"
                            if result.metrics.jump_height
                            else "N/A"
                        ),
                        f"{result.processing_time:.2f}",
                        "Success",
                    ]
                )
            else:
                writer.writerow(
                    [
                        Path(result.video_path).name,
                        "N/A",
                        "N/A",
                        "N/A",
                        f"{result.processing_time:.2f}",
                        f"Failed: {result.error}",
                    ]
                )

    click.echo("CSV summary written successfully", err=True)


def _process_batch(
    video_files: list[str],
    drop_height: float,
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
        video_files, drop_height, quality, output_dir, json_output_dir, expert_params
    )

    # Progress callback
    completed = 0

    def show_progress(result: VideoResult) -> None:
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
    results = process_videos_bulk(
        configs, max_workers=workers, progress_callback=show_progress
    )

    # Display statistics
    _compute_batch_statistics(results)

    # Export CSV summary if requested
    successful = [r for r in results if r.success]
    _write_csv_summary(csv_summary, results, successful)

    click.echo("\nBatch processing complete!", err=True)
