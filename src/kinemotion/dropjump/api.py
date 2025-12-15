"""Public API for drop jump video analysis."""

import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from numpy.typing import NDArray

from ..core.auto_tuning import (
    AnalysisParameters,
    QualityPreset,
    VideoCharacteristics,
    analyze_video_sample,
    auto_tune_parameters,
)
from ..core.filtering import reject_outliers
from ..core.metadata import (
    AlgorithmConfig,
    DetectionConfig,
    DropDetectionConfig,
    ProcessingInfo,
    ResultMetadata,
    SmoothingConfig,
    VideoInfo,
    create_timestamp,
    get_kinemotion_version,
)
from ..core.pipeline_utils import (
    apply_expert_overrides,
    apply_smoothing,
    convert_timer_to_stage_names,
    determine_confidence_levels,
    extract_vertical_positions,
    parse_quality_preset,
    print_verbose_parameters,
    process_all_frames,
    process_videos_bulk_generic,
)
from ..core.pose import PoseTracker
from ..core.quality import QualityAssessment, assess_jump_quality
from ..core.timing import NULL_TIMER, PerformanceTimer, Timer
from ..core.video_io import VideoProcessor
from .analysis import (
    detect_ground_contact,
    find_contact_phases,
)
from .debug_overlay import DebugOverlayRenderer
from .kinematics import DropJumpMetrics, calculate_drop_jump_metrics
from .metrics_validator import DropJumpMetricsValidator


@dataclass
class AnalysisOverrides:
    """Optional overrides for analysis parameters.

    Allows fine-tuning of specific analysis parameters beyond quality presets.
    If None, values will be determined by the quality preset.
    """

    smoothing_window: int | None = None
    velocity_threshold: float | None = None
    min_contact_frames: int | None = None
    visibility_threshold: float | None = None


@dataclass
class DropJumpVideoResult:
    """Result of processing a single drop jump video."""

    video_path: str
    success: bool
    metrics: DropJumpMetrics | None = None
    error: str | None = None
    processing_time: float = 0.0


@dataclass
class DropJumpVideoConfig:
    """Configuration for processing a single drop jump video."""

    video_path: str
    quality: str = "balanced"
    output_video: str | None = None
    json_output: str | None = None
    drop_start_frame: int | None = None
    overrides: AnalysisOverrides | None = None
    detection_confidence: float | None = None
    tracking_confidence: float | None = None


def _assess_dropjump_quality(
    vertical_positions: "NDArray",
    visibilities: "NDArray",
    contact_states: list,
    fps: float,
) -> tuple:
    """Assess tracking quality and detect phases.

    Returns:
        Tuple of (quality_result, outlier_mask, phases_detected, phase_count)
    """
    _, outlier_mask = reject_outliers(
        vertical_positions,
        use_ransac=True,
        use_median=True,
        interpolate=False,
    )

    phases = find_contact_phases(contact_states)
    phases_detected = len(phases) > 0
    phase_count = len(phases)

    quality_result = assess_jump_quality(
        visibilities=visibilities,
        positions=vertical_positions,
        outlier_mask=outlier_mask,
        fps=fps,
        phases_detected=phases_detected,
        phase_count=phase_count,
    )

    return quality_result, outlier_mask, phases_detected, phase_count


def _build_dropjump_metadata(
    video_path: str,
    video: "VideoProcessor",
    params: "AnalysisParameters",
    quality_result: QualityAssessment,
    drop_start_frame: int | None,
    metrics: DropJumpMetrics,
    processing_time: float,
    quality_preset: "QualityPreset",
    timer: Timer,
) -> ResultMetadata:
    """Build complete result metadata."""
    drop_frame = None
    if drop_start_frame is None and metrics.drop_start_frame is not None:
        drop_frame = metrics.drop_start_frame
    elif drop_start_frame is not None:
        drop_frame = drop_start_frame

    algorithm_config = AlgorithmConfig(
        detection_method="forward_search",
        tracking_method="mediapipe_pose",
        model_complexity=1,
        smoothing=SmoothingConfig(
            window_size=params.smoothing_window,
            polynomial_order=params.polyorder,
            use_bilateral_filter=params.bilateral_filter,
            use_outlier_rejection=params.outlier_rejection,
        ),
        detection=DetectionConfig(
            velocity_threshold=params.velocity_threshold,
            min_contact_frames=params.min_contact_frames,
            visibility_threshold=params.visibility_threshold,
            use_curvature_refinement=params.use_curvature,
        ),
        drop_detection=DropDetectionConfig(
            auto_detect_drop_start=(drop_start_frame is None),
            detected_drop_frame=drop_frame,
            min_stationary_duration_s=0.5,
        ),
    )

    video_info = VideoInfo(
        source_path=video_path,
        fps=video.fps,
        width=video.width,
        height=video.height,
        duration_s=video.frame_count / video.fps,
        frame_count=video.frame_count,
        codec=video.codec,
    )

    stage_times = convert_timer_to_stage_names(timer.get_metrics())

    processing_info = ProcessingInfo(
        version=get_kinemotion_version(),
        timestamp=create_timestamp(),
        quality_preset=quality_preset.value,
        processing_time_s=processing_time,
        timing_breakdown=stage_times,
    )

    return ResultMetadata(
        quality=quality_result,
        video=video_info,
        processing=processing_info,
        algorithm=algorithm_config,
    )


