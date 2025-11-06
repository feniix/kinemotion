"""Phase detection logic for Counter Movement Jump (CMJ) analysis."""

from enum import Enum

import numpy as np
from scipy.signal import savgol_filter

from ..core.smoothing import compute_acceleration_from_derivative


def compute_signed_velocity(
    positions: np.ndarray, window_length: int = 5, polyorder: int = 2
) -> np.ndarray:
    """
    Compute SIGNED velocity for CMJ phase detection.

    Unlike drop jump which uses absolute velocity, CMJ needs signed velocity to
    distinguish upward (negative) from downward (positive) motion.

    Args:
        positions: 1D array of y-positions in normalized coordinates
        window_length: Window size for Savitzky-Golay filter
        polyorder: Polynomial order

    Returns:
        Signed velocity array where:
        - Negative = upward motion (y decreasing, jumping up)
        - Positive = downward motion (y increasing, squatting/falling)
    """
    if len(positions) < window_length:
        return np.diff(positions, prepend=positions[0])

    if window_length % 2 == 0:
        window_length += 1

    velocity = savgol_filter(
        positions, window_length, polyorder, deriv=1, delta=1.0, mode="interp"
    )

    return velocity


class CMJPhase(Enum):
    """Phases of a counter movement jump."""

    STANDING = "standing"
    ECCENTRIC = "eccentric"  # Downward movement
    TRANSITION = "transition"  # At lowest point
    CONCENTRIC = "concentric"  # Upward movement
    FLIGHT = "flight"
    LANDING = "landing"
    UNKNOWN = "unknown"


def find_standing_phase(
    positions: np.ndarray,
    velocities: np.ndarray,
    fps: float,
    min_standing_duration: float = 0.5,
    velocity_threshold: float = 0.01,
) -> int | None:
    """
    Find the end of standing phase (start of countermovement).

    Looks for a period of low velocity (standing) followed by consistent downward motion.

    Args:
        positions: Array of vertical positions (normalized 0-1)
        velocities: Array of vertical velocities
        fps: Video frame rate
        min_standing_duration: Minimum standing duration in seconds (default: 0.5s)
        velocity_threshold: Velocity threshold for standing detection

    Returns:
        Frame index where countermovement begins, or None if not detected.
    """
    min_standing_frames = int(fps * min_standing_duration)

    if len(positions) < min_standing_frames:
        return None

    # Find periods of low velocity (standing)
    is_standing = np.abs(velocities) < velocity_threshold

    # Look for first sustained standing period
    standing_count = 0
    standing_end = None

    for i in range(len(is_standing)):
        if is_standing[i]:
            standing_count += 1
            if standing_count >= min_standing_frames:
                standing_end = i
        else:
            if standing_end is not None:
                # Found end of standing phase
                return standing_end
            standing_count = 0

    return None


def find_countermovement_start(
    velocities: np.ndarray,
    fps: float,
    countermovement_threshold: float = 0.015,
    min_eccentric_frames: int = 3,
    standing_start: int | None = None,
) -> int | None:
    """
    Find the start of countermovement (eccentric phase).

    Detects when velocity becomes consistently positive (downward motion in normalized coords).

    Args:
        velocities: Array of SIGNED vertical velocities
        fps: Video frame rate
        countermovement_threshold: Velocity threshold for detecting downward motion (POSITIVE)
        min_eccentric_frames: Minimum consecutive frames of downward motion
        standing_start: Optional frame where standing phase ended

    Returns:
        Frame index where countermovement begins, or None if not detected.
    """
    start_frame = standing_start if standing_start is not None else 0

    # Look for sustained downward velocity (POSITIVE in normalized coords)
    is_downward = velocities[start_frame:] > countermovement_threshold
    consecutive_count = 0

    for i in range(len(is_downward)):
        if is_downward[i]:
            consecutive_count += 1
            if consecutive_count >= min_eccentric_frames:
                # Found start of eccentric phase
                return start_frame + i - consecutive_count + 1
        else:
            consecutive_count = 0

    return None


