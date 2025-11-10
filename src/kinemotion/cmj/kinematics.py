"""Counter Movement Jump (CMJ) metrics calculation."""

from dataclasses import dataclass
from typing import TypedDict

import numpy as np
from numpy.typing import NDArray


class CMJMetricsDict(TypedDict, total=False):
    """Type-safe dictionary for CMJ metrics JSON output."""

    jump_height_m: float
    flight_time_s: float
    countermovement_depth_m: float
    eccentric_duration_s: float
    concentric_duration_s: float
    total_movement_time_s: float
    peak_eccentric_velocity_m_s: float
    peak_concentric_velocity_m_s: float
    transition_time_s: float | None
    standing_start_frame: float | None
    lowest_point_frame: float
    takeoff_frame: float
    landing_frame: float
    video_fps: float
    tracking_method: str


@dataclass
class CMJMetrics:
    """Metrics for a counter movement jump analysis.

    Attributes:
        jump_height: Maximum jump height in meters
        flight_time: Time spent in the air in seconds
        countermovement_depth: Vertical distance traveled during eccentric phase in meters
        eccentric_duration: Time from countermovement start to lowest point in seconds
        concentric_duration: Time from lowest point to takeoff in seconds
        total_movement_time: Total time from countermovement start to takeoff in seconds
        peak_eccentric_velocity: Maximum downward velocity during countermovement in m/s
        peak_concentric_velocity: Maximum upward velocity during propulsion in m/s
        transition_time: Duration at lowest point (amortization phase) in seconds
        standing_start_frame: Frame where standing phase ends (countermovement begins)
        lowest_point_frame: Frame at lowest point of countermovement
        takeoff_frame: Frame where athlete leaves ground
        landing_frame: Frame where athlete lands
        video_fps: Frames per second of the analyzed video
        tracking_method: Method used for tracking ("foot" or "com")
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

    def to_dict(self) -> CMJMetricsDict:
        """Convert metrics to JSON-serializable dictionary.

        Returns:
            Dictionary with all metrics, converting NumPy types to Python types.
        """
        return {
            "jump_height_m": float(self.jump_height),
            "flight_time_s": float(self.flight_time),
            "countermovement_depth_m": float(self.countermovement_depth),
            "eccentric_duration_s": float(self.eccentric_duration),
            "concentric_duration_s": float(self.concentric_duration),
            "total_movement_time_s": float(self.total_movement_time),
            "peak_eccentric_velocity_m_s": float(self.peak_eccentric_velocity),
            "peak_concentric_velocity_m_s": float(self.peak_concentric_velocity),
            "transition_time_s": (
                float(self.transition_time)
                if self.transition_time is not None
                else None
            ),
            "standing_start_frame": (
                float(self.standing_start_frame)
                if self.standing_start_frame is not None
                else None
            ),
            "lowest_point_frame": float(self.lowest_point_frame),
            "takeoff_frame": float(self.takeoff_frame),
            "landing_frame": float(self.landing_frame),
            "video_fps": float(self.video_fps),
            "tracking_method": self.tracking_method,
        }


def calculate_cmj_metrics(
    positions: NDArray[np.float64],
    velocities: NDArray[np.float64],
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
    # Calculate flight time from takeoff to landing
    flight_time = (landing_frame - takeoff_frame) / fps

    # Calculate jump height from flight time using kinematic formula
    # h = g * t^2 / 8 (where t is total flight time)
    g = 9.81  # gravity in m/s^2
    jump_height = (g * flight_time**2) / 8

    # Calculate countermovement depth
    if standing_start_frame is not None:
        standing_position = positions[int(standing_start_frame)]
    else:
        # Use position at start of recording if standing not detected
        standing_position = positions[0]

    lowest_position = positions[int(lowest_point_frame)]
    countermovement_depth = abs(standing_position - lowest_position)

    # Calculate phase durations
    if standing_start_frame is not None:
        eccentric_duration = (lowest_point_frame - standing_start_frame) / fps
        total_movement_time = (takeoff_frame - standing_start_frame) / fps
    else:
        # If no standing phase detected, measure from start
        eccentric_duration = lowest_point_frame / fps
        total_movement_time = takeoff_frame / fps

    concentric_duration = (takeoff_frame - lowest_point_frame) / fps

    # Calculate peak velocities
    # Eccentric phase: negative velocities (downward)
    if standing_start_frame is not None:
        eccentric_start_idx = int(standing_start_frame)
    else:
        eccentric_start_idx = 0

    eccentric_end_idx = int(lowest_point_frame)
    eccentric_velocities = velocities[eccentric_start_idx:eccentric_end_idx]

    if len(eccentric_velocities) > 0:
        # Peak eccentric velocity is most negative value
        peak_eccentric_velocity = float(np.min(eccentric_velocities))
    else:
        peak_eccentric_velocity = 0.0

    # Concentric phase: positive velocities (upward)
    concentric_start_idx = int(lowest_point_frame)
    concentric_end_idx = int(takeoff_frame)
    concentric_velocities = velocities[concentric_start_idx:concentric_end_idx]

    if len(concentric_velocities) > 0:
        peak_concentric_velocity = float(np.max(concentric_velocities))
    else:
        peak_concentric_velocity = 0.0

    # Estimate transition time (amortization phase)
    # Look for period around lowest point where velocity is near zero
    transition_threshold = 0.005  # Very low velocity threshold
    search_window = int(fps * 0.1)  # Search within ±100ms

    transition_start_idx = max(0, int(lowest_point_frame) - search_window)
    transition_end_idx = min(len(velocities), int(lowest_point_frame) + search_window)

    transition_frames = 0
    for i in range(transition_start_idx, transition_end_idx):
        if abs(velocities[i]) < transition_threshold:
            transition_frames += 1

    transition_time = transition_frames / fps if transition_frames > 0 else None

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
