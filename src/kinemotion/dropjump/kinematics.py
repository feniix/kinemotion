"""Kinematic calculations for drop-jump metrics."""

from typing import TypedDict

import numpy as np
from numpy.typing import NDArray

from ..core.smoothing import compute_acceleration_from_derivative
from .analysis import (
    ContactState,
    detect_drop_start,
    find_contact_phases,
    find_interpolated_phase_transitions_with_curvature,
    find_landing_from_acceleration,
)


class DropJumpMetricsDict(TypedDict, total=False):
    """Type-safe dictionary for drop jump metrics JSON output."""

    ground_contact_time_ms: float | None
    flight_time_ms: float | None
    jump_height_m: float | None
    jump_height_kinematic_m: float | None
    jump_height_trajectory_normalized: float | None
    contact_start_frame: int | None
    contact_end_frame: int | None
    flight_start_frame: int | None
    flight_end_frame: int | None
    peak_height_frame: int | None
    contact_start_frame_precise: float | None
    contact_end_frame_precise: float | None
    flight_start_frame_precise: float | None
    flight_end_frame_precise: float | None


class DropJumpMetrics:
    """Container for drop-jump analysis metrics."""

    def __init__(self) -> None:
        self.ground_contact_time: float | None = None
        self.flight_time: float | None = None
        self.jump_height: float | None = None
        self.jump_height_kinematic: float | None = None  # From flight time
        self.jump_height_trajectory: float | None = None  # From position tracking
        self.contact_start_frame: int | None = None
        self.contact_end_frame: int | None = None
        self.flight_start_frame: int | None = None
        self.flight_end_frame: int | None = None
        self.peak_height_frame: int | None = None
        # Fractional frame indices for sub-frame precision timing
        self.contact_start_frame_precise: float | None = None
        self.contact_end_frame_precise: float | None = None
        self.flight_start_frame_precise: float | None = None
        self.flight_end_frame_precise: float | None = None

    def to_dict(self) -> DropJumpMetricsDict:
        """Convert metrics to dictionary for JSON output."""
        return {
            "ground_contact_time_ms": (
                round(self.ground_contact_time * 1000, 2)
                if self.ground_contact_time is not None
                else None
            ),
            "flight_time_ms": (
                round(self.flight_time * 1000, 2)
                if self.flight_time is not None
                else None
            ),
            "jump_height_m": (
                round(self.jump_height, 3) if self.jump_height is not None else None
            ),
            "jump_height_kinematic_m": (
                round(self.jump_height_kinematic, 3)
                if self.jump_height_kinematic is not None
                else None
            ),
            "jump_height_trajectory_normalized": (
                round(self.jump_height_trajectory, 4)
                if self.jump_height_trajectory is not None
                else None
            ),
            "contact_start_frame": (
                int(self.contact_start_frame)
                if self.contact_start_frame is not None
                else None
            ),
            "contact_end_frame": (
                int(self.contact_end_frame)
                if self.contact_end_frame is not None
                else None
            ),
            "flight_start_frame": (
                int(self.flight_start_frame)
                if self.flight_start_frame is not None
                else None
            ),
            "flight_end_frame": (
                int(self.flight_end_frame)
                if self.flight_end_frame is not None
                else None
            ),
            "peak_height_frame": (
                int(self.peak_height_frame)
                if self.peak_height_frame is not None
                else None
            ),
            "contact_start_frame_precise": (
                round(self.contact_start_frame_precise, 3)
                if self.contact_start_frame_precise is not None
                else None
            ),
            "contact_end_frame_precise": (
                round(self.contact_end_frame_precise, 3)
                if self.contact_end_frame_precise is not None
                else None
            ),
            "flight_start_frame_precise": (
                round(self.flight_start_frame_precise, 3)
                if self.flight_start_frame_precise is not None
                else None
            ),
            "flight_end_frame_precise": (
                round(self.flight_end_frame_precise, 3)
                if self.flight_end_frame_precise is not None
                else None
            ),
        }


def _determine_drop_start_frame(
    drop_start_frame: int | None,
    foot_y_positions: NDArray[np.float64],
    fps: float,
    smoothing_window: int,
) -> int:
    """Determine the drop start frame for analysis.

    Args:
        drop_start_frame: Manual drop start frame or None for auto-detection
        foot_y_positions: Vertical positions array
        fps: Video frame rate
        smoothing_window: Smoothing window size

    Returns:
        Drop start frame (0 if not detected/provided)
    """
    if drop_start_frame is None:
        # Auto-detect where drop jump actually starts (skip initial stationary period)
        return detect_drop_start(
            foot_y_positions,
            fps,
            min_stationary_duration=0.5,
            position_change_threshold=0.005,
            smoothing_window=smoothing_window,
        )
    return drop_start_frame


