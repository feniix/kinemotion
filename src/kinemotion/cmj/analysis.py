"""Phase detection logic for Counter Movement Jump (CMJ) analysis."""

from enum import Enum

import numpy as np
from scipy.signal import savgol_filter

from ..core.experimental import unused
from ..core.smoothing import compute_acceleration_from_derivative
from ..core.timing import NULL_TIMER, Timer
from ..core.types import FloatArray


def compute_signed_velocity(
    positions: FloatArray, window_length: int = 5, polyorder: int = 2
) -> FloatArray:
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


@unused(
    reason="Alternative implementation not called by pipeline",
    since="0.34.0",
)
def find_standing_phase(
    positions: FloatArray,
    velocities: FloatArray,
    fps: float,
    min_standing_duration: float = 0.5,
    velocity_threshold: float = 0.01,
) -> int | None:
    """
    Find the end of standing phase (start of countermovement).

    Looks for a period of low velocity (standing) followed by consistent
    downward motion.

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


@unused(
    reason="Alternative implementation not called by pipeline",
    since="0.34.0",
)
def find_countermovement_start(
    velocities: FloatArray,
    countermovement_threshold: float = 0.015,
    min_eccentric_frames: int = 3,
    standing_start: int | None = None,
) -> int | None:
    """
    Find the start of countermovement (eccentric phase).

    Detects when velocity becomes consistently positive (downward motion in
    normalized coords).

    Args:
        velocities: Array of SIGNED vertical velocities
        countermovement_threshold: Velocity threshold for detecting downward
            motion (POSITIVE)
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
    positions: FloatArray,
    velocities: FloatArray,
    min_search_frame: int = 80,
) -> int:
    """
    Find the lowest point of countermovement (transition from eccentric to concentric).

    The lowest point occurs BEFORE the peak height (the jump apex). It's where
    velocity crosses from positive (downward/squatting) to negative (upward/jumping).

    Args:
        positions: Array of vertical positions (higher value = lower in video)
        velocities: Array of SIGNED vertical velocities (positive=down, negative=up)
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


def find_cmj_takeoff_from_velocity_peak(
    positions: FloatArray,
    velocities: FloatArray,
    lowest_point_frame: int,
    fps: float,
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

    Returns:
        Takeoff frame with fractional precision.
    """
    concentric_start = int(lowest_point_frame)
    search_duration = int(fps * 0.3)  # Search next 0.3 seconds (concentric to takeoff is brief)
    search_end = min(len(velocities), concentric_start + search_duration)

    if search_end <= concentric_start:
        return float(concentric_start + 1)

    # Find peak upward velocity (most NEGATIVE velocity)
    # In normalized coords: negative velocity = y decreasing = jumping up
    concentric_velocities = velocities[concentric_start:search_end]
    takeoff_idx = int(np.argmin(concentric_velocities))  # Most negative = fastest upward = takeoff
    takeoff_frame = concentric_start + takeoff_idx

    return float(takeoff_frame)


