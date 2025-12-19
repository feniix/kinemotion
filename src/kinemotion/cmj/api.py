"""Public API for CMJ (Counter Movement Jump) video analysis."""

import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from ..core.auto_tuning import (
    AnalysisParameters,
    QualityPreset,
    analyze_video_sample,
    auto_tune_parameters,
)
from ..core.filtering import reject_outliers
from ..core.metadata import (
    AlgorithmConfig,
    DetectionConfig,
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
from ..core.timing import PerformanceTimer, Timer
from ..core.validation import ValidationResult
from ..core.video_io import VideoProcessor
from .analysis import compute_signed_velocity, detect_cmj_phases
from .debug_overlay import CMJDebugOverlayRenderer
from .kinematics import CMJMetrics, calculate_cmj_metrics
from .metrics_validator import CMJMetricsValidator


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


def _generate_debug_video(
    output_video: str,
    frames: list[NDArray[np.uint8]],
    frame_indices: list[int],
    smoothed_landmarks: list,
    metrics: CMJMetrics,
    video_fps: float,
    timer: Timer,
    verbose: bool,
) -> None:
    """Generate debug video with CMJ analysis overlay."""
    if verbose:
        print(f"Generating debug video: {output_video}")

    debug_h, debug_w = frames[0].shape[:2]
    step = max(1, int(video_fps / 30.0))
    debug_fps = video_fps / step

    with timer.measure("debug_video_generation"):
        with CMJDebugOverlayRenderer(
            output_video,
            debug_w,
            debug_h,
            debug_w,
            debug_h,
            debug_fps,
            timer=timer,
        ) as renderer:
            for frame, idx in zip(frames, frame_indices, strict=True):
                annotated = renderer.render_frame(frame, smoothed_landmarks[idx], idx, metrics)
                renderer.write_frame(annotated)

    if verbose:
        print(f"Debug video saved: {output_video}")


def _save_metrics_to_json(
    metrics: CMJMetrics, json_output: str, timer: Timer, verbose: bool
) -> None:
    """Save metrics to JSON file."""
    with timer.measure("json_serialization"):
        output_path = Path(json_output)
        metrics_dict = metrics.to_dict()
        json_str = json.dumps(metrics_dict, indent=2)
        output_path.write_text(json_str)

    if verbose:
        print(f"Metrics written to: {json_output}")


def _print_timing_summary(start_time: float, timer: Timer, metrics: CMJMetrics) -> None:
    """Print verbose timing summary and metrics."""
    total_time = time.time() - start_time
    stage_times = convert_timer_to_stage_names(timer.get_metrics())

    print("\n=== Timing Summary ===")
    for stage, duration in stage_times.items():
        percentage = (duration / total_time) * 100
        dur_ms = duration * 1000
        print(f"{stage:.<40} {dur_ms:>6.0f}ms ({percentage:>5.1f}%)")
    total_ms = total_time * 1000
    print(f"{'Total':.<40} {total_ms:>6.0f}ms (100.0%)")
    print()

    print(f"\nJump height: {metrics.jump_height:.3f}m")
    print(f"Flight time: {metrics.flight_time * 1000:.1f}ms")
    print(f"Countermovement depth: {metrics.countermovement_depth:.3f}m")


def _print_quality_warnings(quality_result: QualityAssessment, verbose: bool) -> None:
    """Print quality warnings if present."""
    if verbose and quality_result.warnings:
        print("\n⚠️  Quality Warnings:")
        for warning in quality_result.warnings:
            print(f"  - {warning}")
        print()


def _print_validation_results(validation_result: ValidationResult, verbose: bool) -> None:
    """Print validation issues if present."""
    if verbose and validation_result.issues:
        print("\n⚠️  Validation Results:")
        for issue in validation_result.issues:
            print(f"  [{issue.severity.value}] {issue.metric}: {issue.message}")


def _create_algorithm_config(params: AnalysisParameters) -> AlgorithmConfig:
    """Create algorithm configuration from parameters."""
    return AlgorithmConfig(
        detection_method="backward_search",
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
        drop_detection=None,
    )


def _create_video_info(video_path: str, video: VideoProcessor) -> VideoInfo:
    """Create video information metadata."""
    return VideoInfo(
        source_path=video_path,
        fps=video.fps,
        width=video.width,
        height=video.height,
        duration_s=video.frame_count / video.fps,
        frame_count=video.frame_count,
        codec=video.codec,
    )


def _create_processing_info(
    start_time: float, quality_preset: QualityPreset, timer: Timer
) -> ProcessingInfo:
    """Create processing information metadata."""
    processing_time = time.time() - start_time
    stage_times = convert_timer_to_stage_names(timer.get_metrics())

    return ProcessingInfo(
        version=get_kinemotion_version(),
        timestamp=create_timestamp(),
        quality_preset=quality_preset.value,
        processing_time_s=processing_time,
        timing_breakdown=stage_times,
    )


def _create_result_metadata(
    quality_result: QualityAssessment,
    video_info: VideoInfo,
    processing_info: ProcessingInfo,
    algorithm_config: AlgorithmConfig,
) -> ResultMetadata:
    """Create result metadata from components."""
    return ResultMetadata(
        quality=quality_result,
        video=video_info,
        processing=processing_info,
        algorithm=algorithm_config,
    )


def _run_pose_tracking(
    video: VideoProcessor,
    quality_preset: QualityPreset,
    detection_confidence: float | None,
    tracking_confidence: float | None,
    pose_tracker: PoseTracker | None,
    verbose: bool,
    timer: Timer,
) -> tuple[list[NDArray[np.uint8]], list, list[int]]:
    """Initialize tracker and process all frames."""
    if verbose:
        print(
            f"Video: {video.width}x{video.height} @ {video.fps:.2f} fps, "
            f"{video.frame_count} frames"
        )

    det_conf, track_conf = determine_confidence_levels(
        quality_preset, detection_confidence, tracking_confidence
    )

    if verbose:
        print("Processing all frames with MediaPipe pose tracking...")

    tracker = pose_tracker or PoseTracker(
        min_detection_confidence=det_conf,
        min_tracking_confidence=track_conf,
        timer=timer,
    )
    should_close_tracker = pose_tracker is None

    return process_all_frames(video, tracker, verbose, timer, close_tracker=should_close_tracker)


def _get_tuned_parameters(
    video: VideoProcessor,
    landmarks_sequence: list,
    quality_preset: QualityPreset,
    overrides: AnalysisOverrides | None,
    verbose: bool,
    timer: Timer,
) -> AnalysisParameters:
    """Analyze sample and tune parameters with expert overrides."""
    with timer.measure("parameter_auto_tuning"):
        characteristics = analyze_video_sample(landmarks_sequence, video.fps, video.frame_count)
        params = auto_tune_parameters(characteristics, quality_preset)
        params = apply_expert_overrides(
            params,
            overrides.smoothing_window if overrides else None,
            overrides.velocity_threshold if overrides else None,
            overrides.min_contact_frames if overrides else None,
            overrides.visibility_threshold if overrides else None,
        )

        if verbose:
            print_verbose_parameters(video, characteristics, quality_preset, params)

    return params


def _run_kinematic_analysis(
    video: VideoProcessor,
    smoothed_landmarks: list,
    params: AnalysisParameters,
    verbose: bool,
    timer: Timer,
) -> tuple[CMJMetrics, NDArray[np.float64], NDArray[np.float64]]:
    """Extract positions, detect phases, and calculate metrics."""
    if verbose:
        print("Extracting vertical positions (Hip and Foot)...")
    with timer.measure("vertical_position_extraction"):
        vertical_positions, visibilities = extract_vertical_positions(
            smoothed_landmarks, target="hip"
        )
        foot_positions, _ = extract_vertical_positions(smoothed_landmarks, target="foot")

    if verbose:
        print("Detecting CMJ phases...")
    with timer.measure("phase_detection"):
        phases = detect_cmj_phases(
            vertical_positions,
            video.fps,
            window_length=params.smoothing_window,
            polyorder=params.polyorder,
            landing_positions=foot_positions,
            timer=timer,
        )

    if phases is None:
        raise ValueError("Could not detect CMJ phases in video")

    standing_end, lowest_point, takeoff_frame, landing_frame = phases

    if verbose:
        print("Calculating metrics...")
    with timer.measure("metrics_calculation"):
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
            tracking_method="hip_hybrid",
        )

    return metrics, vertical_positions, visibilities


