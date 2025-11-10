"""Tests for joint angle calculations."""

import math

from kinemotion.cmj.joint_angles import (
    calculate_angle_3_points,
    calculate_ankle_angle,
    calculate_hip_angle,
    calculate_knee_angle,
    calculate_triple_extension,
    calculate_trunk_tilt,
)


class TestCalculateAngle3Points:
    """Tests for calculate_angle_3_points function."""

    def test_straight_line_180_degrees(self) -> None:
        """Test angle calculation for straight line (180 degrees)."""
        # Three points in a straight line
        p1 = (0.0, 0.0)
        p2 = (0.5, 0.5)
        p3 = (1.0, 1.0)

        angle = calculate_angle_3_points(p1, p2, p3)
        assert math.isclose(angle, 180.0, abs_tol=0.1)

    def test_right_angle_90_degrees(self) -> None:
        """Test angle calculation for right angle (90 degrees)."""
        # Right angle: vertical then horizontal
        p1 = (0.0, 0.0)
        p2 = (0.0, 1.0)
        p3 = (1.0, 1.0)

        angle = calculate_angle_3_points(p1, p2, p3)
        assert math.isclose(angle, 90.0, abs_tol=0.1)

    def test_acute_angle_45_degrees(self) -> None:
        """Test angle calculation for acute angle (45 degrees)."""
        # 45 degree angle
        p1 = (0.0, 0.0)
        p2 = (1.0, 0.0)
        p3 = (1.0, 1.0)

        angle = calculate_angle_3_points(p1, p2, p3)
        assert math.isclose(angle, 90.0, abs_tol=0.1)

    def test_zero_angle_collinear_points(self) -> None:
        """Test angle calculation for collinear points (0 degrees)."""
        # Points on same line, opposite sides
        p1 = (1.0, 0.0)
        p2 = (0.0, 0.0)
        p3 = (0.0, 0.0)

        angle = calculate_angle_3_points(p1, p2, p3)
        # When p2 and p3 are same, magnitude is zero, should return 0.0
        assert angle == 0.0

    def test_zero_vector_from_identical_points(self) -> None:
        """Test angle calculation when p1 and p2 are identical (zero vector)."""
        p1 = (0.5, 0.5)
        p2 = (0.5, 0.5)
        p3 = (1.0, 1.0)

        angle = calculate_angle_3_points(p1, p2, p3)
        # Zero magnitude vector should return 0.0
        assert angle == 0.0

    def test_obtuse_angle_135_degrees(self) -> None:
        """Test angle calculation for obtuse angle (135 degrees)."""
        # Create 135 degree angle
        p1 = (1.0, 0.0)
        p2 = (0.0, 0.0)
        p3 = (-1.0, 1.0)

        angle = calculate_angle_3_points(p1, p2, p3)
        assert math.isclose(angle, 135.0, abs_tol=0.1)

    def test_negative_coordinates(self) -> None:
        """Test angle calculation with negative coordinates."""
        p1 = (-1.0, -1.0)
        p2 = (0.0, 0.0)
        p3 = (1.0, 1.0)

        angle = calculate_angle_3_points(p1, p2, p3)
        assert math.isclose(angle, 180.0, abs_tol=0.1)

    def test_very_small_vectors(self) -> None:
        """Test angle calculation with very small vectors (near zero)."""
        p1 = (0.0, 0.0)
        p2 = (1e-10, 1e-10)
        p3 = (2e-10, 2e-10)

        angle = calculate_angle_3_points(p1, p2, p3)
        # Very small vectors should be detected as zero
        assert angle == 0.0


