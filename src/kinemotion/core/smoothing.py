"""Landmark smoothing utilities to reduce jitter in pose tracking."""

import numpy as np
from scipy.signal import savgol_filter

from .filtering import (
    bilateral_temporal_filter,
    reject_outliers,
)


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
                landmark_name not in smoothed_sequence[frame_idx]
                and landmark_sequence[frame_idx] is not None
            ):
                # Keep original visibility
                orig_vis = landmark_sequence[frame_idx][landmark_name][2]
                smoothed_sequence[frame_idx][landmark_name] = (
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

    return velocity


def compute_velocity_from_derivative(
    positions: np.ndarray,
    window_length: int = 5,
    polyorder: int = 2,
) -> np.ndarray:
    """
    Compute velocity as derivative of smoothed position trajectory.

    Uses Savitzky-Golay filter to compute the derivative directly, which provides
    a much smoother and more accurate velocity estimate than frame-to-frame differences.

    This method:
    1. Fits a polynomial to the position data in a sliding window
    2. Analytically computes the derivative of that polynomial
    3. Returns smooth velocity values

    Args:
        positions: 1D array of position values (e.g., foot y-positions)
        window_length: Window size for smoothing (must be odd, >= polyorder + 2)
        polyorder: Polynomial order for Savitzky-Golay filter (typically 2 or 3)

    Returns:
        Array of absolute velocity values (magnitude of derivative)
    """
    if len(positions) < window_length:
        # Fallback to simple differences for short sequences
        return np.abs(np.diff(positions, prepend=positions[0]))

    # Ensure window_length is odd
    if window_length % 2 == 0:
        window_length += 1

    # Compute derivative using Savitzky-Golay filter
    # deriv=1: compute first derivative
    # delta=1.0: frame spacing (velocity per frame)
    # mode='interp': interpolate at boundaries
    velocity = savgol_filter(
        positions,
        window_length,
        polyorder,
        deriv=1,  # First derivative
        delta=1.0,  # Frame spacing
        mode="interp",
    )

    # Return absolute velocity (magnitude only)
    return np.abs(velocity)


def compute_acceleration_from_derivative(
    positions: np.ndarray,
    window_length: int = 5,
    polyorder: int = 2,
) -> np.ndarray:
    """
    Compute acceleration as second derivative of smoothed position trajectory.

    Uses Savitzky-Golay filter to compute the second derivative directly,
    providing smooth acceleration (curvature) estimates for detecting
    characteristic patterns at landing and takeoff.

    Landing and takeoff events show distinctive acceleration patterns:
    - Landing: Large acceleration spike as feet decelerate on impact
    - Takeoff: Acceleration change as body accelerates upward
    - In flight: Constant acceleration due to gravity
    - On ground: Near-zero acceleration (stationary position)

    Args:
        positions: 1D array of position values (e.g., foot y-positions)
        window_length: Window size for smoothing (must be odd, >= polyorder + 2)
        polyorder: Polynomial order for Savitzky-Golay filter (typically 2 or 3)

    Returns:
        Array of acceleration values (second derivative of position)
    """
    if len(positions) < window_length:
        # Fallback to simple second differences for short sequences
        velocity = np.diff(positions, prepend=positions[0])
        return np.diff(velocity, prepend=velocity[0])

    # Ensure window_length is odd
    if window_length % 2 == 0:
        window_length += 1

    # Compute second derivative using Savitzky-Golay filter
    # deriv=2: compute second derivative (acceleration/curvature)
    # delta=1.0: frame spacing
    # mode='interp': interpolate at boundaries
    acceleration = savgol_filter(
        positions,
        window_length,
        polyorder,
        deriv=2,  # Second derivative
        delta=1.0,  # Frame spacing
        mode="interp",
    )

    return acceleration


def smooth_landmarks_advanced(
    landmark_sequence: list[dict[str, tuple[float, float, float]] | None],
    window_length: int = 5,
    polyorder: int = 2,
    use_outlier_rejection: bool = True,
    use_bilateral: bool = False,
    ransac_threshold: float = 0.02,
    bilateral_sigma_spatial: float = 3.0,
    bilateral_sigma_intensity: float = 0.02,
) -> list[dict[str, tuple[float, float, float]] | None]:
    """
    Advanced landmark smoothing with outlier rejection and bilateral filtering.

    Combines multiple techniques for robust smoothing:
    1. Outlier rejection (RANSAC + median filtering)
    2. Optional bilateral filtering (edge-preserving)
    3. Savitzky-Golay smoothing

    Args:
        landmark_sequence: List of landmark dictionaries from each frame
        window_length: Length of filter window (must be odd, >= polyorder + 2)
        polyorder: Order of polynomial used to fit samples
        use_outlier_rejection: Apply outlier detection and removal
        use_bilateral: Use bilateral filter instead of Savitzky-Golay
        ransac_threshold: Threshold for RANSAC outlier detection
        bilateral_sigma_spatial: Spatial sigma for bilateral filter
        bilateral_sigma_intensity: Intensity sigma for bilateral filter

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

        x_array = np.array(x_coords)
        y_array = np.array(y_coords)

        # Step 1: Outlier rejection
        if use_outlier_rejection:
            x_array, _ = reject_outliers(
                x_array,
                use_ransac=True,
                use_median=True,
                ransac_threshold=ransac_threshold,
            )
            y_array, _ = reject_outliers(
                y_array,
                use_ransac=True,
                use_median=True,
                ransac_threshold=ransac_threshold,
            )

        # Step 2: Smoothing (bilateral or Savitzky-Golay)
        if use_bilateral:
            x_smooth = bilateral_temporal_filter(
                x_array,
                window_size=window_length,
                sigma_spatial=bilateral_sigma_spatial,
                sigma_intensity=bilateral_sigma_intensity,
            )
            y_smooth = bilateral_temporal_filter(
                y_array,
                window_size=window_length,
                sigma_spatial=bilateral_sigma_spatial,
                sigma_intensity=bilateral_sigma_intensity,
            )
        else:
            # Standard Savitzky-Golay
            x_smooth = savgol_filter(x_array, window_length, polyorder)
            y_smooth = savgol_filter(y_array, window_length, polyorder)

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
                landmark_name not in smoothed_sequence[frame_idx]
                and landmark_sequence[frame_idx] is not None
            ):
                # Keep original visibility
                orig_vis = landmark_sequence[frame_idx][landmark_name][2]
                smoothed_sequence[frame_idx][landmark_name] = (
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