def _save_dropjump_json(
    json_output: str,
    metrics: DropJumpMetrics,
    timer: Timer,
    verbose: bool,
) -> None:
    """Save metrics to JSON file."""
    with timer.measure("json_serialization"):
        output_path = Path(json_output)
        metrics_dict = metrics.to_dict()
        json_str = json.dumps(metrics_dict, indent=2)
        output_path.write_text(json_str)

    if verbose:
        print(f"Metrics written to: {json_output}")


def _print_dropjump_summary(
    start_time: float,
    timer: Timer,
) -> None:
    """Print verbose timing summary."""
    total_time = time.time() - start_time
    stage_times = convert_timer_to_stage_names(timer.get_metrics())

    print("\n=== Timing Summary ===")
    for stage, duration in stage_times.items():
        percentage = (duration / total_time) * 100
        dur_ms = duration * 1000
        print(f"{stage:.<40} {dur_ms:>6.0f}ms ({percentage:>5.1f}%)")
    total_ms = total_time * 1000
    print(f"{('Total'):.>40} {total_ms:>6.0f}ms (100.0%)")
    print()
    print("Analysis complete!")


def _setup_pose_tracker(
    quality_preset: QualityPreset,
    detection_confidence: float | None,
    tracking_confidence: float | None,
    pose_tracker: "PoseTracker | None",
    timer: Timer,
) -> tuple["PoseTracker", bool]:
    """Set up pose tracker and determine if it should be closed."""
    detection_conf, tracking_conf = determine_confidence_levels(
        quality_preset, detection_confidence, tracking_confidence
    )

    tracker = pose_tracker
    should_close_tracker = False

    if tracker is None:
        tracker = PoseTracker(
            min_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
            timer=timer,
        )
        should_close_tracker = True

    return tracker, should_close_tracker


def _process_frames_and_landmarks(
    video: "VideoProcessor",
    tracker: "PoseTracker",
    should_close_tracker: bool,
    verbose: bool,
    timer: Timer,
) -> tuple[list, list, list[int]]:
    """Process all video frames and extract landmarks."""
    if verbose:
        print("Processing all frames with MediaPipe pose tracking...")

    frames, landmarks_sequence, frame_indices = process_all_frames(
        video, tracker, verbose, timer, close_tracker=should_close_tracker
    )

    return frames, landmarks_sequence, frame_indices


def _tune_and_smooth(
    landmarks_sequence: list,
    video_fps: float,
    frame_count: int,
    quality_preset: QualityPreset,
    overrides: AnalysisOverrides | None,
    timer: Timer,
    verbose: bool,
) -> tuple[list, AnalysisParameters, VideoCharacteristics]:
    """Tune parameters and apply smoothing to landmarks.

    Args:
        landmarks_sequence: Sequence of pose landmarks
        video_fps: Video frame rate
        frame_count: Total number of frames
        quality_preset: Quality preset for analysis
        overrides: Optional parameter overrides
        timer: Performance timer
        verbose: Verbose output flag

    Returns:
        Tuple of (smoothed_landmarks, params, characteristics)
    """
    with timer.measure("parameter_auto_tuning"):
        characteristics = analyze_video_sample(landmarks_sequence, video_fps, frame_count)
        params = auto_tune_parameters(characteristics, quality_preset)

        # Apply overrides if provided
        if overrides:
            params = apply_expert_overrides(
                params,
                overrides.smoothing_window,
                overrides.velocity_threshold,
                overrides.min_contact_frames,
                overrides.visibility_threshold,
            )
        else:
            params = apply_expert_overrides(
                params,
                None,
                None,
                None,
                None,
            )

    smoothed_landmarks = apply_smoothing(landmarks_sequence, params, verbose, timer)

    return smoothed_landmarks, params, characteristics