def find_cmj_landing_from_position_peak(
    positions: FloatArray,
    velocities: FloatArray,
    accelerations: FloatArray,
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


@unused(
    reason="Experimental alternative superseded by backward search algorithm",
    since="0.34.0",
)
def find_interpolated_takeoff_landing(
    positions: FloatArray,
    velocities: FloatArray,
    lowest_point_frame: int,
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
        positions, velocities, lowest_point_frame, fps
    )

    # Find landing using position peak and impact detection
    landing_frame = find_cmj_landing_from_position_peak(
        positions, velocities, accelerations, int(takeoff_frame), fps
    )

    return (takeoff_frame, landing_frame)


def find_takeoff_frame(velocities: FloatArray, peak_height_frame: int, fps: float) -> float:
    """Find takeoff frame as peak upward velocity before peak height.

    Robust detection: When velocities are nearly identical (flat), detects
    the transition point rather than using argmin which is unstable.
    """
    takeoff_search_start = max(0, peak_height_frame - int(fps * 0.35))
    takeoff_search_end = peak_height_frame - 2

    takeoff_velocities = velocities[takeoff_search_start:takeoff_search_end]

    if len(takeoff_velocities) == 0:
        return float(peak_height_frame - int(fps * 0.3))

    # Check if velocities are suspiciously identical (flat derivative = ambiguous)
    vel_min = np.min(takeoff_velocities)
    vel_max = np.max(takeoff_velocities)
    vel_range = vel_max - vel_min

    if vel_range < 1e-6:
        # Velocities are essentially identical - algorithm is ambiguous
        # Return the midpoint of the search window as a stable estimate
        return float((takeoff_search_start + takeoff_search_end) / 2.0)
    else:
        # Velocities have variation - use argmin as before
        peak_vel_idx = int(np.argmin(takeoff_velocities))
        return float(takeoff_search_start + peak_vel_idx)


def find_lowest_frame(
    velocities: FloatArray, positions: FloatArray, takeoff_frame: float, fps: float
) -> float:
    """Find lowest point frame before takeoff."""
    lowest_search_start = max(0, int(takeoff_frame) - int(fps * 0.4))
    lowest_search_end = int(takeoff_frame)

    # Find where velocity crosses from positive to negative
    for i in range(lowest_search_end - 1, lowest_search_start, -1):
        if i > 0 and velocities[i] < 0 and velocities[i - 1] >= 0:
            return float(i)

    # Fallback: use maximum position
    lowest_positions = positions[lowest_search_start:lowest_search_end]
    if len(lowest_positions) > 0:
        lowest_idx = int(np.argmax(lowest_positions))
        return float(lowest_search_start + lowest_idx)
    else:
        return float(int(takeoff_frame) - int(fps * 0.2))


def find_landing_frame(
    accelerations: FloatArray,
    velocities: FloatArray,
    peak_height_frame: int,
    fps: float,
) -> float:
    """Find landing frame after peak height.

    Robust detection strategy:
    1. Find peak downward velocity (maximum positive velocity) after peak height.
       This corresponds to the moment just before or at initial ground contact.
    2. Look for maximum deceleration (impact) *after* the peak velocity.
       This filters out mid-air tracking noise/flutter that can cause false
       deceleration spikes while the athlete is still accelerating downward.

    Args:
        accelerations: Vertical acceleration array (deriv=2)
        velocities: Vertical velocity array (deriv=1)
        peak_height_frame: Frame index of peak jump height
        fps: Video frame rate

    Returns:
        Frame index of landing impact.
    """
    # Search window extended to 1.0s to accommodate all realistic flight times
    search_end = min(len(accelerations), peak_height_frame + int(fps * 1.0))

    # 1. Find peak downward velocity (max positive value)
    # Search from peak height to end of window
    vel_search_window = velocities[peak_height_frame:search_end]

    if len(vel_search_window) == 0:
        return float(peak_height_frame + int(fps * 0.3))

    # Index relative to peak_height_frame
    peak_vel_rel_idx = int(np.argmax(vel_search_window))
    peak_vel_frame = peak_height_frame + peak_vel_rel_idx

    # 2. Search for impact (min acceleration) starting from peak velocity
    # We allow a small buffer (e.g., 1-2 frames) before peak velocity just in case
    # peak velocity coincides with impact start due to smoothing
    landing_search_start = max(peak_height_frame, peak_vel_frame - 2)
    landing_search_end = search_end

    landing_accelerations = accelerations[landing_search_start:landing_search_end]

    if len(landing_accelerations) == 0:
        # Fallback if window is empty
        return float(peak_height_frame + int(fps * 0.3))

    # Find minimum acceleration (maximum deceleration spike)
    landing_rel_idx = int(np.argmin(landing_accelerations))
    landing_frame = landing_search_start + landing_rel_idx

    return float(landing_frame)


def compute_average_hip_position(
    landmarks: dict[str, tuple[float, float, float]],
) -> tuple[float, float]:
    """
    Compute average hip position from hip landmarks.

    Args:
        landmarks: Dictionary of landmark positions

    Returns:
        (x, y) average hip position in normalized coordinates
    """
    hip_keys = ["left_hip", "right_hip"]

    x_positions: list[float] = []
    y_positions: list[float] = []

    for key in hip_keys:
        if key in landmarks:
            x, y, visibility = landmarks[key]
            if visibility > 0.5:  # Only use visible landmarks
                x_positions.append(x)
                y_positions.append(y)

    if not x_positions:
        return (0.5, 0.5)  # Default to center if no visible hips

    return (float(np.mean(x_positions)), float(np.mean(y_positions)))


def find_standing_end(
    velocities: FloatArray,
    lowest_point: float,
    _positions: FloatArray | None = None,
    accelerations: FloatArray | None = None,
) -> float | None:
    """
    Find end of standing phase before lowest point.

    Uses acceleration-based detection to identify when downward movement begins.
    Acceleration captures movement initiation even when velocity is negligible,
    making it ideal for detecting slow countermovement starts.

    Args:
        velocities: Signed velocity array (for backward compatibility)
        lowest_point: Frame index of lowest point
        _positions: Intentionally unused - kept for backward compatibility
        accelerations: Acceleration array (if provided, uses
            acceleration-based detection)

    Returns:
        Frame index where standing ends (countermovement begins), or None
    """
    if lowest_point <= 20:
        return None

    # Acceleration-based detection (best for detecting movement initiation)
    if accelerations is not None:
        # Use middle section of standing phase as baseline (avoids initial settling)
        baseline_start = 10
        baseline_end = min(40, int(lowest_point) - 10)

        if baseline_end <= baseline_start:
            return None

        # Calculate baseline acceleration statistics
        baseline_accel = accelerations[baseline_start:baseline_end]
        baseline_mean = float(np.mean(baseline_accel))
        baseline_std = float(np.std(baseline_accel))

        # Threshold: 3 standard deviations above baseline
        # This detects when acceleration significantly increases (movement starts)
        accel_threshold = baseline_mean + 3.0 * baseline_std

        # Search forward from baseline for acceleration spike
        for i in range(baseline_end, int(lowest_point)):
            if accelerations[i] > accel_threshold:
                # Found start of downward acceleration
                return float(i)

        return None

    # Fallback: velocity-based detection (legacy)
    standing_search = velocities[: int(lowest_point)]
    low_vel = np.abs(standing_search) < 0.005
    if np.any(low_vel):
        standing_frames = np.nonzero(low_vel)[0]
        if len(standing_frames) > 10:
            return float(standing_frames[-1])

    return None


def detect_cmj_phases(
    positions: FloatArray,
    fps: float,
    window_length: int = 5,
    polyorder: int = 2,
    landing_positions: FloatArray | None = None,
    timer: Timer | None = None,
) -> tuple[float | None, float, float, float] | None:
    """
    Detect all phases of a counter movement jump using a simplified, robust approach.

    Strategy: Work BACKWARD from peak height to find all phases.
    1. Find peak height (global minimum y)
    2. Find takeoff (peak negative velocity before peak height)
    3. Find lowest point (maximum y value before takeoff)
    4. Find landing (impact after peak height)

    Args:
        positions: Array of vertical positions (normalized 0-1). Typically Hips/CoM.
        fps: Video frame rate
        window_length: Window size for derivative calculations
        polyorder: Polynomial order for Savitzky-Golay filter
        landing_positions: Optional array of positions for landing detection
            (e.g., Feet). If None, uses `positions` (Hips) for landing too.
        timer: Optional Timer for measuring operations

    Returns:
        Tuple of (standing_end_frame, lowest_point_frame, takeoff_frame, landing_frame)
        with fractional precision, or None if phases cannot be detected.
    """
    timer = timer or NULL_TIMER

    # Compute SIGNED velocities and accelerations for primary signal (Hips)
    with timer.measure("cmj_compute_derivatives"):
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

    # Step 2-4: Find all phases using helper functions
    with timer.measure("cmj_find_takeoff"):
        takeoff_frame = find_takeoff_frame(velocities, peak_height_frame, fps)

    with timer.measure("cmj_find_lowest_point"):
        lowest_point = find_lowest_frame(velocities, positions, takeoff_frame, fps)

    # Determine landing frame
    with timer.measure("cmj_find_landing"):
        if landing_positions is not None:
            # Use specific landing signal (Feet) for landing detection
            landing_velocities = compute_signed_velocity(
                landing_positions, window_length=window_length, polyorder=polyorder
            )
            landing_accelerations = compute_acceleration_from_derivative(
                landing_positions, window_length=window_length, polyorder=polyorder
            )
            # We still reference peak_height_frame from Hips, as Feet peak
            # might be different/noisy but generally they align in time.
            landing_frame = find_landing_frame(
                landing_accelerations,
                landing_velocities,
                peak_height_frame,
                fps,
            )
        else:
            # Use primary signal (Hips)
            landing_frame = find_landing_frame(
                accelerations,
                velocities,
                peak_height_frame,
                fps,
            )

    with timer.measure("cmj_find_standing_end"):
        standing_end = find_standing_end(velocities, lowest_point, positions, accelerations)

    return (standing_end, lowest_point, takeoff_frame, landing_frame)
