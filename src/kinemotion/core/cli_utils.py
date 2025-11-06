"""Shared CLI utilities for drop jump and CMJ analysis."""

from typing import Any, Protocol

import click

from .auto_tuning import AutoTunedParams, QualityPreset
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
    params: AutoTunedParams, expert_params: ExpertParameters
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


def smooth_landmark_sequence(landmarks_sequence: list, params: AutoTunedParams) -> list:
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
