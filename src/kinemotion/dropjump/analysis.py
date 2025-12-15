"""Ground contact detection logic for drop-jump analysis."""

from enum import Enum

import numpy as np

from ..core.experimental import unused
from ..core.smoothing import (
    compute_acceleration_from_derivative,
    compute_velocity_from_derivative,
    interpolate_threshold_crossing,
)
from ..core.timing import NULL_TIMER, Timer
from ..core.types import BoolArray, FloatArray


class ContactState(Enum):
    """States for foot-ground contact."""

    IN_AIR = "in_air"
    ON_GROUND = "on_ground"
    UNKNOWN = "unknown"


@unused(
    reason="Not called by analysis pipeline - awaiting CLI integration",
    remove_in="1.0.0",
    since="0.34.0",
)
def calculate_adaptive_threshold(
    positions: FloatArray,
    fps: float,
    baseline_duration: float = 3.0,
    multiplier: float = 1.5,
    smoothing_window: int = 5,
    polyorder: int = 2,
) -> float:
    """
    Calculate adaptive velocity threshold based on baseline motion characteristics.

    .. warning::
        **Status: Implemented but Not Integrated**

        This function is fully implemented and tested but not called by the
        analysis pipeline. See ``docs/development/errors-findings.md`` for details.

        **To integrate**: Add CLI parameter ``--use-adaptive-threshold`` and
        call this function before contact detection.

        **Roadmap**: Planned for Phase 2 if users report issues with varying
        video conditions.

    Analyzes the first few seconds of video (assumed to be relatively stationary,
    e.g., athlete standing on box) to determine the noise floor, then sets threshold
    as a multiple of this baseline noise.

    This adapts to:
    - Different camera distances (closer = more pixel movement)
    - Different lighting conditions (affects tracking quality)
    - Different frame rates (higher fps = smoother motion)
    - Video compression artifacts

    Args:
        positions: Array of vertical positions (0-1 normalized)
        fps: Video frame rate
        baseline_duration: Duration in seconds to analyze for baseline (default: 3.0s)
        multiplier: Factor above baseline noise to set threshold (default: 1.5x)
        smoothing_window: Window size for velocity computation
        polyorder: Polynomial order for Savitzky-Golay filter (default: 2)

    Returns:
        Adaptive velocity threshold value

    Example:
        At 30fps with 3s baseline:
        - Analyzes first 90 frames
        - Computes velocity for this "stationary" period
        - 95th percentile velocity = 0.012 (noise level)
        - Threshold = 0.012 × 1.5 = 0.018
    """
    if len(positions) < 2:
        return 0.02  # Fallback to default

    # Calculate number of frames for baseline analysis
    baseline_frames = int(fps * baseline_duration)
    baseline_frames = min(baseline_frames, len(positions))

    if baseline_frames < smoothing_window:
        return 0.02  # Not enough data, use default

    # Extract baseline period (assumed relatively stationary)
    baseline_positions = positions[:baseline_frames]

    # Compute velocity for baseline period using derivative
    baseline_velocities = compute_velocity_from_derivative(
        baseline_positions, window_length=smoothing_window, polyorder=polyorder
    )

    # Calculate noise floor as 95th percentile of baseline velocities
    # Using 95th percentile instead of max to be robust against outliers
    noise_floor = float(np.percentile(np.abs(baseline_velocities), 95))

    # Set threshold as multiplier of noise floor
    # Minimum threshold to avoid being too sensitive
    adaptive_threshold = max(noise_floor * multiplier, 0.005)

    # Maximum threshold to ensure we still detect contact
    adaptive_threshold = min(adaptive_threshold, 0.05)

    return adaptive_threshold


def _find_stable_baseline(
    positions: FloatArray,
    min_stable_frames: int,
    stability_threshold: float = 0.01,
    debug: bool = False,
) -> tuple[int, float]:
    """Find first stable period and return baseline position.

    Returns:
        Tuple of (baseline_start_frame, baseline_position). Returns (-1, 0.0)
        if not found.
    """
    stable_window = min_stable_frames

    for start_idx in range(0, len(positions) - stable_window, 5):
        window = positions[start_idx : start_idx + stable_window]
        window_std = float(np.std(window))

        if window_std < stability_threshold:
            baseline_start = start_idx
            baseline_position = float(np.median(window))

            if debug:
                end_frame = baseline_start + stable_window - 1
                print("[detect_drop_start] Found stable period:")
                print(f"  frames {baseline_start}-{end_frame}")
                print(f"  baseline_position: {baseline_position:.4f}")
                print(f"  baseline_std: {window_std:.4f} < {stability_threshold:.4f}")

            return baseline_start, baseline_position

    if debug:
        print(
            f"[detect_drop_start] No stable period found "
            f"(variance always > {stability_threshold:.4f})"
        )
    return -1, 0.0


