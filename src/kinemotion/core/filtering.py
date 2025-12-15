"""Advanced filtering techniques for robust trajectory processing."""

import numpy as np
from scipy.signal import medfilt

from .experimental import unused


def detect_outliers_ransac(
    positions: np.ndarray,
    window_size: int = 15,
    threshold: float = 0.02,
    min_inliers: float = 0.7,
) -> np.ndarray:
    """
    Detect outlier positions using RANSAC-based polynomial fitting.

    Uses a sliding window approach to detect positions that deviate significantly
    from a polynomial fit of nearby points. This catches MediaPipe tracking glitches
    where landmarks jump to incorrect positions.

    Args:
        positions: 1D array of position values (e.g., y-coordinates)
        window_size: Size of sliding window for local fitting
        threshold: Distance threshold to consider a point an inlier
        min_inliers: Minimum fraction of points that must be inliers

    Returns:
        Boolean array: True for outliers, False for valid points
    """
    n = len(positions)
    is_outlier = np.zeros(n, dtype=bool)

    if n < window_size:
        return is_outlier

    # Ensure window size is odd
    if window_size % 2 == 0:
        window_size += 1

    half_window = window_size // 2

    for i in range(n):
        # Define window around current point
        start = max(0, i - half_window)
        end = min(n, i + half_window + 1)
        window_positions = positions[start:end]
        window_indices = np.arange(start, end)

        if len(window_positions) < 3:
            continue

        # Fit polynomial (quadratic) to window
        # Use polyfit with degree 2 (parabolic motion)
        try:
            coeffs = np.polyfit(window_indices, window_positions, deg=2)
            predicted = np.polyval(coeffs, window_indices)

            # Calculate residuals
            residuals = np.abs(window_positions - predicted)

            # Point is outlier if its residual is large
            local_idx = i - start
            if local_idx < len(residuals) and residuals[local_idx] > threshold:
                # Also check if most other points are inliers (RANSAC criterion)
                inliers = np.sum(residuals <= threshold)
                if inliers / len(residuals) >= min_inliers:
                    is_outlier[i] = True
        except np.linalg.LinAlgError:
            # Polyfit failed, skip this window
            continue

    return is_outlier


def detect_outliers_median(
    positions: np.ndarray, window_size: int = 5, threshold: float = 0.03
) -> np.ndarray:
    """
    Detect outliers using median filtering.

    Points that deviate significantly from the local median are marked as outliers.
    More robust to noise than mean-based methods.

    Args:
        positions: 1D array of position values
        window_size: Size of median filter window (must be odd)
        threshold: Deviation threshold to mark as outlier

    Returns:
        Boolean array: True for outliers, False for valid points
    """
    if len(positions) < window_size:
        return np.zeros(len(positions), dtype=bool)

    # Ensure window size is odd
    if window_size % 2 == 0:
        window_size += 1

    # Apply median filter
    median_filtered = medfilt(positions, kernel_size=window_size)

    # Calculate absolute deviation from median
    deviations = np.abs(positions - median_filtered)

    # Mark as outlier if deviation exceeds threshold
    is_outlier = deviations > threshold

    return is_outlier


def remove_outliers(
    positions: np.ndarray,
    outlier_mask: np.ndarray,
    method: str = "interpolate",
) -> np.ndarray:
    """
    Replace outlier values with interpolated or median values.

    Args:
        positions: Original position array
        outlier_mask: Boolean array indicating outliers
        method: "interpolate" or "median"
            - interpolate: Linear interpolation from neighboring valid points
            - median: Replace with local median of valid points

    Returns:
        Position array with outliers replaced
    """
    positions_clean = positions.copy()

    if not np.any(outlier_mask):
        return positions_clean

    outlier_indices = np.nonzero(outlier_mask)[0]

    for idx in outlier_indices:
        if method == "interpolate":
            # Find nearest valid points before and after
            valid_before = np.nonzero(~outlier_mask[:idx])[0]
            valid_after = np.nonzero(~outlier_mask[idx + 1 :])[0]

            if len(valid_before) > 0 and len(valid_after) > 0:
                # Linear interpolation between nearest valid points
                idx_before = valid_before[-1]
                idx_after = valid_after[0] + idx + 1

                # Interpolate
                t = (idx - idx_before) / (idx_after - idx_before)
                positions_clean[idx] = positions[idx_before] * (1 - t) + positions[idx_after] * t
            elif len(valid_before) > 0:
                # Use last valid value
                positions_clean[idx] = positions[valid_before[-1]]
            elif len(valid_after) > 0:
                # Use next valid value
                positions_clean[idx] = positions[valid_after[0] + idx + 1]

        elif method == "median":
            # Replace with median of nearby valid points
            window_size = 5
            start = max(0, idx - window_size)
            end = min(len(positions), idx + window_size + 1)

            window_valid = ~outlier_mask[start:end]
            if np.any(window_valid):
                positions_clean[idx] = np.median(positions[start:end][window_valid])

    return positions_clean