def _filter_phases_after_drop(
    phases: list[tuple[int, int, ContactState]],
    interpolated_phases: list[tuple[float, float, ContactState]],
    drop_start_frame: int,
) -> tuple[
    list[tuple[int, int, ContactState]], list[tuple[float, float, ContactState]]
]:
    """Filter phases to only include those after drop start.

    Args:
        phases: Integer frame phases
        interpolated_phases: Sub-frame precision phases
        drop_start_frame: Frame where drop starts

    Returns:
        Tuple of (filtered_phases, filtered_interpolated_phases)
    """
    if drop_start_frame <= 0:
        return phases, interpolated_phases

    filtered_phases = [
        (start, end, state) for start, end, state in phases if end >= drop_start_frame
    ]
    filtered_interpolated = [
        (start, end, state)
        for start, end, state in interpolated_phases
        if end >= drop_start_frame
    ]
    return filtered_phases, filtered_interpolated


def _identify_main_contact_phase(
    phases: list[tuple[int, int, ContactState]],
    ground_phases: list[tuple[int, int, int]],
    air_phases_indexed: list[tuple[int, int, int]],
    foot_y_positions: NDArray[np.float64],
) -> tuple[int, int, bool]:
    """Identify the main contact phase and determine if it's a drop jump.

    Args:
        phases: All phase tuples
        ground_phases: Ground phases with indices
        air_phases_indexed: Air phases with indices
        foot_y_positions: Vertical position array

    Returns:
        Tuple of (contact_start, contact_end, is_drop_jump)
    """
    # Initialize with first ground phase as fallback
    contact_start, contact_end = ground_phases[0][0], ground_phases[0][1]
    is_drop_jump = False

    # Detect if this is a drop jump or regular jump
    if air_phases_indexed and len(ground_phases) >= 2:
        first_ground_start, first_ground_end, first_ground_idx = ground_phases[0]
        first_air_idx = air_phases_indexed[0][2]

        # Find ground phase after first air phase
        ground_after_air = [
            (start, end, idx)
            for start, end, idx in ground_phases
            if idx > first_air_idx
        ]

        if ground_after_air and first_ground_idx < first_air_idx:
            # Check if first ground is at higher elevation (lower y) than ground after air
            first_ground_y = float(
                np.mean(foot_y_positions[first_ground_start : first_ground_end + 1])
            )
            second_ground_start, second_ground_end, _ = ground_after_air[0]
            second_ground_y = float(
                np.mean(foot_y_positions[second_ground_start : second_ground_end + 1])
            )

            # If first ground is significantly higher (>5% of frame), it's a drop jump
            if second_ground_y - first_ground_y > 0.05:
                is_drop_jump = True
                contact_start, contact_end = second_ground_start, second_ground_end

    if not is_drop_jump:
        # Regular jump: use longest ground contact phase
        contact_start, contact_end = max(
            [(s, e) for s, e, _ in ground_phases], key=lambda p: p[1] - p[0]
        )

    return contact_start, contact_end, is_drop_jump


def _find_precise_phase_timing(
    contact_start: int,
    contact_end: int,
    interpolated_phases: list[tuple[float, float, ContactState]],
) -> tuple[float, float]:
    """Find precise sub-frame timing for contact phase.

    Args:
        contact_start: Integer contact start frame
        contact_end: Integer contact end frame
        interpolated_phases: Sub-frame precision phases

    Returns:
        Tuple of (contact_start_frac, contact_end_frac)
    """
    contact_start_frac = float(contact_start)
    contact_end_frac = float(contact_end)

    # Find the matching ground phase in interpolated_phases
    for start_frac, end_frac, state in interpolated_phases:
        if (
            state == ContactState.ON_GROUND
            and int(start_frac) <= contact_start <= int(end_frac) + 1
            and int(start_frac) <= contact_end <= int(end_frac) + 1
        ):
            contact_start_frac = start_frac
            contact_end_frac = end_frac
            break

    return contact_start_frac, contact_end_frac


