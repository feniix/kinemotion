"""Command-line interface for drop jump analysis."""

import json
import sys
from pathlib import Path

import click
import numpy as np

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
@click.argument("video_path", type=click.Path(exists=True))
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
    "--smoothing-window",
    type=int,
    default=5,
    help="Smoothing window size (must be odd, >= 3)",
    show_default=True,
)
@click.option(
    "--polyorder",
    type=int,
    default=2,
    help=(
        "Polynomial order for Savitzky-Golay smoothing "
        "(2=quadratic, 3=cubic, must be < smoothing-window)"
    ),
    show_default=True,
)
@click.option(
    "--outlier-rejection/--no-outlier-rejection",
    default=True,
    help=(
        "Apply RANSAC and median-based outlier rejection to remove tracking glitches "
        "(default: enabled, +1-2%% accuracy)"
    ),
)
@click.option(
    "--bilateral-filter/--no-bilateral-filter",
    default=False,
    help=(
        "Use bilateral temporal filter for edge-preserving smoothing "
        "(default: disabled, experimental)"
    ),
)
@click.option(
    "--velocity-threshold",
    type=float,
    default=0.02,
    help="Velocity threshold for contact detection (normalized units)",
    show_default=True,
)
@click.option(
    "--min-contact-frames",
    type=int,
    default=3,
    help="Minimum frames for valid ground contact",
    show_default=True,
)
@click.option(
    "--visibility-threshold",
    type=float,
    default=0.5,
    help="Minimum landmark visibility score (0-1)",
    show_default=True,
)
@click.option(
    "--detection-confidence",
    type=float,
    default=0.5,
    help="Pose detection confidence threshold (0-1)",
    show_default=True,
)
@click.option(
    "--tracking-confidence",
    type=float,
    default=0.5,
    help="Pose tracking confidence threshold (0-1)",
    show_default=True,
)
@click.option(
    "--drop-height",
    type=float,
    default=None,
    help="Height of drop box/platform in meters (e.g., 0.40 for 40cm) - used for calibration",
)
@click.option(
    "--use-curvature/--no-curvature",
    default=True,
    help="Use trajectory curvature analysis for refining transitions (default: enabled)",
)
@click.option(
    "--kinematic-correction-factor",
    type=float,
    default=1.0,
    help=(
        "Correction factor for kinematic jump height (default: 1.0 = no correction). "
        "Historical testing suggested 1.35, but this is UNVALIDATED. "
        "Use --drop-height for validated measurements."
    ),
    show_default=True,
)
def dropjump_analyze(
    video_path: str,
    output: str | None,
    json_output: str | None,
    smoothing_window: int,
    polyorder: int,
    outlier_rejection: bool,
    bilateral_filter: bool,
    velocity_threshold: float,
    min_contact_frames: int,
    visibility_threshold: float,
    detection_confidence: float,
    tracking_confidence: float,
    drop_height: float | None,
    use_curvature: bool,
    kinematic_correction_factor: float,
) -> None:
    """
    Analyze drop-jump video to estimate ground contact time, flight time, and jump height.

    VIDEO_PATH: Path to the input video file
    """
    click.echo(f"Analyzing video: {video_path}", err=True)

    # Validate parameters
    if smoothing_window < 3:
        click.echo("Error: smoothing-window must be >= 3", err=True)
        sys.exit(1)

    if smoothing_window % 2 == 0:
        smoothing_window += 1
        click.echo(
            f"Adjusting smoothing-window to {smoothing_window} (must be odd)", err=True
        )

    if polyorder < 1:
        click.echo("Error: polyorder must be >= 1", err=True)
        sys.exit(1)

    if polyorder >= smoothing_window:
        click.echo(
            f"Error: polyorder ({polyorder}) must be < smoothing-window ({smoothing_window})",
            err=True,
        )
        sys.exit(1)

    try:
        # Initialize video processor
        with VideoProcessor(video_path) as video:
            click.echo(
                f"Video: {video.width}x{video.height} @ {video.fps:.2f} fps, "
                f"{video.frame_count} frames",
                err=True,
            )

            # Initialize pose tracker
            tracker = PoseTracker(
                min_detection_confidence=detection_confidence,
                min_tracking_confidence=tracking_confidence,
            )

            # Process all frames
            click.echo("Tracking pose landmarks...", err=True)
            landmarks_sequence = []
            frames = []

            frame_idx = 0
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

                    frame_idx += 1
                    bar.update(1)

            tracker.close()

            if not landmarks_sequence:
                click.echo("Error: No frames processed", err=True)
                sys.exit(1)

            # Smooth landmarks
            if outlier_rejection or bilateral_filter:
                if outlier_rejection:
                    click.echo(
                        "Smoothing landmarks with outlier rejection...", err=True
                    )
                if bilateral_filter:
                    click.echo(
                        "Using bilateral temporal filter for edge-preserving smoothing...",
                        err=True,
                    )
                smoothed_landmarks = smooth_landmarks_advanced(
                    landmarks_sequence,
                    window_length=smoothing_window,
                    polyorder=polyorder,
                    use_outlier_rejection=outlier_rejection,
                    use_bilateral=bilateral_filter,
                )
            else:
                click.echo("Smoothing landmarks...", err=True)
                smoothed_landmarks = smooth_landmarks(
                    landmarks_sequence, window_length=smoothing_window, polyorder=polyorder
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
                    position_list.append(
                        position_list[-1] if position_list else 0.5
                    )
                    visibilities_list.append(0.0)

            vertical_positions: np.ndarray = np.array(position_list)
            visibilities: np.ndarray = np.array(visibilities_list)

            # Detect ground contact
            contact_states = detect_ground_contact(
                vertical_positions,
                velocity_threshold=velocity_threshold,
                min_contact_frames=min_contact_frames,
                visibility_threshold=visibility_threshold,
                visibilities=visibilities,
                window_length=smoothing_window,
                polyorder=polyorder,
            )

            # Calculate metrics
            click.echo("Calculating metrics...", err=True)
            if drop_height:
                click.echo(
                    f"Using drop height calibration: {drop_height}m ({drop_height*100:.0f}cm)",
                    err=True,
                )
            metrics = calculate_drop_jump_metrics(
                contact_states,
                vertical_positions,
                video.fps,
                drop_height_m=drop_height,
                velocity_threshold=velocity_threshold,
                smoothing_window=smoothing_window,
                polyorder=polyorder,
                use_curvature=use_curvature,
                kinematic_correction_factor=kinematic_correction_factor,
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
                if video.display_width != video.width or video.display_height != video.height:
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
                    with click.progressbar(
                        length=len(frames), label="Rendering frames"
                    ) as bar:
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
                            bar.update(1)

                click.echo(f"Debug video saved: {output}", err=True)

            click.echo("Analysis complete!", err=True)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)
