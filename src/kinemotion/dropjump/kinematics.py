"""Kinematic calculations for drop-jump metrics."""

from typing import TYPE_CHECKING, TypedDict

import numpy as np
from numpy.typing import NDArray

from ..core.formatting import format_float_metric, format_int_metric
from ..core.smoothing import compute_acceleration_from_derivative
from ..core.timing import NULL_TIMER, Timer
from .analysis import (
    ContactState,
    detect_drop_start,
    find_contact_phases,
    find_interpolated_phase_transitions_with_curvature,
    find_landing_from_acceleration,
)

if TYPE_CHECKING:
    from ..core.dropjump_metrics_validator import ValidationResult
    from ..core.metadata import ResultMetadata
    from ..core.quality import QualityAssessment


class DropJumpDataDict(TypedDict, total=False):
    """Type-safe dictionary for drop jump measurement data."""

    ground_contact_time_ms: float | None
    flight_time_ms: float | None
    jump_height_m: float | None
    jump_height_kinematic_m: float | None
    jump_height_trajectory_m: float | None
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


class DropJumpResultDict(TypedDict, total=False):
    """Type-safe dictionary for complete drop jump result with data and metadata."""

    data: DropJumpDataDict
    metadata: dict  # ResultMetadata.to_dict()
    validation: dict  # ValidationResult.to_dict()


class DropJumpMetrics:
    """Container for drop-jump analysis metrics."""

    def __init__(self) -> None:
        self.ground_contact_time: float | None = None
        self.flight_time: float | None = None
        self.jump_height: float | None = None
        self.jump_height_kinematic: float | None = None  # From flight time
        # From position tracking (normalized)
        self.jump_height_trajectory: float | None = None
        # From position tracking (meters)
        self.jump_height_trajectory_m: float | None = None
        self.drop_start_frame: int | None = None  # Frame when athlete leaves box
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
        # Quality assessment
        self.quality_assessment: QualityAssessment | None = None
        # Complete metadata
        self.result_metadata: ResultMetadata | None = None
        # Validation result
        self.validation_result: ValidationResult | None = None

    def _build_data_dict(self) -> DropJumpDataDict:
        """Build the data portion of the result dictionary.

        Returns:
            Dictionary containing formatted metric values.
        """
        return {
            "ground_contact_time_ms": format_float_metric(self.ground_contact_time, 1000, 2),
            "flight_time_ms": format_float_metric(self.flight_time, 1000, 2),
            "jump_height_m": format_float_metric(self.jump_height, 1, 3),
            "jump_height_kinematic_m": format_float_metric(self.jump_height_kinematic, 1, 3),
            "jump_height_trajectory_m": format_float_metric(self.jump_height_trajectory_m, 1, 3),
            "jump_height_trajectory_normalized": format_float_metric(
                self.jump_height_trajectory, 1, 4
            ),
            "contact_start_frame": format_int_metric(self.contact_start_frame),
            "contact_end_frame": format_int_metric(self.contact_end_frame),
            "flight_start_frame": format_int_metric(self.flight_start_frame),
            "flight_end_frame": format_int_metric(self.flight_end_frame),
            "peak_height_frame": format_int_metric(self.peak_height_frame),
            "contact_start_frame_precise": format_float_metric(
                self.contact_start_frame_precise, 1, 3
            ),
            "contact_end_frame_precise": format_float_metric(self.contact_end_frame_precise, 1, 3),
            "flight_start_frame_precise": format_float_metric(
                self.flight_start_frame_precise, 1, 3
            ),
            "flight_end_frame_precise": format_float_metric(self.flight_end_frame_precise, 1, 3),
        }

    def _build_metadata_dict(self) -> dict:
        """Build the metadata portion of the result dictionary.

        Returns:
            Metadata dictionary from available sources.
        """
        if self.result_metadata is not None:
            return self.result_metadata.to_dict()
        if self.quality_assessment is not None:
            return {"quality": self.quality_assessment.to_dict()}
        return {}

    def to_dict(self) -> DropJumpResultDict:
        """Convert metrics to JSON-serializable dictionary with data/metadata structure.

        Returns:
            Dictionary with nested data and metadata structure.
        """
        result: DropJumpResultDict = {
            "data": self._build_data_dict(),
            "metadata": self._build_metadata_dict(),
        }

        # Include validation results if available
        if self.validation_result is not None:
            result["validation"] = self.validation_result.to_dict()

        return result


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
            position_change_threshold=0.01,  # Improved from 0.005 for better accuracy
            smoothing_window=smoothing_window,
        )
    return drop_start_frame


