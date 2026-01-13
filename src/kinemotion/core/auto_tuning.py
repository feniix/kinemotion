"""Automatic parameter tuning based on video characteristics."""

from dataclasses import dataclass
from enum import Enum

import numpy as np

from .types import FOOT_KEYS


@dataclass
class _PresetConfig:
    """Configuration modifiers for quality presets."""

    velocity_multiplier: float  # Multiplier for velocity threshold
    contact_frames_multiplier: float  # Multiplier for min contact frames
    smoothing_offset: int  # Offset to smoothing window (added to base)
    force_bilateral: bool | None  # None means use quality-based, True=force on, False=force off
    detection_confidence: float
    tracking_confidence: float


@dataclass
class _QualityAdjustment:
    """Smoothing adjustments based on tracking quality."""

    smoothing_add: int  # Frames to add to smoothing window
    enable_bilateral: bool  # Whether to enable bilateral filtering


class QualityPreset(str, Enum):
    """Quality presets for analysis."""

    FAST = "fast"  # Quick analysis, lower precision
    BALANCED = "balanced"  # Default: good balance of speed and accuracy
    ACCURATE = "accurate"  # Research-grade analysis, slower


# Quality preset configurations
# FAST: Speed over accuracy
# BALANCED: Default (uses quality-based settings)
# ACCURATE: Maximum accuracy
_PRESET_CONFIGS: dict[QualityPreset, _PresetConfig] = {
    QualityPreset.FAST: _PresetConfig(
        velocity_multiplier=1.5,
        contact_frames_multiplier=0.67,
        smoothing_offset=-2,
        force_bilateral=False,
        detection_confidence=0.3,
        tracking_confidence=0.3,
    ),
    QualityPreset.BALANCED: _PresetConfig(
        velocity_multiplier=1.0,
        contact_frames_multiplier=1.0,
        smoothing_offset=0,
        force_bilateral=None,
        detection_confidence=0.5,
        tracking_confidence=0.5,
    ),
    QualityPreset.ACCURATE: _PresetConfig(
        velocity_multiplier=0.5,
        contact_frames_multiplier=1.0,
        smoothing_offset=2,
        force_bilateral=True,
        detection_confidence=0.6,
        tracking_confidence=0.6,
    ),
}


# Quality-based adjustments
_QUALITY_ADJUSTMENTS: dict[str, _QualityAdjustment] = {
    "low": _QualityAdjustment(smoothing_add=2, enable_bilateral=True),
    "medium": _QualityAdjustment(smoothing_add=1, enable_bilateral=True),
    "high": _QualityAdjustment(smoothing_add=0, enable_bilateral=False),
}


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

    # Get preset configuration
    preset = _PRESET_CONFIGS[quality_preset]

    # Get quality-based adjustments
    quality_adj = _QUALITY_ADJUSTMENTS[quality]

    # Compute FPS-based baseline parameters
    # Base velocity threshold: 0.012 at 30fps, scaled inversely by fps
    # Must exceed typical MediaPipe landmark jitter (0.5-2% per frame)
    # Previous value of 0.004 was below noise floor, causing false IN_AIR detections
    base_velocity_threshold = 0.012 * (30.0 / fps)
    base_min_contact_frames = max(2, round(3.0 * (fps / 30.0)))

    # Smoothing window: Decrease with higher fps for better temporal resolution
    if fps <= 30:
        base_smoothing_window = 5
    else:
        base_smoothing_window = 3  # 60fps+ use 3-frame window

    # Apply preset modifiers and quality adjustments
    velocity_threshold = base_velocity_threshold * preset.velocity_multiplier
    min_contact_frames = max(2, int(base_min_contact_frames * preset.contact_frames_multiplier))

    # Smoothing window = base + preset offset + quality adjustment
    smoothing_window = base_smoothing_window + preset.smoothing_offset + quality_adj.smoothing_add
    smoothing_window = max(3, min(11, smoothing_window))

    # Ensure smoothing window is odd (required for Savitzky-Golay)
    if smoothing_window % 2 == 0:
        smoothing_window += 1

    # Bilateral filtering: preset can override, otherwise use quality-based
    if preset.force_bilateral is not None:
        bilateral_filter = preset.force_bilateral
    else:
        bilateral_filter = quality_adj.enable_bilateral

    # Fixed optimal values
    polyorder = 2  # Quadratic - optimal for parabolic motion
    visibility_threshold = 0.5  # Standard MediaPipe threshold
    outlier_rejection = True  # Removes tracking glitches
    use_curvature = True  # Trajectory curvature analysis

    return AnalysisParameters(
        smoothing_window=smoothing_window,
        polyorder=polyorder,
        velocity_threshold=velocity_threshold,
        min_contact_frames=min_contact_frames,
        visibility_threshold=visibility_threshold,
        detection_confidence=preset.detection_confidence,
        tracking_confidence=preset.tracking_confidence,
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
    frame_vis = []
    frame_y_positions = []

    for key in FOOT_KEYS:
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
