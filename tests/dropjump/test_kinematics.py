"""Tests for kinematics calculations."""

import numpy as np
import pytest

from kinemotion.dropjump.analysis import ContactState
from kinemotion.dropjump.kinematics import calculate_drop_jump_metrics


def test_calculate_metrics_basic():
    """Test basic metric calculation with sub-frame interpolation."""
    # Create a simple pattern: ground contact then flight
    contact_states = (
        [ContactState.ON_GROUND] * 10  # 10 frames ground contact
        + [ContactState.IN_AIR] * 20  # 20 frames flight
        + [ContactState.ON_GROUND] * 5  # Landing
    )

    # Simple vertical positions (y increases downward)
    positions = np.array(
        [0.8] * 10 + list(np.linspace(0.8, 0.4, 10)) + list(np.linspace(0.4, 0.8, 10)) + [0.8] * 5
    )

    fps = 30.0

    metrics = calculate_drop_jump_metrics(contact_states, positions, fps)

    # Ground contact time should be approximately 10 frames / 30 fps = 0.333 seconds
    # Sub-frame interpolation may adjust this slightly for precision
    assert metrics.ground_contact_time is not None
    assert 0.25 < metrics.ground_contact_time < 0.40  # Approximately 8-12 frames

    # Flight time: acceleration-based landing detection finds impact earlier
    # than simple phase boundary, typically 13-17 frames instead of 20.
    # Relaxed upper bound to 0.70 to account for cases where refinement
    # might not trigger on synthetic linear data (20 frames = 0.66s).
    assert metrics.flight_time is not None
    assert 0.34 < metrics.flight_time < 0.70

    # Jump height should be calculated from flight time
    assert metrics.jump_height is not None
    assert metrics.jump_height > 0

    # Check fractional frame fields are populated
    assert metrics.contact_start_frame_precise is not None
    assert metrics.contact_end_frame_precise is not None
    assert metrics.flight_start_frame_precise is not None
    assert metrics.flight_end_frame_precise is not None

    # Fractional frames should be reasonably close to integer frames
    # (within 2 frames due to sub-frame interpolation and phase detection)
    if metrics.contact_start_frame is not None:
        diff = abs(metrics.contact_start_frame_precise - metrics.contact_start_frame)
        assert diff < 2.0
    if metrics.flight_start_frame is not None:
        diff = abs(metrics.flight_start_frame_precise - metrics.flight_start_frame)
        assert diff < 2.0


def test_metrics_to_dict():
    """Test conversion to dictionary format with new data/metadata structure."""
    contact_states = [ContactState.ON_GROUND] * 5 + [ContactState.IN_AIR] * 10
    positions = np.array(
        [0.8] * 5 + list(np.linspace(0.8, 0.4, 5)) + list(np.linspace(0.4, 0.8, 5))
    )

    metrics = calculate_drop_jump_metrics(contact_states, positions, 30.0)
    result = metrics.to_dict()

    # Check new structure has data and metadata
    assert "data" in result
    assert "metadata" in result

    # Check all expected data fields are present
    assert "ground_contact_time_ms" in result["data"]
    assert "flight_time_ms" in result["data"]
    assert "jump_height_m" in result["data"]
    assert "contact_start_frame" in result["data"]
    assert "flight_start_frame" in result["data"]

    # Check fractional frame fields are present in data
    assert "contact_start_frame_precise" in result["data"]
    assert "contact_end_frame_precise" in result["data"]
    assert "flight_start_frame_precise" in result["data"]
    assert "flight_end_frame_precise" in result["data"]


def test_calculate_drop_jump_metrics_scaled() -> None:
    """Test drop jump metrics with scaling logic for trajectory height."""
    fps = 100.0

    contact_states = []
    contact_states.extend([ContactState.ON_GROUND] * 50)  # Box
    contact_states.extend([ContactState.IN_AIR] * 25)  # Drop
    contact_states.extend([ContactState.ON_GROUND] * 25)  # Contact
    contact_states.extend([ContactState.IN_AIR] * 50)  # Flight
    contact_states.extend([ContactState.ON_GROUND] * 25)  # Landing

    positions = np.concatenate(
        [
            np.ones(50) * 0.2,  # Box
            np.linspace(0.2, 0.8, 25),  # Drop
            np.ones(25) * 0.8,  # Contact
            # Flight parabola
            0.65 + 0.15 * np.linspace(-1, 1, 50) ** 2,
            np.ones(25) * 0.8,  # Landing
        ]
    )

    drop_start_frame = 50
    expected_height_m = 0.3065625

    metrics = calculate_drop_jump_metrics(
        contact_states,
        positions,
        fps,
        drop_start_frame=drop_start_frame,
        velocity_threshold=0.01,
        smoothing_window=3,
        use_curvature=False,
    )

    assert metrics.jump_height_trajectory_m is not None
    assert metrics.jump_height_trajectory_m == pytest.approx(expected_height_m, abs=0.02)