def _find_drop_from_baseline(
    positions: FloatArray,
    baseline_start: int,
    baseline_position: float,
    stable_window: int,
    position_change_threshold: float,
    smoothing_window: int,
    debug: bool = False,
) -> int:
    """Find drop start after stable baseline period.

    Returns:
        Drop frame index, or 0 if not found.
    """
    search_start = baseline_start + stable_window
    window_size = max(3, smoothing_window)

    for i in range(search_start, len(positions) - window_size):
        window_positions = positions[i : i + window_size]
        avg_position = float(np.mean(window_positions))
        position_change = avg_position - baseline_position

        if position_change > position_change_threshold:
            drop_frame = max(baseline_start, i - window_size)

            if debug:
                print(f"[detect_drop_start] Drop detected at frame {drop_frame}")
                print(
                    f"  position_change: {position_change:.4f} > {position_change_threshold:.4f}"
                )
                print(f"  avg_position: {avg_position:.4f} vs baseline: {baseline_position:.4f}")

            return drop_frame

    if debug:
        print("[detect_drop_start] No drop detected after stable period")
    return 0


def detect_drop_start(
    positions: FloatArray,
    fps: float,
    min_stationary_duration: float = 1.0,
    position_change_threshold: float = 0.02,
    smoothing_window: int = 5,
    debug: bool = False,
) -> int:
    """
    Detect when the drop jump actually starts by finding stable period then
    detecting drop.

    Strategy:
    1. Scan forward to find first STABLE period (low variance over N frames)
    2. Use that stable period as baseline
    3. Detect when position starts changing significantly from baseline

    This handles videos where athlete steps onto box at start (unstable beginning).

    Args:
        positions: Array of vertical positions (0-1 normalized, y increases downward)
        fps: Video frame rate
        min_stationary_duration: Minimum duration (seconds) of stable period
            (default: 1.0s)
        position_change_threshold: Position change indicating start of drop
            (default: 0.02 = 2% of frame)
        smoothing_window: Window for computing position variance
        debug: Print debug information (default: False)

    Returns:
        Frame index where drop starts (or 0 if no clear stable period found)

    Example:
        - Frames 0-14: Stepping onto box (noisy, unstable)
        - Frames 15-119: Standing on box (stable, low variance)
        - Frame 119: Drop begins (position changes significantly)
        - Returns: 119
    """
    min_stable_frames = int(fps * min_stationary_duration)
    if len(positions) < min_stable_frames + 30:
        if debug:
            print(
                f"[detect_drop_start] Video too short: {len(positions)} < {min_stable_frames + 30}"
            )
        return 0

    # Find stable baseline period
    baseline_start, baseline_position = _find_stable_baseline(
        positions, min_stable_frames, debug=debug
    )

    if baseline_start < 0:
        return 0

    # Find drop from baseline
    return _find_drop_from_baseline(
        positions,
        baseline_start,
        baseline_position,
        min_stable_frames,
        position_change_threshold,
        smoothing_window,
        debug,
    )


def _filter_stationary_with_visibility(
    is_stationary: BoolArray,
    visibilities: FloatArray | None,
    visibility_threshold: float,
) -> BoolArray:
    """Apply visibility filter to stationary flags.

    Args:
        is_stationary: Boolean array indicating stationary frames
        visibilities: Optional visibility scores for each frame
        visibility_threshold: Minimum visibility to trust landmark

    Returns:
        Filtered is_stationary array
    """
    if visibilities is not None:
        is_visible = visibilities > visibility_threshold
        return is_stationary & is_visible
    return is_stationary


