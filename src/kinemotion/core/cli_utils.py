"""Shared CLI utilities for drop jump and CMJ analysis."""

from collections.abc import Callable
from typing import Any, Protocol

import click

from .auto_tuning import AnalysisParameters, QualityPreset, VideoCharacteristics
from .pose import PoseTracker
from .smoothing import smooth_landmarks, smooth_landmarks_advanced
from .video_io import VideoProcessor


class ExpertParameters(Protocol):
    """Protocol for expert parameter overrides."""

    detection_confidence: float | None
    tracking_confidence: float | None
    smoothing_window: int | None
    velocity_threshold: float | None
    min_contact_frames: int | None
    visibility_threshold: float | None


def determine_initial_confidence(
    quality_preset: QualityPreset,
    expert_params: ExpertParameters,
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


def track_all_frames(video: VideoProcessor, tracker: PoseTracker) -> tuple[list, list]:
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


def apply_expert_param_overrides(
    params: AnalysisParameters, expert_params: ExpertParameters
) -> AnalysisParameters:
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


def print_auto_tuned_params(
    video: VideoProcessor,
    quality_preset: QualityPreset,
    params: AnalysisParameters,
    characteristics: VideoCharacteristics | None = None,
    extra_params: dict[str, Any] | None = None,
) -> None:
    """Print auto-tuned parameters in verbose mode.

    Args:
        video: Video processor
        quality_preset: Quality preset
        params: Auto-tuned parameters
        characteristics: Optional video characteristics (for tracking quality display)
        extra_params: Optional extra parameters to display (e.g., countermovement_threshold)
    """
    click.echo("\n" + "=" * 60, err=True)
    click.echo("AUTO-TUNED PARAMETERS", err=True)
    click.echo("=" * 60, err=True)
    click.echo(f"Video FPS: {video.fps:.2f}", err=True)

    if characteristics:
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

    # Print extra parameters if provided
    if extra_params:
        for key, value in extra_params.items():
            if isinstance(value, float):
                click.echo(f"  {key}: {value:.4f}", err=True)
            else:
                click.echo(f"  {key}: {value}", err=True)

    click.echo(f"  min_contact_frames: {params.min_contact_frames}", err=True)
    click.echo(f"  visibility_threshold: {params.visibility_threshold}", err=True)
    click.echo(f"  detection_confidence: {params.detection_confidence}", err=True)
    click.echo(f"  tracking_confidence: {params.tracking_confidence}", err=True)
    click.echo(f"  outlier_rejection: {params.outlier_rejection}", err=True)
    click.echo(f"  bilateral_filter: {params.bilateral_filter}", err=True)
    click.echo(f"  use_curvature: {params.use_curvature}", err=True)
    click.echo("=" * 60 + "\n", err=True)


def smooth_landmark_sequence(
    landmarks_sequence: list, params: AnalysisParameters
) -> list:
    """Apply smoothing to landmark sequence.

    Args:
        landmarks_sequence: Raw landmark sequence
        params: Auto-tuned parameters

    Returns:
        Smoothed landmark sequence
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
