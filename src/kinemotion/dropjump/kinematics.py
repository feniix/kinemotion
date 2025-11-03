"""Kinematic calculations for drop-jump metrics."""

import numpy as np

from .analysis import (
    ContactState,
    detect_drop_start,
    find_contact_phases,
    find_interpolated_phase_transitions_with_curvature,
)


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

    def to_dict(self) -> dict:
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
    foot_y_positions: np.ndarray,
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
        detected_frame = detect_drop_start(
            foot_y_positions,
            fps,
            min_stationary_duration=0.5,
            position_change_threshold=0.005,
            smoothing_window=smoothing_window,
        )
        return detected_frame if detected_frame is not None else 0
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
    foot_y_positions: np.ndarray,
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


def _calculate_calibration_scale(
    drop_height_m: float | None,
    phases: list[tuple[int, int, ContactState]],
    air_phases_indexed: list[tuple[int, int, int]],
    foot_y_positions: np.ndarray,
) -> float:
    """Calculate calibration scale factor from known drop height.

    Args:
        drop_height_m: Known drop height in meters
        phases: All phase tuples
        air_phases_indexed: Air phases with indices
        foot_y_positions: Vertical position array

    Returns:
        Scale factor (1.0 if no calibration possible)
    """
    scale_factor = 1.0

    if drop_height_m is None or len(phases) < 2:
        return scale_factor

    if not air_phases_indexed:
        return scale_factor

    # Get first air phase (the drop)
    first_air_start, first_air_end, _ = air_phases_indexed[0]

    # Initial position: at start of drop (on the box)
    lookback_start = max(0, first_air_start - 5)
    if lookback_start < first_air_start:
        initial_position = float(
            np.mean(foot_y_positions[lookback_start:first_air_start])
        )
    else:
        initial_position = float(foot_y_positions[first_air_start])

    # Landing position: at the ground after drop
    landing_position = float(foot_y_positions[first_air_end])

    # Drop distance in normalized coordinates (y increases downward)
    drop_normalized = landing_position - initial_position

    if drop_normalized > 0.01:  # Sanity check
        scale_factor = drop_height_m / drop_normalized

    return scale_factor


def _analyze_flight_phase(
    metrics: DropJumpMetrics,
    phases: list[tuple[int, int, ContactState]],
    interpolated_phases: list[tuple[float, float, ContactState]],
    contact_end: int,
    foot_y_positions: np.ndarray,
    fps: float,
    drop_height_m: float | None,
    scale_factor: float,
    kinematic_correction_factor: float,
) -> None:
    """Analyze flight phase and calculate jump height metrics.

    Args:
        metrics: DropJumpMetrics object to populate
        phases: All phase tuples
        interpolated_phases: Sub-frame precision phases
        contact_end: End of contact phase
        foot_y_positions: Vertical position array
        fps: Video frame rate
        drop_height_m: Known drop height (optional)
        scale_factor: Calibration scale factor
        kinematic_correction_factor: Correction for kinematic method
    """
    # Find flight phase after ground contact
    flight_phases = [
        (start, end)
        for start, end, state in phases
        if state == ContactState.IN_AIR and start > contact_end
    ]

    if not flight_phases:
        return

    flight_start, flight_end = flight_phases[0]

    # Store integer frame indices
    metrics.flight_start_frame = flight_start
    metrics.flight_end_frame = flight_end

    # Find precise timing
    flight_start_frac = float(flight_start)
    flight_end_frac = float(flight_end)

    for start_frac, end_frac, state in interpolated_phases:
        if (
            state == ContactState.IN_AIR
            and int(start_frac) <= flight_start <= int(end_frac) + 1
            and int(start_frac) <= flight_end <= int(end_frac) + 1
        ):
            flight_start_frac = start_frac
            flight_end_frac = end_frac
            break

    # Calculate flight time
    flight_frames_precise = flight_end_frac - flight_start_frac
    metrics.flight_time = flight_frames_precise / fps
    metrics.flight_start_frame_precise = flight_start_frac
    metrics.flight_end_frame_precise = flight_end_frac

    # Calculate jump height using kinematic method
    g = 9.81  # m/s^2
    jump_height_kinematic = (g * metrics.flight_time**2) / 8

    # Calculate jump height from trajectory
    takeoff_position = foot_y_positions[flight_start]
    flight_positions = foot_y_positions[flight_start : flight_end + 1]

    if len(flight_positions) > 0:
        peak_idx = np.argmin(flight_positions)
        metrics.peak_height_frame = int(flight_start + peak_idx)
        peak_position = np.min(flight_positions)

        height_normalized = float(takeoff_position - peak_position)
        metrics.jump_height_trajectory = height_normalized

        # Choose measurement method based on calibration availability
        if drop_height_m is not None and scale_factor > 1.0:
            metrics.jump_height = height_normalized * scale_factor
            metrics.jump_height_kinematic = jump_height_kinematic
        else:
            metrics.jump_height = jump_height_kinematic * kinematic_correction_factor
            metrics.jump_height_kinematic = jump_height_kinematic
    else:
        # Fallback to kinematic if no position data
        if drop_height_m is None:
            metrics.jump_height = jump_height_kinematic * kinematic_correction_factor
        else:
            metrics.jump_height = jump_height_kinematic
        metrics.jump_height_kinematic = jump_height_kinematic