def _find_contact_frames(
    is_stationary: BoolArray,
    min_contact_frames: int,
) -> set[int]:
    """Find frames with sustained contact using minimum duration filter.

    Args:
        is_stationary: Boolean array indicating stationary frames
        min_contact_frames: Minimum consecutive frames to confirm contact

    Returns:
        Set of frame indices that meet minimum contact duration
    """
    contact_frames: set[int] = set()
    current_run = []

    for i, stationary in enumerate(is_stationary):
        if stationary:
            current_run.append(i)
        else:
            if len(current_run) >= min_contact_frames:
                contact_frames.update(current_run)
            current_run = []

    # Handle last run
    if len(current_run) >= min_contact_frames:
        contact_frames.update(current_run)

    return contact_frames


def _assign_contact_states(
    n_frames: int,
    contact_frames: set[int],
    visibilities: FloatArray | None,
    visibility_threshold: float,
) -> list[ContactState]:
    """Assign contact states based on contact frames and visibility.

    Args:
        n_frames: Total number of frames
        contact_frames: Set of frames with confirmed contact
        visibilities: Optional visibility scores for each frame
        visibility_threshold: Minimum visibility to trust landmark

    Returns:
        List of ContactState for each frame
    """
    states = []
    for i in range(n_frames):
        if visibilities is not None and visibilities[i] < visibility_threshold:
            states.append(ContactState.UNKNOWN)
        elif i in contact_frames:
            states.append(ContactState.ON_GROUND)
        else:
            states.append(ContactState.IN_AIR)
    return states


def detect_ground_contact(
    foot_positions: FloatArray,
    velocity_threshold: float = 0.02,
    min_contact_frames: int = 3,
    visibility_threshold: float = 0.5,
    visibilities: FloatArray | None = None,
    window_length: int = 5,
    polyorder: int = 2,
    timer: Timer | None = None,
) -> list[ContactState]:
    """
    Detect when feet are in contact with ground based on vertical motion.

    Uses derivative-based velocity calculation via Savitzky-Goyal filter for smooth,
    accurate velocity estimates. This is consistent with the velocity calculation used
    throughout the pipeline for sub-frame interpolation and curvature analysis.

    Args:
        foot_positions: Array of foot y-positions (normalized, 0-1, where 1 is bottom)
        velocity_threshold: Threshold for vertical velocity to consider stationary
        min_contact_frames: Minimum consecutive frames to confirm contact
        visibility_threshold: Minimum visibility score to trust landmark
        visibilities: Array of visibility scores for each frame
        window_length: Window size for velocity derivative calculation (must be odd)
        polyorder: Polynomial order for Savitzky-Golay filter (default: 2)
        timer: Optional Timer for measuring operations

    Returns:
        List of ContactState for each frame
    """
    timer = timer or NULL_TIMER
    n_frames = len(foot_positions)

    if n_frames < 2:
        return [ContactState.UNKNOWN] * n_frames

    # Compute vertical velocity using derivative-based method
    with timer.measure("dj_compute_velocity"):
        velocities = compute_velocity_from_derivative(
            foot_positions, window_length=window_length, polyorder=polyorder
        )

    # Detect stationary frames based on velocity threshold
    is_stationary = np.abs(velocities) < velocity_threshold

    # Apply visibility filter
    is_stationary = _filter_stationary_with_visibility(
        is_stationary, visibilities, visibility_threshold
    )

    # Find frames with sustained contact
    with timer.measure("dj_find_contact_frames"):
        contact_frames = _find_contact_frames(is_stationary, min_contact_frames)

    # Assign states
    return _assign_contact_states(n_frames, contact_frames, visibilities, visibility_threshold)


def find_contact_phases(
    contact_states: list[ContactState],
) -> list[tuple[int, int, ContactState]]:
    """
    Identify continuous phases of contact/flight.

    Args:
        contact_states: List of ContactState for each frame

    Returns:
        List of (start_frame, end_frame, state) tuples for each phase
    """
    phases: list[tuple[int, int, ContactState]] = []
    if not contact_states:
        return phases

    current_state = contact_states[0]
    phase_start = 0

    for i in range(1, len(contact_states)):
        if contact_states[i] != current_state:
            # Phase transition
            phases.append((phase_start, i - 1, current_state))
            current_state = contact_states[i]
            phase_start = i

    # Don't forget the last phase
    phases.append((phase_start, len(contact_states) - 1, current_state))

    return phases


