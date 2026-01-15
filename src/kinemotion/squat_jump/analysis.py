"""Phase detection logic for Squat Jump (SJ) analysis."""

from enum import Enum

import numpy as np
from scipy.signal import savgol_filter

from ..core.types import FloatArray


class SJPhase(Enum):
    """Phases of a squat jump."""

    SQUAT_HOLD = "squat_hold"
    CONCENTRIC = "concentric"
    FLIGHT = "flight"
    LANDING = "landing"
    UNKNOWN = "unknown"


def detect_sj_phases(
    positions: FloatArray,
    fps: float,
    velocity_threshold: float = 0.1,
    window_length: int = 5,
    polyorder: int = 2,
) -> tuple[int, int, int, int] | None:
    """Detect phases in a squat jump video.

    Squat Jump phase detection follows this progression:
    1. Squat hold - static squat position
    2. Concentric - upward movement from squat
    3. Takeoff - feet leave ground
    4. Flight - in the air
    5. Landing - feet contact ground

    Args:
        positions: 1D array of vertical positions (normalized coordinates)
        fps: Video frames per second
        velocity_threshold: Threshold for detecting flight phase (m/s)
        window_length: Window size for velocity smoothing
        polyorder: Polynomial order for smoothing

    Returns:
        Tuple of (squat_hold_start, concentric_start, takeoff_frame, landing_frame)
        or None if phases cannot be detected
    """
    if len(positions) < 20:  # Minimum viable sequence length
        return None

    # Ensure window length is appropriate for derivative calculations
    if window_length % 2 == 0:
        window_length += 1

    # Step 1: Detect squat hold start
    squat_hold_start = detect_squat_start(
        positions,
        fps,
        velocity_threshold=velocity_threshold,
        window_length=window_length,
        polyorder=polyorder,
    )

    if squat_hold_start is None:
        # If no squat hold detected, start from reasonable beginning
        squat_hold_start = len(positions) // 4

    # Step 2: Compute signed velocities for phase detection
    if len(positions) < window_length:
        # Fallback for short sequences
        velocities = np.diff(positions, prepend=positions[0])
    else:
        velocities = savgol_filter(
            positions, window_length, polyorder, deriv=1, delta=1.0, mode="interp"
        )

    # Step 3: Detect takeoff (this marks the start of concentric phase)
    takeoff_frame = detect_takeoff(
        positions, velocities, fps, velocity_threshold=velocity_threshold
    )

    if takeoff_frame is None:
        return None

    # Concentric start begins when upward movement starts after squat hold
    # This is just before takeoff when velocity becomes significantly negative
    concentric_start = takeoff_frame
    # Look backward from takeoff to find where concentric phase truly begins
    for i in range(takeoff_frame - 1, max(squat_hold_start, 0), -1):
        if velocities[i] <= -velocity_threshold * 0.5:  # Start of upward movement
            concentric_start = i
            break

    # Step 4: Detect landing
    landing_frame = detect_landing(
        positions,
        velocities,
        fps,
        velocity_threshold=velocity_threshold,
        min_flight_frames=5,
        landing_search_window_s=0.5,
        window_length=window_length,
        polyorder=polyorder,
    )

    if landing_frame is None:
        # Fallback: estimate landing from peak height + typical flight time
        # takeoff_frame is guaranteed to be an int here (we returned earlier if None)
        peak_search_start = takeoff_frame
        peak_search_end = min(len(positions), takeoff_frame + int(fps * 1.0))
        if peak_search_end > peak_search_start:
            flight_positions = positions[peak_search_start:peak_search_end]
            peak_idx = int(np.argmin(flight_positions))
            peak_frame = peak_search_start + peak_idx
            # Estimate landing as 0.3s after peak (typical SJ flight time)
            landing_frame = peak_frame + int(fps * 0.3)
        else:
            return None

    # Validate the detected phases
    if landing_frame <= takeoff_frame or takeoff_frame <= squat_hold_start:
        # Invalid phase sequence
        return None

    # Return all detected phases
    return (squat_hold_start, concentric_start, takeoff_frame, landing_frame)


