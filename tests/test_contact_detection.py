"""Tests for contact detection module."""

import numpy as np

from dropjump.contact_detection import (
    ContactState,
    detect_ground_contact,
    find_contact_phases,
)


def test_detect_ground_contact_simple():
    """Test basic ground contact detection with stationary feet."""
    # Create simple trajectory: on ground, jump, land
    positions = np.array([0.8, 0.8, 0.8, 0.7, 0.6, 0.5, 0.6, 0.7, 0.8, 0.8, 0.8])
    visibilities = np.ones(len(positions))

    states = detect_ground_contact(
        positions,
        velocity_threshold=0.05,
        min_contact_frames=2,
        visibilities=visibilities,
    )

    # First few frames should be on ground
    assert states[0] == ContactState.ON_GROUND
    assert states[1] == ContactState.ON_GROUND

    # Middle frames (during jump) should be in air
    assert ContactState.IN_AIR in states[3:8]

    # Last few frames should be on ground again
    assert states[-1] == ContactState.ON_GROUND


def test_find_contact_phases():
    """Test phase identification from contact states."""
    states = [
        ContactState.ON_GROUND,
        ContactState.ON_GROUND,
        ContactState.IN_AIR,
        ContactState.IN_AIR,
        ContactState.IN_AIR,
        ContactState.ON_GROUND,
        ContactState.ON_GROUND,
    ]

    phases = find_contact_phases(states)

    assert len(phases) == 3
    assert phases[0] == (0, 1, ContactState.ON_GROUND)
    assert phases[1] == (2, 4, ContactState.IN_AIR)
    assert phases[2] == (5, 6, ContactState.ON_GROUND)


def test_visibility_filtering():
    """Test that low visibility landmarks are ignored."""
    positions = np.array([0.8, 0.8, 0.8, 0.8, 0.8])
    visibilities = np.array([0.9, 0.9, 0.1, 0.9, 0.9])  # Middle frame low visibility

    states = detect_ground_contact(
        positions,
        velocity_threshold=0.05,
        min_contact_frames=1,
        visibility_threshold=0.5,
        visibilities=visibilities,
    )

    # Middle frame should be unknown due to low visibility
    assert states[2] == ContactState.UNKNOWN