def _finalize_analysis_results(
    metrics: CMJMetrics,
    video: VideoProcessor,
    video_path: str,
    vertical_positions: NDArray[np.float64],
    visibilities: NDArray[np.float64],
    params: AnalysisParameters,
    quality_preset: QualityPreset,
    start_time: float,
    timer: Timer,
    verbose: bool,
) -> None:
    """Assess quality, validate metrics, and attach metadata."""
    if verbose:
        print("Assessing tracking quality...")
    with timer.measure("quality_assessment"):
        _, outlier_mask = reject_outliers(
            vertical_positions,
            use_ransac=True,
            use_median=True,
            interpolate=False,
        )
        quality_result = assess_jump_quality(
            visibilities=visibilities,
            positions=vertical_positions,
            outlier_mask=outlier_mask,
            fps=video.fps,
            phases_detected=True,
            phase_count=4,
        )

    _print_quality_warnings(quality_result, verbose)

    with timer.measure("metrics_validation"):
        validator = CMJMetricsValidator()
        validation_result = validator.validate(metrics.to_dict())  # type: ignore[arg-type]
        metrics.validation_result = validation_result

    algorithm_config = _create_algorithm_config(params)
    video_info = _create_video_info(video_path, video)
    processing_info = _create_processing_info(start_time, quality_preset, timer)
    result_metadata = _create_result_metadata(
        quality_result, video_info, processing_info, algorithm_config
    )
    metrics.result_metadata = result_metadata

    _print_validation_results(validation_result, verbose)


