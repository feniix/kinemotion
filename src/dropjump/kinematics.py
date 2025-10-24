"""Kinematic calculations for drop-jump metrics."""


import numpy as np

from .contact_detection import ContactState, find_contact_phases


class DropJumpMetrics:
    """Container for drop-jump analysis metrics."""

    def __init__(self) -> None:
        self.ground_contact_time: float | None = None
        self.flight_time: float | None = None
        self.jump_height: float | None = None
        self.contact_start_frame: int | None = None
        self.contact_end_frame: int | None = None
        self.flight_start_frame: int | None = None
        self.flight_end_frame: int | None = None
        self.peak_height_frame: int | None = None

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
        }


def calculate_drop_jump_metrics(
    contact_states: list[ContactState],
    foot_y_positions: np.ndarray,
    fps: float,
    reference_height_m: float | None = None,
) -> DropJumpMetrics:
    """
    Calculate drop-jump metrics from contact states and positions.

    Args:
        contact_states: Contact state for each frame
        foot_y_positions: Vertical positions of feet (normalized 0-1)
        fps: Video frame rate
        reference_height_m: Known height in meters for calibration (optional)

    Returns:
        DropJumpMetrics object with calculated values
    """
    metrics = DropJumpMetrics()
    phases = find_contact_phases(contact_states)

    if not phases:
        return metrics

    # Find the main contact phase (should be the longest ON_GROUND after initial landing)
    ground_phases = [
        (start, end) for start, end, state in phases if state == ContactState.ON_GROUND
    ]

    if not ground_phases:
        return metrics

    # Use the longest ground contact phase
    contact_start, contact_end = max(ground_phases, key=lambda p: p[1] - p[0])

    # Calculate ground contact time
    contact_frames = contact_end - contact_start + 1
    metrics.ground_contact_time = contact_frames / fps
    metrics.contact_start_frame = contact_start
    metrics.contact_end_frame = contact_end

    # Find flight phase after ground contact
    flight_phases = [
        (start, end)
        for start, end, state in phases
        if state == ContactState.IN_AIR and start > contact_end
    ]

    if flight_phases:
        flight_start, flight_end = flight_phases[0]
        flight_frames = flight_end - flight_start + 1
        metrics.flight_time = flight_frames / fps
        metrics.flight_start_frame = flight_start
        metrics.flight_end_frame = flight_end

        # Calculate jump height using flight time
        # h = (g * t^2) / 8, where t is total flight time
        g = 9.81  # m/s^2
        metrics.jump_height = (g * metrics.flight_time**2) / 8

        # Find peak height frame (lowest y value during flight)
        flight_positions = foot_y_positions[flight_start : flight_end + 1]
        if len(flight_positions) > 0:
            peak_idx = np.argmin(flight_positions)
            metrics.peak_height_frame = int(flight_start + peak_idx)

    # If reference height provided, calibrate the jump height
    if reference_height_m is not None and metrics.jump_height is not None:
        # This is a simple calibration - in practice you'd want to measure
        # pixel distance vs real height for more accurate results
        pass

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