def find_lowest_point(
    positions: np.ndarray,
    velocities: np.ndarray,
    eccentric_start: int | None = None,
    min_search_frame: int = 80,
) -> int:
    """
    Find the lowest point of countermovement (transition from eccentric to concentric).

    The lowest point occurs BEFORE the peak height (the jump apex). It's where
    velocity crosses from positive (downward/squatting) to negative (upward/jumping).

    Args:
        positions: Array of vertical positions (higher value = lower in video)
        velocities: Array of SIGNED vertical velocities (positive=down, negative=up)
        eccentric_start: Optional frame where eccentric phase started
        min_search_frame: Minimum frame to start searching (default: frame 80)

    Returns:
        Frame index of lowest point.
    """
    # First, find the peak height (minimum y value = highest jump point)
    peak_height_frame = int(np.argmin(positions))

    # Lowest point MUST be before peak height
    # Search from min_search_frame to peak_height_frame
    start_frame = min_search_frame
    end_frame = peak_height_frame

    if end_frame <= start_frame:
        start_frame = int(len(positions) * 0.3)
        end_frame = int(len(positions) * 0.7)

    search_positions = positions[start_frame:end_frame]

    if len(search_positions) == 0:
        return start_frame

    # Find maximum position value in this range (lowest point in video)
    lowest_idx = int(np.argmax(search_positions))
    lowest_frame = start_frame + lowest_idx

    return lowest_frame


def refine_transition_with_curvature(
    positions: np.ndarray,
    velocities: np.ndarray,
    initial_frame: int,
    transition_type: str,
    search_radius: int = 3,
    window_length: int = 5,
    polyorder: int = 2,
) -> float:
    """
    Refine transition frame using trajectory curvature (acceleration patterns).

    Uses acceleration (second derivative) to identify characteristic patterns:
    - Landing: Large acceleration spike (impact deceleration)
    - Takeoff: Acceleration change (transition from static to flight)

    Args:
        positions: Array of vertical positions
        velocities: Array of vertical velocities
        initial_frame: Initial estimate of transition frame
        transition_type: Type of transition ("takeoff" or "landing")
        search_radius: Frames to search around initial estimate (±radius)
        window_length: Window size for acceleration calculation
        polyorder: Polynomial order for Savitzky-Golay filter

    Returns:
        Refined fractional frame index.
    """
    # Compute acceleration using second derivative
    acceleration = compute_acceleration_from_derivative(
        positions, window_length=window_length, polyorder=polyorder
    )

    # Define search window
    search_start = max(0, initial_frame - search_radius)
    search_end = min(len(positions), initial_frame + search_radius + 1)

    if search_start >= search_end:
        return float(initial_frame)

    search_accel = acceleration[search_start:search_end]

    if transition_type == "landing":
        # Landing: Find maximum absolute acceleration (impact)
        peak_idx = int(np.argmax(np.abs(search_accel)))
    elif transition_type == "takeoff":
        # Takeoff: Find maximum acceleration change
        accel_change = np.abs(np.diff(search_accel))
        if len(accel_change) > 0:
            peak_idx = int(np.argmax(accel_change))
        else:
            peak_idx = 0
    else:
        return float(initial_frame)

    curvature_frame = search_start + peak_idx

    # Blend curvature-based estimate with velocity-based estimate
    # 70% curvature, 30% velocity
    blended_frame = 0.7 * curvature_frame + 0.3 * initial_frame

    return float(blended_frame)


def interpolate_threshold_crossing(
    vel_before: float,
    vel_after: float,
    velocity_threshold: float,
) -> float:
    """
    Find fractional offset where velocity crosses threshold between two frames.

    Uses linear interpolation assuming velocity changes linearly between frames.

    Args:
        vel_before: Velocity at frame boundary N (absolute value)
        vel_after: Velocity at frame boundary N+1 (absolute value)
        velocity_threshold: Threshold value

    Returns:
        Fractional offset from frame N (0.0 to 1.0)
    """
    # Handle edge cases
    if abs(vel_after - vel_before) < 1e-9:  # Velocity not changing
        return 0.5

    # Linear interpolation
    t = (velocity_threshold - vel_before) / (vel_after - vel_before)

    # Clamp to [0, 1] range
    return float(max(0.0, min(1.0, t)))


def find_cmj_takeoff_from_velocity_peak(
    positions: np.ndarray,
    velocities: np.ndarray,
    lowest_point_frame: int,
    fps: float,
    window_length: int = 5,
    polyorder: int = 2,
) -> float:
    """
    Find CMJ takeoff frame as peak upward velocity during concentric phase.

    Takeoff occurs at maximum push-off velocity (most negative velocity),
    just as feet leave the ground. This is BEFORE peak height is reached.

    Args:
        positions: Array of vertical positions
        velocities: Array of SIGNED vertical velocities (negative = upward)
        lowest_point_frame: Frame at lowest point
        fps: Video frame rate
        window_length: Window size for derivative calculations
        polyorder: Polynomial order for Savitzky-Golay filter

    Returns:
        Takeoff frame with fractional precision.
    """
    concentric_start = int(lowest_point_frame)
    search_duration = int(
        fps * 0.3
    )  # Search next 0.3 seconds (concentric to takeoff is brief)
    search_end = min(len(velocities), concentric_start + search_duration)

    if search_end <= concentric_start:
        return float(concentric_start + 1)

    # Find peak upward velocity (most NEGATIVE velocity)
    # In normalized coords: negative velocity = y decreasing = jumping up
    concentric_velocities = velocities[concentric_start:search_end]
    takeoff_idx = int(
        np.argmin(concentric_velocities)
    )  # Most negative = fastest upward = takeoff
    takeoff_frame = concentric_start + takeoff_idx

    return float(takeoff_frame)


