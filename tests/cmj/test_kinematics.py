"""Tests for CMJ kinematics calculations."""

import numpy as np
import pytest

from kinemotion.cmj.kinematics import CMJMetrics, calculate_cmj_metrics


def test_calculate_cmj_metrics_basic() -> None:
    """Test basic CMJ metrics calculation."""
    # Create synthetic CMJ trajectory
    # Standing (frames 0-30): position = 0.5
    # Eccentric (frames 30-60): position increases to 0.7 (moving down)
    # Concentric (frames 60-90): position decreases to 0.5 (moving up)
    # Flight (frames 90-120): position decreases further (airborne)
    # Landing (frame 120): back to 0.5

    positions = np.concatenate(
        [
            np.ones(30) * 0.5,  # Standing
            np.linspace(0.5, 0.7, 30),  # Eccentric
            np.linspace(0.7, 0.5, 30),  # Concentric
            np.linspace(0.5, 0.3, 30),  # Flight
            np.ones(10) * 0.5,  # Landing
        ]
    )

    # Create synthetic velocities (derivative of position)
    velocities = np.diff(positions, prepend=positions[0])

    # Phase frames
    standing_start = 30.0  # End of standing
    lowest_point = 60.0  # Transition point
    takeoff = 90.0
    landing = 120.0

    fps = 30.0

    metrics = calculate_cmj_metrics(
        positions,
        velocities,
        standing_start,
        lowest_point,
        takeoff,
        landing,
        fps,
        tracking_method="foot",
    )

    # Verify basic properties
    assert isinstance(metrics, CMJMetrics)
    assert metrics.video_fps == pytest.approx(fps)
    assert metrics.tracking_method == "foot"

    # Verify frames are set correctly
    assert metrics.standing_start_frame == pytest.approx(standing_start)
    assert metrics.lowest_point_frame == pytest.approx(lowest_point)
    assert metrics.takeoff_frame == pytest.approx(takeoff)
    assert metrics.landing_frame == pytest.approx(landing)

    # Verify durations
    assert metrics.flight_time > 0
    assert metrics.eccentric_duration > 0
    assert metrics.concentric_duration > 0
    assert metrics.total_movement_time > 0

    # Verify jump height is positive
    assert metrics.jump_height > 0

    # Verify countermovement depth is positive
    assert metrics.countermovement_depth > 0


def test_cmj_metrics_to_dict() -> None:
    """Test CMJ metrics conversion to dictionary."""
    # Create synthetic metrics
    positions = np.linspace(0.5, 0.3, 100)
    velocities = np.diff(positions, prepend=positions[0])

    metrics = calculate_cmj_metrics(
        positions,
        velocities,
        standing_start_frame=10.0,
        lowest_point_frame=50.0,
        takeoff_frame=75.0,
        landing_frame=90.0,
        fps=30.0,
        tracking_method="foot",
    )

    result_dict = metrics.to_dict()

    # Check new structure
    assert "data" in result_dict
    assert "metadata" in result_dict

    # Verify all expected keys are present in data
    expected_keys = [
        "jump_height_m",
        "flight_time_ms",
        "countermovement_depth_m",
        "eccentric_duration_ms",
        "concentric_duration_ms",
        "total_movement_time_ms",
        "peak_eccentric_velocity_m_s",
        "peak_concentric_velocity_m_s",
        "transition_time_ms",
        "standing_start_frame",
        "lowest_point_frame",
        "takeoff_frame",
        "landing_frame",
        "tracking_method",
    ]

    for key in expected_keys:
        assert key in result_dict["data"], f"Missing key in data: {key}"

    # Verify all numeric values are Python types (not NumPy)
    data = result_dict["data"]
    assert isinstance(data.get("jump_height_m"), float)
    assert isinstance(data.get("flight_time_ms"), float)
    assert isinstance(data.get("tracking_method"), str)


