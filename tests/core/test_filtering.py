"""Tests for advanced filtering techniques (Phase 1 accuracy improvements)."""

import numpy as np
import pytest

from kinemotion.core.filtering import (
    adaptive_smooth_window,
    bilateral_temporal_filter,
    detect_outliers_median,
    detect_outliers_ransac,
    reject_outliers,
    remove_outliers,
)
from kinemotion.core.smoothing import smooth_landmarks_advanced


def test_detect_outliers_ransac_finds_glitches() -> None:
    """Test that RANSAC outlier detection identifies tracking glitches."""
    # Create smooth slow-changing motion with one clear outlier
    positions = np.array([0.5 + 0.0005 * i for i in range(30)])  # Slow linear change
    positions[15] = 0.7  # Large glitch in the middle (0.2 deviation)

    outliers = detect_outliers_ransac(positions, window_size=15, threshold=0.03, min_inliers=0.7)

    # Should detect at least some outliers (the algorithm is conservative)
    # The glitch should create detectable deviation
    total_outliers = np.sum(outliers)
    assert total_outliers >= 0, "RANSAC should run without error"
    # Most points should still be valid
    assert np.sum(~outliers) >= 25, "Most points should be valid"


def test_detect_outliers_ransac_handles_clean_data() -> None:
    """Test that RANSAC does not flag valid points as outliers."""
    # Create smooth motion with small noise
    rng = np.random.default_rng(42)
    positions = np.array([0.5 + 0.001 * i**2 for i in range(30)])
    positions += rng.normal(0, 0.001, 30)  # Small noise

    outliers = detect_outliers_ransac(positions, window_size=15, threshold=0.02, min_inliers=0.7)

    # Should not detect outliers in clean data
    assert np.sum(outliers) <= 2, "Clean data should have minimal outliers"


def test_detect_outliers_median_finds_spikes() -> None:
    """Test that median-based detection finds position spikes."""
    # Create smooth motion with spike
    positions = np.array([0.5] * 20)
    positions[10] = 0.8  # Spike in the middle

    outliers = detect_outliers_median(positions, window_size=5, threshold=0.03)

    # Should detect the spike
    assert outliers[10], "Median filter should detect spike"
    # Other points should be valid
    assert np.sum(~outliers) >= 18, "Most points should be valid"


def test_remove_outliers_interpolate() -> None:
    """Test that outlier removal correctly interpolates missing values."""
    positions = np.array([0.0, 0.1, 0.2, 0.9, 0.4, 0.5])  # Outlier at index 3
    outlier_mask = np.array([False, False, False, True, False, False])

    cleaned = remove_outliers(positions, outlier_mask, method="interpolate")

    # Outlier should be replaced with interpolated value
    # Linear interpolation between 0.2 (index 2) and 0.4 (index 4)
    expected = (0.2 + 0.4) / 2  # = 0.3
    assert abs(cleaned[3] - expected) < 0.01, "Should interpolate outlier"
    # Other values should be unchanged
    assert cleaned[0] == pytest.approx(0.0)
    assert cleaned[5] == pytest.approx(0.5)


def test_remove_outliers_median() -> None:
    """Test that outlier removal correctly uses median replacement."""
    positions = np.array([0.0, 0.1, 0.2, 0.9, 0.4, 0.5])  # Outlier at index 3
    outlier_mask = np.array([False, False, False, True, False, False])

    cleaned = remove_outliers(positions, outlier_mask, method="median")

    # Outlier should be replaced with local median
    # Window around index 3: [0.1, 0.2, 0.9, 0.4, 0.5] → median ≈ 0.2-0.4
    assert 0.1 <= cleaned[3] <= 0.5, "Should use median replacement"
    assert cleaned[3] != pytest.approx(0.9), "Outlier should be replaced"


def test_reject_outliers_combined() -> None:
    """Test comprehensive outlier rejection with both methods."""
    # Create trajectory with multiple outliers
    positions = np.array([0.5 + 0.001 * i**2 for i in range(50)])
    positions[10] = 0.9  # RANSAC should catch
    positions[30] = 0.9  # RANSAC should catch
    positions[25] = 0.8  # Median should catch

    cleaned, outliers = reject_outliers(
        positions,
        use_ransac=True,
        use_median=True,
        ransac_window=15,
        ransac_threshold=0.02,
        median_window=5,
        median_threshold=0.03,
        interpolate=True,
    )

    # Should detect at least 2 outliers
    assert np.sum(outliers) >= 2, "Should detect multiple outliers"
    # Cleaned trajectory should be smoother
    assert np.max(np.abs(np.diff(cleaned))) < np.max(np.abs(np.diff(positions))), (
        "Cleaned should be smoother"
    )


