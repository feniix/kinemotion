"""Counter Movement Jump (CMJ) metrics calculation."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, TypedDict

import numpy as np

from ..core.formatting import format_float_metric
from ..core.types import FloatArray

if TYPE_CHECKING:
    from ..core.cmj_metrics_validator import ValidationResult
    from ..core.metadata import ResultMetadata
    from ..core.quality import QualityAssessment


class CMJDataDict(TypedDict, total=False):
    """Type-safe dictionary for CMJ measurement data."""

    jump_height_m: float
    flight_time_ms: float
    countermovement_depth_m: float
    eccentric_duration_ms: float
    concentric_duration_ms: float
    total_movement_time_ms: float
    peak_eccentric_velocity_m_s: float
    peak_concentric_velocity_m_s: float
    transition_time_ms: float | None
    standing_start_frame: float | None
    lowest_point_frame: float
    takeoff_frame: float
    landing_frame: float
    tracking_method: str


class CMJResultDict(TypedDict, total=False):
    """Type-safe dictionary for complete CMJ result with data and metadata."""

    data: CMJDataDict
    metadata: dict  # ResultMetadata.to_dict()
    validation: dict  # ValidationResult.to_dict()


@dataclass
class CMJMetrics:
    """Metrics for a counter movement jump analysis.

    Attributes:
        jump_height: Maximum jump height in meters
        flight_time: Time spent in the air in milliseconds
        countermovement_depth: Vertical distance traveled during eccentric
            phase in meters
        eccentric_duration: Time from countermovement start to lowest point in
            milliseconds
        concentric_duration: Time from lowest point to takeoff in milliseconds
        total_movement_time: Total time from countermovement start to takeoff
            in milliseconds
        peak_eccentric_velocity: Maximum downward velocity during
            countermovement in m/s
        peak_concentric_velocity: Maximum upward velocity during propulsion in
            m/s
        transition_time: Duration at lowest point (amortization phase) in milliseconds
        standing_start_frame: Frame where standing phase ends (countermovement begins)
        lowest_point_frame: Frame at lowest point of countermovement
        takeoff_frame: Frame where athlete leaves ground
        landing_frame: Frame where athlete lands
        video_fps: Frames per second of the analyzed video
        tracking_method: Method used for tracking ("foot" or "com")
        quality_assessment: Optional quality assessment with confidence and warnings
        validation_result: Optional validation result with physiological bounds checks
    """

    jump_height: float
    flight_time: float
    countermovement_depth: float
    eccentric_duration: float
    concentric_duration: float
    total_movement_time: float
    peak_eccentric_velocity: float
    peak_concentric_velocity: float
    transition_time: float | None
    standing_start_frame: float | None
    lowest_point_frame: float
    takeoff_frame: float
    landing_frame: float
    video_fps: float
    tracking_method: str
    quality_assessment: "QualityAssessment | None" = None
    result_metadata: "ResultMetadata | None" = None
    validation_result: "ValidationResult | None" = None

    def to_dict(self) -> CMJResultDict:
        """Convert metrics to JSON-serializable dictionary with data/metadata structure.

        Returns:
            Dictionary with nested data and metadata structure.
        """
        data: CMJDataDict = {
            "jump_height_m": format_float_metric(self.jump_height, 1, 3),  # type: ignore[typeddict-item]
            "flight_time_ms": format_float_metric(self.flight_time, 1000, 2),  # type: ignore[typeddict-item]
            "countermovement_depth_m": format_float_metric(self.countermovement_depth, 1, 3),  # type: ignore[typeddict-item]
            "eccentric_duration_ms": format_float_metric(self.eccentric_duration, 1000, 2),  # type: ignore[typeddict-item]
            "concentric_duration_ms": format_float_metric(self.concentric_duration, 1000, 2),  # type: ignore[typeddict-item]
            "total_movement_time_ms": format_float_metric(self.total_movement_time, 1000, 2),  # type: ignore[typeddict-item]
            "peak_eccentric_velocity_m_s": format_float_metric(self.peak_eccentric_velocity, 1, 4),  # type: ignore[typeddict-item]
            "peak_concentric_velocity_m_s": format_float_metric(
                self.peak_concentric_velocity, 1, 4
            ),  # type: ignore[typeddict-item]
            "transition_time_ms": format_float_metric(self.transition_time, 1000, 2),
            "standing_start_frame": (
                float(self.standing_start_frame) if self.standing_start_frame is not None else None
            ),
            "lowest_point_frame": float(self.lowest_point_frame),
            "takeoff_frame": float(self.takeoff_frame),
            "landing_frame": float(self.landing_frame),
            "tracking_method": self.tracking_method,
        }

        # Build metadata from ResultMetadata if available, otherwise use legacy quality
        if self.result_metadata is not None:
            metadata = self.result_metadata.to_dict()
        elif self.quality_assessment is not None:
            # Fallback for backwards compatibility during transition
            metadata = {"quality": self.quality_assessment.to_dict()}
        else:
            # No metadata available
            metadata = {}

        result: CMJResultDict = {"data": data, "metadata": metadata}

        # Include validation results if available
        if self.validation_result is not None:
            result["validation"] = self.validation_result.to_dict()

        return result


def _calculate_scale_factor(
    positions: FloatArray,
    takeoff_frame: float,
    landing_frame: float,
    jump_height: float,
) -> float:
    """Calculate meters per normalized unit scaling factor from flight phase.

    Args:
        positions: Array of vertical positions
        takeoff_frame: Takeoff frame index
        landing_frame: Landing frame index
        jump_height: Calculated jump height in meters

    Returns:
        Scale factor (meters per normalized unit)
    """
    flight_start_idx = int(takeoff_frame)
    flight_end_idx = int(landing_frame)
    flight_positions = positions[flight_start_idx:flight_end_idx]

    if len(flight_positions) == 0:
        return 0.0

    peak_flight_pos = np.min(flight_positions)
    takeoff_pos = positions[flight_start_idx]
    flight_displacement = takeoff_pos - peak_flight_pos

    if flight_displacement > 0.001:
        return jump_height / flight_displacement
    return 0.0


def _calculate_countermovement_depth(
    positions: FloatArray,
    standing_start_frame: float | None,
    lowest_point_frame: float,
    scale_factor: float,
) -> float:
    """Calculate countermovement depth in meters.

    Args:
        positions: Array of vertical positions
        standing_start_frame: Standing phase end frame (or None)
        lowest_point_frame: Lowest point frame index
        scale_factor: Meters per normalized unit

    Returns:
        Countermovement depth in meters
    """
    standing_position = (
        positions[int(standing_start_frame)] if standing_start_frame is not None else positions[0]
    )
    lowest_position = positions[int(lowest_point_frame)]
    depth_normalized = abs(standing_position - lowest_position)
    return depth_normalized * scale_factor


def _calculate_phase_durations(
    standing_start_frame: float | None,
    lowest_point_frame: float,
    takeoff_frame: float,
    fps: float,
) -> tuple[float, float, float]:
    """Calculate phase durations in seconds.

    Args:
        standing_start_frame: Standing phase end frame (or None)
        lowest_point_frame: Lowest point frame index
        takeoff_frame: Takeoff frame index
        fps: Frames per second

    Returns:
        Tuple of (eccentric_duration, concentric_duration, total_movement_time)
    """
    if standing_start_frame is not None:
        eccentric_duration = (lowest_point_frame - standing_start_frame) / fps
        total_movement_time = (takeoff_frame - standing_start_frame) / fps
    else:
        eccentric_duration = lowest_point_frame / fps
        total_movement_time = takeoff_frame / fps

    concentric_duration = (takeoff_frame - lowest_point_frame) / fps
    return eccentric_duration, concentric_duration, total_movement_time


def _calculate_peak_velocities(
    velocities: FloatArray,
    standing_start_frame: float | None,
    lowest_point_frame: float,
    takeoff_frame: float,
    velocity_scale: float,
) -> tuple[float, float]:
    """Calculate peak eccentric and concentric velocities.

    Args:
        velocities: Array of velocities
        standing_start_frame: Standing phase end frame (or None)
        lowest_point_frame: Lowest point frame index
        takeoff_frame: Takeoff frame index
        velocity_scale: Velocity scaling factor

    Returns:
        Tuple of (peak_eccentric_velocity, peak_concentric_velocity)
    """
    eccentric_start_idx = int(standing_start_frame) if standing_start_frame else 0
    eccentric_end_idx = int(lowest_point_frame)
    eccentric_velocities = velocities[eccentric_start_idx:eccentric_end_idx]

    peak_eccentric_velocity = 0.0
    if len(eccentric_velocities) > 0:
        peak = float(np.max(eccentric_velocities)) * velocity_scale
        peak_eccentric_velocity = max(0.0, peak)

    concentric_start_idx = int(lowest_point_frame)
    concentric_end_idx = int(takeoff_frame)
    concentric_velocities = velocities[concentric_start_idx:concentric_end_idx]

    peak_concentric_velocity = 0.0
    if len(concentric_velocities) > 0:
        peak_concentric_velocity = abs(float(np.min(concentric_velocities))) * velocity_scale

    return peak_eccentric_velocity, peak_concentric_velocity


def _calculate_transition_time(
    velocities: FloatArray,
    lowest_point_frame: float,
    fps: float,
) -> float | None:
    """Calculate transition/amortization time around lowest point.

    Args:
        velocities: Array of velocities
        lowest_point_frame: Lowest point frame index
        fps: Frames per second

    Returns:
        Transition time in seconds, or None if no transition detected
    """
    transition_threshold = 0.005
    search_window = int(fps * 0.1)

    transition_start_idx = max(0, int(lowest_point_frame) - search_window)
    transition_end_idx = min(len(velocities), int(lowest_point_frame) + search_window)

    transition_frames = sum(
        1
        for i in range(transition_start_idx, transition_end_idx)
        if abs(velocities[i]) < transition_threshold
    )

    return transition_frames / fps if transition_frames > 0 else None


def calculate_cmj_metrics(
    positions: FloatArray,
    velocities: FloatArray,
    standing_start_frame: float | None,
    lowest_point_frame: float,
    takeoff_frame: float,
    landing_frame: float,
    fps: float,
    tracking_method: str = "foot",
) -> CMJMetrics:
    """Calculate all CMJ metrics from detected phases.

    Args:
        positions: Array of vertical positions (normalized coordinates)
        velocities: Array of vertical velocities
        standing_start_frame: Frame where countermovement begins (fractional)
        lowest_point_frame: Frame at lowest point (fractional)
        takeoff_frame: Frame at takeoff (fractional)
        landing_frame: Frame at landing (fractional)
        fps: Video frames per second
        tracking_method: Tracking method used ("foot" or "com")

    Returns:
        CMJMetrics object with all calculated metrics.
    """
    # Calculate jump height from flight time using kinematic formula: h = g*t²/8
    g = 9.81
    flight_time = (landing_frame - takeoff_frame) / fps
    jump_height = (g * flight_time**2) / 8

    # Calculate scaling factor and derived metrics
    scale_factor = _calculate_scale_factor(positions, takeoff_frame, landing_frame, jump_height)
    countermovement_depth = _calculate_countermovement_depth(
        positions, standing_start_frame, lowest_point_frame, scale_factor
    )

    eccentric_duration, concentric_duration, total_movement_time = _calculate_phase_durations(
        standing_start_frame, lowest_point_frame, takeoff_frame, fps
    )

    velocity_scale = scale_factor * fps
    peak_eccentric_velocity, peak_concentric_velocity = _calculate_peak_velocities(
        velocities,
        standing_start_frame,
        lowest_point_frame,
        takeoff_frame,
        velocity_scale,
    )

    transition_time = _calculate_transition_time(velocities, lowest_point_frame, fps)

    return CMJMetrics(
        jump_height=jump_height,
        flight_time=flight_time,
        countermovement_depth=countermovement_depth,
        eccentric_duration=eccentric_duration,
        concentric_duration=concentric_duration,
        total_movement_time=total_movement_time,
        peak_eccentric_velocity=peak_eccentric_velocity,
        peak_concentric_velocity=peak_concentric_velocity,
        transition_time=transition_time,
        standing_start_frame=standing_start_frame,
        lowest_point_frame=lowest_point_frame,
        takeoff_frame=takeoff_frame,
        landing_frame=landing_frame,
        video_fps=fps,
        tracking_method=tracking_method,
    )