def reject_outliers(
    positions: np.ndarray,
    use_ransac: bool = True,
    use_median: bool = True,
    ransac_window: int = 15,
    ransac_threshold: float = 0.02,
    median_window: int = 5,
    median_threshold: float = 0.03,
    interpolate: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Comprehensive outlier rejection using multiple methods.

    Combines RANSAC-based and median-based outlier detection for robust
    identification of tracking glitches.

    Args:
        positions: 1D array of position values
        use_ransac: Enable RANSAC-based outlier detection
        use_median: Enable median-based outlier detection
        ransac_window: Window size for RANSAC
        ransac_threshold: Deviation threshold for RANSAC
        median_window: Window size for median filter
        median_threshold: Deviation threshold for median
        interpolate: Replace outliers with interpolated values

    Returns:
        Tuple of (cleaned_positions, outlier_mask)
        - cleaned_positions: Positions with outliers replaced
        - outlier_mask: Boolean array marking outliers
    """
    outlier_mask = np.zeros(len(positions), dtype=bool)

    # Detect outliers using RANSAC
    if use_ransac:
        ransac_outliers = detect_outliers_ransac(
            positions, window_size=ransac_window, threshold=ransac_threshold
        )
        outlier_mask |= ransac_outliers

    # Detect outliers using median filtering
    if use_median:
        median_outliers = detect_outliers_median(
            positions, window_size=median_window, threshold=median_threshold
        )
        outlier_mask |= median_outliers

    # Remove/replace outliers
    if interpolate:
        cleaned_positions = remove_outliers(positions, outlier_mask, method="interpolate")
    else:
        cleaned_positions = positions.copy()

    return cleaned_positions, outlier_mask


@unused(
    reason="Not called by analysis pipeline - alternative adaptive smoothing approach",
    remove_in="1.0.0",
    since="0.34.0",
)
def adaptive_smooth_window(
    positions: np.ndarray,
    base_window: int = 5,
    velocity_threshold: float = 0.02,
    min_window: int = 3,
    max_window: int = 11,
) -> np.ndarray:
    """
    Determine adaptive smoothing window size based on local motion velocity.

    Uses larger windows during slow motion (ground contact) and smaller windows
    during fast motion (flight) to preserve details where needed while smoothing
    where safe.

    Args:
        positions: 1D array of position values
        base_window: Base window size (default: 5)
        velocity_threshold: Velocity below which to use larger window
        min_window: Minimum window size (for fast motion)
        max_window: Maximum window size (for slow motion)

    Returns:
        Array of window sizes for each frame
    """
    n = len(positions)
    windows = np.full(n, base_window, dtype=int)

    if n < 2:
        return windows

    # Compute local velocity (simple diff)
    velocities = np.abs(np.diff(positions, prepend=positions[0]))

    # Smooth velocity to avoid spurious changes
    if n >= 5:
        from scipy.signal import medfilt

        velocities = medfilt(velocities, kernel_size=5)

    # Assign window sizes based on velocity
    for i in range(n):
        if velocities[i] < velocity_threshold / 2:
            # Very slow motion - use maximum window
            windows[i] = max_window
        elif velocities[i] < velocity_threshold:
            # Slow motion - use larger window
            windows[i] = (base_window + max_window) // 2
        else:
            # Fast motion - use smaller window
            windows[i] = min_window

    # Ensure windows are odd
    windows = np.where(windows % 2 == 0, windows + 1, windows)

    return windows


def bilateral_temporal_filter(
    positions: np.ndarray,
    window_size: int = 9,
    sigma_spatial: float = 3.0,
    sigma_intensity: float = 0.02,
) -> np.ndarray:
    """
    Apply bilateral filter in temporal domain for edge-preserving smoothing.

    Unlike Savitzky-Golay which smooths uniformly across all frames, the bilateral
    filter preserves sharp transitions (like landing/takeoff) while smoothing within
    smooth regions (flight phase, ground contact).

    The filter weights each neighbor by both:
    1. Temporal distance (like regular smoothing)
    2. Intensity similarity (preserves edges)

    Args:
        positions: 1D array of position values
        window_size: Temporal window size (must be odd)
        sigma_spatial: Std dev for spatial (temporal) Gaussian kernel
        sigma_intensity: Std dev for intensity (position difference) kernel

    Returns:
        Filtered position array
    """
    n = len(positions)
    filtered = np.zeros(n)

    # Ensure window size is odd
    if window_size % 2 == 0:
        window_size += 1

    half_window = window_size // 2

    for i in range(n):
        # Define window
        start = max(0, i - half_window)
        end = min(n, i + half_window + 1)

        # Get window positions
        window_pos = positions[start:end]
        center_pos = positions[i]

        # Compute spatial (temporal) weights
        temporal_indices = np.arange(start - i, end - i)
        spatial_weights = np.exp(-(temporal_indices**2) / (2 * sigma_spatial**2))

        # Compute intensity (position difference) weights
        intensity_diff = window_pos - center_pos
        intensity_weights = np.exp(-(intensity_diff**2) / (2 * sigma_intensity**2))

        # Combined weights (bilateral)
        weights = spatial_weights * intensity_weights
        weights /= np.sum(weights)  # Normalize

        # Weighted average
        filtered[i] = np.sum(weights * window_pos)

    return filtered
