"""Landmark smoothing utilities to reduce jitter in pose tracking."""

from collections.abc import Callable

import numpy as np
from scipy.signal import savgol_filter

from .filtering import (
    bilateral_temporal_filter,
    reject_outliers,
)
from .timing import NULL_TIMER, Timer
from .types import FloatArray, LandmarkCoord, LandmarkSequence

# Type alias for smoothing function callback
SmootherFn = Callable[[list[float], list[float], list[int]], tuple[FloatArray, FloatArray]]


def _extract_landmark_coordinates(
    landmark_sequence: LandmarkSequence,
    landmark_name: str,
) -> tuple[list[float], list[float], list[int]]:
    """
    Extract x, y coordinates and valid frame indices for a specific landmark.

    Args:
        landmark_sequence: List of landmark dictionaries from each frame
        landmark_name: Name of the landmark to extract

    Returns:
        Tuple of (x_coords, y_coords, valid_frames)
    """
    x_coords: list[float] = []
    y_coords: list[float] = []
    valid_frames: list[int] = []

    for i, frame_landmarks in enumerate(landmark_sequence):
        if frame_landmarks is not None and landmark_name in frame_landmarks:
            x, y, _ = frame_landmarks[landmark_name]  # vis not used
            x_coords.append(x)
            y_coords.append(y)
            valid_frames.append(i)

    return x_coords, y_coords, valid_frames


def _get_landmark_names(
    landmark_sequence: LandmarkSequence,
) -> list[str] | None:
    """
    Extract landmark names from first valid frame.

    Args:
        landmark_sequence: List of landmark dictionaries from each frame

    Returns:
        List of landmark names or None if no valid frame found
    """
    for frame_landmarks in landmark_sequence:
        if frame_landmarks is not None:
            return list(frame_landmarks.keys())
    return None


def _fill_missing_frames(
    smoothed_sequence: LandmarkSequence,
    landmark_sequence: LandmarkSequence,
) -> None:
    """
    Fill in any missing frames in smoothed sequence with original data.

    Args:
        smoothed_sequence: Smoothed sequence (modified in place)
        landmark_sequence: Original sequence
    """
    for i in range(len(landmark_sequence)):
        if i >= len(smoothed_sequence) or not smoothed_sequence[i]:
            if i < len(smoothed_sequence):
                smoothed_sequence[i] = landmark_sequence[i]
            else:
                smoothed_sequence.append(landmark_sequence[i])


def _store_smoothed_landmarks(
    smoothed_sequence: LandmarkSequence,
    landmark_sequence: LandmarkSequence,
    landmark_name: str,
    x_smooth: FloatArray,
    y_smooth: FloatArray,
    valid_frames: list[int],
) -> None:
    """
    Store smoothed landmark values back into the sequence.

    Args:
        smoothed_sequence: Sequence to store smoothed values into (modified in place)
        landmark_sequence: Original sequence (for visibility values)
        landmark_name: Name of the landmark being smoothed
        x_smooth: Smoothed x coordinates
        y_smooth: Smoothed y coordinates
        valid_frames: Frame indices corresponding to smoothed values
    """
    for idx, frame_idx in enumerate(valid_frames):
        if frame_idx >= len(smoothed_sequence):
            empty_frames: list[dict[str, LandmarkCoord]] = [{}] * (
                frame_idx - len(smoothed_sequence) + 1
            )
            smoothed_sequence.extend(empty_frames)

        # Ensure smoothed_sequence[frame_idx] is a dict, not None
        if smoothed_sequence[frame_idx] is None:
            smoothed_sequence[frame_idx] = {}

        # Type narrowing: after the check above, we know it's a dict
        frame_dict = smoothed_sequence[frame_idx]
        assert frame_dict is not None  # for type checker

        if landmark_name not in frame_dict and landmark_sequence[frame_idx] is not None:
            # Keep original visibility
            orig_landmarks = landmark_sequence[frame_idx]
            assert orig_landmarks is not None  # for type checker
            orig_vis = orig_landmarks[landmark_name][2]
            frame_dict[landmark_name] = (
                float(x_smooth[idx]),
                float(y_smooth[idx]),
                orig_vis,
            )


def _smooth_landmarks_core(  # NOSONAR(S1172) - polyorder used via closure
    # capture in smoother_fn
    landmark_sequence: LandmarkSequence,
    window_length: int,
    polyorder: int,
    smoother_fn: SmootherFn,
) -> LandmarkSequence:
    """
    Core smoothing logic shared by both standard and advanced smoothing.

    Args:
        landmark_sequence: List of landmark dictionaries from each frame
        window_length: Length of filter window (must be odd)
        polyorder: Order of polynomial used to fit samples (captured by
            smoother_fn closure)
        smoother_fn: Function that takes (x_coords, y_coords, valid_frames)
            and returns (x_smooth, y_smooth)

    Returns:
        Smoothed landmark sequence
    """
    landmark_names = _get_landmark_names(landmark_sequence)
    if landmark_names is None:
        return landmark_sequence

    smoothed_sequence: LandmarkSequence = []

    for landmark_name in landmark_names:
        x_coords, y_coords, valid_frames = _extract_landmark_coordinates(
            landmark_sequence, landmark_name
        )

        if len(x_coords) < window_length:
            continue

        # Apply smoothing function
        x_smooth, y_smooth = smoother_fn(x_coords, y_coords, valid_frames)

        # Store smoothed values back
        _store_smoothed_landmarks(
            smoothed_sequence,
            landmark_sequence,
            landmark_name,
            x_smooth,
            y_smooth,
            valid_frames,
        )

    # Fill in any missing frames with original data
    _fill_missing_frames(smoothed_sequence, landmark_sequence)

    return smoothed_sequence