def _extract_positions_and_detect_contact(
    smoothed_landmarks: list,
    params: AnalysisParameters,
    timer: Timer,
    verbose: bool,
) -> tuple["NDArray", "NDArray", list]:
    """Extract vertical positions and detect ground contact."""
    if verbose:
        print("Extracting foot positions...")
    with timer.measure("vertical_position_extraction"):
        vertical_positions, visibilities = extract_vertical_positions(smoothed_landmarks)

    if verbose:
        print("Detecting ground contact...")
    with timer.measure("ground_contact_detection"):
        contact_states = detect_ground_contact(
            vertical_positions,
            velocity_threshold=params.velocity_threshold,
            min_contact_frames=params.min_contact_frames,
            visibility_threshold=params.visibility_threshold,
            visibilities=visibilities,
            window_length=params.smoothing_window,
            polyorder=params.polyorder,
            timer=timer,
        )

    return vertical_positions, visibilities, contact_states


def _calculate_metrics_and_assess_quality(
    contact_states: list,
    vertical_positions: "NDArray",
    visibilities: "NDArray",
    video_fps: float,
    drop_start_frame: int | None,
    params: AnalysisParameters,
    timer: Timer,
    verbose: bool,
) -> tuple[DropJumpMetrics, QualityAssessment]:
    """Calculate metrics and assess quality."""
    if verbose:
        print("Calculating metrics...")
    with timer.measure("metrics_calculation"):
        metrics = calculate_drop_jump_metrics(
            contact_states,
            vertical_positions,
            video_fps,
            drop_start_frame=drop_start_frame,
            velocity_threshold=params.velocity_threshold,
            smoothing_window=params.smoothing_window,
            polyorder=params.polyorder,
            use_curvature=params.use_curvature,
            timer=timer,
        )

    if verbose:
        print("Assessing tracking quality...")
    with timer.measure("quality_assessment"):
        quality_result, _, _, _ = _assess_dropjump_quality(
            vertical_positions, visibilities, contact_states, video_fps
        )

    return metrics, quality_result


def _print_quality_warnings(quality_result: QualityAssessment, verbose: bool) -> None:
    """Print quality warnings if present."""
    if verbose and quality_result.warnings:
        print("\n⚠️  Quality Warnings:")
        for warning in quality_result.warnings:
            print(f"  - {warning}")
        print()


def _validate_metrics_and_print_results(
    metrics: DropJumpMetrics,
    timer: Timer,
    verbose: bool,
) -> None:
    """Validate metrics and print validation results if verbose."""
    with timer.measure("metrics_validation"):
        validator = DropJumpMetricsValidator()
        validation_result = validator.validate(metrics.to_dict())  # type: ignore[arg-type]
        metrics.validation_result = validation_result

    if verbose and validation_result.issues:
        print("\n⚠️  Validation Results:")
        for issue in validation_result.issues:
            print(f"  [{issue.severity.value}] {issue.metric}: {issue.message}")


def _generate_debug_video(
    output_video: str,
    frames: list,
    frame_indices: list[int],
    video_fps: float,
    smoothed_landmarks: list,
    contact_states: list,
    metrics: DropJumpMetrics,
    timer: Timer | None,
    verbose: bool,
) -> None:
    """Generate debug video with overlay."""
    if verbose:
        print(f"Generating debug video: {output_video}")

    if not frames:
        return

    timer = timer or NULL_TIMER
    debug_h, debug_w = frames[0].shape[:2]

    if video_fps > 30:
        debug_fps = video_fps / (video_fps / 30.0)
    else:
        debug_fps = video_fps

    if len(frames) < len(smoothed_landmarks):
        step = max(1, int(video_fps / 30.0))
        debug_fps = video_fps / step

    def _render_frames(renderer: DebugOverlayRenderer) -> None:
        for frame, idx in zip(frames, frame_indices, strict=True):
            annotated = renderer.render_frame(
                frame,
                smoothed_landmarks[idx],
                contact_states[idx],
                idx,
                metrics,
                use_com=False,
            )
            renderer.write_frame(annotated)

    renderer_context = DebugOverlayRenderer(
        output_video,
        debug_w,
        debug_h,
        debug_w,
        debug_h,
        debug_fps,
        timer=timer,
    )

    with timer.measure("debug_video_generation"):
        with renderer_context as renderer:
            _render_frames(renderer)

    if verbose:
        print(f"Debug video saved: {output_video}")