def detect_squat_start(
    positions: FloatArray,
    fps: float,
    velocity_threshold: float = 0.1,
    min_hold_duration: float = 0.15,
    min_search_frame: int = 20,
    window_length: int = 5,
    polyorder: int = 2,
) -> int | None:
    """Detect start of squat hold phase.

    Squat hold is detected when the athlete maintains a relatively stable
    position with low velocity for a minimum duration.

    Args:
        positions: 1D array of vertical positions (normalized coordinates)
        fps: Video frames per second
        velocity_threshold: Maximum velocity to consider stationary (m/s)
        min_hold_duration: Minimum duration to maintain stable position (seconds)
        min_search_frame: Minimum frame to start searching (avoid initial settling)
        window_length: Window size for velocity smoothing
        polyorder: Polynomial order for smoothing

    Returns:
        Frame index where squat hold begins, or None if not detected
    """
    if len(positions) < min_search_frame + 10:
        return None

    # Compute velocity to detect stationary periods
    if len(positions) < window_length:
        velocities = np.abs(np.diff(positions, prepend=positions[0]))
    else:
        if window_length % 2 == 0:
            window_length += 1
        velocities = np.abs(
            savgol_filter(positions, window_length, polyorder, deriv=1, delta=1.0, mode="interp")
        )

    # Search for stable period with low velocity
    min_hold_frames = int(min_hold_duration * fps)
    start_search = min_search_frame
    end_search = len(positions) - min_hold_frames

    # Look for consecutive frames with velocity below threshold
    for i in range(start_search, end_search):
        # Check if we have a stable period of sufficient duration
        stable_period = velocities[i : i + min_hold_frames]
        if np.all(stable_period <= velocity_threshold):
            # Found a stable period - return start of this period
            return i

    return None


def _find_takeoff_threshold_crossing(
    velocities: FloatArray,
    search_start: int,
    search_end: int,
    velocity_threshold: float,
    min_duration_frames: int,
) -> int | None:
    """Find first frame where velocity exceeds threshold for minimum duration."""
    above_threshold = velocities[search_start:search_end] <= -velocity_threshold
    if not np.any(above_threshold):
        return None

    threshold_indices = np.nonzero(above_threshold)[0]
    for idx in threshold_indices:
        if idx + min_duration_frames < len(above_threshold):
            if np.all(above_threshold[idx : idx + min_duration_frames]):
                return search_start + idx
    return None


def detect_takeoff(
    positions: FloatArray,
    velocities: FloatArray,
    fps: float,
    velocity_threshold: float = 0.1,
    min_duration_frames: int = 5,
    search_window_s: float = 0.3,
) -> int | None:
    """Detect takeoff frame in squat jump.

    Takeoff occurs at peak upward velocity during the concentric phase.
    For SJ, this is simply the maximum negative velocity after squat hold
    before the upward movement.

    Args:
        positions: 1D array of vertical positions (normalized coordinates)
        velocities: 1D array of SIGNED vertical velocities (negative = upward)
        fps: Video frames per second
        velocity_threshold: Minimum velocity threshold for takeoff (m/s)
        min_duration_frames: Minimum frames above threshold to confirm takeoff
        search_window_s: Time window to search for takeoff after squat hold (seconds)

    Returns:
        Frame index where takeoff occurs, or None if not detected
    """
    if len(positions) == 0 or len(velocities) == 0:
        return None

    # Find squat start to determine where to begin search
    squat_start = detect_squat_start(positions, fps)
    if squat_start is None:
        # If no squat start detected, start from reasonable middle point
        squat_start = len(positions) // 3

    # Search for takeoff after squat start
    search_start = squat_start
    search_end = min(len(velocities), int(squat_start + search_window_s * fps))

    if search_end <= search_start:
        return None

    # Focus on concentric phase where velocity becomes negative (upward)
    concentric_velocities = velocities[search_start:search_end]

    # Find the most negative velocity (peak upward velocity = takeoff)
    takeoff_idx = int(np.argmin(concentric_velocities))
    takeoff_frame = search_start + takeoff_idx

    # Verify velocity exceeds threshold
    if velocities[takeoff_frame] > -velocity_threshold:
        # Velocity not high enough - actual takeoff may be later
        # Look for frames where velocity exceeds threshold with duration filter
        return _find_takeoff_threshold_crossing(
            velocities, search_start, search_end, velocity_threshold, min_duration_frames
        )

    return takeoff_frame if velocities[takeoff_frame] <= -velocity_threshold else None