def _filter_phases_after_drop(
    phases: list[tuple[int, int, ContactState]],
    interpolated_phases: list[tuple[float, float, ContactState]],
    drop_start_frame: int,
) -> tuple[list[tuple[int, int, ContactState]], list[tuple[float, float, ContactState]]]:
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
        (start, end, state) for start, end, state in interpolated_phases if end >= drop_start_frame
    ]
    return filtered_phases, filtered_interpolated


def _compute_robust_phase_position(
    foot_y_positions: NDArray[np.float64],
    phase_start: int,
    phase_end: int,
    temporal_window: int = 11,
) -> float:
    """Compute robust position estimate using temporal averaging.

    Uses median over a fixed temporal window to reduce sensitivity to
    MediaPipe landmark noise, improving reproducibility.

    Args:
        foot_y_positions: Vertical position array
        phase_start: Start frame of phase
        phase_end: End frame of phase
        temporal_window: Number of frames to average (default: 11)

    Returns:
        Robust position estimate using median
    """
    # Center the temporal window on the phase midpoint
    phase_mid = (phase_start + phase_end) // 2
    window_start = max(0, phase_mid - temporal_window // 2)
    window_end = min(len(foot_y_positions), phase_mid + temporal_window // 2 + 1)

    # Use median for robustness to outliers
    window_positions = foot_y_positions[window_start:window_end]
    return float(np.median(window_positions))


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
            (start, end, idx) for start, end, idx in ground_phases if idx > first_air_idx
        ]

        if ground_after_air and first_ground_idx < first_air_idx:
            # Check if first ground is at higher elevation (lower y) than
            # ground after air using robust temporal averaging
            first_ground_y = _compute_robust_phase_position(
                foot_y_positions, first_ground_start, first_ground_end
            )
            second_ground_start, second_ground_end, _ = ground_after_air[0]
            second_ground_y = _compute_robust_phase_position(
                foot_y_positions, second_ground_start, second_ground_end
            )

            # If first ground is significantly higher (>7% of frame), it's a drop jump
            # Increased from 0.05 to 0.07 with 11-frame temporal averaging
            # for reproducibility (balances detection sensitivity with noise robustness)
            # Note: MediaPipe has inherent non-determinism (Google issue #3945)
            if second_ground_y - first_ground_y > 0.07:
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

        # Calculate scale factor and metric height
        # Scale factor = kinematic height / normalized height
        if height_normalized > 0.001:
            scale_factor = metrics.jump_height_kinematic / height_normalized
            metrics.jump_height_trajectory_m = height_normalized * scale_factor
        else:
            metrics.jump_height_trajectory_m = 0.0


def calculate_drop_jump_metrics(
    contact_states: list[ContactState],
    foot_y_positions: NDArray[np.float64],
    fps: float,
    drop_start_frame: int | None = None,
    velocity_threshold: float = 0.02,
    smoothing_window: int = 5,
    polyorder: int = 2,
    use_curvature: bool = True,
    timer: Timer | None = None,
) -> DropJumpMetrics:
    """
    Calculate drop-jump metrics from contact states and positions.

    Jump height is calculated from flight time using kinematic formula: h = g × t² / 8

    Args:
        contact_states: Contact state for each frame
        foot_y_positions: Vertical positions of feet (normalized 0-1)
        fps: Video frame rate
        drop_start_frame: Optional manual drop start frame
        velocity_threshold: Velocity threshold used for contact detection
            (for interpolation)
        smoothing_window: Window size for velocity/acceleration smoothing
            (must be odd)
        polyorder: Polynomial order for Savitzky-Golay filter (default: 2)
        use_curvature: Whether to use curvature analysis for refining transitions
        timer: Optional Timer for measuring operations

    Returns:
        DropJumpMetrics object with calculated values
    """
    timer = timer or NULL_TIMER
    metrics = DropJumpMetrics()

    # Determine drop start frame
    with timer.measure("dj_detect_drop_start"):
        drop_start_frame_value = _determine_drop_start_frame(
            drop_start_frame, foot_y_positions, fps, smoothing_window
        )

    # Store drop start frame in metrics
    metrics.drop_start_frame = drop_start_frame_value if drop_start_frame_value > 0 else None

    # Find contact phases
    with timer.measure("dj_find_phases"):
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
    with timer.measure("dj_identify_contact"):
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
    with timer.measure("dj_analyze_flight"):
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