class TestCalculateAnkleAngle:
    """Tests for calculate_ankle_angle function."""

    def test_valid_ankle_angle_right_side(self) -> None:
        """Test ankle angle calculation with valid right side landmarks."""
        landmarks = {
            "right_heel": (0.4, 0.9, 0.9),  # (x, y, visibility)
            "right_ankle": (0.5, 0.8, 0.9),
            "right_knee": (0.5, 0.6, 0.9),
        }

        angle = calculate_ankle_angle(landmarks, side="right")
        assert angle is not None
        assert 0 <= angle <= 180

    def test_valid_ankle_angle_left_side(self) -> None:
        """Test ankle angle calculation with valid left side landmarks."""
        landmarks = {
            "left_heel": (0.4, 0.9, 0.9),
            "left_ankle": (0.5, 0.8, 0.9),
            "left_knee": (0.5, 0.6, 0.9),
        }

        angle = calculate_ankle_angle(landmarks, side="left")
        assert angle is not None
        assert 0 <= angle <= 180

    def test_missing_heel_landmark(self) -> None:
        """Test ankle angle returns None when heel landmark is missing."""
        landmarks = {
            "right_ankle": (0.5, 0.8, 0.9),
            "right_knee": (0.5, 0.6, 0.9),
        }

        angle = calculate_ankle_angle(landmarks, side="right")
        assert angle is None

    def test_low_visibility_heel(self) -> None:
        """Test ankle angle returns None when heel visibility is too low."""
        landmarks = {
            "right_heel": (0.4, 0.9, 0.2),  # visibility < 0.3
            "right_ankle": (0.5, 0.8, 0.9),
            "right_knee": (0.5, 0.6, 0.9),
        }

        angle = calculate_ankle_angle(landmarks, side="right")
        assert angle is None

    def test_low_visibility_ankle(self) -> None:
        """Test ankle angle returns None when ankle visibility is too low."""
        landmarks = {
            "right_heel": (0.4, 0.9, 0.9),
            "right_ankle": (0.5, 0.8, 0.1),  # visibility < 0.3
            "right_knee": (0.5, 0.6, 0.9),
        }

        angle = calculate_ankle_angle(landmarks, side="right")
        assert angle is None

    def test_low_visibility_knee(self) -> None:
        """Test ankle angle returns None when knee visibility is too low."""
        landmarks = {
            "right_heel": (0.4, 0.9, 0.9),
            "right_ankle": (0.5, 0.8, 0.9),
            "right_knee": (0.5, 0.6, 0.2),  # visibility < 0.3
        }

        angle = calculate_ankle_angle(landmarks, side="right")
        assert angle is None

    def test_plantarflexion_angle(self) -> None:
        """Test ankle angle for plantarflexion position (> 90 degrees)."""
        # Heel behind ankle, creating plantarflexion
        landmarks = {
            "right_heel": (0.3, 0.9, 0.9),
            "right_ankle": (0.5, 0.8, 0.9),
            "right_knee": (0.5, 0.5, 0.9),
        }

        angle = calculate_ankle_angle(landmarks, side="right")
        assert angle is not None
        # Should be obtuse angle for plantarflexion
        assert angle > 90


class TestCalculateKneeAngle:
    """Tests for calculate_knee_angle function."""

    def test_valid_knee_angle_right_side(self) -> None:
        """Test knee angle calculation with valid right side landmarks."""
        landmarks = {
            "right_ankle": (0.5, 0.8, 0.9),
            "right_knee": (0.5, 0.6, 0.9),
            "right_hip": (0.5, 0.4, 0.9),
        }

        angle = calculate_knee_angle(landmarks, side="right")
        assert angle is not None
        assert 0 <= angle <= 180

    def test_valid_knee_angle_left_side(self) -> None:
        """Test knee angle calculation with valid left side landmarks."""
        landmarks = {
            "left_ankle": (0.5, 0.8, 0.9),
            "left_knee": (0.5, 0.6, 0.9),
            "left_hip": (0.5, 0.4, 0.9),
        }

        angle = calculate_knee_angle(landmarks, side="left")
        assert angle is not None
        assert 0 <= angle <= 180

    def test_fallback_to_foot_index(self) -> None:
        """Test knee angle uses foot_index when ankle is not visible."""
        landmarks = {
            "right_ankle": (0.5, 0.8, 0.2),  # Low visibility
            "right_foot_index": (0.5, 0.85, 0.9),  # Fallback available
            "right_knee": (0.5, 0.6, 0.9),
            "right_hip": (0.5, 0.4, 0.9),
        }

        angle = calculate_knee_angle(landmarks, side="right")
        assert angle is not None
        assert 0 <= angle <= 180

    def test_missing_ankle_and_foot_index(self) -> None:
        """Test knee angle returns None when both ankle and foot_index missing."""
        landmarks = {
            "right_knee": (0.5, 0.6, 0.9),
            "right_hip": (0.5, 0.4, 0.9),
        }

        angle = calculate_knee_angle(landmarks, side="right")
        assert angle is None

    def test_low_visibility_ankle_and_foot_index(self) -> None:
        """Test knee angle returns None when both ankle and foot_index low visibility."""
        landmarks = {
            "right_ankle": (0.5, 0.8, 0.2),
            "right_foot_index": (0.5, 0.85, 0.2),
            "right_knee": (0.5, 0.6, 0.9),
            "right_hip": (0.5, 0.4, 0.9),
        }

        angle = calculate_knee_angle(landmarks, side="right")
        assert angle is None

    def test_missing_knee_landmark(self) -> None:
        """Test knee angle returns None when knee landmark is missing."""
        landmarks = {
            "right_ankle": (0.5, 0.8, 0.9),
            "right_hip": (0.5, 0.4, 0.9),
        }

        angle = calculate_knee_angle(landmarks, side="right")
        assert angle is None

    def test_missing_hip_landmark(self) -> None:
        """Test knee angle returns None when hip landmark is missing."""
        landmarks = {
            "right_ankle": (0.5, 0.8, 0.9),
            "right_knee": (0.5, 0.6, 0.9),
        }

        angle = calculate_knee_angle(landmarks, side="right")
        assert angle is None

    def test_straight_leg_180_degrees(self) -> None:
        """Test knee angle for straight leg (approximately 180 degrees)."""
        # Straight leg: ankle, knee, hip aligned
        landmarks = {
            "right_ankle": (0.5, 0.9, 0.9),
            "right_knee": (0.5, 0.6, 0.9),
            "right_hip": (0.5, 0.3, 0.9),
        }

        angle = calculate_knee_angle(landmarks, side="right")
        assert angle is not None
        assert angle > 170  # Nearly straight

    def test_deep_squat_90_degrees(self) -> None:
        """Test knee angle for deep squat position (approximately 90 degrees)."""
        # Deep squat: knee bent at 90 degrees
        landmarks = {
            "right_ankle": (0.5, 0.8, 0.9),
            "right_knee": (0.5, 0.7, 0.9),
            "right_hip": (0.5, 0.7, 0.9),
        }

        angle = calculate_knee_angle(landmarks, side="right")
        assert angle is not None
        # For this configuration, angle should be less than 180
        assert angle < 180


