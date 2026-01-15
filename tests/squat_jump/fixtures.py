"""Squat Jump (SJ) specific test fixtures.

This module contains fixtures for testing Squat Jump analysis, providing
sample data for phase detection, kinematics calculations, and validation.
"""

import numpy as np
import pytest

from kinemotion.core.types import FloatArray
from kinemotion.squat_jump.kinematics import SJDataDict, SJMetrics


@pytest.fixture
def sj_sample_positions() -> FloatArray:
    """Create sample SJ trajectory data.

    Returns positions showing:
    - Frames 0-30: Static squat hold (position = 0.6)
    - Frames 30-60: Concentric phase (rising to 0.4)
    - Frames 60-90: Flight phase (falling to 0.2)
    - Frames 90-100: Landing phase (back to 0.6)
    """
    return np.concatenate(
        [
            np.ones(30) * 0.6,  # Squat hold
            np.linspace(0.6, 0.4, 30),  # Concentric (rising)
            np.linspace(0.4, 0.2, 30),  # Flight (falling)
            np.linspace(0.2, 0.6, 10),  # Landing
        ]
    )


@pytest.fixture
def sj_sample_velocities() -> FloatArray:
    """Create sample SJ velocity data corresponding to positions."""
    positions = sj_sample_positions()
    # Simple derivative approximation
    velocities = np.zeros_like(positions)
    velocities[1:] = np.diff(positions)
    return velocities


@pytest.fixture
def sj_phase_frames() -> dict[str, float]:
    """Expected phase frame numbers for sample data."""
    return {
        "squat_hold_start": 0.0,
        "concentric_start": 30.0,
        "takeoff_frame": 60.0,
        "landing_frame": 90.0,
    }


@pytest.fixture
def sj_sample_metrics() -> SJMetrics:
    """Create sample SJ metrics data."""
    return SJMetrics(
        jump_height=0.25,
        flight_time=0.333,
        squat_hold_duration=1.0,
        concentric_duration=1.0,
        peak_concentric_velocity=2.0,
        peak_force=1500.0,
        peak_power=3000.0,
        mean_power=2500.0,
        squat_hold_start_frame=0.0,
        concentric_start_frame=30.0,
        takeoff_frame=60.0,
        landing_frame=90.0,
        mass_kg=75.0,
        tracking_method="foot",
    )


@pytest.fixture
def sj_sample_metrics_dict() -> SJDataDict:
    """Create sample SJ metrics as dictionary."""
    return {
        "jump_height_m": 0.25,
        "flight_time_ms": 333.3,
        "squat_hold_duration_ms": 1000.0,
        "concentric_duration_ms": 1000.0,
        "peak_concentric_velocity_m_s": 2.0,
        "peak_force_n": 1500.0,
        "peak_power_w": 3000.0,
        "mean_power_w": 2500.0,
        "squat_hold_start_frame": 0.0,
        "concentric_start_frame": 30.0,
        "takeoff_frame": 60.0,
        "landing_frame": 90.0,
        "mass_kg": 75.0,
        "tracking_method": "foot",
    }


@pytest.fixture
def sj_invalid_short_hold() -> FloatArray:
    """Create SJ trajectory with very short squat hold."""
    return np.concatenate(
        [
            np.ones(3) * 0.6,  # Very short hold (3 frames = ~100ms, below min threshold)
            np.linspace(0.6, 0.4, 30),  # Concentric
            np.linspace(0.4, 0.2, 30),  # Flight
            np.linspace(0.2, 0.6, 10),  # Landing
        ]
    )


@pytest.fixture
def sj_invalid_no_hold() -> FloatArray:
    """Create SJ trajectory with no squat hold."""
    # Create data with constant motion (no stable periods)
    # Use oscillating pattern to ensure velocity never stays low
    n_frames = 70
    t = np.linspace(0, 4 * np.pi, n_frames)  # Two complete oscillations
    positions = 0.4 + 0.2 * np.sin(t)  # Oscillate between 0.2 and 0.6

    # Add general downward trend then upward to simulate jump
    trend = np.concatenate(
        [
            np.linspace(0.0, -0.3, 50),  # General downward movement
            np.linspace(-0.3, 0.2, 20),  # Upward movement
        ]
    )
    positions = positions + trend

    return np.clip(positions, 0.0, 0.9)  # Keep within reasonable bounds


@pytest.fixture
def sj_shallow_squat() -> FloatArray:
    """Create SJ trajectory with shallow squat angle."""
    return np.concatenate(
        [
            np.ones(30) * 0.8,  # High position (shallow squat)
            np.linspace(0.8, 0.6, 30),  # Concentric
            np.linspace(0.6, 0.4, 30),  # Flight
            np.linspace(0.4, 0.8, 10),  # Landing
        ]
    )


@pytest.fixture
def sj_deep_squat() -> FloatArray:
    """Create SJ trajectory with very deep squat."""
    return np.concatenate(
        [
            np.ones(30) * 0.4,  # Very deep squat
            np.linspace(0.4, 0.2, 30),  # Concentric
            np.linspace(0.2, 0.0, 30),  # Flight
            np.linspace(0.0, 0.4, 10),  # Landing
        ]
    )


@pytest.fixture
def sj_empty_trajectory() -> FloatArray:
    """Create empty trajectory for edge case testing."""
    return np.array([], dtype=np.float64)


@pytest.fixture
def sj_single_frame() -> FloatArray:
    """Create single-frame trajectory for edge case testing."""
    return np.array([0.6])


@pytest.fixture
def sj_video_config() -> dict[str, float]:
    """Create sample video configuration for testing."""
    return {
        "fps": 30.0,
        "squat_hold_threshold": 0.02,
        "velocity_threshold": 0.1,
        "window_length": 5,
        "polyorder": 2,
    }


@pytest.fixture
def test_mass_values() -> list[float | None]:
    """Test mass values for power/force calculations."""
    return [60.0, 75.0, 80.0, 100.0, None]


@pytest.fixture
def sj_athlete_profiles() -> list[str]:
    """List of athlete profiles for validation testing."""
    return ["elderly", "untrained", "recreational", "trained", "elite"]
