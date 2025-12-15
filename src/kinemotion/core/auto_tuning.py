"""Automatic parameter tuning based on video characteristics."""

from dataclasses import dataclass
from enum import Enum

import numpy as np


class QualityPreset(str, Enum):
    """Quality presets for analysis."""

    FAST = "fast"  # Quick analysis, lower precision
    BALANCED = "balanced"  # Default: good balance of speed and accuracy
    ACCURATE = "accurate"  # Research-grade analysis, slower


@dataclass
class VideoCharacteristics:
    """Characteristics extracted from video analysis."""

    fps: float
    frame_count: int
    avg_visibility: float  # Average landmark visibility (0-1)
    position_variance: float  # Variance in foot positions
    has_stable_period: bool  # Whether video has initial stationary period
    tracking_quality: str  # "low", "medium", "high"


@dataclass
class AnalysisParameters:
    """Auto-tuned parameters for drop jump analysis."""

    smoothing_window: int
    polyorder: int
    velocity_threshold: float
    min_contact_frames: int
    visibility_threshold: float
    detection_confidence: float
    tracking_confidence: float
    outlier_rejection: bool
    bilateral_filter: bool
    use_curvature: bool

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "smoothing_window": self.smoothing_window,
            "polyorder": self.polyorder,
            "velocity_threshold": self.velocity_threshold,
            "min_contact_frames": self.min_contact_frames,
            "visibility_threshold": self.visibility_threshold,
            "detection_confidence": self.detection_confidence,
            "tracking_confidence": self.tracking_confidence,
            "outlier_rejection": self.outlier_rejection,
            "bilateral_filter": self.bilateral_filter,
            "use_curvature": self.use_curvature,
        }


def analyze_tracking_quality(avg_visibility: float) -> str:
    """
    Classify tracking quality based on average landmark visibility.

    Args:
        avg_visibility: Average visibility score across all tracked landmarks

    Returns:
        Quality classification: "low", "medium", or "high"
    """
    if avg_visibility < 0.4:
        return "low"
    elif avg_visibility < 0.7:
        return "medium"
    else:
        return "high"


def auto_tune_parameters(
    characteristics: VideoCharacteristics,
    quality_preset: QualityPreset = QualityPreset.BALANCED,
) -> AnalysisParameters:
    """
    Automatically tune analysis parameters based on video characteristics.

    This function implements heuristics to select optimal parameters without
    requiring user expertise in video analysis or kinematic tracking.

    Key principles:
    1. FPS-based scaling: Higher fps needs lower velocity thresholds
    2. Quality-based smoothing: Noisy video needs more smoothing
    3. Always enable proven features: outlier rejection, curvature analysis
    4. Preset modifiers: fast/balanced/accurate adjust base parameters

    Args:
        characteristics: Analyzed video characteristics
        quality_preset: Quality vs speed tradeoff

    Returns:
        AnalysisParameters with auto-tuned values
    """
    fps = characteristics.fps
    quality = characteristics.tracking_quality

    # =================================================================
    # STEP 1: FPS-based baseline parameters
    # These scale automatically with frame rate to maintain consistent
    # temporal resolution and sensitivity
    # =================================================================

    # Velocity threshold: Scale inversely with fps
    # Empirically validated with 45° oblique videos at 60fps:
    # - Standing (stationary): ~0.001 mean, 0.0011 max
    # - Flight/drop (moving): ~0.005-0.009
    # Target threshold: 0.002 at 60fps for clear separation
    # Formula: threshold = 0.004 * (30 / fps)
    base_velocity_threshold = 0.004 * (30.0 / fps)

    # Min contact frames: Scale with fps to maintain same time duration
    # Goal: ~100ms minimum contact (3 frames @ 30fps, 6 frames @ 60fps)
    # Formula: frames = round(3 * (fps / 30))
    base_min_contact_frames = max(2, round(3.0 * (fps / 30.0)))

    # Smoothing window: Decrease with higher fps for better temporal resolution
    # Lower fps (30fps): 5-frame window = 167ms
    # Higher fps (60fps): 3-frame window = 50ms (same temporal resolution)
    if fps <= 30:
        base_smoothing_window = 5
    elif fps <= 60:
        base_smoothing_window = 3
    else:
        base_smoothing_window = 3  # Even at 120fps, 3 is minimum for Savitzky-Golay

    # =================================================================
    # STEP 2: Quality-based adjustments
    # Adapt smoothing and filtering based on tracking quality
    # =================================================================

    smoothing_adjustment = 0
    enable_bilateral = False

    if quality == "low":
        # Poor tracking quality: aggressive smoothing and filtering
        smoothing_adjustment = +2
        enable_bilateral = True
    elif quality == "medium":
        # Moderate quality: slight smoothing increase
        smoothing_adjustment = +1
        enable_bilateral = True
    else:  # high quality
        # Good tracking: preserve detail, minimal smoothing
        smoothing_adjustment = 0
        enable_bilateral = False

    # =================================================================
    # STEP 3: Apply quality preset modifiers
    # User can choose speed vs accuracy tradeoff
    # =================================================================

    if quality_preset == QualityPreset.FAST:
        # Fast: Trade accuracy for speed
        velocity_threshold = base_velocity_threshold * 1.5  # Less sensitive
        min_contact_frames = max(2, int(base_min_contact_frames * 0.67))
        smoothing_window = max(3, base_smoothing_window - 2 + smoothing_adjustment)
        bilateral_filter = False  # Skip expensive filtering
        detection_confidence = 0.3
        tracking_confidence = 0.3

    elif quality_preset == QualityPreset.ACCURATE:
        # Accurate: Maximize accuracy, accept slower processing
        velocity_threshold = base_velocity_threshold * 0.5  # More sensitive
        min_contact_frames = base_min_contact_frames  # Don't increase (would miss brief)
        smoothing_window = min(11, base_smoothing_window + 2 + smoothing_adjustment)
        bilateral_filter = True  # Always use for best accuracy
        detection_confidence = 0.6
        tracking_confidence = 0.6

    else:  # QualityPreset.BALANCED (default)
        # Balanced: Good accuracy, reasonable speed
        velocity_threshold = base_velocity_threshold
        min_contact_frames = base_min_contact_frames
        smoothing_window = max(3, base_smoothing_window + smoothing_adjustment)
        bilateral_filter = enable_bilateral
        detection_confidence = 0.5
        tracking_confidence = 0.5

    # Ensure smoothing window is odd (required for Savitzky-Golay)
    if smoothing_window % 2 == 0:
        smoothing_window += 1

    # =================================================================
    # STEP 4: Set fixed optimal values
    # These are always the same regardless of video characteristics
    # =================================================================

    # Polyorder: Always 2 (quadratic) - optimal for jump physics (parabolic motion)
    polyorder = 2

    # Visibility threshold: Standard MediaPipe threshold
    visibility_threshold = 0.5

    # Always enable proven accuracy features
    outlier_rejection = True  # Removes tracking glitches (minimal cost)
    use_curvature = True  # Trajectory curvature analysis (minimal cost)

    return AnalysisParameters(
        smoothing_window=smoothing_window,
        polyorder=polyorder,
        velocity_threshold=velocity_threshold,
        min_contact_frames=min_contact_frames,
        visibility_threshold=visibility_threshold,
        detection_confidence=detection_confidence,
        tracking_confidence=tracking_confidence,
        outlier_rejection=outlier_rejection,
        bilateral_filter=bilateral_filter,
        use_curvature=use_curvature,
    )


