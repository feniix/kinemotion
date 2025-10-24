"""Ground contact detection logic for drop-jump analysis."""

from enum import Enum

import numpy as np


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
