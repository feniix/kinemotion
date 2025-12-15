"""Tests for pose tracking and center of mass estimation."""

import numpy as np
import pytest

from kinemotion.core.pose import PoseTracker, compute_center_of_mass

pytestmark = [pytest.mark.unit, pytest.mark.core]

# ===== PoseTracker Tests =====


def test_pose_tracker_initialization() -> None:
    """Test PoseTracker initialization with default parameters."""
    tracker = PoseTracker()

    assert tracker.mp_pose is not None
    assert tracker.pose is not None

    tracker.close()


def test_pose_tracker_initialization_with_custom_confidence() -> None:
    """Test PoseTracker initialization with custom confidence thresholds."""
    tracker = PoseTracker(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.6,
    )

    assert tracker.mp_pose is not None
    assert tracker.pose is not None

    tracker.close()


def test_pose_tracker_process_frame_with_no_pose() -> None:
    """Test PoseTracker.process_frame() returns None when no pose detected."""
    tracker = PoseTracker()

    # Create empty black frame (no person)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    result = tracker.process_frame(frame)

    # Should return None when no pose detected
    assert result is None

    tracker.close()


def test_pose_tracker_process_frame_returns_expected_landmarks() -> None:
    """Test PoseTracker.process_frame() returns expected landmark names."""
    tracker = PoseTracker()

    # Create a synthetic frame with simple pattern
    # (MediaPipe might not detect a pose, but we test the interface)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Add a vertical white rectangle to simulate a person
    frame[100:400, 300:340, :] = 255

    result = tracker.process_frame(frame)

    # Result might be None (no pose detected in synthetic frame)
    # or might contain landmarks
    if result is not None:
        # Verify expected landmark names are present
        expected_landmarks = [
            "left_ankle",
            "right_ankle",
            "left_heel",
            "right_heel",
            "left_foot_index",
            "right_foot_index",
            "left_hip",
            "right_hip",
            "left_shoulder",
            "right_shoulder",
            "nose",
            "left_knee",
            "right_knee",
        ]

        for landmark_name in expected_landmarks:
            assert landmark_name in result
            x, y, vis = result[landmark_name]
            # Coordinates should be normalized (0-1)
            assert 0 <= x <= 1
            assert 0 <= y <= 1
            assert 0 <= vis <= 1

    tracker.close()


def test_pose_tracker_close() -> None:
    """Test PoseTracker.close() releases resources."""
    tracker = PoseTracker()

    # Close should not raise an exception
    tracker.close()

    # Note: MediaPipe may raise ValueError on second close
    # This is expected behavior - resources already released


# ===== Center of Mass Tests =====


def test_com_full_body_visible() -> None:
    """Test CoM estimation with all body segments visible."""
    # Create sample landmarks with all segments visible
    landmarks = {
        # Head
        "nose": (0.5, 0.2, 0.9),
        # Shoulders
        "left_shoulder": (0.45, 0.3, 0.95),
        "right_shoulder": (0.55, 0.3, 0.95),
        # Hips
        "left_hip": (0.45, 0.5, 0.95),
        "right_hip": (0.55, 0.5, 0.95),
        # Knees
        "left_knee": (0.45, 0.7, 0.9),
        "right_knee": (0.55, 0.7, 0.9),
        # Ankles
        "left_ankle": (0.45, 0.9, 0.85),
        "right_ankle": (0.55, 0.9, 0.85),
        # Feet
        "left_heel": (0.43, 0.92, 0.8),
        "right_heel": (0.53, 0.92, 0.8),
        "left_foot_index": (0.47, 0.95, 0.75),
        "right_foot_index": (0.57, 0.95, 0.75),
    }

    com_x, com_y, com_vis = compute_center_of_mass(landmarks)

    # CoM should be centered horizontally (x ≈ 0.5)
    assert 0.45 <= com_x <= 0.55, f"CoM x={com_x} should be near center"

    # CoM should be in upper-middle region (trunk is heaviest, 50% of body)
    # Should be between trunk (0.3-0.5) and legs (0.5-0.9)
    # Expected around 0.4-0.5 due to trunk weight dominance
    assert 0.35 <= com_y <= 0.55, f"CoM y={com_y} should be in trunk region"

    # Visibility should be high since all landmarks are visible
    assert com_vis > 0.8, f"CoM visibility={com_vis} should be high"


