"""Kinematic calculations for drop-jump metrics."""


import numpy as np

from .contact_detection import (
    ContactState,
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


def calculate_drop_jump_metrics(
    contact_states: list[ContactState],
    foot_y_positions: np.ndarray,
    fps: float,
    drop_height_m: float | None = None,
    velocity_threshold: float = 0.02,
    smoothing_window: int = 5,
    polyorder: int = 2,
    use_curvature: bool = True,
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

    Returns:
        DropJumpMetrics object with calculated values
    """
    metrics = DropJumpMetrics()
    phases = find_contact_phases(contact_states)

    # Get interpolated phases with curvature-based refinement
    # Combines velocity interpolation + acceleration pattern analysis
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

    # Find the main contact phase
    # For drop jumps: find first ON_GROUND after first IN_AIR (the landing after drop)
    # For regular jumps: use longest ON_GROUND phase
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

    # Detect if this is a drop jump or regular jump
    # Drop jump: first ground phase is elevated (lower y), followed by drop, then landing (higher y)
    is_drop_jump = False
    if air_phases_indexed and len(ground_phases) >= 2:
        first_ground_start, first_ground_end, first_ground_idx = ground_phases[0]
        first_air_idx = air_phases_indexed[0][2]

        # Find ground phase after first air phase
        ground_after_air = [
            (start, end, idx) for start, end, idx in ground_phases if idx > first_air_idx
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

    # Store integer frame indices (for visualization)
    metrics.contact_start_frame = contact_start
    metrics.contact_end_frame = contact_end

    # Find corresponding interpolated phase for precise timing
    contact_start_frac = float(contact_start)
    contact_end_frac = float(contact_end)

    # Find the matching ground phase in interpolated_phases
    for start_frac, end_frac, state in interpolated_phases:
        # Match by checking if integer frames are within this phase
        if (
            state == ContactState.ON_GROUND
            and int(start_frac) <= contact_start <= int(end_frac) + 1
            and int(start_frac) <= contact_end <= int(end_frac) + 1
        ):
            contact_start_frac = start_frac
            contact_end_frac = end_frac
            break

    # Calculate ground contact time using fractional frames
    contact_frames_precise = contact_end_frac - contact_start_frac
    metrics.ground_contact_time = contact_frames_precise / fps
    metrics.contact_start_frame_precise = contact_start_frac
    metrics.contact_end_frame_precise = contact_end_frac

    # Calculate calibration scale factor from drop height if provided
    scale_factor = 1.0
    if drop_height_m is not None and len(phases) >= 2:
        # Find the initial drop by looking for first IN_AIR phase
        # This represents the drop from the box

        if air_phases_indexed and ground_phases:
            # Get first air phase (the drop)
            first_air_start, first_air_end, _ = air_phases_indexed[0]

            # Initial position: at start of drop (on the box)
            # Look back a few frames to get stable position on box
            lookback_start = max(0, first_air_start - 5)
            if lookback_start < first_air_start:
                initial_position = float(np.mean(foot_y_positions[lookback_start:first_air_start]))
            else:
                initial_position = float(foot_y_positions[first_air_start])

            # Landing position: at the ground after drop
            # Use position at end of first air phase
            landing_position = float(foot_y_positions[first_air_end])

            # Drop distance in normalized coordinates (y increases downward)
            drop_normalized = landing_position - initial_position

            if drop_normalized > 0.01:  # Sanity check (at least 1% of frame height)
                # Calculate scale factor: real_meters / normalized_distance
                scale_factor = drop_height_m / drop_normalized

    # Find flight phase after ground contact
    flight_phases = [
        (start, end)
        for start, end, state in phases
        if state == ContactState.IN_AIR and start > contact_end
    ]

    if flight_phases:
        flight_start, flight_end = flight_phases[0]

        # Store integer frame indices (for visualization)
        metrics.flight_start_frame = flight_start
        metrics.flight_end_frame = flight_end

        # Find corresponding interpolated phase for precise timing
        flight_start_frac = float(flight_start)
        flight_end_frac = float(flight_end)

        # Find the matching air phase in interpolated_phases
        for start_frac, end_frac, state in interpolated_phases:
            # Match by checking if integer frames are within this phase
            if (
                state == ContactState.IN_AIR
                and int(start_frac) <= flight_start <= int(end_frac) + 1
                and int(start_frac) <= flight_end <= int(end_frac) + 1
            ):
                flight_start_frac = start_frac
                flight_end_frac = end_frac
                break

        # Calculate flight time using fractional frames
        flight_frames_precise = flight_end_frac - flight_start_frac
        metrics.flight_time = flight_frames_precise / fps
        metrics.flight_start_frame_precise = flight_start_frac
        metrics.flight_end_frame_precise = flight_end_frac

        # Calculate jump height using flight time (kinematic method)
        # h = (g * t^2) / 8, where t is total flight time
        g = 9.81  # m/s^2
        jump_height_kinematic = (g * metrics.flight_time**2) / 8

        # Calculate jump height from trajectory (position-based method)
        # This measures actual vertical displacement from takeoff to peak
        takeoff_position = foot_y_positions[flight_start]
        flight_positions = foot_y_positions[flight_start : flight_end + 1]

        if len(flight_positions) > 0:
            peak_idx = np.argmin(flight_positions)
            metrics.peak_height_frame = int(flight_start + peak_idx)
            peak_position = np.min(flight_positions)

            # Height in normalized coordinates (0-1 range)
            height_normalized = float(takeoff_position - peak_position)

            # Store trajectory value (in normalized coordinates)
            metrics.jump_height_trajectory = height_normalized

            # Choose measurement method based on calibration availability
            if drop_height_m is not None and scale_factor > 1.0:
                # Use calibrated trajectory measurement (most accurate)
                metrics.jump_height = height_normalized * scale_factor
                metrics.jump_height_kinematic = jump_height_kinematic
            else:
                # Use empirical correction factor for kinematic method
                # Testing shows kinematic method underestimates by ~29% due to:
                # 1. Contact detection timing (detects landing slightly early)
                # 2. Frame rate limitations (30 fps = 33ms intervals)
                # 3. Foot position vs center of mass difference
                kinematic_correction_factor = 1.35
                metrics.jump_height = jump_height_kinematic * kinematic_correction_factor
                metrics.jump_height_kinematic = jump_height_kinematic
        else:
            # Fallback to kinematic if no position data
            if drop_height_m is None:
                kinematic_correction_factor = 1.35
                metrics.jump_height = jump_height_kinematic * kinematic_correction_factor
            else:
                metrics.jump_height = jump_height_kinematic
            metrics.jump_height_kinematic = jump_height_kinematic

    return metrics


def estimate_jump_height_from_trajectory(
    foot_y_positions: np.ndarray,
    contact_start: int,
    flight_start: int,
    flight_end: int,
    pixel_to_meter_ratio: float | None = None,
) -> float:
    """
    Estimate jump height from position trajectory.

    Args:
        foot_y_positions: Vertical positions of feet (normalized or pixels)
        contact_start: Frame where ground contact starts
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
