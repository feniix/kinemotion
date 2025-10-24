"""Command-line interface for kinemetry analysis."""

import json
import sys
from pathlib import Path

import click
import numpy as np

from .contact_detection import (
    compute_average_foot_position,
    detect_ground_contact,
)
from .i18n import _, setup_i18n
from .kinematics import calculate_drop_jump_metrics
from .pose_tracker import PoseTracker
from .smoothing import smooth_landmarks
from .video_io import DebugOverlayRenderer, VideoProcessor


@click.group()
@click.version_option(package_name="dropjump-analyze")
@click.option(
    "--language",
    "-l",
    type=click.Choice(["en", "es"], case_sensitive=False),
    default=None,
    help="Language for messages (default: system locale)",
)
def cli(language: str | None) -> None:
    """Kinemetry: Video-based kinematic analysis for athletic performance."""
    # Set up translations
    setup_i18n(language)


@cli.command(name="dropjump-analyze")
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
def dropjump_analyze(
    video_path: str,
    output: str | None,
    json_output: str | None,
    smoothing_window: int,
    velocity_threshold: float,
    min_contact_frames: int,
    visibility_threshold: float,
    detection_confidence: float,
    tracking_confidence: float,
    drop_height: float | None,
    use_curvature: bool,
) -> None:
    """
    Analyze drop-jump video to estimate ground contact time, flight time, and jump height.

    VIDEO_PATH: Path to the input video file
    """
    click.echo(_("Analyzing video: {path}").format(path=video_path), err=True)

    # Validate parameters
    if smoothing_window < 3:
        click.echo(_("Error: smoothing-window must be >= 3"), err=True)
        sys.exit(1)

    if smoothing_window % 2 == 0:
        smoothing_window += 1
        click.echo(
            _("Adjusting smoothing-window to {window} (must be odd)").format(
                window=smoothing_window
            ),
            err=True,
        )

    try:
        # Initialize video processor
        with VideoProcessor(video_path) as video:
            click.echo(
                _("Video: {width}x{height} @ {fps:.2f} fps, {frames} frames").format(
                    width=video.width,
                    height=video.height,
                    fps=video.fps,
                    frames=video.frame_count,
                ),
                err=True,
            )

            # Initialize pose tracker
            tracker = PoseTracker(
                min_detection_confidence=detection_confidence,
                min_tracking_confidence=tracking_confidence,
            )

            # Process all frames
            click.echo(_("Tracking pose landmarks..."), err=True)
            landmarks_sequence = []
            frames = []

            frame_idx = 0
            with click.progressbar(
                length=video.frame_count, label=_("Processing frames")
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
                click.echo(_("Error: No frames processed"), err=True)
                sys.exit(1)

            # Smooth landmarks
            click.echo(_("Smoothing landmarks..."), err=True)
            smoothed_landmarks = smooth_landmarks(
                landmarks_sequence, window_length=smoothing_window
            )

            # Extract foot positions
            click.echo(_("Detecting ground contact..."), err=True)
            foot_positions_list: list[float] = []
            visibilities_list: list[float] = []

            for frame_landmarks in smoothed_landmarks:
                if frame_landmarks:
                    foot_x, foot_y = compute_average_foot_position(frame_landmarks)
                    foot_positions_list.append(foot_y)

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
                    foot_positions_list.append(
                        foot_positions_list[-1] if foot_positions_list else 0.5
                    )
                    visibilities_list.append(0.0)

            foot_positions: np.ndarray = np.array(foot_positions_list)
            visibilities: np.ndarray = np.array(visibilities_list)

            # Detect ground contact
            contact_states = detect_ground_contact(
                foot_positions,
                velocity_threshold=velocity_threshold,
                min_contact_frames=min_contact_frames,
                visibility_threshold=visibility_threshold,
                visibilities=visibilities,
            )

            # Calculate metrics
            click.echo(_("Calculating metrics..."), err=True)
            if drop_height:
                click.echo(
                    _("Using drop height calibration: {height}m ({cm:.0f}cm)").format(
                        height=drop_height, cm=drop_height * 100
                    ),
                    err=True,
                )
            metrics = calculate_drop_jump_metrics(
                contact_states,
                foot_positions,
                video.fps,
                drop_height_m=drop_height,
                velocity_threshold=velocity_threshold,
                smoothing_window=smoothing_window,
                use_curvature=use_curvature,
            )

            # Output metrics as JSON
            metrics_dict = metrics.to_dict()
            metrics_json = json.dumps(metrics_dict, indent=2)

            if json_output:
                output_path = Path(json_output)
                output_path.write_text(metrics_json)
                click.echo(_("Metrics written to: {path}").format(path=json_output), err=True)
            else:
                click.echo(metrics_json)

            # Generate debug video if requested
            if output:
                click.echo(_("Generating debug video: {path}").format(path=output), err=True)
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
                        length=len(frames), label=_("Rendering frames")
                    ) as bar:
                        for i, frame in enumerate(frames):
                            annotated = renderer.render_frame(
                                frame,
                                smoothed_landmarks[i],
                                contact_states[i],
                                i,
                                metrics,
                            )
                            renderer.write_frame(annotated)
                            bar.update(1)

                click.echo(_("Debug video saved: {path}").format(path=output), err=True)

            click.echo(_("Analysis complete!"), err=True)

    except Exception as e:
        click.echo(_("Error: {message}").format(message=str(e)), err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
