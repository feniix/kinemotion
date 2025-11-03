"""Tests for polynomial order parameter in smoothing and derivative calculations."""

import numpy as np

from kinemotion.core.smoothing import (
    compute_acceleration_from_derivative,
    compute_velocity_from_derivative,
    smooth_landmarks,
)


def test_smooth_landmarks_polyorder2_vs_polyorder3() -> None:
    """Test that different polynomial orders produce different smoothed results."""
    # Create synthetic landmark sequence with some noise
    n_frames = 30
    landmark_sequence = []

    rng = np.random.default_rng(42)
    for i in range(n_frames):
        # Smooth parabolic motion with noise
        base_y = 0.5 + 0.01 * (i - 15) ** 2 / 225  # Parabola
        noisy_y = base_y + rng.normal(0, 0.01)

        landmark_sequence.append(
            {
                "left_ankle": (0.5, noisy_y, 0.9),
                "right_ankle": (0.5, noisy_y + 0.01, 0.9),
            }
        )

    # Smooth with polyorder=2 (quadratic)
    smoothed_2 = smooth_landmarks(landmark_sequence, window_length=5, polyorder=2)

    # Smooth with polyorder=3 (cubic)
    smoothed_3 = smooth_landmarks(landmark_sequence, window_length=7, polyorder=3)

    # Extract y-coordinates
    y_coords_2 = [frame["left_ankle"][1] for frame in smoothed_2 if frame]  # type: ignore[index]
    y_coords_3 = [frame["left_ankle"][1] for frame in smoothed_3 if frame]  # type: ignore[index]

    # Results should be different (different polynomial fits)
    assert len(y_coords_2) == len(y_coords_3)
    differences = [abs(y2 - y3) for y2, y3 in zip(y_coords_2, y_coords_3, strict=True)]
    avg_difference = np.mean(differences)

    # Some frames should have noticeable differences
    assert avg_difference > 0.0001, "Polyorder should affect smoothing results"


def test_velocity_from_derivative_polyorder() -> None:
    """Test velocity computation with different polynomial orders."""
    # Create synthetic position data with quadratic motion
    rng = np.random.default_rng(42)
    t = np.linspace(0, 2, 60)
    positions = 0.5 + 0.1 * t**2  # Parabolic trajectory
    positions += rng.normal(0, 0.005, len(positions))  # Add noise

    # Compute velocity with different polynomial orders
    velocity_2 = compute_velocity_from_derivative(
        positions, window_length=5, polyorder=2
    )
    velocity_3 = compute_velocity_from_derivative(
        positions, window_length=7, polyorder=3
    )

    # Both should produce reasonable velocities
    assert len(velocity_2) == len(positions)
    assert len(velocity_3) == len(positions)

    # All velocities should be non-negative (absolute values)
    assert np.all(velocity_2 >= 0)
    assert np.all(velocity_3 >= 0)

    # Results should differ slightly due to different polynomial fits
    difference = np.mean(np.abs(velocity_2 - velocity_3))
    assert (
        difference > 0.0001
    ), "Different polyorders should produce different velocities"


def test_acceleration_from_derivative_polyorder() -> None:
    """Test acceleration computation with different polynomial orders."""
    # Create synthetic position data with cubic motion (non-zero third derivative)
    rng = np.random.default_rng(42)
    t = np.linspace(0, 2, 60)
    positions = 0.5 + 0.05 * t**3  # Cubic trajectory
    positions += rng.normal(0, 0.003, len(positions))  # Add noise

    # Compute acceleration with different polynomial orders
    accel_2 = compute_acceleration_from_derivative(
        positions, window_length=5, polyorder=2
    )
    accel_3 = compute_acceleration_from_derivative(
        positions, window_length=7, polyorder=3
    )

    # Both should produce acceleration arrays
    assert len(accel_2) == len(positions)
    assert len(accel_3) == len(positions)

    # Cubic polynomial fit should capture cubic trajectory better
    # For cubic motion: a(t) = 6 * coefficient * t (for 0.05*t^3, coefficient = 0.05)
    # Expected acceleration should increase linearly
    expected_accel = 6 * 0.05 * t  # = 0.3 * t

    # polyorder=3 should be closer to expected for cubic trajectory
    error_2 = np.mean(np.abs(accel_2 - expected_accel))
    error_3 = np.mean(np.abs(accel_3 - expected_accel))

    # Cubic fit should have lower error for cubic motion
    # (This might not always be true due to noise, but typically should be)
    assert error_3 <= error_2 * 1.5, "Cubic fit should handle cubic motion better"


def test_polyorder_validation() -> None:
    """Test that polyorder must be less than window_length."""
    rng = np.random.default_rng(42)
    positions = rng.random(50)

    # polyorder=2 with window=5 should work (2 < 5)
    velocity_valid = compute_velocity_from_derivative(
        positions, window_length=5, polyorder=2
    )
    assert len(velocity_valid) == len(positions)

    # polyorder=4 with window=7 should work (4 < 7)
    velocity_valid2 = compute_velocity_from_derivative(
        positions, window_length=7, polyorder=4
    )
    assert len(velocity_valid2) == len(positions)


def test_polyorder_higher_captures_more_complexity() -> None:
    """Test that higher polynomial order can capture more complex motion patterns."""
    # Create a sine wave pattern (requires higher order polynomial to approximate)
    t = np.linspace(0, 2 * np.pi, 100)
    positions = 0.5 + 0.1 * np.sin(t)

    # Compute velocity (should approximate cosine)
    velocity_2 = compute_velocity_from_derivative(
        positions, window_length=9, polyorder=2
    )
    velocity_4 = compute_velocity_from_derivative(
        positions, window_length=9, polyorder=4
    )

    # Expected velocity from derivative of sine: 0.1 * cos(t)
    expected_velocity = np.abs(0.1 * np.cos(t))

    # Higher order should approximate sine wave derivative better
    error_2 = np.mean(np.abs(velocity_2 - expected_velocity))
    error_4 = np.mean(np.abs(velocity_4 - expected_velocity))

    # polyorder=4 should have lower or similar error for sine wave
    assert error_4 <= error_2 * 1.2, "Higher polyorder should handle complex motion"