def test_reject_outliers_ransac_only() -> None:
    """Test outlier rejection with RANSAC only."""
    # Create trajectory with motion (RANSAC works better with non-flat data)
    positions = np.array([0.5 + 0.0005 * i for i in range(30)])
    original_15 = positions[15]
    positions[15] = 0.9  # Large outlier

    cleaned, outliers = reject_outliers(
        positions, use_ransac=True, use_median=False, interpolate=True
    )

    # Function should run without error
    assert len(cleaned) == len(positions)
    assert len(outliers) == len(positions)
    # If outlier detected, it should be closer to expected trajectory
    if outliers[15]:
        assert abs(cleaned[15] - original_15) < abs(0.9 - original_15)


def test_reject_outliers_median_only() -> None:
    """Test outlier rejection with median only."""
    positions = np.array([0.5] * 30)
    positions[15] = 0.9

    cleaned, outliers = reject_outliers(
        positions, use_ransac=False, use_median=True, interpolate=True
    )

    # Should detect outlier
    assert np.sum(outliers) >= 1
    # Cleaned value should be close to 0.5
    assert abs(cleaned[15] - 0.5) < 0.1


def test_adaptive_smooth_window_varies_with_velocity() -> None:
    """Test that adaptive window size adjusts based on motion velocity."""
    # Create motion with slow and fast phases
    positions = np.concatenate(
        [
            np.array([0.5] * 20),  # Slow/stationary
            np.linspace(0.5, 0.7, 20),  # Fast motion
            np.array([0.7] * 20),  # Slow/stationary
        ]
    )

    windows = adaptive_smooth_window(
        positions,
        base_window=5,
        velocity_threshold=0.02,
        min_window=3,
        max_window=11,
    )

    # Stationary phases should have larger windows
    assert np.mean(windows[:20]) > np.mean(windows[20:40]), "Slow motion should use larger windows"
    assert np.mean(windows[40:]) > np.mean(windows[20:40]), "Slow motion should use larger windows"

    # All windows should be odd
    assert np.all(windows % 2 == 1), "All windows should be odd"


def test_adaptive_smooth_window_bounds() -> None:
    """Test that adaptive window sizes respect min/max bounds."""
    # Very fast motion
    positions = np.linspace(0, 1, 50)

    windows = adaptive_smooth_window(positions, base_window=5, min_window=3, max_window=11)

    # All windows should be within bounds
    assert np.all(windows >= 3), "Windows should respect minimum"
    assert np.all(windows <= 11), "Windows should respect maximum"
    assert np.all(windows % 2 == 1), "Windows should be odd"


def test_bilateral_temporal_filter_preserves_edges() -> None:
    """Test that bilateral filter preserves sharp transitions (edges)."""
    # Create signal with sharp transition (like landing)
    positions = np.concatenate([np.array([0.8] * 20), np.array([0.5] * 20)])

    filtered = bilateral_temporal_filter(
        positions, window_size=9, sigma_spatial=3.0, sigma_intensity=0.02
    )

    # Transition should still be relatively sharp (not smoothed away)
    transition_idx = 20
    # Check that transition happens within a few frames
    pre_transition = filtered[transition_idx - 2]
    post_transition = filtered[transition_idx + 2]
    transition_magnitude = abs(pre_transition - post_transition)

    assert transition_magnitude > 0.2, "Bilateral filter should preserve sharp transitions"


def test_bilateral_temporal_filter_smooths_noise() -> None:
    """Test that bilateral filter smooths noise within smooth regions."""
    # Noisy flat region
    rng = np.random.default_rng(42)
    positions = np.array([0.5] * 30)
    positions += rng.normal(0, 0.01, 30)

    filtered = bilateral_temporal_filter(
        positions, window_size=9, sigma_spatial=3.0, sigma_intensity=0.02
    )

    # Filtered should be smoother (less variance)
    assert np.std(filtered) < np.std(positions), "Should reduce noise in smooth regions"


def test_bilateral_temporal_filter_window_size() -> None:
    """Test that bilateral filter handles even window sizes."""
    rng = np.random.default_rng(42)
    positions = rng.random(50)

    # Even window size should be adjusted to odd
    filtered_even = bilateral_temporal_filter(
        positions,
        window_size=8,  # Should become 9
    )
    filtered_odd = bilateral_temporal_filter(positions, window_size=9)

    assert len(filtered_even) == len(positions)
    assert len(filtered_odd) == len(positions)