def _ensure_odd_window_length(window_length: int) -> int:
    """Ensure window_length is odd (required for Savitzky-Golay filter).

    Args:
        window_length: Desired window length

    Returns:
        Odd window length (increments by 1 if even)
    """
    return window_length + 1 if window_length % 2 == 0 else window_length


def smooth_landmarks(
    landmark_sequence: LandmarkSequence,
    window_length: int = 5,
    polyorder: int = 2,
) -> LandmarkSequence:
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
        return landmark_sequence

    window_length = _ensure_odd_window_length(window_length)

    def savgol_smoother(
        x_coords: list[float], y_coords: list[float], _valid_frames: list[int]
    ) -> tuple[FloatArray, FloatArray]:
        x_smooth: FloatArray = savgol_filter(x_coords, window_length, polyorder)
        y_smooth: FloatArray = savgol_filter(y_coords, window_length, polyorder)
        return x_smooth, y_smooth

    return _smooth_landmarks_core(landmark_sequence, window_length, polyorder, savgol_smoother)


def compute_velocity(positions: np.ndarray, fps: float, smooth_window: int = 3) -> np.ndarray:
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
        smooth_window = _ensure_odd_window_length(smooth_window)
        for dim in range(velocity.shape[1]):
            velocity[:, dim] = savgol_filter(velocity[:, dim], smooth_window, 1)

    return velocity


def _compute_derivative(
    positions: np.ndarray,
    deriv_order: int,
    window_length: int = 5,
    polyorder: int = 2,
) -> np.ndarray:
    """
    Compute nth derivative using Savitzky-Golay filter.

    This unified function handles both velocity (first derivative) and
    acceleration (second derivative) computation with a single implementation.

    Args:
        positions: 1D array of position values (e.g., foot y-positions)
        deriv_order: Order of derivative (1 for velocity, 2 for acceleration)
        window_length: Window size for smoothing (must be odd, >= polyorder + 2)
        polyorder: Polynomial order for Savitzky-Golay filter (typically 2 or 3)

    Returns:
        Array of derivative values
    """
    if len(positions) < window_length:
        # Fallback to simple differences for short sequences
        if deriv_order == 1:
            return np.abs(np.diff(positions, prepend=positions[0]))
        # Second derivative fallback
        velocity = np.diff(positions, prepend=positions[0])
        return np.diff(velocity, prepend=velocity[0])

    window_length = _ensure_odd_window_length(window_length)

    # Compute derivative using Savitzky-Golay filter
    # delta=1.0: frame spacing
    # mode='interp': interpolate at boundaries
    result = savgol_filter(
        positions,
        window_length,
        polyorder,
        deriv=deriv_order,
        delta=1.0,
        mode="interp",
    )

    # Return absolute values for velocity (first derivative)
    return np.abs(result) if deriv_order == 1 else result


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
    return _compute_derivative(
        positions, deriv_order=1, window_length=window_length, polyorder=polyorder
    )


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
    return _compute_derivative(
        positions, deriv_order=2, window_length=window_length, polyorder=polyorder
    )


def smooth_landmarks_advanced(
    landmark_sequence: LandmarkSequence,
    window_length: int = 5,
    polyorder: int = 2,
    use_outlier_rejection: bool = True,
    use_bilateral: bool = False,
    ransac_threshold: float = 0.02,
    bilateral_sigma_spatial: float = 3.0,
    bilateral_sigma_intensity: float = 0.02,
    timer: Timer | None = None,
) -> LandmarkSequence:
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
        timer: Optional Timer for measuring operations

    Returns:
        Smoothed landmark sequence with same structure as input
    """
    timer = timer or NULL_TIMER
    if len(landmark_sequence) < window_length:
        return landmark_sequence

    window_length = _ensure_odd_window_length(window_length)

    def advanced_smoother(
        x_coords: list[float], y_coords: list[float], _valid_frames: list[int]
    ) -> tuple[FloatArray, FloatArray]:
        x_array: FloatArray = np.array(x_coords)
        y_array: FloatArray = np.array(y_coords)

        # Step 1: Outlier rejection
        if use_outlier_rejection:
            with timer.measure("smoothing_outlier_rejection"):
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
            with timer.measure("smoothing_bilateral"):
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
            with timer.measure("smoothing_savgol"):
                x_smooth: FloatArray = savgol_filter(x_array, window_length, polyorder)  # type: ignore[reportUnknownVariableType]
                y_smooth: FloatArray = savgol_filter(y_array, window_length, polyorder)  # type: ignore[reportUnknownVariableType]

        return x_smooth, y_smooth

    return _smooth_landmarks_core(landmark_sequence, window_length, polyorder, advanced_smoother)


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
