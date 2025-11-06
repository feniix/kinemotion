"""Tests for kinematics calculations."""

import numpy as np

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
        [0.8] * 10
        + list(np.linspace(0.8, 0.4, 10))
        + list(np.linspace(0.4, 0.8, 10))
        + [0.8] * 5
    )

    fps = 30.0

    metrics = calculate_drop_jump_metrics(contact_states, positions, fps)

    # Ground contact time should be approximately 10 frames / 30 fps = 0.333 seconds
    # Sub-frame interpolation may adjust this slightly for precision
    assert metrics.ground_contact_time is not None
    assert 0.25 < metrics.ground_contact_time < 0.40  # Approximately 8-12 frames

    # Flight time: acceleration-based landing detection finds impact earlier
    # than simple phase boundary, typically 13-17 frames instead of 20
    assert metrics.flight_time is not None
    assert 0.35 < metrics.flight_time < 0.65  # Approximately 10-20 frames

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
    assert abs(metrics.contact_start_frame_precise - metrics.contact_start_frame) < 2.0
    assert abs(metrics.flight_start_frame_precise - metrics.flight_start_frame) < 2.0


def test_metrics_to_dict():
    """Test conversion to dictionary format."""
    contact_states = [ContactState.ON_GROUND] * 5 + [ContactState.IN_AIR] * 10
    positions = np.array(
        [0.8] * 5 + list(np.linspace(0.8, 0.4, 5)) + list(np.linspace(0.4, 0.8, 5))
    )

    metrics = calculate_drop_jump_metrics(contact_states, positions, 30.0)
    result = metrics.to_dict()

    # Check all expected keys are present
    assert "ground_contact_time_ms" in result
    assert "flight_time_ms" in result
    assert "jump_height_m" in result
    assert "contact_start_frame" in result
    assert "flight_start_frame" in result

    # Check fractional frame fields are present
    assert "contact_start_frame_precise" in result
    assert "contact_end_frame_precise" in result
    assert "flight_start_frame_precise" in result
    assert "flight_end_frame_precise" in result