def _analyze_flight_phase(
    metrics: DropJumpMetrics,
    phases: list[tuple[int, int, ContactState]],
    interpolated_phases: list[tuple[float, float, ContactState]],
    contact_end: int,
    foot_y_positions: NDArray[np.float64],
    fps: float,
    smoothing_window: int,
    polyorder: int,
) -> None:
    """Analyze flight phase and calculate jump height metrics.

    Uses acceleration-based landing detection (like CMJ) for accurate flight time,
    then calculates jump height using kinematic formula h = g*t²/8.

    Args:
        metrics: DropJumpMetrics object to populate
        phases: All phase tuples
        interpolated_phases: Sub-frame precision phases
        contact_end: End of contact phase
        foot_y_positions: Vertical position array
        fps: Video frame rate
        smoothing_window: Window size for acceleration computation
        polyorder: Polynomial order for Savitzky-Golay filter
    """
    # Find takeoff frame (end of ground contact)
    flight_start = contact_end

    # Compute accelerations for landing detection
    accelerations = compute_acceleration_from_derivative(
        foot_y_positions, window_length=smoothing_window, polyorder=polyorder
    )

    # Use acceleration-based landing detection (like CMJ)
    # This finds the actual ground impact, not just when velocity drops
    flight_end = find_landing_from_acceleration(
        foot_y_positions, accelerations, flight_start, fps, search_duration=0.7
    )

    # Store integer frame indices
    metrics.flight_start_frame = flight_start
    metrics.flight_end_frame = flight_end

    # Find precise sub-frame timing for takeoff
    flight_start_frac = float(flight_start)
    flight_end_frac = float(flight_end)

    for start_frac, end_frac, state in interpolated_phases:
        if (
            state == ContactState.ON_GROUND
            and int(start_frac) <= flight_start <= int(end_frac) + 1
        ):
            # Use end of ground contact as precise takeoff
            flight_start_frac = end_frac
            break

    # Calculate flight time
    flight_frames_precise = flight_end_frac - flight_start_frac
    metrics.flight_time = flight_frames_precise / fps
    metrics.flight_start_frame_precise = flight_start_frac
    metrics.flight_end_frame_precise = flight_end_frac

    # Calculate jump height using kinematic method (like CMJ)
    # h = g * t² / 8
    g = 9.81  # m/s^2
    jump_height_kinematic = (g * metrics.flight_time**2) / 8

    # Always use kinematic method for jump height (like CMJ)
    metrics.jump_height = jump_height_kinematic
    metrics.jump_height_kinematic = jump_height_kinematic

    # Calculate trajectory-based height for reference
    takeoff_position = foot_y_positions[flight_start]
    flight_positions = foot_y_positions[flight_start : flight_end + 1]

    if len(flight_positions) > 0:
        peak_idx = np.argmin(flight_positions)
        metrics.peak_height_frame = int(flight_start + peak_idx)
        peak_position = np.min(flight_positions)

        height_normalized = float(takeoff_position - peak_position)
        metrics.jump_height_trajectory = height_normalized


def calculate_drop_jump_metrics(
    contact_states: list[ContactState],
    foot_y_positions: NDArray[np.float64],
    fps: float,
    drop_start_frame: int | None = None,
    velocity_threshold: float = 0.02,
    smoothing_window: int = 5,
    polyorder: int = 2,
    use_curvature: bool = True,
) -> DropJumpMetrics:
    """
    Calculate drop-jump metrics from contact states and positions.

    Jump height is calculated from flight time using kinematic formula: h = g × t² / 8

    Args:
        contact_states: Contact state for each frame
        foot_y_positions: Vertical positions of feet (normalized 0-1)
        fps: Video frame rate
        drop_start_frame: Optional manual drop start frame
        velocity_threshold: Velocity threshold used for contact detection (for interpolation)
        smoothing_window: Window size for velocity/acceleration smoothing (must be odd)
        polyorder: Polynomial order for Savitzky-Golay filter (default: 2)
        use_curvature: Whether to use curvature analysis for refining transitions

    Returns:
        DropJumpMetrics object with calculated values
    """
    metrics = DropJumpMetrics()

    # Determine drop start frame
    drop_start_frame_value = _determine_drop_start_frame(
        drop_start_frame, foot_y_positions, fps, smoothing_window
    )

    # Find contact phases
    phases = find_contact_phases(contact_states)
    interpolated_phases = find_interpolated_phase_transitions_with_curvature(
        foot_y_positions,
        contact_states,
        velocity_threshold,
        smoothing_window,
        polyorder,
        use_curvature,
    )

    if not phases:
        return metrics

    # Filter phases to only include those after drop start
    phases, interpolated_phases = _filter_phases_after_drop(
        phases, interpolated_phases, drop_start_frame_value
    )

    if not phases:
        return metrics

    # Separate ground and air phases
    ground_phases = [
        (start, end, i)
        for i, (start, end, state) in enumerate(phases)
        if state == ContactState.ON_GROUND
    ]
    air_phases_indexed = [
        (start, end, i)
        for i, (start, end, state) in enumerate(phases)
        if state == ContactState.IN_AIR
    ]

    if not ground_phases:
        return metrics

    # Identify main contact phase
    contact_start, contact_end, _ = _identify_main_contact_phase(
        phases, ground_phases, air_phases_indexed, foot_y_positions
    )

    # Store integer frame indices
    metrics.contact_start_frame = contact_start
    metrics.contact_end_frame = contact_end

    # Find precise timing for contact phase
    contact_start_frac, contact_end_frac = _find_precise_phase_timing(
        contact_start, contact_end, interpolated_phases
    )

    # Calculate ground contact time
    contact_frames_precise = contact_end_frac - contact_start_frac
    metrics.ground_contact_time = contact_frames_precise / fps
    metrics.contact_start_frame_precise = contact_start_frac
    metrics.contact_end_frame_precise = contact_end_frac

    # Analyze flight phase and calculate jump height
    _analyze_flight_phase(
        metrics,
        phases,
        interpolated_phases,
        contact_end,
        foot_y_positions,
        fps,
        smoothing_window,
        polyorder,
    )

    return metrics