def _interpolate_phase_start(
    start_idx: int,
    state: ContactState,
    velocities: FloatArray,
    velocity_threshold: float,
) -> float:
    """Interpolate start boundary of a phase with sub-frame precision.

    Returns:
        Fractional start frame, or float(start_idx) if no interpolation.
    """
    if start_idx <= 0 or start_idx >= len(velocities):
        return float(start_idx)

    vel_before = velocities[start_idx - 1]
    vel_at = velocities[start_idx]

    # Check threshold crossing based on state
    is_landing = state == ContactState.ON_GROUND and vel_before > velocity_threshold > vel_at
    is_takeoff = state == ContactState.IN_AIR and vel_before < velocity_threshold < vel_at

    if is_landing or is_takeoff:
        offset = interpolate_threshold_crossing(vel_before, vel_at, velocity_threshold)
        return (start_idx - 1) + offset

    return float(start_idx)


def _interpolate_phase_end(
    end_idx: int,
    state: ContactState,
    velocities: FloatArray,
    velocity_threshold: float,
    max_idx: int,
) -> float:
    """Interpolate end boundary of a phase with sub-frame precision.

    Returns:
        Fractional end frame, or float(end_idx) if no interpolation.
    """
    if end_idx >= max_idx - 1 or end_idx + 1 >= len(velocities):
        return float(end_idx)

    vel_at = velocities[end_idx]
    vel_after = velocities[end_idx + 1]

    # Check threshold crossing based on state
    is_takeoff = state == ContactState.ON_GROUND and vel_at < velocity_threshold < vel_after
    is_landing = state == ContactState.IN_AIR and vel_at > velocity_threshold > vel_after

    if is_takeoff or is_landing:
        offset = interpolate_threshold_crossing(vel_at, vel_after, velocity_threshold)
        return end_idx + offset

    return float(end_idx)


def find_interpolated_phase_transitions(
    foot_positions: FloatArray,
    contact_states: list[ContactState],
    velocity_threshold: float,
    smoothing_window: int = 5,
) -> list[tuple[float, float, ContactState]]:
    """
    Find contact phases with sub-frame interpolation for precise timing.

    Uses derivative-based velocity from smoothed trajectory for interpolation.
    This provides much smoother velocity estimates than frame-to-frame differences,
    leading to more accurate threshold crossing detection.

    Args:
        foot_positions: Array of foot y-positions (normalized, 0-1)
        contact_states: List of ContactState for each frame
        velocity_threshold: Threshold used for contact detection
        smoothing_window: Window size for velocity smoothing (must be odd)

    Returns:
        List of (start_frame, end_frame, state) tuples with fractional frame indices
    """
    phases = find_contact_phases(contact_states)
    if not phases or len(foot_positions) < 2:
        return []

    velocities = compute_velocity_from_derivative(
        foot_positions, window_length=smoothing_window, polyorder=2
    )

    interpolated_phases: list[tuple[float, float, ContactState]] = []

    for start_idx, end_idx, state in phases:
        start_frac = _interpolate_phase_start(start_idx, state, velocities, velocity_threshold)
        end_frac = _interpolate_phase_end(
            end_idx, state, velocities, velocity_threshold, len(foot_positions)
        )
        interpolated_phases.append((start_frac, end_frac, state))

    return interpolated_phases


