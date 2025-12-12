"""Core functionality shared across all jump analysis types."""

from .filtering import (
    adaptive_smooth_window,
    bilateral_temporal_filter,
    detect_outliers_median,
    detect_outliers_ransac,
    reject_outliers,
    remove_outliers,
)
from .pose import PoseTracker, compute_center_of_mass
from .quality import (
    QualityAssessment,
    QualityIndicators,
    assess_jump_quality,
    calculate_position_stability,
)
from .smoothing import (
    compute_acceleration_from_derivative,
    compute_velocity,
    compute_velocity_from_derivative,
    smooth_landmarks,
    smooth_landmarks_advanced,
)
from .timing import (
    NULL_TIMER,
    NullTimer,
    PerformanceTimer,
    Timer,
)
from .video_io import VideoProcessor

__all__ = [
    # Pose tracking
    "PoseTracker",
    "compute_center_of_mass",
    # Smoothing
    "smooth_landmarks",
    "smooth_landmarks_advanced",
    "compute_velocity",
    "compute_velocity_from_derivative",
    "compute_acceleration_from_derivative",
    # Filtering
    "detect_outliers_ransac",
    "detect_outliers_median",
    "remove_outliers",
    "reject_outliers",
    "adaptive_smooth_window",
    "bilateral_temporal_filter",
    # Quality Assessment
    "QualityAssessment",
    "QualityIndicators",
    "assess_jump_quality",
    "calculate_position_stability",
    # Timing
    "PerformanceTimer",
    "Timer",
    "NullTimer",
    "NULL_TIMER",
    # Video I/O
    "VideoProcessor",
]