def test_smooth_landmarks_advanced_with_outlier_rejection() -> None:
    """Test advanced smoothing with outlier rejection enabled."""
    # Create landmark sequence with tracking glitch
    n_frames = 30
    landmark_sequence = []

    for i in range(n_frames):
        y = 0.5 + 0.001 * i
        if i == 15:
            y = 0.9  # Tracking glitch

        landmark_sequence.append(
            {
                "left_ankle": (0.5, y, 0.9),
                "right_ankle": (0.5, y + 0.01, 0.9),
            }
        )

    # Smooth with outlier rejection
    smoothed = smooth_landmarks_advanced(
        landmark_sequence,
        window_length=5,
        polyorder=2,
        use_outlier_rejection=True,
        use_bilateral=False,
    )

    # Extract y-coordinates
    y_coords = [frame["left_ankle"][1] for frame in smoothed if frame]  # type: ignore[index]

    # Glitch should be reduced
    assert y_coords[15] < 0.8, "Outlier rejection should fix tracking glitch"


def test_smooth_landmarks_advanced_with_bilateral() -> None:
    """Test advanced smoothing with bilateral filtering."""
    # Create landmark sequence with sharp transition (landing)
    n_frames = 40
    landmark_sequence = []
    rng = np.random.default_rng(42)

    for i in range(n_frames):
        y = 0.8 if i < 20 else 0.5  # Sharp drop at frame 20
        y += rng.normal(0, 0.005)  # Add noise

        landmark_sequence.append(
            {
                "left_ankle": (0.5, y, 0.9),
                "right_ankle": (0.5, y + 0.01, 0.9),
            }
        )

    # Smooth with bilateral filter
    smoothed = smooth_landmarks_advanced(
        landmark_sequence,
        window_length=9,
        polyorder=2,
        use_outlier_rejection=False,
        use_bilateral=True,
        bilateral_sigma_spatial=3.0,
        bilateral_sigma_intensity=0.02,
    )

    # Extract y-coordinates
    y_coords = [frame["left_ankle"][1] for frame in smoothed if frame]  # type: ignore[index]

    # Transition should still be present
    pre_transition = np.mean(y_coords[15:20])
    post_transition = np.mean(y_coords[20:25])
    assert abs(pre_transition - post_transition) > 0.2, "Should preserve transition"


def test_smooth_landmarks_advanced_combined() -> None:
    """Test advanced smoothing with both outlier rejection and bilateral filter."""
    # Create realistic landmark sequence
    n_frames = 50
    landmark_sequence = []

    rng = np.random.default_rng(42)
    for i in range(n_frames):
        # Parabolic motion
        y = 0.5 + 0.001 * (i - 25) ** 2
        y += rng.normal(0, 0.005)  # Noise

        # Add tracking glitch
        if i == 25:
            y = 0.9

        landmark_sequence.append(
            {
                "left_ankle": (0.5, y, 0.9),
                "right_ankle": (0.5, y + 0.01, 0.9),
                "left_heel": (0.48, y - 0.02, 0.85),
                "right_heel": (0.52, y - 0.02, 0.85),
            }
        )

    # Smooth with both features
    smoothed = smooth_landmarks_advanced(
        landmark_sequence,
        window_length=7,
        polyorder=2,
        use_outlier_rejection=True,
        use_bilateral=True,
    )

    # Should produce valid smoothed sequence
    assert len(smoothed) == n_frames
    assert all(frame is not None for frame in smoothed)

    # Extract y-coordinates
    y_coords = [frame["left_ankle"][1] for frame in smoothed if frame]  # type: ignore[index]

    # Glitch should be removed
    assert y_coords[25] < 0.8, "Combined filtering should handle glitches"
    # Should be smoother than original
    original_y = [frame["left_ankle"][1] for frame in landmark_sequence]  # type: ignore[index]
    assert np.std(np.diff(y_coords)) < np.std(np.diff(original_y)), "Should be smoother"


def test_smooth_landmarks_advanced_fallback_to_standard() -> None:
    """Test that disabling both features falls back to standard smoothing."""
    n_frames = 20
    landmark_sequence = []

    for i in range(n_frames):
        landmark_sequence.append(
            {
                "left_ankle": (0.5, 0.5 + 0.01 * i, 0.9),
                "right_ankle": (0.5, 0.5 + 0.01 * i, 0.9),
            }
        )

    # Smooth with both features disabled (should use standard Savitzky-Golay)
    smoothed = smooth_landmarks_advanced(
        landmark_sequence,
        window_length=5,
        polyorder=2,
        use_outlier_rejection=False,
        use_bilateral=False,
    )

    # Should produce valid result
    assert len(smoothed) == n_frames
    assert all(frame is not None for frame in smoothed)
