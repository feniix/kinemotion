"""Public API for programmatic use of kinemotion analysis."""

import time
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .core.auto_tuning import (
    AnalysisParameters,
    QualityPreset,
    VideoCharacteristics,
    analyze_video_sample,
    auto_tune_parameters,
)
from .core.pose import PoseTracker
from .core.smoothing import smooth_landmarks, smooth_landmarks_advanced
from .core.video_io import VideoProcessor
from .dropjump.analysis import (
    ContactState,
    compute_average_foot_position,
    detect_ground_contact,
)
from .dropjump.debug_overlay import DebugOverlayRenderer
from .dropjump.kinematics import DropJumpMetrics, calculate_drop_jump_metrics


def _parse_quality_preset(quality: str) -> QualityPreset:
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


def _determine_confidence_levels(
    quality_preset: QualityPreset,
    detection_confidence: float | None,
    tracking_confidence: float | None,
) -> tuple[float, float]:
    """Determine detection and tracking confidence levels.

    Confidence levels are set based on quality preset and can be overridden
    by expert parameters.

    Args:
        quality_preset: Quality preset enum
        detection_confidence: Optional expert override for detection confidence
        tracking_confidence: Optional expert override for tracking confidence

    Returns:
        Tuple of (detection_confidence, tracking_confidence)
    """
    # Set initial confidence from quality preset
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

    return initial_detection_conf, initial_tracking_conf