def process_dropjump_video(
    video_path: str,
    quality: str = "balanced",
    output_video: str | None = None,
    json_output: str | None = None,
    drop_start_frame: int | None = None,
    overrides: AnalysisOverrides | None = None,
    detection_confidence: float | None = None,
    tracking_confidence: float | None = None,
    verbose: bool = False,
    timer: Timer | None = None,
    pose_tracker: "PoseTracker | None" = None,
) -> DropJumpMetrics:
    """
    Process a single drop jump video and return metrics.

    Jump height is calculated from flight time using kinematic formula (h = g*t²/8).

    Args:
        video_path: Path to the input video file
        quality: Analysis quality preset ("fast", "balanced", or "accurate")
        output_video: Optional path for debug video output
        json_output: Optional path for JSON metrics output
        drop_start_frame: Optional manual drop start frame
        overrides: Optional AnalysisOverrides for fine-tuning parameters
        detection_confidence: Optional override for pose detection confidence
        tracking_confidence: Optional override for pose tracking confidence
        verbose: Print processing details
        timer: Optional Timer for measuring operations
        pose_tracker: Optional pre-initialized PoseTracker instance (reused if provided)

    Returns:
        DropJumpMetrics object containing analysis results

    Raises:
        ValueError: If video cannot be processed or parameters are invalid
        FileNotFoundError: If video file does not exist
    """
    if not Path(video_path).exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    from ..core.determinism import set_deterministic_mode

    set_deterministic_mode(seed=42)

    start_time = time.time()
    timer = timer or PerformanceTimer()
    quality_preset = parse_quality_preset(quality)

    with timer.measure("video_initialization"):
        with VideoProcessor(video_path, timer=timer) as video:
            tracker, should_close_tracker = _setup_pose_tracker(
                quality_preset,
                detection_confidence,
                tracking_confidence,
                pose_tracker,
                timer,
            )

            frames, landmarks_sequence, frame_indices = _process_frames_and_landmarks(
                video, tracker, should_close_tracker, verbose, timer
            )

            smoothed_landmarks, params, characteristics = _tune_and_smooth(
                landmarks_sequence,
                video.fps,
                video.frame_count,
                quality_preset,
                overrides,
                timer,
                verbose,
            )

            if verbose:
                print_verbose_parameters(video, characteristics, quality_preset, params)

            vertical_positions, visibilities, contact_states = (
                _extract_positions_and_detect_contact(smoothed_landmarks, params, timer, verbose)
            )

            metrics, quality_result = _calculate_metrics_and_assess_quality(
                contact_states,
                vertical_positions,
                visibilities,
                video.fps,
                drop_start_frame,
                params,
                timer,
                verbose,
            )

            _print_quality_warnings(quality_result, verbose)

            if output_video:
                _generate_debug_video(
                    output_video,
                    frames,
                    frame_indices,
                    video.fps,
                    smoothed_landmarks,
                    contact_states,
                    metrics,
                    timer,
                    verbose,
                )

            _validate_metrics_and_print_results(metrics, timer, verbose)

            processing_time = time.time() - start_time
            result_metadata = _build_dropjump_metadata(
                video_path,
                video,
                params,
                quality_result,
                drop_start_frame,
                metrics,
                processing_time,
                quality_preset,
                timer,
            )
            metrics.result_metadata = result_metadata

            if json_output:
                _save_dropjump_json(json_output, metrics, timer, verbose)

            if verbose:
                _print_dropjump_summary(start_time, timer)

            return metrics


def process_dropjump_videos_bulk(
    configs: list[DropJumpVideoConfig],
    max_workers: int = 4,
    progress_callback: Callable[[DropJumpVideoResult], None] | None = None,
) -> list[DropJumpVideoResult]:
    """
    Process multiple drop jump videos in parallel.
    """

    def error_factory(video_path: str, error_msg: str) -> DropJumpVideoResult:
        return DropJumpVideoResult(video_path=video_path, success=False, error=error_msg)

    return process_videos_bulk_generic(
        configs,
        _process_dropjump_video_wrapper,
        error_factory,
        max_workers,
        progress_callback,
    )


def _process_dropjump_video_wrapper(config: DropJumpVideoConfig) -> DropJumpVideoResult:
    """Wrapper function for parallel processing."""
    start_time = time.time()

    try:
        metrics = process_dropjump_video(
            video_path=config.video_path,
            quality=config.quality,
            output_video=config.output_video,
            json_output=config.json_output,
            drop_start_frame=config.drop_start_frame,
            overrides=config.overrides,
            detection_confidence=config.detection_confidence,
            tracking_confidence=config.tracking_confidence,
            verbose=False,
        )

        processing_time = time.time() - start_time

        return DropJumpVideoResult(
            video_path=config.video_path,
            success=True,
            metrics=metrics,
            processing_time=processing_time,
        )

    except Exception as e:
        processing_time = time.time() - start_time

        return DropJumpVideoResult(
            video_path=config.video_path,
            success=False,
            error=str(e),
            processing_time=processing_time,
        )