def find_cmj_landing_from_position_peak(
    positions: np.ndarray,
    velocities: np.ndarray,
    accelerations: np.ndarray,
    takeoff_frame: int,
    fps: float,
) -> float:
    """
    Find CMJ landing frame by detecting impact after peak height.

    Landing occurs when feet contact ground after peak height, detected by
    finding where velocity transitions from negative (still going up/at peak)
    to positive (falling) and position stabilizes.

    Args:
        positions: Array of vertical positions
        velocities: Array of SIGNED vertical velocities (negative = up, positive = down)
        accelerations: Array of accelerations (second derivative)
        takeoff_frame: Frame at takeoff
        fps: Video frame rate

    Returns:
        Landing frame with fractional precision.
    """
    # Find peak height (minimum position value in normalized coords)
    search_start = int(takeoff_frame)
    search_duration = int(fps * 0.7)  # Search next 0.7 seconds for peak
    search_end = min(len(positions), search_start + search_duration)

    if search_end <= search_start:
        return float(search_start + int(fps * 0.3))

    # Find peak height (minimum y value = highest point in frame)
    flight_positions = positions[search_start:search_end]
    peak_idx = int(np.argmin(flight_positions))
    peak_frame = search_start + peak_idx

    # After peak, look for landing (impact with ground)
    # Landing is detected by maximum positive acceleration (deceleration on impact)
    landing_search_start = peak_frame + 2
    landing_search_end = min(len(accelerations), landing_search_start + int(fps * 0.5))

    if landing_search_end <= landing_search_start:
        return float(peak_frame + int(fps * 0.2))

    # Find impact: maximum positive acceleration after peak
    # Positive acceleration = slowing down upward motion or impact deceleration
    landing_accelerations = accelerations[landing_search_start:landing_search_end]
    impact_idx = int(np.argmax(landing_accelerations))  # Max positive = impact
    landing_frame = landing_search_start + impact_idx

    return float(landing_frame)


def find_interpolated_takeoff_landing(
    positions: np.ndarray,
    velocities: np.ndarray,
    lowest_point_frame: int,
    velocity_threshold: float = 0.02,
    min_flight_frames: int = 3,
    use_curvature: bool = True,
    window_length: int = 5,
    polyorder: int = 2,
) -> tuple[float, float] | None:
    """
    Find takeoff and landing frames for CMJ using physics-based detection.

    CMJ-specific: Takeoff is detected as peak velocity (end of push-off),
    not as high velocity threshold (which detects mid-flight).

    Args:
        positions: Array of vertical positions
        velocities: Array of vertical velocities
        lowest_point_frame: Frame at lowest point
        velocity_threshold: Velocity threshold (unused for CMJ, kept for API compatibility)
        min_flight_frames: Minimum consecutive frames for valid flight phase
        use_curvature: Whether to use trajectory curvature refinement
        window_length: Window size for derivative calculations
        polyorder: Polynomial order for Savitzky-Golay filter

    Returns:
        Tuple of (takeoff_frame, landing_frame) with fractional precision, or None.
    """
    # Get FPS from velocity array length and assumed duration
    # This is approximate but sufficient for search windows
    fps = 30.0  # Default assumption

    # Compute accelerations for landing detection
    accelerations = compute_acceleration_from_derivative(
        positions, window_length=window_length, polyorder=polyorder
    )

    # Find takeoff using peak velocity method (CMJ-specific)
    takeoff_frame = find_cmj_takeoff_from_velocity_peak(
        positions, velocities, lowest_point_frame, fps, window_length, polyorder
    )

    # Find landing using position peak and impact detection
    landing_frame = find_cmj_landing_from_position_peak(
        positions, velocities, accelerations, int(takeoff_frame), fps
    )

    return (takeoff_frame, landing_frame)


