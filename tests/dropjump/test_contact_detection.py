"""Tests for contact detection module."""

import numpy as np

from kinemotion.dropjump.analysis import (
    ContactState,
    calculate_adaptive_threshold,
    compute_average_foot_position,
    detect_drop_start,
    detect_ground_contact,
    extract_foot_positions_and_visibilities,
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


def test_compute_average_foot_position():
    """Test average foot position calculation from landmarks."""
    landmarks = {
        "left_ankle": (0.3, 0.8, 0.9),
        "right_ankle": (0.7, 0.8, 0.9),
        "left_heel": (0.3, 0.9, 0.8),
        "right_heel": (0.7, 0.9, 0.8),
    }

    x, y = compute_average_foot_position(landmarks)

    assert 0.4 < x < 0.6  # Average of 0.3 and 0.7
    assert 0.8 < y < 0.9  # Average around 0.85


def test_compute_average_foot_position_partial_visibility():
    """Test average foot position with some low visibility landmarks."""
    landmarks = {
        "left_ankle": (0.3, 0.8, 0.3),  # Low visibility - should be excluded
        "right_ankle": (0.7, 0.8, 0.9),  # Good visibility
        "left_heel": (0.3, 0.9, 0.9),  # Good visibility
        "right_heel": (0.7, 0.9, 0.9),  # Good visibility
    }

    x, y = compute_average_foot_position(landmarks)

    # Should average only visible landmarks (right_ankle, left_heel, right_heel)
    assert x > 0  # Valid position
    assert y > 0  # Valid position


def test_compute_average_foot_position_no_visible_feet():
    """Test fallback when no visible foot landmarks."""
    landmarks = {
        "left_ankle": (0.3, 0.8, 0.1),  # All low visibility
        "right_ankle": (0.7, 0.8, 0.2),
    }

    x, y = compute_average_foot_position(landmarks)

    # Should return default center position
    assert x == 0.5
    assert y == 0.5


def test_extract_foot_positions_and_visibilities():
    """Test extraction of foot positions and visibilities from landmarks."""
    smoothed_landmarks = [
        {
            "left_ankle": (0.3, 0.8, 0.9),
            "right_ankle": (0.7, 0.8, 0.9),
            "left_heel": (0.3, 0.85, 0.8),
            "right_heel": (0.7, 0.85, 0.8),
        },
        {
            "left_ankle": (0.3, 0.7, 0.9),
            "right_ankle": (0.7, 0.7, 0.9),
            "left_heel": (0.3, 0.75, 0.8),
            "right_heel": (0.7, 0.75, 0.8),
        },
        None,  # Missing frame
        {
            "left_ankle": (0.3, 0.8, 0.9),
            "right_ankle": (0.7, 0.8, 0.9),
            "left_heel": (0.3, 0.85, 0.8),
            "right_heel": (0.7, 0.85, 0.8),
        },
    ]

    positions, visibilities = extract_foot_positions_and_visibilities(smoothed_landmarks)

    assert len(positions) == 4
    assert len(visibilities) == 4
    assert 0 < positions[0] < 1  # Valid normalized position
    assert 0 < positions[1] < 1
    assert 0 < visibilities[0] <= 1  # Valid visibility
    assert visibilities[2] == 0.0  # Missing frame should have 0 visibility


def test_calculate_adaptive_threshold_short_array():
    """Test adaptive threshold with very short position array."""
    positions = np.array([0.5])  # Single element

    threshold = calculate_adaptive_threshold(positions, fps=30.0)

    # Should return default fallback threshold
    assert threshold == 0.02


def test_calculate_adaptive_threshold_insufficient_baseline():
    """Test adaptive threshold when baseline period too short."""
    positions = np.array([0.5, 0.51, 0.52])  # Only 3 frames
    fps = 30.0

    threshold = calculate_adaptive_threshold(
        positions, fps=fps, baseline_duration=3.0, smoothing_window=5
    )

    # Should return default threshold due to insufficient data
    assert threshold == 0.02


def test_detect_drop_start_with_debug():
    """Test drop start detection with debug mode enabled."""
    # Create trajectory: unstable start, then stable on box, then drop
    positions = np.concatenate(
        [
            np.random.uniform(0.3, 0.35, 15),  # Unstable stepping onto box
            np.ones(60) * 0.3,  # Stable on box
            np.linspace(0.3, 0.8, 30),  # Drop
        ]
    )
    fps = 30.0

    drop_frame = detect_drop_start(positions, fps, debug=True)

    # Should detect drop after stable period
    assert drop_frame > 15  # After unstable start
    assert drop_frame < 90  # Before end


def test_detect_drop_start_no_stable_period():
    """Test drop start when no stable period is found."""
    # Create noisy trajectory without clear stable period
    positions = np.random.uniform(0.3, 0.5, 50)
    fps = 30.0

    drop_frame = detect_drop_start(positions, fps, debug=True)

    # Should return 0 when no stable period found
    assert drop_frame == 0


def test_detect_drop_start_too_short_video():
    """Test drop start with video too short for analysis."""
    positions = np.ones(20) * 0.3  # Only 20 frames
    fps = 30.0

    drop_frame = detect_drop_start(positions, fps, min_stationary_duration=1.0, debug=True)

    # Should return 0 for too-short video
    assert drop_frame == 0