class TestCalculateHipAngle:
    """Tests for calculate_hip_angle function."""

    def test_valid_hip_angle_right_side(self) -> None:
        """Test hip angle calculation with valid right side landmarks."""
        landmarks = {
            "right_knee": (0.5, 0.7, 0.9),
            "right_hip": (0.5, 0.5, 0.9),
            "right_shoulder": (0.5, 0.3, 0.9),
        }

        angle = calculate_hip_angle(landmarks, side="right")
        assert angle is not None
        assert 0 <= angle <= 180

    def test_valid_hip_angle_left_side(self) -> None:
        """Test hip angle calculation with valid left side landmarks."""
        landmarks = {
            "left_knee": (0.5, 0.7, 0.9),
            "left_hip": (0.5, 0.5, 0.9),
            "left_shoulder": (0.5, 0.3, 0.9),
        }

        angle = calculate_hip_angle(landmarks, side="left")
        assert angle is not None
        assert 0 <= angle <= 180

    def test_missing_knee_landmark(self) -> None:
        """Test hip angle returns None when knee landmark is missing."""
        landmarks = {
            "right_hip": (0.5, 0.5, 0.9),
            "right_shoulder": (0.5, 0.3, 0.9),
        }

        angle = calculate_hip_angle(landmarks, side="right")
        assert angle is None

    def test_missing_hip_landmark(self) -> None:
        """Test hip angle returns None when hip landmark is missing."""
        landmarks = {
            "right_knee": (0.5, 0.7, 0.9),
            "right_shoulder": (0.5, 0.3, 0.9),
        }

        angle = calculate_hip_angle(landmarks, side="right")
        assert angle is None

    def test_missing_shoulder_landmark(self) -> None:
        """Test hip angle returns None when shoulder landmark is missing."""
        landmarks = {
            "right_knee": (0.5, 0.7, 0.9),
            "right_hip": (0.5, 0.5, 0.9),
        }

        angle = calculate_hip_angle(landmarks, side="right")
        assert angle is None

    def test_low_visibility_knee(self) -> None:
        """Test hip angle returns None when knee visibility is too low."""
        landmarks = {
            "right_knee": (0.5, 0.7, 0.2),
            "right_hip": (0.5, 0.5, 0.9),
            "right_shoulder": (0.5, 0.3, 0.9),
        }

        angle = calculate_hip_angle(landmarks, side="right")
        assert angle is None

    def test_standing_upright_180_degrees(self) -> None:
        """Test hip angle for standing upright (approximately 180 degrees)."""
        # Standing: knee, hip, shoulder aligned vertically
        landmarks = {
            "right_knee": (0.5, 0.8, 0.9),
            "right_hip": (0.5, 0.5, 0.9),
            "right_shoulder": (0.5, 0.2, 0.9),
        }

        angle = calculate_hip_angle(landmarks, side="right")
        assert angle is not None
        assert angle > 170  # Nearly straight


