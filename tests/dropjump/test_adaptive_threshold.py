"""Tests for adaptive velocity threshold calculation."""

import numpy as np
import pytest

from kinemotion.dropjump.analysis import calculate_adaptive_threshold


def test_adaptive_threshold_basic() -> None:
    """Test basic adaptive threshold calculation with stationary baseline."""
    # Create position data with low-noise baseline (first 3 seconds)
    # and then movement
    fps = 30.0
    baseline_frames = int(3 * fps)  # 90 frames

    # Baseline: small random noise around position 0.5
    rng = np.random.default_rng(42)
    baseline_positions = 0.5 + rng.normal(0, 0.005, baseline_frames)

    # Movement: larger position changes
    movement_positions = np.linspace(0.5, 0.7, 60)

    positions = np.concatenate([baseline_positions, movement_positions])

    threshold = calculate_adaptive_threshold(positions, fps)

    # Threshold should be above baseline noise but below movement velocity
    assert 0.005 <= threshold <= 0.03, f"Threshold {threshold} not in expected range"
    # With very low noise, minimum threshold (0.005) kicks in
    assert 0.005 <= threshold <= 0.015, f"Threshold {threshold} not scaled correctly"


def test_adaptive_threshold_high_noise() -> None:
    """Test adaptive threshold adapts to high-noise baseline."""
    fps = 30.0
    baseline_frames = int(3 * fps)

    # High noise baseline
    rng = np.random.default_rng(42)
    baseline_positions = 0.5 + rng.normal(0, 0.015, baseline_frames)
    movement_positions = np.linspace(0.5, 0.8, 60)
    positions = np.concatenate([baseline_positions, movement_positions])

    threshold = calculate_adaptive_threshold(positions, fps)

    # With higher noise, threshold should be proportionally higher
    # Noise std=0.015 with multiplier 1.5 gives ~0.012-0.022 range
    assert 0.010 <= threshold <= 0.05, f"Threshold {threshold} should adapt to high noise"


def test_adaptive_threshold_low_noise() -> None:
    """Test adaptive threshold with very low noise baseline."""
    fps = 30.0
    baseline_frames = int(3 * fps)

    # Very low noise baseline
    rng = np.random.default_rng(42)
    baseline_positions = 0.5 + rng.normal(0, 0.002, baseline_frames)
    movement_positions = np.linspace(0.5, 0.7, 60)
    positions = np.concatenate([baseline_positions, movement_positions])

    threshold = calculate_adaptive_threshold(positions, fps)

    # Should still have minimum threshold to avoid being too sensitive
    assert threshold >= 0.005, f"Threshold {threshold} should respect minimum"
    assert threshold <= 0.015, f"Threshold {threshold} should be low for low noise"


def test_adaptive_threshold_minimum_bound() -> None:
    """Test adaptive threshold respects minimum bound."""
    fps = 30.0
    baseline_frames = int(3 * fps)

    # Perfectly stationary (no noise)
    baseline_positions = np.full(baseline_frames, 0.5)
    movement_positions = np.linspace(0.5, 0.7, 60)
    positions = np.concatenate([baseline_positions, movement_positions])

    threshold = calculate_adaptive_threshold(positions, fps)

    # Should have minimum threshold even with zero noise
    assert threshold >= 0.005, f"Threshold {threshold} should respect minimum of 0.005"


def test_adaptive_threshold_maximum_bound() -> None:
    """Test adaptive threshold respects maximum bound."""
    fps = 30.0
    baseline_frames = int(3 * fps)

    # Extreme noise baseline
    rng = np.random.default_rng(42)
    baseline_positions = 0.5 + rng.normal(0, 0.05, baseline_frames)
    movement_positions = np.linspace(0.5, 0.8, 60)
    positions = np.concatenate([baseline_positions, movement_positions])

    threshold = calculate_adaptive_threshold(positions, fps)

    # Should cap at maximum to ensure contact detection still works
    assert threshold <= 0.05, f"Threshold {threshold} should respect maximum of 0.05"


def test_adaptive_threshold_short_video() -> None:
    """Test adaptive threshold with video shorter than baseline duration."""
    fps = 30.0

    # Only 60 frames (2 seconds) - less than 3 second baseline
    rng = np.random.default_rng(42)
    positions = 0.5 + rng.normal(0, 0.01, 60)

    threshold = calculate_adaptive_threshold(positions, fps, baseline_duration=3.0)

    # Should still work with available frames
    assert 0.005 <= threshold <= 0.05, f"Threshold {threshold} should work with short video"


def test_adaptive_threshold_very_short_video() -> None:
    """Test adaptive threshold fallback with very short video."""
    fps = 30.0

    # Only 3 frames - not enough for analysis
    positions = np.array([0.5, 0.51, 0.52])

    threshold = calculate_adaptive_threshold(positions, fps, smoothing_window=5)

    # Should return default threshold
    assert threshold == pytest.approx(0.02), "Should return default 0.02 for very short video"


def test_adaptive_threshold_different_fps() -> None:
    """Test adaptive threshold adapts to different frame rates."""
    # Higher FPS should still work correctly
    fps = 60.0
    baseline_frames = int(3 * fps)  # 180 frames

    rng = np.random.default_rng(42)
    baseline_positions = 0.5 + rng.normal(0, 0.008, baseline_frames)
    movement_positions = np.linspace(0.5, 0.7, 120)
    positions = np.concatenate([baseline_positions, movement_positions])

    threshold = calculate_adaptive_threshold(positions, fps)

    # Should work regardless of FPS
    assert 0.005 <= threshold <= 0.05, f"Threshold {threshold} should work at 60fps"


def test_adaptive_threshold_custom_multiplier() -> None:
    """Test adaptive threshold with custom multiplier."""
    fps = 30.0
    baseline_frames = int(3 * fps)

    rng = np.random.default_rng(42)
    baseline_positions = 0.5 + rng.normal(0, 0.008, baseline_frames)
    movement_positions = np.linspace(0.5, 0.7, 60)
    positions = np.concatenate([baseline_positions, movement_positions])

    # Test with different multipliers
    threshold_conservative = calculate_adaptive_threshold(
        positions, fps, multiplier=2.0
    )  # More conservative
    threshold_aggressive = calculate_adaptive_threshold(
        positions, fps, multiplier=1.2
    )  # More aggressive

    # Higher multiplier should give higher threshold
    assert threshold_conservative > threshold_aggressive, (
        "Conservative multiplier should give higher threshold"
    )
    # With minimum threshold, ratio may be small, but should still show difference
    assert (threshold_conservative / threshold_aggressive) >= 1.05, (
        "Multiplier should have some effect"
    )


def test_adaptive_threshold_baseline_duration() -> None:
    """Test adaptive threshold with different baseline durations."""
    fps = 30.0

    # Long video with different noise in different sections
    rng = np.random.default_rng(42)
    first_3s = 0.5 + rng.normal(0, 0.005, int(3 * fps))  # Low noise
    next_2s = 0.5 + rng.normal(0, 0.015, int(2 * fps))  # High noise
    movement = np.linspace(0.5, 0.7, 60)

    positions = np.concatenate([first_3s, next_2s, movement])

    # Use only first 3 seconds (low noise)
    threshold_3s = calculate_adaptive_threshold(positions, fps, baseline_duration=3.0)

    # Use first 5 seconds (includes high noise section)
    threshold_5s = calculate_adaptive_threshold(positions, fps, baseline_duration=5.0)

    # 5s baseline should have higher threshold due to including high-noise section
    assert threshold_5s >= threshold_3s, (
        "Longer baseline including noise should give higher threshold"
    )
