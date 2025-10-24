"""Tests for kinematics calculations."""

import numpy as np

from dropjump.contact_detection import ContactState
from dropjump.kinematics import calculate_drop_jump_metrics


def test_calculate_metrics_basic():
    """Test basic metric calculation."""
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

    # Ground contact time should be 10 frames / 30 fps = 0.333 seconds
    assert metrics.ground_contact_time is not None
    assert abs(metrics.ground_contact_time - 10 / 30) < 0.01

    # Flight time should be 20 frames / 30 fps = 0.667 seconds
    assert metrics.flight_time is not None
    assert abs(metrics.flight_time - 20 / 30) < 0.01

    # Jump height should be calculated from flight time
    assert metrics.jump_height is not None
    assert metrics.jump_height > 0


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