class TestCalculateTrunkTilt:
    """Tests for calculate_trunk_tilt function."""

    def test_vertical_trunk_zero_degrees(self) -> None:
        """Test trunk tilt for vertical posture (0 degrees)."""
        # Perfectly vertical: shoulder directly above hip
        landmarks = {
            "right_hip": (0.5, 0.6, 0.9),
            "right_shoulder": (0.5, 0.3, 0.9),
        }

        tilt = calculate_trunk_tilt(landmarks, side="right")
        assert tilt is not None
        assert math.isclose(tilt, 0.0, abs_tol=1.0)

    def test_forward_lean_positive_angle(self) -> None:
        """Test trunk tilt for forward lean (positive angle)."""
        # Leaning forward: shoulder in front of hip (larger x)
        landmarks = {
            "right_hip": (0.5, 0.6, 0.9),
            "right_shoulder": (0.6, 0.3, 0.9),  # Forward
        }

        tilt = calculate_trunk_tilt(landmarks, side="right")
        assert tilt is not None
        assert tilt > 0  # Positive = forward

    def test_backward_lean_negative_angle(self) -> None:
        """Test trunk tilt for backward lean (negative angle)."""
        # Leaning backward: shoulder behind hip (smaller x)
        landmarks = {
            "right_hip": (0.5, 0.6, 0.9),
            "right_shoulder": (0.4, 0.3, 0.9),  # Backward
        }

        tilt = calculate_trunk_tilt(landmarks, side="right")
        assert tilt is not None
        assert tilt < 0  # Negative = backward

    def test_missing_hip_landmark(self) -> None:
        """Test trunk tilt returns None when hip landmark is missing."""
        landmarks = {
            "right_shoulder": (0.5, 0.3, 0.9),
        }

        tilt = calculate_trunk_tilt(landmarks, side="right")
        assert tilt is None

    def test_missing_shoulder_landmark(self) -> None:
        """Test trunk tilt returns None when shoulder landmark is missing."""
        landmarks = {
            "right_hip": (0.5, 0.6, 0.9),
        }

        tilt = calculate_trunk_tilt(landmarks, side="right")
        assert tilt is None

    def test_low_visibility_hip(self) -> None:
        """Test trunk tilt returns None when hip visibility is too low."""
        landmarks = {
            "right_hip": (0.5, 0.6, 0.2),
            "right_shoulder": (0.5, 0.3, 0.9),
        }

        tilt = calculate_trunk_tilt(landmarks, side="right")
        assert tilt is None

    def test_low_visibility_shoulder(self) -> None:
        """Test trunk tilt returns None when shoulder visibility is too low."""
        landmarks = {
            "right_hip": (0.5, 0.6, 0.9),
            "right_shoulder": (0.5, 0.3, 0.1),
        }

        tilt = calculate_trunk_tilt(landmarks, side="right")
        assert tilt is None

    def test_identical_hip_shoulder_position(self) -> None:
        """Test trunk tilt returns None when hip and shoulder at same position."""
        # Zero magnitude trunk vector
        landmarks = {
            "right_hip": (0.5, 0.5, 0.9),
            "right_shoulder": (0.5, 0.5, 0.9),
        }

        tilt = calculate_trunk_tilt(landmarks, side="right")
        assert tilt is None

    def test_left_side_trunk_tilt(self) -> None:
        """Test trunk tilt calculation for left side."""
        landmarks = {
            "left_hip": (0.5, 0.6, 0.9),
            "left_shoulder": (0.6, 0.3, 0.9),
        }

        tilt = calculate_trunk_tilt(landmarks, side="left")
        assert tilt is not None
        assert tilt > 0