def _collect_foot_visibility_and_positions(
    frame_landmarks: dict[str, tuple[float, float, float]],
) -> tuple[list[float], list[float]]:
    """
    Collect visibility scores and Y positions from foot landmarks.

    Args:
        frame_landmarks: Landmarks for a single frame

    Returns:
        Tuple of (visibility_scores, y_positions)
    """
    foot_keys = [
        "left_ankle",
        "right_ankle",
        "left_heel",
        "right_heel",
        "left_foot_index",
        "right_foot_index",
    ]

    frame_vis = []
    frame_y_positions = []

    for key in foot_keys:
        if key in frame_landmarks:
            _, y, vis = frame_landmarks[key]  # x not needed for analysis
            frame_vis.append(vis)
            frame_y_positions.append(y)

    return frame_vis, frame_y_positions


def _check_stable_period(positions: list[float]) -> bool:
    """
    Check if video has a stable period at the start.

    A stable period (low variance in first 30 frames) indicates
    the subject is standing on an elevated platform before jumping.

    Args:
        positions: List of average Y positions per frame

    Returns:
        True if stable period detected, False otherwise
    """
    if len(positions) < 30:
        return False

    first_30_std = float(np.std(positions[:30]))
    return first_30_std < 0.01  # Very stable = on platform


def analyze_video_sample(
    landmarks_sequence: list[dict[str, tuple[float, float, float]] | None],
    fps: float,
    frame_count: int,
) -> VideoCharacteristics:
    """
    Analyze video characteristics from a sample of frames.

    This function should be called after tracking the first 30-60 frames
    to understand video quality and characteristics.

    Args:
        landmarks_sequence: Tracked landmarks from sample frames
        fps: Video frame rate
        frame_count: Total number of frames in video

    Returns:
        VideoCharacteristics with analyzed properties
    """
    visibilities = []
    positions = []

    # Collect visibility and position data from all frames
    for frame_landmarks in landmarks_sequence:
        if not frame_landmarks:
            continue

        frame_vis, frame_y_positions = _collect_foot_visibility_and_positions(frame_landmarks)

        if frame_vis:
            visibilities.append(float(np.mean(frame_vis)))
        if frame_y_positions:
            positions.append(float(np.mean(frame_y_positions)))

    # Compute metrics
    avg_visibility = float(np.mean(visibilities)) if visibilities else 0.5
    position_variance = float(np.var(positions)) if len(positions) > 1 else 0.0

    # Determine tracking quality
    tracking_quality = analyze_tracking_quality(avg_visibility)

    # Check for stable period (indicates drop jump from elevated platform)
    has_stable_period = _check_stable_period(positions)

    return VideoCharacteristics(
        fps=fps,
        frame_count=frame_count,
        avg_visibility=avg_visibility,
        position_variance=position_variance,
        has_stable_period=has_stable_period,
        tracking_quality=tracking_quality,
    )