@dataclass
class CMJVideoConfig:
    """Configuration for processing a single CMJ video."""

    video_path: str
    quality: str = "balanced"
    output_video: str | None = None
    json_output: str | None = None
    overrides: AnalysisOverrides | None = None
    detection_confidence: float | None = None
    tracking_confidence: float | None = None


@dataclass
class CMJVideoResult:
    """Result of processing a single CMJ video."""

    video_path: str
    success: bool
    metrics: CMJMetrics | None = None
    error: str | None = None
    processing_time: float = 0.0


def process_cmj_video(
    video_path: str,
    quality: str = "balanced",
    output_video: str | None = None,
    json_output: str | None = None,
    overrides: AnalysisOverrides | None = None,
    detection_confidence: float | None = None,
    tracking_confidence: float | None = None,
    verbose: bool = False,
    timer: Timer | None = None,
    pose_tracker: PoseTracker | None = None,
) -> CMJMetrics:
    """
    Process a single CMJ video and return metrics.

    CMJ (Counter Movement Jump) is performed at floor level without a drop box.
    Athletes start standing, perform a countermovement (eccentric phase), then
    jump upward (concentric phase).

    Args:
        video_path: Path to the input video file
        quality: Analysis quality preset ("fast", "balanced", or "accurate")
        output_video: Optional path for debug video output
        json_output: Optional path for JSON metrics output
        overrides: Optional AnalysisOverrides with parameter fine-tuning
        detection_confidence: Optional override for pose detection confidence
        tracking_confidence: Optional override for pose tracking confidence
        verbose: Print processing details
        timer: Optional Timer for measuring operations
        pose_tracker: Optional pre-initialized PoseTracker instance (reused if provided)

    Returns:
        CMJMetrics object containing analysis results

    Raises:
        ValueError: If video cannot be processed or parameters are invalid
        FileNotFoundError: If video file does not exist
    """
    if not Path(video_path).exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    start_time = time.time()
    timer = timer or PerformanceTimer()
    quality_preset = parse_quality_preset(quality)

    with timer.measure("video_initialization"):
        with VideoProcessor(video_path, timer=timer) as video:
            # 1. Pose Tracking
            frames, landmarks_sequence, frame_indices = _run_pose_tracking(
                video,
                quality_preset,
                detection_confidence,
                tracking_confidence,
                pose_tracker,
                verbose,
                timer,
            )

            # 2. Parameters & Smoothing
            params = _get_tuned_parameters(
                video, landmarks_sequence, quality_preset, overrides, verbose, timer
            )
            smoothed_landmarks = apply_smoothing(landmarks_sequence, params, verbose, timer)

            # 3. Kinematic Analysis
            metrics, vertical_positions, visibilities = _run_kinematic_analysis(
                video, smoothed_landmarks, params, verbose, timer
            )

            # 4. Debug Video Generation (Optional)
            if output_video:
                _generate_debug_video(
                    output_video,
                    frames,
                    frame_indices,
                    smoothed_landmarks,
                    metrics,
                    video.fps,
                    timer,
                    verbose,
                )

            # 5. Finalization (Quality, Metadata, Validation)
            _finalize_analysis_results(
                metrics,
                video,
                video_path,
                vertical_positions,
                visibilities,
                params,
                quality_preset,
                start_time,
                timer,
                verbose,
            )

            if json_output:
                _save_metrics_to_json(metrics, json_output, timer, verbose)

            if verbose:
                _print_timing_summary(start_time, timer, metrics)

            return metrics


def process_cmj_videos_bulk(
    configs: list[CMJVideoConfig],
    max_workers: int = 4,
    progress_callback: Callable[[CMJVideoResult], None] | None = None,
) -> list[CMJVideoResult]:
    """
    Process multiple CMJ videos in parallel.
    """

    def error_factory(video_path: str, error_msg: str) -> CMJVideoResult:
        return CMJVideoResult(video_path=video_path, success=False, error=error_msg)

    return process_videos_bulk_generic(
        configs,
        _process_cmj_video_wrapper,
        error_factory,
        max_workers,
        progress_callback,
    )


def _process_cmj_video_wrapper(config: CMJVideoConfig) -> CMJVideoResult:
    """Wrapper function for parallel CMJ processing."""
    start_time = time.time()

    try:
        metrics = process_cmj_video(
            video_path=config.video_path,
            quality=config.quality,
            output_video=config.output_video,
            json_output=config.json_output,
            overrides=config.overrides,
            detection_confidence=config.detection_confidence,
            tracking_confidence=config.tracking_confidence,
            verbose=False,
        )

        processing_time = time.time() - start_time

        return CMJVideoResult(
            video_path=config.video_path,
            success=True,
            metrics=metrics,
            processing_time=processing_time,
        )

    except Exception as e:
        processing_time = time.time() - start_time

        return CMJVideoResult(
            video_path=config.video_path,
            success=False,
            error=str(e),
            processing_time=processing_time,
        )
