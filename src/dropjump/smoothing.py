"""Landmark smoothing utilities to reduce jitter in pose tracking."""


import numpy as np
from scipy.signal import savgol_filter


def smooth_landmarks(
    landmark_sequence: list[dict[str, tuple[float, float, float]] | None],
    window_length: int = 5,
    polyorder: int = 2,
) -> list[dict[str, tuple[float, float, float]] | None]:
    """
    Smooth landmark trajectories using Savitzky-Golay filter.

    Args:
        landmark_sequence: List of landmark dictionaries from each frame
        window_length: Length of filter window (must be odd, >= polyorder + 2)
        polyorder: Order of polynomial used to fit samples

    Returns:
        Smoothed landmark sequence with same structure as input
    """
    if len(landmark_sequence) < window_length:
        # Not enough frames to smooth effectively
        return landmark_sequence

    # Ensure window_length is odd
    if window_length % 2 == 0:
        window_length += 1

    # Extract landmark names from first valid frame
    landmark_names = None
    for frame_landmarks in landmark_sequence:
        if frame_landmarks is not None:
            landmark_names = list(frame_landmarks.keys())
            break

    if landmark_names is None:
        return landmark_sequence

    # Build arrays for each landmark coordinate
    smoothed_sequence: list[dict[str, tuple[float, float, float]] | None] = []

    for landmark_name in landmark_names:
        # Extract x, y coordinates for this landmark across all frames
        x_coords = []
        y_coords = []
        valid_frames = []

        for i, frame_landmarks in enumerate(landmark_sequence):
            if frame_landmarks is not None and landmark_name in frame_landmarks:
                x, y, vis = frame_landmarks[landmark_name]
                x_coords.append(x)
                y_coords.append(y)
                valid_frames.append(i)

        if len(x_coords) < window_length:
            continue

        # Apply Savitzky-Golay filter
        x_smooth = savgol_filter(x_coords, window_length, polyorder)
        y_smooth = savgol_filter(y_coords, window_length, polyorder)

        # Store smoothed values back
        for idx, frame_idx in enumerate(valid_frames):
            if frame_idx >= len(smoothed_sequence):
                smoothed_sequence.extend(
                    [{}] * (frame_idx - len(smoothed_sequence) + 1)
                )

            # Ensure smoothed_sequence[frame_idx] is a dict, not None
            if smoothed_sequence[frame_idx] is None:
                smoothed_sequence[frame_idx] = {}

            if (
                landmark_name not in smoothed_sequence[frame_idx]  # type: ignore[operator]
                and landmark_sequence[frame_idx] is not None
            ):
                # Keep original visibility
                orig_vis = landmark_sequence[frame_idx][landmark_name][2]  # type: ignore[index]
                smoothed_sequence[frame_idx][landmark_name] = (  # type: ignore[index]
                    float(x_smooth[idx]),
                    float(y_smooth[idx]),
                    orig_vis,
                )

    # Fill in any missing frames with original data
    for i in range(len(landmark_sequence)):
        if i >= len(smoothed_sequence) or not smoothed_sequence[i]:
            if i < len(smoothed_sequence):
                smoothed_sequence[i] = landmark_sequence[i]
            else:
                smoothed_sequence.append(landmark_sequence[i])

    return smoothed_sequence


def compute_velocity(
    positions: np.ndarray, fps: float, smooth_window: int = 3
) -> np.ndarray:
    """
    Compute velocity from position data.

    Args:
        positions: Array of positions over time (n_frames, n_dims)
        fps: Frames per second of the video
        smooth_window: Window size for velocity smoothing

    Returns:
        Velocity array (n_frames, n_dims)
    """
    dt = 1.0 / fps
    velocity = np.gradient(positions, dt, axis=0)

    # Smooth velocity if we have enough data
    if len(velocity) >= smooth_window and smooth_window > 1:
        if smooth_window % 2 == 0:
            smooth_window += 1
        for dim in range(velocity.shape[1]):
            velocity[:, dim] = savgol_filter(velocity[:, dim], smooth_window, 1)

    return velocity  # type: ignore[no-any-return]