def refine_transition_with_curvature(
    foot_positions: FloatArray,
    estimated_frame: float,
    transition_type: str,
    search_window: int = 3,
    smoothing_window: int = 5,
    polyorder: int = 2,
) -> float:
    """
    Refine phase transition timing using trajectory curvature analysis.

    Looks for characteristic acceleration patterns near estimated transition:
    - Landing: Large acceleration spike (rapid deceleration on impact)
    - Takeoff: Acceleration change (transition from static to upward motion)

    Args:
        foot_positions: Array of foot y-positions (normalized, 0-1)
        estimated_frame: Initial estimate of transition frame (from velocity)
        transition_type: Type of transition ("landing" or "takeoff")
        search_window: Number of frames to search around estimate
        smoothing_window: Window size for acceleration computation
        polyorder: Polynomial order for Savitzky-Golay filter (default: 2)

    Returns:
        Refined fractional frame index
    """
    if len(foot_positions) < smoothing_window:
        return estimated_frame

    # Compute acceleration (second derivative)
    acceleration = compute_acceleration_from_derivative(
        foot_positions, window_length=smoothing_window, polyorder=polyorder
    )

    # Define search range around estimated transition
    est_int = int(estimated_frame)
    search_start = max(0, est_int - search_window)
    search_end = min(len(acceleration), est_int + search_window + 1)

    if search_end <= search_start:
        return estimated_frame

    # Extract acceleration in search window
    accel_window = acceleration[search_start:search_end]

    if len(accel_window) == 0:
        return estimated_frame

    if transition_type == "landing":
        # Landing: Look for large magnitude acceleration (impact deceleration)
        # Find frame with maximum absolute acceleration
        peak_idx = np.argmax(np.abs(accel_window))
        refined_frame = float(search_start + peak_idx)

    elif transition_type == "takeoff":
        # Takeoff: Look for acceleration magnitude change
        # Find frame with large acceleration change (derivative of acceleration)
        if len(accel_window) < 2:
            return estimated_frame

        accel_diff = np.abs(np.diff(accel_window))
        peak_idx = np.argmax(accel_diff)
        refined_frame = float(search_start + peak_idx)

    else:
        return estimated_frame

    # Blend with original estimate (don't stray too far)
    # 70% curvature-based, 30% velocity-based
    blend_factor = 0.7
    refined_frame = blend_factor * refined_frame + (1 - blend_factor) * estimated_frame

    return refined_frame


def find_interpolated_phase_transitions_with_curvature(
    foot_positions: FloatArray,
    contact_states: list[ContactState],
    velocity_threshold: float,
    smoothing_window: int = 5,
    polyorder: int = 2,
    use_curvature: bool = True,
) -> list[tuple[float, float, ContactState]]:
    """
    Find contact phases with sub-frame interpolation and curvature refinement.

    Combines three methods for maximum accuracy:
    1. Velocity thresholding (coarse integer frame detection)
    2. Velocity interpolation (sub-frame precision)
    3. Curvature analysis (refinement based on acceleration patterns)

    Args:
        foot_positions: Array of foot y-positions (normalized, 0-1)
        contact_states: List of ContactState for each frame
        velocity_threshold: Threshold used for contact detection
        smoothing_window: Window size for velocity/acceleration smoothing
        polyorder: Polynomial order for Savitzky-Golay filter (default: 2)
        use_curvature: Whether to apply curvature-based refinement

    Returns:
        List of (start_frame, end_frame, state) tuples with fractional frame indices
    """
    # Get interpolated phases using velocity
    interpolated_phases = find_interpolated_phase_transitions(
        foot_positions, contact_states, velocity_threshold, smoothing_window
    )

    if not use_curvature or len(interpolated_phases) == 0:
        return interpolated_phases

    # Refine phase boundaries using curvature analysis
    refined_phases: list[tuple[float, float, ContactState]] = []

    for start_frac, end_frac, state in interpolated_phases:
        refined_start = start_frac
        refined_end = end_frac

        if state == ContactState.ON_GROUND:
            # Refine landing (start of ground contact)
            refined_start = refine_transition_with_curvature(
                foot_positions,
                start_frac,
                "landing",
                search_window=3,
                smoothing_window=smoothing_window,
                polyorder=polyorder,
            )
            # Refine takeoff (end of ground contact)
            refined_end = refine_transition_with_curvature(
                foot_positions,
                end_frac,
                "takeoff",
                search_window=3,
                smoothing_window=smoothing_window,
                polyorder=polyorder,
            )

        elif state == ContactState.IN_AIR:
            # For flight phases, takeoff is at start, landing is at end
            refined_start = refine_transition_with_curvature(
                foot_positions,
                start_frac,
                "takeoff",
                search_window=3,
                smoothing_window=smoothing_window,
                polyorder=polyorder,
            )
            refined_end = refine_transition_with_curvature(
                foot_positions,
                end_frac,
                "landing",
                search_window=3,
                smoothing_window=smoothing_window,
                polyorder=polyorder,
            )

        refined_phases.append((refined_start, refined_end, state))

    return refined_phases