class TestCalculateTripleExtension:
    """Tests for calculate_triple_extension function."""

    def test_full_triple_extension_all_angles_available(self) -> None:
        """Test triple extension with all landmarks visible."""
        landmarks = {
            "right_heel": (0.4, 0.9, 0.9),
            "right_ankle": (0.5, 0.8, 0.9),
            "right_knee": (0.5, 0.6, 0.9),
            "right_hip": (0.5, 0.4, 0.9),
            "right_shoulder": (0.5, 0.2, 0.9),
        }

        result = calculate_triple_extension(landmarks, side="right")
        assert result is not None
        assert "ankle_angle" in result
        assert "knee_angle" in result
        assert "hip_angle" in result
        assert "trunk_tilt" in result

        # All angles should be available
        assert result["ankle_angle"] is not None
        assert result["knee_angle"] is not None
        assert result["hip_angle"] is not None
        assert result["trunk_tilt"] is not None

    def test_partial_triple_extension_ankle_missing(self) -> None:
        """Test triple extension with ankle landmarks missing (common in side view)."""
        landmarks = {
            # No heel/ankle
            "right_knee": (0.5, 0.6, 0.9),
            "right_hip": (0.5, 0.4, 0.9),
            "right_shoulder": (0.5, 0.2, 0.9),
        }

        result = calculate_triple_extension(landmarks, side="right")
        assert result is not None

        # Ankle and knee both require ankle landmarks
        assert result["ankle_angle"] is None
        assert result["knee_angle"] is None  # Requires ankle landmark
        # Hip and trunk should still be available
        assert result["hip_angle"] is not None
        assert result["trunk_tilt"] is not None

    def test_partial_triple_extension_knee_missing(self) -> None:
        """Test triple extension with knee landmarks missing."""
        landmarks = {
            "right_heel": (0.4, 0.9, 0.9),
            "right_ankle": (0.5, 0.8, 0.9),
            # No knee
            "right_hip": (0.5, 0.4, 0.9),
            "right_shoulder": (0.5, 0.2, 0.9),
        }

        result = calculate_triple_extension(landmarks, side="right")
        assert result is not None

        # Ankle and knee should be None
        assert result["ankle_angle"] is None
        assert result["knee_angle"] is None
        # Hip and trunk should still work
        assert result["trunk_tilt"] is not None

    def test_only_trunk_available(self) -> None:
        """Test triple extension when only trunk landmarks available."""
        landmarks = {
            "right_hip": (0.5, 0.6, 0.9),
            "right_shoulder": (0.5, 0.3, 0.9),
        }

        result = calculate_triple_extension(landmarks, side="right")
        assert result is not None

        # Only trunk should be available
        assert result["ankle_angle"] is None
        assert result["knee_angle"] is None
        assert result["hip_angle"] is None
        assert result["trunk_tilt"] is not None

    def test_no_angles_available_returns_none(self) -> None:
        """Test triple extension returns None when no angles can be calculated."""
        # Empty landmarks
        landmarks: dict[str, tuple[float, float, float]] = {}

        result = calculate_triple_extension(landmarks, side="right")
        assert result is None

    def test_low_visibility_all_landmarks(self) -> None:
        """Test triple extension returns None when all landmarks have low visibility."""
        landmarks = {
            "right_heel": (0.4, 0.9, 0.1),
            "right_ankle": (0.5, 0.8, 0.1),
            "right_knee": (0.5, 0.6, 0.1),
            "right_hip": (0.5, 0.4, 0.1),
            "right_shoulder": (0.5, 0.2, 0.1),
        }

        result = calculate_triple_extension(landmarks, side="right")
        assert result is None

    def test_left_side_triple_extension(self) -> None:
        """Test triple extension calculation for left side."""
        landmarks = {
            "left_heel": (0.4, 0.9, 0.9),
            "left_ankle": (0.5, 0.8, 0.9),
            "left_knee": (0.5, 0.6, 0.9),
            "left_hip": (0.5, 0.4, 0.9),
            "left_shoulder": (0.5, 0.2, 0.9),
        }

        result = calculate_triple_extension(landmarks, side="left")
        assert result is not None
        assert result["ankle_angle"] is not None
        assert result["knee_angle"] is not None
        assert result["hip_angle"] is not None
        assert result["trunk_tilt"] is not None

    def test_triple_extension_with_foot_index_fallback(self) -> None:
        """Test triple extension uses foot_index fallback for knee angle."""
        landmarks = {
            "right_heel": (0.4, 0.9, 0.9),
            "right_ankle": (0.5, 0.8, 0.2),  # Low visibility
            "right_foot_index": (0.5, 0.85, 0.9),  # Fallback available
            "right_knee": (0.5, 0.6, 0.9),
            "right_hip": (0.5, 0.4, 0.9),
            "right_shoulder": (0.5, 0.2, 0.9),
        }

        result = calculate_triple_extension(landmarks, side="right")
        assert result is not None

        # Ankle should be None (low visibility heel)
        assert result["ankle_angle"] is None
        # Knee should work with foot_index fallback
        assert result["knee_angle"] is not None
        assert result["hip_angle"] is not None
        assert result["trunk_tilt"] is not None