def test_com_partial_occlusion() -> None:
    """Test CoM estimation with some landmarks occluded."""
    # Create landmarks with feet occluded (low visibility)
    landmarks = {
        "nose": (0.5, 0.2, 0.9),
        "left_shoulder": (0.45, 0.3, 0.95),
        "right_shoulder": (0.55, 0.3, 0.95),
        "left_hip": (0.45, 0.5, 0.95),
        "right_hip": (0.55, 0.5, 0.95),
        "left_knee": (0.45, 0.7, 0.9),
        "right_knee": (0.55, 0.7, 0.9),
        # Feet have low visibility (occluded)
        "left_ankle": (0.45, 0.9, 0.3),  # Below threshold
        "right_ankle": (0.55, 0.9, 0.3),  # Below threshold
        "left_heel": (0.43, 0.92, 0.2),
        "right_heel": (0.53, 0.92, 0.2),
    }

    com_x, com_y, com_vis = compute_center_of_mass(landmarks, visibility_threshold=0.5)

    # Should still compute valid CoM from visible segments
    assert 0.4 <= com_x <= 0.6, f"CoM x={com_x} should be reasonable"
    assert 0.3 <= com_y <= 0.6, f"CoM y={com_y} should be reasonable"

    # Visibility should be lower due to occluded feet
    assert 0.5 <= com_vis <= 0.95, f"CoM visibility={com_vis} should be moderate"


def test_com_hip_fallback() -> None:
    """Test CoM falls back to hip average when no other segments visible."""
    # Only hips visible
    landmarks = {
        "left_hip": (0.4, 0.5, 0.9),
        "right_hip": (0.6, 0.5, 0.9),
        # Everything else has low visibility
        "nose": (0.5, 0.2, 0.3),
        "left_shoulder": (0.45, 0.3, 0.3),
        "right_shoulder": (0.55, 0.3, 0.3),
    }

    com_x, com_y, com_vis = compute_center_of_mass(landmarks, visibility_threshold=0.5)

    # Should fall back to hip average
    assert com_x == pytest.approx(0.5, abs=0.01), "CoM should be hip midpoint x"
    assert com_y == pytest.approx(0.5, abs=0.01), "CoM should be hip midpoint y"
    assert com_vis == pytest.approx(0.9, abs=0.01), "CoM visibility should match hips"


def test_com_no_visible_landmarks() -> None:
    """Test CoM with all landmarks below visibility threshold."""
    landmarks = {
        "nose": (0.5, 0.2, 0.2),
        "left_hip": (0.4, 0.5, 0.3),
        "right_hip": (0.6, 0.5, 0.3),
        "left_ankle": (0.45, 0.9, 0.1),
        "right_ankle": (0.55, 0.9, 0.1),
    }

    com_x, com_y, com_vis = compute_center_of_mass(landmarks, visibility_threshold=0.5)

    # Should return hip fallback position (even with low visibility)
    assert com_x == pytest.approx(0.5, abs=0.01), "CoM should fall back to hip center x"
    assert com_y == pytest.approx(0.5, abs=0.01), "CoM should fall back to hip center y"
    # Visibility will be the average of hip visibilities (0.3)
    assert com_vis == pytest.approx(0.3, abs=0.01), "CoM visibility should be hip average"


def test_com_biomechanical_weights() -> None:
    """Test that CoM respects biomechanical segment weights."""
    # Create landmarks where trunk is higher than legs
    # CoM should be pulled toward trunk due to its 50% weight
    landmarks = {
        # Head at top
        "nose": (0.5, 0.1, 0.9),
        # Trunk segment (shoulders + hips) at 0.3
        "left_shoulder": (0.45, 0.3, 0.95),
        "right_shoulder": (0.55, 0.3, 0.95),
        "left_hip": (0.45, 0.3, 0.95),
        "right_hip": (0.55, 0.3, 0.95),
        # Legs much lower at 0.8
        "left_knee": (0.45, 0.6, 0.9),
        "right_knee": (0.55, 0.6, 0.9),
        "left_ankle": (0.45, 0.8, 0.85),
        "right_ankle": (0.55, 0.8, 0.85),
    }

    _, com_y, _ = compute_center_of_mass(landmarks)

    # CoM should be closer to trunk (0.3) than to ankles (0.8)
    # Due to trunk being 50% of body weight
    trunk_y = 0.3
    ankles_y = 0.8

    # CoM should be much closer to trunk than midpoint (0.55)
    midpoint_y = (trunk_y + ankles_y) / 2
    assert com_y < midpoint_y, f"CoM y={com_y} should be above midpoint {midpoint_y}"
    assert com_y < 0.5, f"CoM y={com_y} should be closer to trunk at {trunk_y}"


def test_com_lateral_asymmetry() -> None:
    """Test CoM with asymmetric lateral position (leaning)."""
    # Create landmarks with body leaning to the left
    landmarks = {
        "nose": (0.4, 0.2, 0.9),
        "left_shoulder": (0.35, 0.3, 0.95),
        "right_shoulder": (0.45, 0.3, 0.95),
        "left_hip": (0.35, 0.5, 0.95),
        "right_hip": (0.45, 0.5, 0.95),
        "left_knee": (0.35, 0.7, 0.9),
        "right_knee": (0.45, 0.7, 0.9),
        "left_ankle": (0.35, 0.9, 0.85),
        "right_ankle": (0.45, 0.9, 0.85),
    }

    com_x, _, _ = compute_center_of_mass(landmarks)

    # CoM should be shifted left (x < 0.5)
    assert com_x < 0.45, f"CoM x={com_x} should be shifted left"
    assert 0.35 <= com_x <= 0.45, f"CoM x={com_x} should be in left region"