def detect_cmj_phases(
    positions: np.ndarray,
    fps: float,
    velocity_threshold: float = 0.02,
    countermovement_threshold: float = -0.015,
    min_contact_frames: int = 3,
    min_eccentric_frames: int = 3,
    use_curvature: bool = True,
    window_length: int = 5,
    polyorder: int = 2,
) -> tuple[float | None, float, float, float] | None:
    """
    Detect all phases of a counter movement jump using a simplified, robust approach.

    Strategy: Work BACKWARD from peak height to find all phases.
    1. Find peak height (global minimum y)
    2. Find takeoff (peak negative velocity before peak height)
    3. Find lowest point (maximum y value before takeoff)
    4. Find landing (impact after peak height)

    Args:
        positions: Array of vertical positions (normalized 0-1)
        fps: Video frame rate
        velocity_threshold: Velocity threshold (not used)
        countermovement_threshold: Velocity threshold (not used)
        min_contact_frames: Minimum frames for ground contact
        min_eccentric_frames: Minimum frames for eccentric phase
        use_curvature: Whether to use trajectory curvature refinement
        window_length: Window size for derivative calculations
        polyorder: Polynomial order for Savitzky-Golay filter

    Returns:
        Tuple of (standing_end_frame, lowest_point_frame, takeoff_frame, landing_frame)
        with fractional precision, or None if phases cannot be detected.
    """
    # Compute SIGNED velocities and accelerations
    velocities = compute_signed_velocity(
        positions, window_length=window_length, polyorder=polyorder
    )
    accelerations = compute_acceleration_from_derivative(
        positions, window_length=window_length, polyorder=polyorder
    )

    # Step 1: Find peak height (global minimum y = highest point in frame)
    peak_height_frame = int(np.argmin(positions))

    if peak_height_frame < 10:
        return None  # Peak too early, invalid

    # Step 2: Find takeoff as peak upward velocity
    # Takeoff occurs at maximum upward velocity (most negative) before peak height
    # Typical: 0.3 seconds before peak (9 frames at 30fps)
    takeoff_search_start = max(0, peak_height_frame - int(fps * 0.35))
    takeoff_search_end = peak_height_frame - 2  # Must be at least 2 frames before peak

    takeoff_velocities = velocities[takeoff_search_start:takeoff_search_end]

    if len(takeoff_velocities) > 0:
        # Takeoff = peak upward velocity (most negative)
        peak_vel_idx = int(np.argmin(takeoff_velocities))
        takeoff_frame = float(takeoff_search_start + peak_vel_idx)
    else:
        # Fallback
        takeoff_frame = float(peak_height_frame - int(fps * 0.3))

    # Step 3: Find lowest point (countermovement bottom) before takeoff
    # This is where velocity crosses from positive (squatting) to negative (jumping)
    # Search backward from takeoff for where velocity was last positive/zero
    lowest_search_start = max(0, int(takeoff_frame) - int(fps * 0.4))
    lowest_search_end = int(takeoff_frame)

    # Find where velocity crosses from positive to negative (transition point)
    lowest_frame_found = None
    for i in range(lowest_search_end - 1, lowest_search_start, -1):
        if i > 0:
            # Look for velocity crossing from positive/zero to negative
            if velocities[i] < 0 and velocities[i - 1] >= 0:
                lowest_frame_found = float(i)
                break

    # Fallback: use maximum position (lowest point in frame) if no velocity crossing
    if lowest_frame_found is None:
        lowest_positions = positions[lowest_search_start:lowest_search_end]
        if len(lowest_positions) > 0:
            lowest_idx = int(np.argmax(lowest_positions))
            lowest_point = float(lowest_search_start + lowest_idx)
        else:
            lowest_point = float(int(takeoff_frame) - int(fps * 0.2))
    else:
        lowest_point = lowest_frame_found

    # Step 4: Find landing (impact after peak height)
    # Landing shows as large negative acceleration spike (impact deceleration)
    landing_search_start = peak_height_frame
    landing_search_end = min(len(accelerations), peak_height_frame + int(fps * 0.5))
    landing_accelerations = accelerations[landing_search_start:landing_search_end]

    if len(landing_accelerations) > 0:
        # Find most negative acceleration (maximum impact deceleration)
        # Landing acceleration should be around -0.008 to -0.010
        landing_idx = int(np.argmin(landing_accelerations))  # Most negative = impact
        landing_frame = float(landing_search_start + landing_idx)
    else:
        landing_frame = float(peak_height_frame + int(fps * 0.3))

    # Optional: Find standing phase (not critical)
    standing_end = None
    if lowest_point > 20:
        # Look for low-velocity period before lowest point
        standing_search = velocities[: int(lowest_point)]
        low_vel = np.abs(standing_search) < 0.005
        if np.any(low_vel):
            # Find last low-velocity frame before countermovement
            standing_frames = np.where(low_vel)[0]
            if len(standing_frames) > 10:
                standing_end = float(standing_frames[-1])

    return (standing_end, lowest_point, takeoff_frame, landing_frame)