def find_landing_from_acceleration(
    positions: FloatArray,
    accelerations: FloatArray,
    takeoff_frame: int,
    fps: float,
    search_duration: float = 0.7,
) -> int:
    """
    Find landing frame by detecting impact acceleration after takeoff.

    Detects the moment of initial ground contact, characterized by a sharp
    deceleration (positive acceleration spike) as downward velocity is arrested.

    Args:
        positions: Array of vertical positions (normalized 0-1)
        accelerations: Array of accelerations (second derivative)
        takeoff_frame: Frame at takeoff (end of ground contact)
        fps: Video frame rate
        search_duration: Duration in seconds to search for landing (default: 0.7s)

    Returns:
        Landing frame index (integer)
    """
    # Find peak height (minimum y value = highest point)
    search_start = takeoff_frame
    search_end = min(len(positions), takeoff_frame + int(fps * search_duration))

    if search_end <= search_start:
        return min(len(positions) - 1, takeoff_frame + int(fps * 0.3))

    flight_positions = positions[search_start:search_end]
    peak_idx = int(np.argmin(flight_positions))
    peak_frame = search_start + peak_idx

    # After peak, look for landing (impact with ground)
    # Landing is detected by maximum positive acceleration (deceleration on impact)
    landing_search_start = peak_frame + 2
    landing_search_end = min(len(accelerations), landing_search_start + int(fps * 0.6))

    if landing_search_end <= landing_search_start:
        return min(len(positions) - 1, peak_frame + int(fps * 0.2))

    # Find impact: maximum negative acceleration after peak (deceleration on impact)
    # The impact creates a large upward force (negative acceleration in Y-down)
    landing_accelerations = accelerations[landing_search_start:landing_search_end]
    impact_idx = int(np.argmin(landing_accelerations))
    landing_frame = landing_search_start + impact_idx

    return landing_frame


def compute_average_foot_position(
    landmarks: dict[str, tuple[float, float, float]],
) -> tuple[float, float]:
    """
    Compute average foot position from ankle and foot landmarks.

    Args:
        landmarks: Dictionary of landmark positions

    Returns:
        (x, y) average foot position in normalized coordinates
    """
    foot_keys = [
        "left_ankle",
        "right_ankle",
        "left_heel",
        "right_heel",
        "left_foot_index",
        "right_foot_index",
    ]

    x_positions = []
    y_positions = []

    for key in foot_keys:
        if key in landmarks:
            x, y, visibility = landmarks[key]
            if visibility > 0.5:  # Only use visible landmarks
                x_positions.append(x)
                y_positions.append(y)

    if not x_positions:
        return (0.5, 0.5)  # Default to center if no visible feet

    return (float(np.mean(x_positions)), float(np.mean(y_positions)))


def _calculate_average_visibility(
    frame_landmarks: dict[str, tuple[float, float, float]],
) -> float:
    """Calculate average visibility of foot landmarks in a frame.

    Args:
        frame_landmarks: Landmark dictionary for a single frame

    Returns:
        Average visibility of foot landmarks (0.0 if none visible)
    """
    foot_keys = ["left_ankle", "right_ankle", "left_heel", "right_heel"]
    foot_vis = [frame_landmarks[key][2] for key in foot_keys if key in frame_landmarks]
    return float(np.mean(foot_vis)) if foot_vis else 0.0


@unused(
    reason="Alternative implementation not called by pipeline",
    since="0.34.0",
)
def extract_foot_positions_and_visibilities(
    smoothed_landmarks: list[dict[str, tuple[float, float, float]] | None],
) -> tuple[np.ndarray, np.ndarray]:
    """
    Extract vertical positions and average visibilities from smoothed
    landmarks.

    This utility function eliminates code duplication between CLI and
    programmatic usage.

    Args:
        smoothed_landmarks: Smoothed landmark sequence from tracking

    Returns:
        Tuple of (vertical_positions, visibilities) as numpy arrays
    """
    position_list: list[float] = []
    visibilities_list: list[float] = []

    for frame_landmarks in smoothed_landmarks:
        if frame_landmarks:
            _, foot_y = compute_average_foot_position(frame_landmarks)
            position_list.append(foot_y)
            visibilities_list.append(_calculate_average_visibility(frame_landmarks))
        else:
            # Fill missing frames with last known position or default
            position_list.append(position_list[-1] if position_list else 0.5)
            visibilities_list.append(0.0)

    return np.array(position_list), np.array(visibilities_list)
