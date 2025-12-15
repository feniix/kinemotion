"Shared pipeline utilities for kinematic analysis."

from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import TypeVar

import cv2
import numpy as np

from ..cmj.analysis import compute_average_hip_position
from ..dropjump.analysis import compute_average_foot_position
from .auto_tuning import AnalysisParameters, QualityPreset, VideoCharacteristics
from .pose import PoseTracker
from .smoothing import smooth_landmarks, smooth_landmarks_advanced
from .timing import NULL_TIMER, Timer
from .video_io import VideoProcessor

TResult = TypeVar("TResult")
TConfig = TypeVar("TConfig")


def parse_quality_preset(quality: str) -> QualityPreset:
    """Parse and validate quality preset string.

    Args:
        quality: Quality preset string ('fast', 'balanced', or 'accurate')

    Returns:
        QualityPreset enum value

    Raises:
        ValueError: If quality preset is invalid
    """
    try:
        return QualityPreset(quality.lower())
    except ValueError as e:
        raise ValueError(
            f"Invalid quality preset: {quality}. Must be 'fast', 'balanced', or 'accurate'"
        ) from e


def determine_confidence_levels(
    quality_preset: QualityPreset,
    detection_confidence: float | None,
    tracking_confidence: float | None,
) -> tuple[float, float]:
    """Determine detection and tracking confidence levels.

    Args:
        quality_preset: Quality preset enum
        detection_confidence: Optional expert override for detection confidence
        tracking_confidence: Optional expert override for tracking confidence

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

    if detection_confidence is not None:
        initial_detection_conf = detection_confidence
    if tracking_confidence is not None:
        initial_tracking_conf = tracking_confidence

    return initial_detection_conf, initial_tracking_conf


def apply_expert_overrides(
    params: AnalysisParameters,
    smoothing_window: int | None,
    velocity_threshold: float | None,
    min_contact_frames: int | None,
    visibility_threshold: float | None,
) -> AnalysisParameters:
    """Apply expert parameter overrides to auto-tuned parameters.

    Args:
        params: Auto-tuned parameters object
        smoothing_window: Optional override for smoothing window
        velocity_threshold: Optional override for velocity threshold
        min_contact_frames: Optional override for minimum contact frames
        visibility_threshold: Optional override for visibility threshold

    Returns:
        Modified params object (mutated in place)
    """
    if smoothing_window is not None:
        params.smoothing_window = smoothing_window
    if velocity_threshold is not None:
        params.velocity_threshold = velocity_threshold
    if min_contact_frames is not None:
        params.min_contact_frames = min_contact_frames
    if visibility_threshold is not None:
        params.visibility_threshold = visibility_threshold
    return params


def print_verbose_parameters(
    video: VideoProcessor,
    characteristics: VideoCharacteristics,
    quality_preset: QualityPreset,
    params: AnalysisParameters,
) -> None:
    """Print auto-tuned parameters in verbose mode.

    Args:
        video: Video processor with fps and dimensions
        characteristics: Video analysis characteristics
        quality_preset: Selected quality preset
        params: Auto-tuned parameters
    """
    print("\n" + "=" * 60)
    print("AUTO-TUNED PARAMETERS")
    print("=" * 60)
    print(f"Video FPS: {video.fps:.2f}")
    print(
        f"Tracking quality: {characteristics.tracking_quality} "
        f"(avg visibility: {characteristics.avg_visibility:.2f})"
    )
    print(f"Quality preset: {quality_preset.value}")
    print("\nSelected parameters:")
    print(f"  smoothing_window: {params.smoothing_window}")
    print(f"  polyorder: {params.polyorder}")
    print(f"  velocity_threshold: {params.velocity_threshold:.4f}")
    print(f"  min_contact_frames: {params.min_contact_frames}")
    print(f"  visibility_threshold: {params.visibility_threshold}")
    print(f"  detection_confidence: {params.detection_confidence}")
    print(f"  tracking_confidence: {params.tracking_confidence}")
    print(f"  outlier_rejection: {params.outlier_rejection}")
    print(f"  bilateral_filter: {params.bilateral_filter}")
    print(f"  use_curvature: {params.use_curvature}")
    print("=" * 60 + "\n")


def _process_frames_loop(
    video: VideoProcessor,
    tracker: PoseTracker,
    step: int,
    should_resize: bool,
    debug_w: int,
    debug_h: int,
) -> tuple[list, list, list]:
    """Internal loop for processing frames to reduce complexity."""
    landmarks_sequence = []
    debug_frames = []
    frame_indices = []
    frame_idx = 0

    while True:
        frame = video.read_frame()
        if frame is None:
            break

        landmarks = tracker.process_frame(frame)
        landmarks_sequence.append(landmarks)

        if frame_idx % step == 0:
            if should_resize:
                processed_frame = cv2.resize(
                    frame, (debug_w, debug_h), interpolation=cv2.INTER_LINEAR
                )
            else:
                processed_frame = frame

            debug_frames.append(processed_frame)
            frame_indices.append(frame_idx)

        frame_idx += 1

    return debug_frames, landmarks_sequence, frame_indices


def process_all_frames(
    video: VideoProcessor,
    tracker: PoseTracker,
    verbose: bool,
    timer: Timer | None = None,
    close_tracker: bool = True,
    target_debug_fps: float = 30.0,
    max_debug_dim: int = 720,
) -> tuple[list, list, list]:
    """Process all frames from video and extract pose landmarks.

    Args:
        video: Video processor to read frames from
        tracker: Pose tracker for landmark detection
        verbose: Print progress messages
        timer: Optional Timer for measuring operations
        close_tracker: Whether to close the tracker after processing (default: True)
        target_debug_fps: Target FPS for debug video (default: 30.0)
        max_debug_dim: Max dimension for debug video frames (default: 720)

    Returns:
        Tuple of (debug_frames, landmarks_sequence, frame_indices)

    Raises:
        ValueError: If no frames could be processed
    """
    if verbose:
        print("Tracking pose landmarks...")

    timer = timer or NULL_TIMER
    step = max(1, int(video.fps / target_debug_fps))

    w, h = video.display_width, video.display_height
    scale = 1.0
    if max(w, h) > max_debug_dim:
        scale = max_debug_dim / max(w, h)

    debug_w = int(w * scale) // 2 * 2
    debug_h = int(h * scale) // 2 * 2
    should_resize = (debug_w != video.width) or (debug_h != video.height)

    with timer.measure("pose_tracking"):
        debug_frames, landmarks_sequence, frame_indices = _process_frames_loop(
            video, tracker, step, should_resize, debug_w, debug_h
        )

    if close_tracker:
        tracker.close()

    if not landmarks_sequence:
        raise ValueError("No frames could be processed from video")

    return debug_frames, landmarks_sequence, frame_indices


def apply_smoothing(
    landmarks_sequence: list,
    params: AnalysisParameters,
    verbose: bool,
    timer: Timer | None = None,
) -> list:
    """Apply smoothing to landmark sequence with auto-tuned parameters.

    Args:
        landmarks_sequence: Sequence of landmarks from all frames
        params: Auto-tuned parameters containing smoothing settings
        verbose: Print progress messages
        timer: Optional Timer for measuring operations

    Returns:
        Smoothed landmarks sequence
    """
    timer = timer or NULL_TIMER
    use_advanced = params.outlier_rejection or params.bilateral_filter

    if verbose:
        if use_advanced:
            if params.outlier_rejection:
                print("Smoothing landmarks with outlier rejection...")
            if params.bilateral_filter:
                print("Using bilateral temporal filter...")
        else:
            print("Smoothing landmarks...")

    def _run_smoothing() -> list:
        if use_advanced:
            return smooth_landmarks_advanced(
                landmarks_sequence,
                window_length=params.smoothing_window,
                polyorder=params.polyorder,
                use_outlier_rejection=params.outlier_rejection,
                use_bilateral=params.bilateral_filter,
                timer=timer,
            )
        else:
            return smooth_landmarks(
                landmarks_sequence,
                window_length=params.smoothing_window,
                polyorder=params.polyorder,
            )

    with timer.measure("smoothing"):
        return _run_smoothing()


def calculate_foot_visibility(frame_landmarks: dict) -> float:
    """Calculate average visibility of foot landmarks.

    Args:
        frame_landmarks: Dictionary of landmarks for a frame

    Returns:
        Average visibility value (0-1)
    """
    foot_keys = ["left_ankle", "right_ankle", "left_heel", "right_heel"]
    foot_vis = [frame_landmarks[key][2] for key in foot_keys if key in frame_landmarks]
    return float(np.mean(foot_vis)) if foot_vis else 0.0


def extract_vertical_positions(
    smoothed_landmarks: list,
    target: str = "foot",
) -> tuple[np.ndarray, np.ndarray]:
    """Extract vertical positions and visibilities from smoothed landmarks.

    Args:
        smoothed_landmarks: Smoothed landmark sequence
        target: Tracking target "foot" or "hip" (default: "foot")

    Returns:
        Tuple of (vertical_positions, visibilities) as numpy arrays
    """
    position_list: list[float] = []
    visibilities_list: list[float] = []

    for frame_landmarks in smoothed_landmarks:
        if frame_landmarks:
            if target == "hip":
                _, y = compute_average_hip_position(frame_landmarks)
                vis = calculate_foot_visibility(frame_landmarks)
            else:
                _, y = compute_average_foot_position(frame_landmarks)
                vis = calculate_foot_visibility(frame_landmarks)

            position_list.append(y)
            visibilities_list.append(vis)
        else:
            position_list.append(position_list[-1] if position_list else 0.5)
            visibilities_list.append(0.0)

    return np.array(position_list), np.array(visibilities_list)


def convert_timer_to_stage_names(
    timer_metrics: dict[str, float],
) -> dict[str, float]:
    """Convert timer metric names to human-readable stage names.

    Args:
        timer_metrics: Dictionary from Timer.get_metrics()

    Returns:
        Dictionary with human-readable stage names as keys
    """
    mapping = {
        "video_initialization": "Video initialization",
        "pose_tracking": "Pose tracking",
        "parameter_auto_tuning": "Parameter auto-tuning",
        "smoothing": "Smoothing",
        "vertical_position_extraction": "Vertical position extraction",
        "ground_contact_detection": "Ground contact detection",
        "metrics_calculation": "Metrics calculation",
        "quality_assessment": "Quality assessment",
        "metadata_building": "Metadata building",
        "metrics_validation": "Metrics validation",
        "phase_detection": "Phase detection",
        "json_serialization": "JSON serialization",
        "debug_video_generation": "Debug video generation",
        "debug_video_reencode": "Debug video re-encoding",
        "frame_rotation": "Frame rotation",
        "debug_video_resize": "Debug video resizing",
        "debug_video_copy": "Debug video frame copy",
        "debug_video_draw": "Debug video drawing",
        "debug_video_write": "Debug video encoding",
        # Granular metrics
        "frame_conversion": "Frame BGR-RGB conversion",
        "mediapipe_inference": "MediaPipe inference",
        "landmark_extraction": "Landmark extraction",
        "smoothing_outlier_rejection": "Smoothing (outlier rejection)",
        "smoothing_bilateral": "Smoothing (bilateral)",
        "smoothing_savgol": "Smoothing (Savitzky-Golay)",
        "cmj_compute_derivatives": "CMJ derivatives computation",
        "cmj_find_takeoff": "CMJ takeoff detection",
        "cmj_find_lowest_point": "CMJ lowest point detection",
        "cmj_find_landing": "CMJ landing detection",
        "cmj_find_standing_end": "CMJ standing end detection",
        "dj_compute_velocity": "DJ velocity computation",
        "dj_find_contact_frames": "DJ contact frame search",
        "dj_detect_drop_start": "DJ drop start detection",
        "dj_find_phases": "DJ phase finding",
        "dj_identify_contact": "DJ contact identification",
        "dj_analyze_flight": "DJ flight analysis",
    }
    return {mapping.get(k, k): v for k, v in timer_metrics.items()}


def process_videos_bulk_generic(
    configs: list[TConfig],
    processor_func: Callable[[TConfig], TResult],
    error_factory: Callable[[str, str], TResult],
    max_workers: int = 4,
    progress_callback: Callable[[TResult], None] | None = None,
) -> list[TResult]:
    """
    Generic function to process multiple videos in parallel.

    Args:
        configs: List of configuration objects
        processor_func: Function to process a single config (must be picklable)
        error_factory: Function that takes (video_path, error_msg) and returns a
            result object
        max_workers: Maximum number of parallel workers
        progress_callback: Optional callback for progress updates

    Returns:
        List of result objects
    """
    results: list[TResult] = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_config = {executor.submit(processor_func, config): config for config in configs}

        for future in as_completed(future_to_config):
            config = future_to_config[future]
            # Assume config has video_path - this is a constraint on TConfig
            # but we can't easily enforce it with TypeVar in generic way
            # without Protocol
            # For now we assume dynamic access is okay or TConfig is duck-typed
            video_path = getattr(config, "video_path", "unknown")

            try:
                result = future.result()
            except Exception as exc:
                result = error_factory(video_path, f"Unexpected error: {str(exc)}")

            results.append(result)

            if progress_callback:
                progress_callback(result)

    return results