def _detect_impact_landing(
    accelerations: FloatArray,
    search_start: int,
    search_end: int,
) -> int | None:
    """Detect landing by finding the maximum acceleration spike."""
    landing_accelerations = accelerations[search_start:search_end]
    if len(landing_accelerations) == 0:
        return None

    # Find maximum acceleration spike (impact)
    landing_idx = int(np.argmax(landing_accelerations))
    return search_start + landing_idx


def _refine_landing_by_velocity(
    velocities: FloatArray,
    landing_frame: int,
) -> int:
    """Refine landing frame by looking for positive (downward) velocity."""
    if landing_frame < len(velocities) and velocities[landing_frame] < 0:
        # Velocity still upward - landing might not be detected yet
        # Look ahead for where velocity becomes positive
        for i in range(landing_frame, min(landing_frame + 10, len(velocities))):
            if velocities[i] >= 0:
                return i
    return landing_frame


def detect_landing(
    positions: FloatArray,
    velocities: FloatArray,
    fps: float,
    velocity_threshold: float = 0.1,
    min_flight_frames: int = 5,
    landing_search_window_s: float = 0.5,
    window_length: int = 5,
    polyorder: int = 2,
) -> int | None:
    """Detect landing frame in squat jump.

    Landing occurs after peak height when feet contact the ground.
    Similar to CMJ - find position peak, then detect maximum deceleration
    which corresponds to impact.

    Args:
        positions: 1D array of vertical positions (normalized coordinates)
        velocities: 1D array of SIGNED vertical velocities (negative = up, positive = down)
        fps: Video frames per second
        velocity_threshold: Maximum velocity threshold for landing detection
        min_flight_frames: Minimum frames in flight before landing
        landing_search_window_s: Time window to search for landing after peak (seconds)
        window_length: Window size for velocity smoothing
        polyorder: Polynomial order for smoothing

    Returns:
        Frame index where landing occurs, or None if not detected
    """
    if len(positions) == 0 or len(velocities) == 0:
        return None

    # Find takeoff first (needed to determine where to start peak search)
    takeoff_frame = detect_takeoff(
        positions, velocities, fps, velocity_threshold, 5, landing_search_window_s
    )
    if takeoff_frame is None:
        return None

    # Find peak height after takeoff
    search_start = takeoff_frame
    search_duration = int(fps * 0.7)  # Search next 0.7 seconds for peak
    search_end = min(len(positions), search_start + search_duration)

    if search_end <= search_start:
        return None

    # Find peak height (minimum position value in normalized coords = highest point)
    flight_positions = positions[search_start:search_end]
    peak_frame = search_start + int(np.argmin(flight_positions))

    # After peak, look for landing using impact detection
    landing_search_start = peak_frame + min_flight_frames
    landing_search_end = min(
        len(positions),
        landing_search_start + int(landing_search_window_s * fps),
    )

    if landing_search_end <= landing_search_start:
        return None

    # Compute accelerations for impact detection
    if len(positions) >= 5:
        landing_window = window_length
        if landing_window % 2 == 0:
            landing_window += 1
        # Use polyorder for smoothing (must be at least 2 for deriv=2)
        eff_polyorder = max(2, polyorder)
        accelerations = np.abs(
            savgol_filter(
                positions, landing_window, eff_polyorder, deriv=2, delta=1.0, mode="interp"
            )
        )
    else:
        # Fallback for short sequences
        velocities_abs = np.abs(velocities)
        accelerations = np.abs(np.diff(velocities_abs, prepend=velocities_abs[0]))

    # Find impact: maximum positive acceleration (deceleration spike)
    landing_frame = _detect_impact_landing(accelerations, landing_search_start, landing_search_end)

    if landing_frame is None:
        return None

    # Additional verification: velocity should be positive (downward) at landing
    return _refine_landing_by_velocity(velocities, landing_frame)