def test_cmj_metrics_without_standing_phase() -> None:
    """Test CMJ metrics calculation when standing phase is not detected."""
    # Create trajectory without clear standing phase
    positions = np.linspace(0.5, 0.3, 100)
    velocities = np.diff(positions, prepend=positions[0])

    metrics = calculate_cmj_metrics(
        positions,
        velocities,
        standing_start_frame=None,  # No standing detected
        lowest_point_frame=50.0,
        takeoff_frame=75.0,
        landing_frame=90.0,
        fps=30.0,
        tracking_method="foot",
    )

    # Verify metrics are still calculated
    assert metrics.standing_start_frame is None
    assert metrics.eccentric_duration > 0
    assert metrics.concentric_duration > 0
    assert metrics.jump_height > 0


def test_cmj_velocity_calculations() -> None:
    """Test that peak velocities are calculated correctly."""
    # Create trajectory with clear velocity profile
    fps = 30.0

    # Create position with distinct eccentric and concentric phases
    # Eccentric: frames 0-45 (downward motion - position increases)
    # Concentric: frames 45-90 (upward motion - position decreases)
    positions_eccentric = np.linspace(0.5, 0.8, 45)  # Downward (position increases)
    positions_concentric = np.linspace(0.8, 0.3, 45)  # Upward (position decreases)
    positions = np.concatenate([positions_eccentric, positions_concentric])

    # Compute velocities using derivative method (matches implementation)
    from kinemotion.core.smoothing import compute_velocity_from_derivative

    velocities = compute_velocity_from_derivative(positions, window_length=5, polyorder=2)

    metrics = calculate_cmj_metrics(
        positions,
        velocities,
        standing_start_frame=0.0,
        lowest_point_frame=45.0,
        takeoff_frame=85.0,
        landing_frame=89.0,
        fps=fps,
        tracking_method="foot",
    )

    # Peak eccentric velocity should be negative (downward) or at least not zero
    # In normalized coordinates, downward motion (increasing y) has positive derivative
    # But we expect the function to capture the motion direction
    assert metrics.eccentric_duration > 0
    assert metrics.concentric_duration > 0

    # Verify velocities are calculated (may need to check signs based on
    # coordinate system)
    assert abs(metrics.peak_eccentric_velocity) > 1e-6
    assert abs(metrics.peak_concentric_velocity) > 1e-6


def test_calculate_cmj_metrics_scaled() -> None:
    """Test CMJ metrics with scaling logic for depth and velocity."""
    fps = 100.0

    # Define phases
    # Standing: 0.5
    standing = np.ones(50) * 0.5

    # Eccentric: 0.5 -> 0.7 (downward, positive velocity)
    eccentric = np.linspace(0.5, 0.7, 51)[:-1]  # 50 frames

    # Concentric: 0.7 -> 0.5 (upward, negative velocity)
    concentric = np.linspace(0.7, 0.5, 26)[:-1]  # 25 frames

    # Flight: 0.5 -> 0.35 -> 0.5 (upward then downward)
    # Parabola centered at 0.5s (25 frames)
    t = np.linspace(-1, 1, 51)
    flight = 0.35 + 0.15 * t**2  # at t=0, 0.35. at t=1, 0.5.

    # Landing
    landing_phase = np.ones(25) * 0.5

    positions = np.concatenate([standing, eccentric, concentric, flight, landing_phase])

    # Compute velocities
    velocities = np.gradient(positions)  # approximate derivative

    # Frames
    standing_start = 50.0
    lowest_point = 100.0
    takeoff = 125.0
    landing = 175.0  # 125 + 50 frames flight

    metrics = calculate_cmj_metrics(
        positions,
        velocities,
        standing_start,
        lowest_point,
        takeoff,
        landing,
        fps,
    )

    # Check scaling logic
    # Flight time = 0.5s
    # Jump height = 9.81 * 0.5^2 / 8 = 0.30656 m
    expected_height = 0.30656
    assert metrics.jump_height == pytest.approx(expected_height, rel=1e-3)

    # Flight displacement (units) = 0.5 - 0.35 = 0.15
    # Scale factor = 0.30656 / 0.15 = 2.0437 m/unit
    scale_factor = expected_height / 0.15

    # Depth (units) = 0.7 - 0.5 = 0.2
    # Expected depth (m) = 0.2 * scale_factor = 0.4087 m
    assert metrics.countermovement_depth == pytest.approx(0.2 * scale_factor, rel=1e-2)
