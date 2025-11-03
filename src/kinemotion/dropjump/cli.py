"""Command-line interface for drop jump analysis."""

import csv
import glob
import json
import sys
from pathlib import Path
from typing import Any

import click
import numpy as np

from ..api import VideoConfig, VideoResult, process_videos_bulk
from ..core.auto_tuning import (
    QualityPreset,
    analyze_video_sample,
    auto_tune_parameters,
)
from ..core.pose import PoseTracker
from ..core.smoothing import smooth_landmarks, smooth_landmarks_advanced
from ..core.video_io import VideoProcessor
from .analysis import (
    compute_average_foot_position,
    detect_ground_contact,
)
from .debug_overlay import DebugOverlayRenderer
from .kinematics import calculate_drop_jump_metrics


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

    if use_batch:
        _process_batch(
            video_files,
            drop_height,
            quality,
            workers,
            output_dir,
            json_output_dir,
            csv_summary,
            drop_start_frame,
            smoothing_window,
            velocity_threshold,
            min_contact_frames,
            visibility_threshold,
            detection_confidence,
            tracking_confidence,
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
            drop_start_frame,
            smoothing_window,
            velocity_threshold,
            min_contact_frames,
            visibility_threshold,
            detection_confidence,
            tracking_confidence,
        )


def _process_single(
    video_path: str,
    output: str | None,
    json_output: str | None,
    drop_height: float,
    quality: str,
    verbose: bool,
    drop_start_frame: int | None,
    smoothing_window: int | None,
    velocity_threshold: float | None,
    min_contact_frames: int | None,
    visibility_threshold: float | None,
    detection_confidence: float | None,
    tracking_confidence: float | None,
) -> None:
    """Process a single video (original CLI behavior)."""
    click.echo(f"Analyzing video: {video_path}", err=True)

    # Convert quality string to enum
    quality_preset = QualityPreset(quality.lower())

    try:
        # Initialize video processor
        with VideoProcessor(video_path) as video:
            click.echo(
                f"Video: {video.width}x{video.height} @ {video.fps:.2f} fps, "
                f"{video.frame_count} frames",
                err=True,
            )

            # ================================================================
            # STEP 1: Auto-tune parameters based on video characteristics
            # ================================================================

            # Analyze video characteristics from a sample to determine optimal parameters
            # We'll use detection/tracking confidence from quality preset for initial tracking
            initial_detection_conf = 0.5
            initial_tracking_conf = 0.5

            if quality_preset == QualityPreset.FAST:
                initial_detection_conf = 0.3
                initial_tracking_conf = 0.3
            elif quality_preset == QualityPreset.ACCURATE:
                initial_detection_conf = 0.6
                initial_tracking_conf = 0.6

            # Override with expert values if provided
            if detection_confidence is not None:
                initial_detection_conf = detection_confidence
            if tracking_confidence is not None:
                initial_tracking_conf = tracking_confidence

            # Initialize pose tracker
            tracker = PoseTracker(
                min_detection_confidence=initial_detection_conf,
                min_tracking_confidence=initial_tracking_conf,
            )

            # Process all frames
            click.echo("Tracking pose landmarks...", err=True)
            landmarks_sequence = []
            frames = []

            bar: Any
            with click.progressbar(
                length=video.frame_count, label="Processing frames"
            ) as bar:
                while True:
                    frame = video.read_frame()
                    if frame is None:
                        break

                    frames.append(frame)
                    landmarks = tracker.process_frame(frame)
                    landmarks_sequence.append(landmarks)

                    bar.update(1)

            tracker.close()

            if not landmarks_sequence:
                click.echo("Error: No frames processed", err=True)
                sys.exit(1)

            # ================================================================
            # STEP 2: Analyze video characteristics and auto-tune parameters
            # ================================================================

            characteristics = analyze_video_sample(
                landmarks_sequence, video.fps, video.frame_count
            )

            # Auto-tune parameters based on video characteristics
            params = auto_tune_parameters(characteristics, quality_preset)

            # Apply expert overrides if provided
            if smoothing_window is not None:
                params.smoothing_window = smoothing_window
            if velocity_threshold is not None:
                params.velocity_threshold = velocity_threshold
            if min_contact_frames is not None:
                params.min_contact_frames = min_contact_frames
            if visibility_threshold is not None:
                params.visibility_threshold = visibility_threshold

            # Show selected parameters if verbose
            if verbose:
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
                click.echo(
                    f"  velocity_threshold: {params.velocity_threshold:.4f}", err=True
                )
                click.echo(
                    f"  min_contact_frames: {params.min_contact_frames}", err=True
                )
                click.echo(
                    f"  visibility_threshold: {params.visibility_threshold}", err=True
                )
                click.echo(
                    f"  detection_confidence: {params.detection_confidence}", err=True
                )
                click.echo(
                    f"  tracking_confidence: {params.tracking_confidence}", err=True
                )
                click.echo(f"  outlier_rejection: {params.outlier_rejection}", err=True)
                click.echo(f"  bilateral_filter: {params.bilateral_filter}", err=True)
                click.echo(f"  use_curvature: {params.use_curvature}", err=True)
                click.echo("=" * 60 + "\n", err=True)

            # ================================================================
            # STEP 3: Apply smoothing with auto-tuned parameters
            # ================================================================

            # Smooth landmarks using auto-tuned parameters
            if params.outlier_rejection or params.bilateral_filter:
                if params.outlier_rejection:
                    click.echo(
                        "Smoothing landmarks with outlier rejection...", err=True
                    )
                if params.bilateral_filter:
                    click.echo(
                        "Using bilateral temporal filter for edge-preserving smoothing...",
                        err=True,
                    )
                smoothed_landmarks = smooth_landmarks_advanced(
                    landmarks_sequence,
                    window_length=params.smoothing_window,
                    polyorder=params.polyorder,
                    use_outlier_rejection=params.outlier_rejection,
                    use_bilateral=params.bilateral_filter,
                )
            else:
                click.echo("Smoothing landmarks...", err=True)
                smoothed_landmarks = smooth_landmarks(
                    landmarks_sequence,
                    window_length=params.smoothing_window,
                    polyorder=params.polyorder,
                )

            # Extract vertical positions from feet
            click.echo("Extracting foot positions...", err=True)

            position_list: list[float] = []
            visibilities_list: list[float] = []

            for frame_landmarks in smoothed_landmarks:
                if frame_landmarks:
                    # Use average foot position
                    _, foot_y = compute_average_foot_position(frame_landmarks)
                    position_list.append(foot_y)

                    # Average visibility of foot landmarks
                    foot_vis = []
                    for key in [
                        "left_ankle",
                        "right_ankle",
                        "left_heel",
                        "right_heel",
                    ]:
                        if key in frame_landmarks:
                            foot_vis.append(frame_landmarks[key][2])
                    visibilities_list.append(
                        float(np.mean(foot_vis)) if foot_vis else 0.0
                    )
                else:
                    # Use previous position if available, otherwise default
                    position_list.append(position_list[-1] if position_list else 0.5)
                    visibilities_list.append(0.0)

            vertical_positions: np.ndarray = np.array(position_list)
            visibilities: np.ndarray = np.array(visibilities_list)

            # Detect ground contact using auto-tuned parameters
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
                drop_start_frame=drop_start_frame,
                velocity_threshold=params.velocity_threshold,
                smoothing_window=params.smoothing_window,
                polyorder=params.polyorder,
                use_curvature=params.use_curvature,
                kinematic_correction_factor=1.0,  # Always 1.0 now (no experimental correction)
            )

            # Output metrics as JSON
            metrics_dict = metrics.to_dict()
            metrics_json = json.dumps(metrics_dict, indent=2)

            if json_output:
                output_path = Path(json_output)
                output_path.write_text(metrics_json)
                click.echo(f"Metrics written to: {json_output}", err=True)
            else:
                click.echo(metrics_json)

            # Generate debug video if requested
            if output:
                click.echo(f"Generating debug video: {output}", err=True)
                if (
                    video.display_width != video.width
                    or video.display_height != video.height
                ):
                    click.echo(
                        f"Source video encoded: {video.width}x{video.height}",
                        err=True,
                    )
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

            click.echo("Analysis complete!", err=True)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