def calculate_drop_jump_metrics(
    contact_states: list[ContactState],
    foot_y_positions: np.ndarray,
    fps: float,
    drop_height_m: float | None = None,
    drop_start_frame: int | None = None,
    velocity_threshold: float = 0.02,
    smoothing_window: int = 5,
    polyorder: int = 2,
    use_curvature: bool = True,
    kinematic_correction_factor: float = 1.0,
) -> DropJumpMetrics:
    """
    Calculate drop-jump metrics from contact states and positions.

    Args:
        contact_states: Contact state for each frame
        foot_y_positions: Vertical positions of feet (normalized 0-1)
        fps: Video frame rate
        drop_height_m: Known drop box/platform height in meters for calibration (optional)
        velocity_threshold: Velocity threshold used for contact detection (for interpolation)
        smoothing_window: Window size for velocity/acceleration smoothing (must be odd)
        polyorder: Polynomial order for Savitzky-Golay filter (default: 2)
        use_curvature: Whether to use curvature analysis for refining transitions
        kinematic_correction_factor: Correction factor for kinematic jump height calculation
            (default: 1.0 = no correction). Historical testing suggested 1.35, but this is
            unvalidated. Use calibrated measurement (--drop-height) for validated results.

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

    # Calculate calibration scale factor
    scale_factor = _calculate_calibration_scale(
        drop_height_m, phases, air_phases_indexed, foot_y_positions
    )

    # Analyze flight phase and calculate jump height
    _analyze_flight_phase(
        metrics,
        phases,
        interpolated_phases,
        contact_end,
        foot_y_positions,
        fps,
        drop_height_m,
        scale_factor,
        kinematic_correction_factor,
    )

    return metrics


def estimate_jump_height_from_trajectory(
    foot_y_positions: np.ndarray,
    flight_start: int,
    flight_end: int,
    pixel_to_meter_ratio: float | None = None,
) -> float:
    """
    Estimate jump height from position trajectory.

    Args:
        foot_y_positions: Vertical positions of feet (normalized or pixels)
        flight_start: Frame where flight begins
        flight_end: Frame where flight ends
        pixel_to_meter_ratio: Conversion factor from pixels to meters

    Returns:
        Estimated jump height in meters (or normalized units if no calibration)
    """
    if flight_end < flight_start:
        return 0.0

    # Get position at takeoff (end of contact) and peak (minimum y during flight)
    takeoff_position = foot_y_positions[flight_start]
    flight_positions = foot_y_positions[flight_start : flight_end + 1]

    if len(flight_positions) == 0:
        return 0.0

    peak_position = np.min(flight_positions)

    # Height difference (in normalized coordinates, y increases downward)
    height_diff = takeoff_position - peak_position

    # Convert to meters if calibration available
    if pixel_to_meter_ratio is not None:
        return float(height_diff * pixel_to_meter_ratio)

    return float(height_diff)
