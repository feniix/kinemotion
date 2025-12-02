"""Drop jump analysis module."""

from ..core.smoothing import interpolate_threshold_crossing
from .analysis import (
    ContactState,
    calculate_adaptive_threshold,
    compute_average_foot_position,
    detect_ground_contact,
    find_interpolated_phase_transitions_with_curvature,
    refine_transition_with_curvature,
)
from .debug_overlay import DebugOverlayRenderer
from .kinematics import DropJumpMetrics, calculate_drop_jump_metrics

__all__ = [
    # Contact detection
    "ContactState",
    "detect_ground_contact",
    "compute_average_foot_position",
    "calculate_adaptive_threshold",
    "interpolate_threshold_crossing",
    "refine_transition_with_curvature",
    "find_interpolated_phase_transitions_with_curvature",
    # Metrics
    "DropJumpMetrics",
    "calculate_drop_jump_metrics",
    # Debug overlay
    "DebugOverlayRenderer",
]