def _process_batch(
    video_files: list[str],
    drop_height: float,
    quality: str,
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
    """Process multiple videos in batch mode using parallel processing."""
    click.echo(
        f"\nBatch processing {len(video_files)} videos with {workers} workers", err=True
    )
    click.echo("=" * 70, err=True)

    # Create output directories if specified
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        click.echo(f"Debug videos will be saved to: {output_dir}", err=True)

    if json_output_dir:
        Path(json_output_dir).mkdir(parents=True, exist_ok=True)
        click.echo(f"JSON metrics will be saved to: {json_output_dir}", err=True)

    # Build configurations for each video
    configs: list[VideoConfig] = []
    for video_file in video_files:
        video_name = Path(video_file).stem

        # Determine output paths
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
            drop_start_frame=drop_start_frame,
            smoothing_window=smoothing_window,
            velocity_threshold=velocity_threshold,
            min_contact_frames=min_contact_frames,
            visibility_threshold=visibility_threshold,
            detection_confidence=detection_confidence,
            tracking_confidence=tracking_confidence,
        )
        configs.append(config)

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

    # Generate summary
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
            # Type assertion: filtering ensures metrics and ground_contact_time are not None
            avg_gct = sum(
                r.metrics.ground_contact_time * 1000
                for r in with_gct
                if r.metrics and r.metrics.ground_contact_time is not None
            ) / len(with_gct)
            click.echo(f"\nAverage ground contact time: {avg_gct:.1f} ms", err=True)

        if with_flight:
            # Type assertion: filtering ensures metrics and flight_time are not None
            avg_flight = sum(
                r.metrics.flight_time * 1000
                for r in with_flight
                if r.metrics and r.metrics.flight_time is not None
            ) / len(with_flight)
            click.echo(f"Average flight time: {avg_flight:.1f} ms", err=True)

        if with_jump:
            # Type assertion: filtering ensures metrics and jump_height are not None
            avg_jump = sum(
                r.metrics.jump_height
                for r in with_jump
                if r.metrics and r.metrics.jump_height is not None
            ) / len(with_jump)
            click.echo(
                f"Average jump height: {avg_jump:.3f} m ({avg_jump * 100:.1f} cm)",
                err=True,
            )

    # Export CSV summary if requested
    if csv_summary and successful:
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

    click.echo("\nBatch processing complete!", err=True)