def _apply_expert_overrides(
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


def _print_verbose_parameters(
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


def _process_all_frames(
    video: VideoProcessor, tracker: PoseTracker, verbose: bool
) -> tuple[list, list]:
    """Process all frames from video and extract pose landmarks.

    Args:
        video: Video processor to read frames from
        tracker: Pose tracker for landmark detection
        verbose: Print progress messages

    Returns:
        Tuple of (frames, landmarks_sequence)

    Raises:
        ValueError: If no frames could be processed
    """
    if verbose:
        print("Tracking pose landmarks...")

    landmarks_sequence = []
    frames = []

    while True:
        frame = video.read_frame()
        if frame is None:
            break

        frames.append(frame)
        landmarks = tracker.process_frame(frame)
        landmarks_sequence.append(landmarks)

    tracker.close()

    if not landmarks_sequence:
        raise ValueError("No frames could be processed from video")

    return frames, landmarks_sequence


def _apply_smoothing(
    landmarks_sequence: list, params: AnalysisParameters, verbose: bool
) -> list:
    """Apply smoothing to landmark sequence with auto-tuned parameters.

    Args:
        landmarks_sequence: Sequence of landmarks from all frames
        params: Auto-tuned parameters containing smoothing settings
        verbose: Print progress messages

    Returns:
        Smoothed landmarks sequence
    """
    if params.outlier_rejection or params.bilateral_filter:
        if verbose:
            if params.outlier_rejection:
                print("Smoothing landmarks with outlier rejection...")
            if params.bilateral_filter:
                print("Using bilateral temporal filter...")
        return smooth_landmarks_advanced(
            landmarks_sequence,
            window_length=params.smoothing_window,
            polyorder=params.polyorder,
            use_outlier_rejection=params.outlier_rejection,
            use_bilateral=params.bilateral_filter,
        )
    else:
        if verbose:
            print("Smoothing landmarks...")
        return smooth_landmarks(
            landmarks_sequence,
            window_length=params.smoothing_window,
            polyorder=params.polyorder,
        )


def _extract_vertical_positions(
    smoothed_landmarks: list,
) -> tuple[np.ndarray, np.ndarray]:
    """Extract vertical foot positions and visibilities from smoothed landmarks.

    Args:
        smoothed_landmarks: Smoothed landmark sequence

    Returns:
        Tuple of (vertical_positions, visibilities) as numpy arrays
    """
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


def _generate_outputs(
    metrics: DropJumpMetrics,
    json_output: str | None,
    output_video: str | None,
    frames: list,
    smoothed_landmarks: list,
    contact_states: list[ContactState],
    video: VideoProcessor,
    verbose: bool,
) -> None:
    """Generate JSON and debug video outputs if requested.

    Args:
        metrics: Calculated drop jump metrics
        json_output: Optional path for JSON output
        output_video: Optional path for debug video
        frames: List of video frames
        smoothed_landmarks: Smoothed landmark sequence
        contact_states: Ground contact state for each frame
        video: Video processor with dimensions and fps
        verbose: Print progress messages
    """
    # Save JSON if requested
    if json_output:
        import json

        output_path = Path(json_output)
        output_path.write_text(json.dumps(metrics.to_dict(), indent=2))
        if verbose:
            print(f"Metrics written to: {json_output}")

    # Generate debug video if requested
    if output_video:
        if verbose:
            print(f"Generating debug video: {output_video}")

        with DebugOverlayRenderer(
            output_video,
            video.width,
            video.height,
            video.display_width,
            video.display_height,
            video.fps,
        ) as renderer:
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

        if verbose:
            print(f"Debug video saved: {output_video}")


@dataclass
class VideoResult:
    """Result of processing a single video."""

    video_path: str
    success: bool
    metrics: DropJumpMetrics | None = None
    error: str | None = None
    processing_time: float = 0.0


@dataclass
class VideoConfig:
    """Configuration for processing a single video."""

    video_path: str
    drop_height: float
    quality: str = "balanced"
    output_video: str | None = None
    json_output: str | None = None
    drop_start_frame: int | None = None
    smoothing_window: int | None = None
    velocity_threshold: float | None = None
    min_contact_frames: int | None = None
    visibility_threshold: float | None = None
    detection_confidence: float | None = None
    tracking_confidence: float | None = None


def process_video(
    video_path: str,
    drop_height: float,
    quality: str = "balanced",
    output_video: str | None = None,
    json_output: str | None = None,
    drop_start_frame: int | None = None,
    smoothing_window: int | None = None,
    velocity_threshold: float | None = None,
    min_contact_frames: int | None = None,
    visibility_threshold: float | None = None,
    detection_confidence: float | None = None,
    tracking_confidence: float | None = None,
    verbose: bool = False,
) -> DropJumpMetrics:
    """
    Process a single drop jump video and return metrics.

    Args:
        video_path: Path to the input video file
        drop_height: Height of drop box/platform in meters (e.g., 0.40 for 40cm)
        quality: Analysis quality preset ("fast", "balanced", or "accurate")
        output_video: Optional path for debug video output
        json_output: Optional path for JSON metrics output
        drop_start_frame: Optional manual drop start frame
        smoothing_window: Optional override for smoothing window
        velocity_threshold: Optional override for velocity threshold
        min_contact_frames: Optional override for minimum contact frames
        visibility_threshold: Optional override for visibility threshold
        detection_confidence: Optional override for pose detection confidence
        tracking_confidence: Optional override for pose tracking confidence
        verbose: Print processing details

    Returns:
        DropJumpMetrics object containing analysis results

    Raises:
        ValueError: If video cannot be processed or parameters are invalid
        FileNotFoundError: If video file does not exist
    """
    if not Path(video_path).exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Convert quality string to enum
    quality_preset = _parse_quality_preset(quality)

    # Initialize video processor
    with VideoProcessor(video_path) as video:
        if verbose:
            print(
                f"Video: {video.width}x{video.height} @ {video.fps:.2f} fps, "
                f"{video.frame_count} frames"
            )

        # Determine detection/tracking confidence levels
        detection_conf, tracking_conf = _determine_confidence_levels(
            quality_preset, detection_confidence, tracking_confidence
        )

        # Process all frames with pose tracking
        tracker = PoseTracker(
            min_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
        )
        frames, landmarks_sequence = _process_all_frames(video, tracker, verbose)

        # Analyze video characteristics and auto-tune parameters
        characteristics = analyze_video_sample(
            landmarks_sequence, video.fps, video.frame_count
        )
        params = auto_tune_parameters(characteristics, quality_preset)

        # Apply expert overrides if provided
        params = _apply_expert_overrides(
            params,
            smoothing_window,
            velocity_threshold,
            min_contact_frames,
            visibility_threshold,
        )

        # Show selected parameters if verbose
        if verbose:
            _print_verbose_parameters(video, characteristics, quality_preset, params)

        # Apply smoothing with auto-tuned parameters
        smoothed_landmarks = _apply_smoothing(landmarks_sequence, params, verbose)

        # Extract vertical positions from feet
        if verbose:
            print("Extracting foot positions...")
        vertical_positions, visibilities = _extract_vertical_positions(
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
        if verbose:
            print("Calculating metrics...")
            print(
                f"Using drop height calibration: {drop_height}m ({drop_height*100:.0f}cm)"
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
            kinematic_correction_factor=1.0,
        )

        # Generate outputs (JSON and debug video)
        _generate_outputs(
            metrics,
            json_output,
            output_video,
            frames,
            smoothed_landmarks,
            contact_states,
            video,
            verbose,
        )

        if verbose:
            print("Analysis complete!")

        return metrics


def process_videos_bulk(
    configs: list[VideoConfig],
    max_workers: int = 4,
    progress_callback: Callable[[VideoResult], None] | None = None,
) -> list[VideoResult]:
    """
    Process multiple videos in parallel using ProcessPoolExecutor.

    Args:
        configs: List of VideoConfig objects specifying video paths and parameters
        max_workers: Maximum number of parallel workers (default: 4)
        progress_callback: Optional callback function called after each video completes.
                         Receives VideoResult object.

    Returns:
        List of VideoResult objects, one per input video, in completion order

    Example:
        >>> configs = [
        ...     VideoConfig("video1.mp4", drop_height=0.40),
        ...     VideoConfig("video2.mp4", drop_height=0.30, quality="accurate"),
        ...     VideoConfig("video3.mp4", drop_height=0.50, output_video="debug3.mp4"),
        ... ]
        >>> results = process_videos_bulk(configs, max_workers=4)
        >>> for result in results:
        ...     if result.success:
        ...         print(f"{result.video_path}: {result.metrics.jump_height_m:.3f}m")
        ...     else:
        ...         print(f"{result.video_path}: FAILED - {result.error}")
    """
    results: list[VideoResult] = []

    # Use ProcessPoolExecutor for CPU-bound video processing
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs
        future_to_config = {
            executor.submit(_process_video_wrapper, config): config
            for config in configs
        }

        # Process results as they complete
        for future in as_completed(future_to_config):
            config = future_to_config[future]
            result: VideoResult

            try:
                result = future.result()
            except Exception as exc:
                # Handle unexpected errors
                result = VideoResult(
                    video_path=config.video_path,
                    success=False,
                    error=f"Unexpected error: {str(exc)}",
                )

            results.append(result)

            # Call progress callback if provided
            if progress_callback:
                progress_callback(result)

    return results


def _process_video_wrapper(config: VideoConfig) -> VideoResult:
    """
    Wrapper function for parallel processing. Must be picklable (top-level function).

    Args:
        config: VideoConfig object with processing parameters

    Returns:
        VideoResult object with metrics or error information
    """
    start_time = time.time()

    try:
        metrics = process_video(
            video_path=config.video_path,
            drop_height=config.drop_height,
            quality=config.quality,
            output_video=config.output_video,
            json_output=config.json_output,
            drop_start_frame=config.drop_start_frame,
            smoothing_window=config.smoothing_window,
            velocity_threshold=config.velocity_threshold,
            min_contact_frames=config.min_contact_frames,
            visibility_threshold=config.visibility_threshold,
            detection_confidence=config.detection_confidence,
            tracking_confidence=config.tracking_confidence,
            verbose=False,  # Disable verbose in parallel mode
        )

        processing_time = time.time() - start_time

        return VideoResult(
            video_path=config.video_path,
            success=True,
            metrics=metrics,
            processing_time=processing_time,
        )

    except Exception as e:
        processing_time = time.time() - start_time

        return VideoResult(
            video_path=config.video_path,
            success=False,
            error=str(e),
            processing_time=processing_time,
        )
