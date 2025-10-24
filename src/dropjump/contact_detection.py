"""Ground contact detection logic for drop-jump analysis."""

from enum import Enum

import numpy as np

from .smoothing import compute_velocity_from_derivative


class ContactState(Enum):
    """States for foot-ground contact."""

    IN_AIR = "in_air"
    ON_GROUND = "on_ground"
    UNKNOWN = "unknown"


def detect_ground_contact(
    foot_positions: np.ndarray,
    velocity_threshold: float = 0.02,
    min_contact_frames: int = 3,
    visibility_threshold: float = 0.5,
    visibilities: np.ndarray | None = None,
) -> list[ContactState]:
    """
    Detect when feet are in contact with ground based on vertical motion.

    Args:
        foot_positions: Array of foot y-positions (normalized, 0-1, where 1 is bottom)
        velocity_threshold: Threshold for vertical velocity to consider stationary
        min_contact_frames: Minimum consecutive frames to confirm contact
        visibility_threshold: Minimum visibility score to trust landmark
        visibilities: Array of visibility scores for each frame

    Returns:
        List of ContactState for each frame
    """
    n_frames = len(foot_positions)
    states = [ContactState.UNKNOWN] * n_frames

    if n_frames < 2:
        return states

    # Compute vertical velocity (positive = moving down in image coordinates)
    velocities = np.diff(foot_positions, prepend=foot_positions[0])

    # Detect potential contact frames based on low velocity
    is_stationary = np.abs(velocities) < velocity_threshold

    # Apply visibility filter
    if visibilities is not None:
        is_visible = visibilities > visibility_threshold
        is_stationary = is_stationary & is_visible

    # Apply minimum contact duration filter
    contact_frames = []
    current_run = []

    for i, stationary in enumerate(is_stationary):
        if stationary:
            current_run.append(i)
        else:
            if len(current_run) >= min_contact_frames:
                contact_frames.extend(current_run)
            current_run = []

    # Don't forget the last run
    if len(current_run) >= min_contact_frames:
        contact_frames.extend(current_run)

    # Set states
    for i in range(n_frames):
        if visibilities is not None and visibilities[i] < visibility_threshold:
            states[i] = ContactState.UNKNOWN
        elif i in contact_frames:
            states[i] = ContactState.ON_GROUND
        else:
            states[i] = ContactState.IN_AIR

    return states


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

    # Linear interpolation: at what fraction t does velocity equal threshold?
    # vel(t) = vel_before + t * (vel_after - vel_before)
    # Solve for t when vel(t) = threshold:
    # threshold = vel_before + t * (vel_after - vel_before)
    # t = (threshold - vel_before) / (vel_after - vel_before)

    t = (velocity_threshold - vel_before) / (vel_after - vel_before)

    # Clamp to [0, 1] range
    return float(max(0.0, min(1.0, t)))


def find_interpolated_phase_transitions(
    foot_positions: np.ndarray,
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
    # First get integer frame phases
    phases = find_contact_phases(contact_states)
    if not phases or len(foot_positions) < 2:
        return []

    # Compute velocities from derivative of smoothed trajectory
    # This gives much smoother velocity estimates than simple frame differences
    velocities = compute_velocity_from_derivative(
        foot_positions, window_length=smoothing_window, polyorder=2
    )

    interpolated_phases: list[tuple[float, float, ContactState]] = []

    for start_idx, end_idx, state in phases:
        start_frac = float(start_idx)
        end_frac = float(end_idx)

        # Interpolate start boundary (transition INTO this phase)
        if start_idx > 0 and start_idx < len(velocities):
            vel_before = velocities[start_idx - 1] if start_idx > 0 else velocities[start_idx]
            vel_at = velocities[start_idx]

            # Check if we're crossing the threshold at this boundary
            if state == ContactState.ON_GROUND:
                # Transition air→ground: velocity dropping below threshold
                if vel_before > velocity_threshold > vel_at:
                    # Interpolate between start_idx-1 and start_idx
                    offset = interpolate_threshold_crossing(
                        vel_before, vel_at, velocity_threshold
                    )
                    start_frac = (start_idx - 1) + offset
            elif state == ContactState.IN_AIR:
                # Transition ground→air: velocity rising above threshold
                if vel_before < velocity_threshold < vel_at:
                    # Interpolate between start_idx-1 and start_idx
                    offset = interpolate_threshold_crossing(
                        vel_before, vel_at, velocity_threshold
                    )
                    start_frac = (start_idx - 1) + offset

        # Interpolate end boundary (transition OUT OF this phase)
        if end_idx < len(foot_positions) - 1 and end_idx + 1 < len(velocities):
            vel_at = velocities[end_idx]
            vel_after = velocities[end_idx + 1]

            # Check if we're crossing the threshold at this boundary
            if state == ContactState.ON_GROUND:
                # Transition ground→air: velocity rising above threshold
                if vel_at < velocity_threshold < vel_after:
                    # Interpolate between end_idx and end_idx+1
                    offset = interpolate_threshold_crossing(
                        vel_at, vel_after, velocity_threshold
                    )
                    end_frac = end_idx + offset
            elif state == ContactState.IN_AIR:
                # Transition air→ground: velocity dropping below threshold
                if vel_at > velocity_threshold > vel_after:
                    # Interpolate between end_idx and end_idx+1
                    offset = interpolate_threshold_crossing(
                        vel_at, vel_after, velocity_threshold
                    )
                    end_frac = end_idx + offset

        interpolated_phases.append((start_frac, end_frac, state))

    return interpolated_phases


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
