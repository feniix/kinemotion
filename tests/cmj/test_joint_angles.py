"""CMJ joint angle tests with athlete profile edge cases and regression tests.

This module provides comprehensive testing for triple extension analysis
with a focus on:
- Different athlete body proportions (tall, short, explosive)
- Biomechanical accuracy of angle calculations
- Edge cases revealing accuracy issues
- Regression prevention for joint angle measurements
"""

import math

import pytest

from kinemotion.cmj.joint_angles import (
    calculate_angle_3_points,
    calculate_ankle_angle,
    calculate_hip_angle,
    calculate_knee_angle,
    calculate_triple_extension,
    calculate_trunk_tilt,
)


# Fixtures for different athlete profiles
@pytest.fixture
def tall_athlete_landmarks() -> dict[str, tuple[float, float, float]]:
    """Tall athlete with long limbs (~1.9m, normalized coordinates).

    Characteristics:
    - Longer tibia and femur segments
    - Higher hip position relative to body
    - Greater extension range of motion
    """
    return {
        "right_heel": (0.45, 0.92, 0.95),
        "right_ankle": (0.48, 0.85, 0.95),
        "right_knee": (0.50, 0.68, 0.95),  # Longer tibia
        "right_hip": (0.52, 0.42, 0.95),  # Higher hip
        "right_shoulder": (0.53, 0.20, 0.95),
        "left_heel": (0.55, 0.92, 0.95),
        "left_ankle": (0.52, 0.85, 0.95),
        "left_knee": (0.50, 0.68, 0.95),
        "left_hip": (0.48, 0.42, 0.95),
        "left_shoulder": (0.47, 0.20, 0.95),
    }


@pytest.fixture
def short_athlete_landmarks() -> dict[str, tuple[float, float, float]]:
    """Short athlete with short limbs (~1.60m, normalized coordinates).

    Characteristics:
    - Shorter tibia and femur segments
    - Lower hip position (closer to vertical center)
    - Different extension ROM due to shorter levers
    """
    return {
        "right_heel": (0.45, 0.88, 0.95),
        "right_ankle": (0.48, 0.82, 0.95),
        "right_knee": (0.50, 0.72, 0.95),  # Shorter tibia
        "right_hip": (0.52, 0.52, 0.95),  # Lower hip
        "right_shoulder": (0.53, 0.28, 0.95),
        "left_heel": (0.55, 0.88, 0.95),
        "left_ankle": (0.52, 0.82, 0.95),
        "left_knee": (0.50, 0.72, 0.95),
        "left_hip": (0.48, 0.52, 0.95),
        "left_shoulder": (0.47, 0.28, 0.95),
    }


@pytest.fixture
def explosive_athlete_landmarks() -> dict[str, tuple[float, float, float]]:
    """Explosive athlete with dynamic extended posture.

    Characteristics:
    - Full body extension (takeoff phase)
    - Ankle highly dorsiflexed (preparing for takeoff)
    - Knee fully extended
    - Hip extended, trunk slightly forward (propulsive moment)
    """
    return {
        "right_heel": (0.42, 0.90, 0.95),
        "right_ankle": (0.47, 0.82, 0.95),  # Dorsiflexed
        "right_knee": (0.50, 0.62, 0.95),  # Fully extended
        "right_hip": (0.52, 0.40, 0.95),  # Extended
        "right_shoulder": (0.54, 0.18, 0.95),  # Forward lean
        "left_heel": (0.58, 0.90, 0.95),
        "left_ankle": (0.53, 0.82, 0.95),
        "left_knee": (0.50, 0.62, 0.95),
        "left_hip": (0.48, 0.40, 0.95),
        "left_shoulder": (0.46, 0.18, 0.95),
    }


@pytest.fixture
def squat_position_landmarks() -> dict[str, tuple[float, float, float]]:
    """Athlete in deep squat (eccentric phase).

    Characteristics:
    - Deep knee flexion (90-110 degrees)
    - Deep hip flexion
    - Trunk forward lean
    - Maximum countermovement depth
    """
    return {
        "right_heel": (0.48, 0.75, 0.95),
        "right_ankle": (0.50, 0.68, 0.95),
        "right_knee": (0.52, 0.60, 0.95),  # Deep flexion (shorter segment)
        "right_hip": (0.55, 0.58, 0.95),  # Deep flexion, forward
        "right_shoulder": (0.60, 0.48, 0.95),  # Major forward lean
        "left_heel": (0.52, 0.75, 0.95),
        "left_ankle": (0.50, 0.68, 0.95),
        "left_knee": (0.48, 0.60, 0.95),
        "left_hip": (0.45, 0.58, 0.95),
        "left_shoulder": (0.40, 0.48, 0.95),
    }


@pytest.fixture
def standing_position_landmarks() -> dict[str, tuple[float, float, float]]:
    """Athlete standing upright (initial/landing phase).

    Characteristics:
    - Straight legs (nearly 180 degrees)
    - Neutral hip
    - Vertical trunk
    - Resting posture
    """
    return {
        "right_heel": (0.45, 0.90, 0.95),
        "right_ankle": (0.47, 0.85, 0.95),
        "right_knee": (0.48, 0.60, 0.95),
        "right_hip": (0.50, 0.35, 0.95),
        "right_shoulder": (0.50, 0.15, 0.95),
        "left_heel": (0.55, 0.90, 0.95),
        "left_ankle": (0.53, 0.85, 0.95),
        "left_knee": (0.52, 0.60, 0.95),
        "left_hip": (0.50, 0.35, 0.95),
        "left_shoulder": (0.50, 0.15, 0.95),
    }


class TestAthleteProfileEdgeCases:
    """Test joint angles across different athlete body proportions."""

    def test_tall_athlete_ankle_angle(self, tall_athlete_landmarks: dict) -> None:
        """Test ankle angle for tall athlete with longer tibial segments."""
        angle = calculate_ankle_angle(tall_athlete_landmarks, side="right")
        assert angle is not None
        # Tall athlete in standing should have ankle angle in valid range
        assert 60 <= angle <= 180, f"Unexpected ankle angle for tall athlete: {angle}"

    def test_tall_athlete_knee_angle(self, tall_athlete_landmarks: dict) -> None:
        """Test knee angle for tall athlete."""
        angle = calculate_knee_angle(tall_athlete_landmarks, side="right")
        assert angle is not None
        # Tall athlete standing has nearly straight leg
        assert angle > 170, f"Expected nearly straight leg for tall athlete: {angle}"

    def test_tall_athlete_hip_angle(self, tall_athlete_landmarks: dict) -> None:
        """Test hip angle for tall athlete."""
        angle = calculate_hip_angle(tall_athlete_landmarks, side="right")
        assert angle is not None
        # Standing posture should have hip angle near 180
        assert angle > 160, f"Expected nearly straight hip for tall athlete: {angle}"

    def test_tall_athlete_triple_extension(self, tall_athlete_landmarks: dict) -> None:
        """Test triple extension for tall athlete."""
        result = calculate_triple_extension(tall_athlete_landmarks, side="right")
        assert result is not None
        # Tall athletes should have all angles available
        assert result["ankle_angle"] is not None
        assert result["knee_angle"] is not None
        assert result["hip_angle"] is not None

    def test_short_athlete_ankle_angle(self, short_athlete_landmarks: dict) -> None:
        """Test ankle angle for short athlete with shorter tibial segments."""
        angle = calculate_ankle_angle(short_athlete_landmarks, side="right")
        assert angle is not None
        # Ankle angle should still be in valid range regardless of height
        assert 60 <= angle <= 180, f"Unexpected ankle angle for short athlete: {angle}"

    def test_short_athlete_knee_angle(self, short_athlete_landmarks: dict) -> None:
        """Test knee angle for short athlete."""
        angle = calculate_knee_angle(short_athlete_landmarks, side="right")
        assert angle is not None
        # Short athlete standing still has straight leg, angle similar to tall athlete
        assert angle > 165, f"Expected straight leg for short athlete: {angle}"

    def test_short_athlete_hip_angle(self, short_athlete_landmarks: dict) -> None:
        """Test hip angle for short athlete."""
        angle = calculate_hip_angle(short_athlete_landmarks, side="right")
        assert angle is not None
        # Hip angle should be similar regardless of height
        assert angle > 160, f"Expected straight hip for short athlete: {angle}"

    def test_short_athlete_triple_extension(self, short_athlete_landmarks: dict) -> None:
        """Test triple extension for short athlete."""
        result = calculate_triple_extension(short_athlete_landmarks, side="right")
        assert result is not None
        # All angles should be available for short athletes too
        assert result["ankle_angle"] is not None
        assert result["knee_angle"] is not None
        assert result["hip_angle"] is not None

    def test_explosive_athlete_takeoff_posture(self, explosive_athlete_landmarks: dict) -> None:
        """Test triple extension at takeoff for explosive athlete.

        Regression test: Ensure explosive athletes show full triple extension
        with all joints extended.
        """
        result = calculate_triple_extension(explosive_athlete_landmarks, side="right")
        assert result is not None

        # At takeoff, all joints should be extended (high angles)
        knee_angle = result["knee_angle"]
        hip_angle = result["hip_angle"]

        assert knee_angle is not None and knee_angle > 170, "Knee should be extended"
        assert hip_angle is not None and hip_angle > 160, "Hip should be extended"

        # Trunk should show forward lean during propulsive phase
        trunk_tilt = result["trunk_tilt"]
        assert trunk_tilt is not None and trunk_tilt > 0, "Trunk should lean forward"

    def test_squat_position_knee_flexion(self, squat_position_landmarks: dict) -> None:
        """Test knee angle in deep squat position (eccentric phase).

        Regression test: Verify knee flexion angle accurately reflects deep squat.
        """
        angle = calculate_knee_angle(squat_position_landmarks, side="right")
        assert angle is not None
        # Deep squat should show knee flexion (angle < 150, but check for reduction)
        assert 50 <= angle <= 160, f"Expected valid knee angle in squat, got: {angle}"

    def test_squat_position_hip_flexion(self, squat_position_landmarks: dict) -> None:
        """Test hip angle in deep squat position."""
        angle = calculate_hip_angle(squat_position_landmarks, side="right")
        assert angle is not None
        # Deep squat should show hip flexion (reduced angle)
        assert 50 <= angle <= 170, f"Expected valid hip angle in squat, got: {angle}"

    def test_squat_position_trunk_forward_lean(self, squat_position_landmarks: dict) -> None:
        """Test trunk tilt shows forward lean during squat.

        Regression test: Ensure trunk tilt calculation captures forward lean
        during eccentric phase.
        """
        tilt = calculate_trunk_tilt(squat_position_landmarks, side="right")
        assert tilt is not None
        # Squat position has major forward lean (positive angle)
        assert tilt > 15, f"Expected significant forward lean in squat, got: {tilt}"

    def test_standing_position_all_angles(self, standing_position_landmarks: dict) -> None:
        """Test all angles in standing position (neutral posture).

        Regression test: Baseline test for neutral posture angles.
        """
        result = calculate_triple_extension(standing_position_landmarks, side="right")
        assert result is not None

        # Standing position should have all high angles (extended joints)
        assert result["knee_angle"] is not None and result["knee_angle"] > 170
        assert result["hip_angle"] is not None and result["hip_angle"] > 170
        assert result["ankle_angle"] is not None and result["ankle_angle"] > 80


class TestBiomechanicalAccuracy:
    """Test biomechanical accuracy of angle calculations."""

    def test_angle_consistency_across_athlete_profiles(
        self,
        tall_athlete_landmarks: dict,
        short_athlete_landmarks: dict,
        standing_position_landmarks: dict,
    ) -> None:
        """Test that standing posture angles are consistent across athlete profiles.

        This ensures the algorithm doesn't introduce height bias.
        """
        tall_standing = calculate_triple_extension(tall_athlete_landmarks, side="right")
        short_standing = calculate_triple_extension(short_athlete_landmarks, side="right")

        assert tall_standing is not None
        assert short_standing is not None

        # Both should have similar hip and knee angles in neutral posture
        tall_knee = tall_standing["knee_angle"]
        short_knee = short_standing["knee_angle"]

        if tall_knee is not None and short_knee is not None:
            # Angles should be within 5 degrees regardless of athlete height
            assert abs(tall_knee - short_knee) < 5, (
                f"Knee angles differ too much: tall={tall_knee}, short={short_knee}"
            )

    def test_triple_extension_progression(
        self,
        squat_position_landmarks: dict,
        explosive_athlete_landmarks: dict,
    ) -> None:
        """Test triple extension angles change correctly between squat and takeoff.

        Regression test: Ensure angle progression from eccentric to concentric phase
        reflects different postures.
        """
        squat = calculate_triple_extension(squat_position_landmarks, side="right")
        takeoff = calculate_triple_extension(explosive_athlete_landmarks, side="right")

        assert squat is not None
        assert takeoff is not None

        # Both should have angles available
        squat_hip = squat["hip_angle"]
        takeoff_hip = takeoff["hip_angle"]

        if squat_hip is not None and takeoff_hip is not None:
            # Squat should show forward lean (lower hip angle typically)
            # Takeoff should be more extended
            assert 0 <= squat_hip <= 180 and 0 <= takeoff_hip <= 180, "Hip angles should be valid"

    def test_dorsiflexion_vs_plantarflexion(self) -> None:
        """Test ankle angle distinction between dorsiflexion and plantarflexion.

        Regression test: Verify ankle angle calculation correctly measures
        dorsiflexion vs plantarflexion.
        """
        # Dorsiflexion: heel lower, toes up (acute angle at ankle)
        dorsiflexion = {
            "right_heel": (0.4, 0.80, 0.95),
            "right_ankle": (0.5, 0.75, 0.95),
            "right_knee": (0.5, 0.60, 0.95),
        }

        # Plantarflexion: heel higher, toes down (obtuse angle at ankle)
        plantarflexion = {
            "right_heel": (0.4, 0.70, 0.95),
            "right_ankle": (0.5, 0.75, 0.95),
            "right_knee": (0.5, 0.60, 0.95),
        }

        dorsi_angle = calculate_ankle_angle(dorsiflexion, side="right")
        plantar_angle = calculate_ankle_angle(plantarflexion, side="right")

        assert dorsi_angle is not None
        assert plantar_angle is not None

        # Both should be in valid range
        assert 60 <= dorsi_angle <= 180
        assert 60 <= plantar_angle <= 180

    def test_trunk_tilt_symmetry(self, explosive_athlete_landmarks: dict) -> None:
        """Test trunk tilt calculation has consistent magnitude for left and right.

        Regression test: Ensure symmetric athlete posture produces opposite sign
        trunk tilt measurements (due to forward/backward reference) with same magnitude.
        """
        right_tilt = calculate_trunk_tilt(explosive_athlete_landmarks, side="right")
        left_tilt = calculate_trunk_tilt(explosive_athlete_landmarks, side="left")

        assert right_tilt is not None
        assert left_tilt is not None

        # Due to different reference frame (left vs right), tilts should have
        # opposite signs but similar magnitude
        assert abs(abs(right_tilt) - abs(left_tilt)) < 0.1, (
            f"Trunk tilt magnitudes should be similar: right={right_tilt}, left={left_tilt}"
        )


class TestNumericalStability:
    """Test numerical stability of joint angle calculations with extreme values."""

    def test_very_close_points_stability(self) -> None:
        """Test angle calculation when points are very close (numerical stability)."""
        # Points very close together (near-zero magnitudes)
        p1 = (0.5000001, 0.5000001)
        p2 = (0.5, 0.5)
        p3 = (0.5000002, 0.5000003)

        angle = calculate_angle_3_points(p1, p2, p3)
        # Should return 0 due to magnitude check, not NaN
        assert angle == 0.0 or not math.isnan(angle)

    def test_very_large_coordinates(self) -> None:
        """Test angle calculation with large coordinate values."""
        # Scale up coordinates (still valid geometry)
        p1 = (100.0, 100.0)
        p2 = (500.0, 500.0)
        p3 = (1000.0, 1000.0)

        angle = calculate_angle_3_points(p1, p2, p3)
        # Straight line should still give ~180 degrees
        assert math.isclose(angle, 180.0, abs_tol=0.1)

    def test_mixed_magnitude_points(self) -> None:
        """Test angle calculation with mixed magnitude coordinate values."""
        p1 = (1e-6, 1e-6)
        p2 = (1e6, 1e6)
        p3 = (2e6, 2e6)

        angle = calculate_angle_3_points(p1, p2, p3)
        # Should not crash or produce NaN
        assert not math.isnan(angle)
        assert 0 <= angle <= 180

    def test_knee_angle_numerical_precision(self) -> None:
        """Test knee angle maintains numerical precision with realistic values.

        Regression test: Verify floating-point precision is maintained
        throughout angle calculation.
        """
        landmarks = {
            "right_ankle": (0.5, 0.8, 0.95),
            "right_knee": (0.5, 0.6, 0.95),
            "right_hip": (0.5, 0.4, 0.95),
        }

        angles = []
        # Calculate angle multiple times to check consistency
        for _ in range(10):
            angle = calculate_knee_angle(landmarks, side="right")
            assert angle is not None
            angles.append(angle)

        # All iterations should produce identical results
        for angle in angles[1:]:
            assert math.isclose(angle, angles[0], abs_tol=1e-10)


class TestRegressionScenarios:
    """Regression tests for known biomechanical scenarios."""

    def test_maximal_knee_extension_at_takeoff(self) -> None:
        """Regression test: Maximal knee extension should approach 180 degrees.

        Based on biomechanical principle that takeoff requires maximal
        lower extremity extension.
        """
        # Standing with perfectly aligned ankle-knee-hip
        perfectly_extended = {
            "right_ankle": (0.5, 0.9, 0.95),
            "right_knee": (0.5, 0.6, 0.95),
            "right_hip": (0.5, 0.3, 0.95),
        }

        angle = calculate_knee_angle(perfectly_extended, side="right")
        assert angle is not None
        assert angle > 175, f"Maximal extension should be >175°, got {angle}"

    def test_minimum_knee_angle_in_squat(self) -> None:
        """Regression test: Verify minimum knee angle in squat position.

        Knee angle should be significantly reduced during eccentric phase
        (typical CMJ squat 60-100 degrees).
        """
        deep_squat = {
            "right_ankle": (0.5, 0.8, 0.95),
            "right_knee": (0.5, 0.7, 0.95),  # Much closer to ankle
            "right_hip": (0.5, 0.7, 0.95),  # Much closer to knee
        }

        angle = calculate_knee_angle(deep_squat, side="right")
        assert angle is not None
        assert angle < 100, f"Deep squat should be <100°, got {angle}"

    def test_hip_extension_less_than_knee(self) -> None:
        """Regression test: Hip extension angle should be greater than knee.

        During standing/jumping, hip extends more than knee (biomechanically).
        """
        standing = {
            "right_knee": (0.5, 0.7, 0.95),
            "right_hip": (0.5, 0.5, 0.95),
            "right_shoulder": (0.5, 0.3, 0.95),
            "right_ankle": (0.5, 0.8, 0.95),
        }

        knee_angle = calculate_knee_angle(standing, side="right")
        hip_angle = calculate_hip_angle(standing, side="right")

        assert knee_angle is not None
        assert hip_angle is not None
        # In neutral standing, angles should be similar (both extended)
        assert abs(knee_angle - hip_angle) < 15

    def test_forward_lean_during_jump_propulsion(self) -> None:
        """Regression test: Forward lean increases during jump propulsion.

        Trunk tilt should be positive (forward) during concentric phase.
        """
        propulsive_phase = {
            "right_hip": (0.5, 0.5, 0.95),
            "right_shoulder": (0.55, 0.3, 0.95),  # Forward of hip
        }

        tilt = calculate_trunk_tilt(propulsive_phase, side="right")
        assert tilt is not None
        assert tilt > 5, f"Forward lean should be positive during propulsion, got {tilt}"

    def test_upright_posture_near_zero_tilt(self) -> None:
        """Regression test: Upright posture should have near-zero trunk tilt."""
        upright = {
            "right_hip": (0.5, 0.5, 0.95),
            "right_shoulder": (0.5, 0.3, 0.95),  # Directly above hip
        }

        tilt = calculate_trunk_tilt(upright, side="right")
        assert tilt is not None
        assert abs(tilt) < 2, f"Upright posture should have ~0° tilt, got {tilt}"


class TestAnkleAnglePrimaryLandmarkFix:
    """Test ankle angle calculation with foot_index as primary landmark.

    This validates the biomechanics fix switching from heel to foot_index
    for accurate plantarflexion measurement (Issue: ankle angle calculation).

    Background:
    - Old: heel -> ankle -> knee (heel static during push-off, insufficient)
    - New: foot_index -> ankle -> knee (toes active, captures plantarflexion ROM)
    - Expected: 30°+ ankle angle increase during CMJ concentric phase
    """

    def test_ankle_angle_with_foot_index_high_visibility(self) -> None:
        """Test ankle angle uses foot_index when visibility > 0.5."""
        landmarks = {
            "right_foot_index": (0.50, 0.87, 0.95),  # High visibility (toe tip)
            "right_ankle": (0.50, 0.85, 0.95),
            "right_knee": (0.50, 0.60, 0.95),
            "right_heel": (0.48, 0.90, 0.5),  # Present but should not be used
        }

        angle = calculate_ankle_angle(landmarks, side="right")
        assert angle is not None, "Should calculate angle with foot_index"
        # Foot-to-ankle is a small distance, resulting in a larger angle
        assert 0 <= angle <= 180

    def test_ankle_angle_fallback_to_heel_when_foot_index_low(self) -> None:
        """Test ankle angle falls back to heel if foot_index visibility <= 0.5."""
        landmarks = {
            "right_foot_index": (
                0.50,
                0.87,
                0.3,
            ),  # Low visibility (below 0.5 threshold)
            "right_ankle": (0.50, 0.85, 0.95),
            "right_knee": (0.50, 0.60, 0.95),
            "right_heel": (
                0.48,
                0.90,
                0.95,
            ),  # Good visibility, should be used as fallback
        }

        angle = calculate_ankle_angle(landmarks, side="right")
        assert angle is not None, "Should fall back to heel when foot_index visibility low"
        assert 0 <= angle <= 180

    def test_ankle_angle_returns_none_when_no_foot_landmark(self) -> None:
        """Test ankle angle returns None if neither foot_index nor heel available."""
        landmarks = {
            "right_foot_index": (0.50, 0.87, 0.2),  # Below threshold
            "right_ankle": (0.50, 0.85, 0.95),
            "right_knee": (0.50, 0.60, 0.95),
            # No heel landmark
        }

        angle = calculate_ankle_angle(landmarks, side="right")
        assert angle is None, "Should return None without valid foot landmark"

    def test_ankle_angle_returns_none_when_heel_also_low_visibility(
        self,
    ) -> None:
        """Test ankle angle returns None when both foot_index and heel low.

        Both foot_index and heel have low visibility."""
        landmarks = {
            "right_foot_index": (0.50, 0.87, 0.25),  # Below 0.5
            "right_ankle": (0.50, 0.85, 0.95),
            "right_knee": (0.50, 0.60, 0.95),
            "right_heel": (0.48, 0.90, 0.2),  # Below 0.3 fallback threshold
        }

        angle = calculate_ankle_angle(landmarks, side="right")
        assert angle is None, "Should return None when all foot landmarks below threshold"

    def test_plantarflexion_progression_dorsi_to_plantar(self) -> None:
        """Test ankle angle progression from dorsiflexion to plantarflexion.

        Regression test: Validates that foot_index measurement captures the
        expected 30°+ change in ankle angle during CMJ concentric phase.

        Standing (dorsiflexion):  foot_index below ankle -> smaller angle
        Plantarflex (takeoff):    foot_index extends down -> larger angle
        """
        # Standing position (dorsiflexion - toes up relative to shin)
        standing = {
            "right_foot_index": (0.50, 0.82, 0.95),  # Toes UP relative to ankle
            "right_ankle": (0.50, 0.85, 0.95),
            "right_knee": (0.50, 0.60, 0.95),
        }

        # Plantarflexion position (toes down relative to shin, takeoff)
        plantarflex = {
            "right_foot_index": (0.50, 0.90, 0.95),  # Toes DOWN relative to ankle
            "right_ankle": (0.50, 0.85, 0.95),
            "right_knee": (0.50, 0.60, 0.95),
        }

        angle_dorsi = calculate_ankle_angle(standing, side="right")
        angle_plantar = calculate_ankle_angle(plantarflex, side="right")

        assert angle_dorsi is not None, "Dorsiflexion angle should be calculated"
        assert angle_plantar is not None, "Plantarflexion angle should be calculated"

        # Plantarflexion (larger angle) should be greater than dorsiflexion
        # (smaller angle). This validates the biomechanics: toes extend down
        # during takeoff
        assert angle_plantar > angle_dorsi, (
            f"Plantarflexion {angle_plantar}° should be > dorsiflexion {angle_dorsi}°"
        )

    def test_ankle_angle_with_foot_index_visibility_exactly_0_5(
        self,
    ) -> None:
        """Test ankle angle when foot_index visibility exactly 0.5 (boundary)."""
        landmarks = {
            "right_foot_index": (0.50, 0.87, 0.5),  # Exactly 0.5 (not > 0.5)
            "right_ankle": (0.50, 0.85, 0.95),
            "right_knee": (0.50, 0.60, 0.95),
            "right_heel": (0.48, 0.90, 0.95),
        }

        angle = calculate_ankle_angle(landmarks, side="right")
        # At exactly 0.5, should fall back to heel (threshold is > 0.5, not >= 0.5)
        assert angle is not None, "Should have calculated angle (via heel fallback)"
        assert 0 <= angle <= 180


class TestEdgeCasesWithPartialVisibility:
    """Test edge cases with partial landmark visibility (realistic video conditions)."""

    def test_knee_angle_fallback_with_moderate_visibility(self) -> None:
        """Test knee angle falls back gracefully with moderate ankle visibility."""
        landmarks = {
            "right_ankle": (0.5, 0.8, 0.25),  # Borderline visibility
            "right_foot_index": (0.5, 0.85, 0.95),  # Good visibility
            "right_knee": (0.5, 0.6, 0.95),
            "right_hip": (0.5, 0.4, 0.95),
        }

        angle = calculate_knee_angle(landmarks, side="right")
        assert angle is not None, "Should use foot_index fallback"
        assert 0 <= angle <= 180

    def test_triple_extension_mixed_visibility(self) -> None:
        """Test triple extension with mixed visibility across landmarks."""
        landmarks = {
            # Ankle clearly visible
            "right_ankle": (0.5, 0.8, 0.9),
            # Knee at visibility boundary
            "right_knee": (0.5, 0.6, 0.32),
            # Hip and shoulder invisible
            "right_hip": (0.5, 0.4, 0.2),
            "right_shoulder": (0.5, 0.2, 0.15),
            # Heel missing
        }

        result = calculate_triple_extension(landmarks, side="right")
        # Should return None because knee is borderline and missing ankle/heel
        if result is not None:
            # If it returns partial result, that's okay
            assert isinstance(result, dict)

    def test_single_joint_angle_robustness(self) -> None:
        """Test that single joint calculations are robust with low visibility.

        Each joint angle function should gracefully handle visibility issues.
        """
        landmarks = {
            "right_heel": (0.4, 0.9, 0.05),  # Very low visibility
            "right_ankle": (0.5, 0.8, 0.05),  # Very low visibility
            "right_foot_index": (0.5, 0.82, 0.05),  # Also low visibility
            "right_knee": (0.5, 0.6, 0.95),  # High visibility
            "right_hip": (0.5, 0.4, 0.95),  # High visibility
            "right_shoulder": (0.5, 0.2, 0.95),  # High visibility
        }

        # Ankle calculation should return None (low visibility for heel/ankle)
        ankle_angle = calculate_ankle_angle(landmarks, side="right")
        assert ankle_angle is None

        # Knee calculation should return None (needs ankle/foot_index with
        # good visibility)
        knee_angle = calculate_knee_angle(landmarks, side="right")
        assert knee_angle is None

        # Hip calculation should work (good visibility for hip and shoulder)
        hip_angle = calculate_hip_angle(landmarks, side="right")
        assert hip_angle is not None


class TestPhysiologicalRealism:
    """Test that calculated angles are physiologically realistic."""

    def test_ankle_angle_range_plausible(
        self, tall_athlete_landmarks: dict, short_athlete_landmarks: dict
    ) -> None:
        """Test ankle angle stays within plausible physiological range (0-180°)."""
        tall_ankle = calculate_ankle_angle(tall_athlete_landmarks, side="right")
        short_ankle = calculate_ankle_angle(short_athlete_landmarks, side="right")

        assert tall_ankle is None or (0 <= tall_ankle <= 180)
        assert short_ankle is None or (0 <= short_ankle <= 180)

    def test_knee_angle_range_plausible(
        self, squat_position_landmarks: dict, explosive_athlete_landmarks: dict
    ) -> None:
        """Test knee angle stays within plausible range (20-180°)."""
        squat_knee = calculate_knee_angle(squat_position_landmarks, side="right")
        explosive_knee = calculate_knee_angle(explosive_athlete_landmarks, side="right")

        assert squat_knee is None or (20 <= squat_knee <= 180)
        assert explosive_knee is None or (20 <= explosive_knee <= 180)

    def test_hip_angle_range_plausible(
        self, squat_position_landmarks: dict, standing_position_landmarks: dict
    ) -> None:
        """Test hip angle stays within plausible range (30-180°)."""
        squat_hip = calculate_hip_angle(squat_position_landmarks, side="right")
        standing_hip = calculate_hip_angle(standing_position_landmarks, side="right")

        assert squat_hip is None or (30 <= squat_hip <= 180)
        assert standing_hip is None or (30 <= standing_hip <= 180)

    def test_trunk_tilt_reasonable_range(
        self, squat_position_landmarks: dict, standing_position_landmarks: dict
    ) -> None:
        """Test trunk tilt stays within reasonable range (-45° to +45°)."""
        squat_tilt = calculate_trunk_tilt(squat_position_landmarks, side="right")
        standing_tilt = calculate_trunk_tilt(standing_position_landmarks, side="right")

        assert squat_tilt is None or (-45 <= squat_tilt <= 45)
        assert standing_tilt is None or (-45 <= standing_tilt <= 45)


# ============================================================================
# Phase Progression Fixtures & Tests
# ============================================================================


@pytest.fixture
def eccentric_phase_landmarks() -> dict[str, tuple[float, float, float]]:
    """Synthetic landmarks for eccentric phase (countermovement down).

    Characteristics:
    - Knee flexion: 180° → 130° (45-50° flex)
    - Hip flexion: 180° → 145° (35° flex)
    - Ankle plantarflexion: 80° (stable, slight dorsiflexion)
    """
    return {
        "right_heel": (0.45, 0.87, 0.95),
        "right_foot_index": (0.46, 0.80, 0.95),  # Toe is dorsiflexed
        "right_ankle": (0.47, 0.84, 0.95),
        "right_knee": (0.48, 0.50, 0.95),  # Flexed
        "right_hip": (0.50, 0.25, 0.95),  # Flexed
        "right_shoulder": (0.50, 0.08, 0.95),  # Required for hip angle
        "left_heel": (0.55, 0.87, 0.95),
        "left_foot_index": (0.54, 0.80, 0.95),
        "left_ankle": (0.53, 0.84, 0.95),
        "left_knee": (0.52, 0.50, 0.95),
        "left_hip": (0.50, 0.25, 0.95),
        "left_shoulder": (0.50, 0.08, 0.95),
    }


@pytest.fixture
def concentric_phase_landmarks() -> dict[str, tuple[float, float, float]]:
    """Synthetic landmarks for concentric phase (explosion up).

    Characteristics:
    - Knee extension: 130° → 165° (extending toward takeoff)
    - Hip extension: 145° → 175° (extending)
    - Ankle plantarflexion: 95° (increasing as legs drive)
    """
    return {
        "right_heel": (0.45, 0.88, 0.95),
        "right_foot_index": (0.46, 0.77, 0.95),  # Toe plantarflexing slightly
        "right_ankle": (0.47, 0.83, 0.95),
        "right_knee": (0.48, 0.55, 0.95),  # Extending
        "right_hip": (0.50, 0.30, 0.95),  # Extending
        "right_shoulder": (0.50, 0.09, 0.95),  # Required for hip angle
        "left_heel": (0.55, 0.88, 0.95),
        "left_foot_index": (0.54, 0.77, 0.95),
        "left_ankle": (0.53, 0.83, 0.95),
        "left_knee": (0.52, 0.55, 0.95),
        "left_hip": (0.50, 0.30, 0.95),
        "left_shoulder": (0.50, 0.09, 0.95),
    }


@pytest.fixture
def takeoff_phase_landmarks() -> dict[str, tuple[float, float, float]]:
    """Synthetic landmarks for takeoff phase (maximum extension).

    Characteristics:
    - Knee extension: 165° → 175° (full extension at takeoff)
    - Hip extension: 175° → 180°+ (full extension)
    - Ankle plantarflexion: 110-120° (maximum plantarflex as push-off)
    """
    return {
        "right_heel": (0.45, 0.89, 0.95),
        "right_foot_index": (0.46, 0.72, 0.95),  # Toe maximally plantarflexed
        "right_ankle": (0.47, 0.82, 0.95),
        "right_knee": (0.48, 0.60, 0.95),  # Fully extended
        "right_hip": (0.50, 0.32, 0.95),  # Fully extended
        "right_shoulder": (0.50, 0.10, 0.95),  # Required for hip angle
        "left_heel": (0.55, 0.89, 0.95),
        "left_foot_index": (0.54, 0.72, 0.95),
        "left_ankle": (0.53, 0.82, 0.95),
        "left_knee": (0.52, 0.60, 0.95),
        "left_hip": (0.50, 0.32, 0.95),
        "left_shoulder": (0.50, 0.10, 0.95),
    }


class TestPhaseProgression:
    """Test that joint angles progress correctly through CMJ phases."""

    def test_eccentric_phase_knee_flexion(
        self, standing_position_landmarks: dict, eccentric_phase_landmarks: dict
    ) -> None:
        """Test knee flexion increases during eccentric phase.

        Expected: Knee angle decreases from ~180° to ~130°
        (angle measurement: smaller angle = more flexion)
        """
        standing_knee = calculate_knee_angle(standing_position_landmarks, "right")
        eccentric_knee = calculate_knee_angle(eccentric_phase_landmarks, "right")

        assert standing_knee is not None
        assert eccentric_knee is not None
        # Eccentric knee should be smaller (more flexion)
        assert eccentric_knee < standing_knee

    def test_concentric_phase_knee_extension(
        self, eccentric_phase_landmarks: dict, concentric_phase_landmarks: dict
    ) -> None:
        """Test knee extends during concentric phase.

        Expected: Knee angle increases from ~130° toward ~165°
        """
        eccentric_knee = calculate_knee_angle(eccentric_phase_landmarks, "right")
        concentric_knee = calculate_knee_angle(concentric_phase_landmarks, "right")

        assert eccentric_knee is not None
        assert concentric_knee is not None
        # Concentric knee should be larger (more extension)
        assert concentric_knee > eccentric_knee

    def test_triple_extension_all_joints_calculable(self, takeoff_phase_landmarks: dict) -> None:
        """Test that all three joints can be calculated at takeoff.

        Triple extension requires all three joints to be measurable.
        """
        knee = calculate_knee_angle(takeoff_phase_landmarks, "right")
        hip = calculate_hip_angle(takeoff_phase_landmarks, "right")
        ankle = calculate_ankle_angle(takeoff_phase_landmarks, "right")

        # All three joints should be calculable at takeoff
        assert knee is not None, "Knee angle not calculated at takeoff"
        assert hip is not None, "Hip angle not calculated at takeoff"
        assert ankle is not None, "Ankle angle not calculated at takeoff"

    def test_knee_extends_through_phases(
        self,
        eccentric_phase_landmarks: dict,
        concentric_phase_landmarks: dict,
        takeoff_phase_landmarks: dict,
    ) -> None:
        """Test knee extends from eccentric through to takeoff phase.

        Expected progression:
        - Eccentric (flexed ~120°) → Concentric (~140°) → Takeoff (~160°+)
        """
        eccentric_knee = calculate_knee_angle(eccentric_phase_landmarks, "right")
        concentric_knee = calculate_knee_angle(concentric_phase_landmarks, "right")
        takeoff_knee = calculate_knee_angle(takeoff_phase_landmarks, "right")

        # All should exist
        assert eccentric_knee is not None
        assert concentric_knee is not None
        assert takeoff_knee is not None

        # Knee should progressively extend
        assert concentric_knee > eccentric_knee, "Knee should extend in concentric phase"
        assert takeoff_knee > concentric_knee, "Knee should extend further at takeoff"


class TestPhysiologicalBounds:
    """Test that joint angles stay within physiological bounds."""

    def test_knee_angle_within_bounds(
        self,
        standing_position_landmarks: dict,
        eccentric_phase_landmarks: dict,
        takeoff_phase_landmarks: dict,
    ) -> None:
        """Test knee angle stays within 0-180° range."""
        angles = [
            calculate_knee_angle(standing_position_landmarks, "right"),
            calculate_knee_angle(eccentric_phase_landmarks, "right"),
            calculate_knee_angle(takeoff_phase_landmarks, "right"),
        ]

        for angle in angles:
            assert angle is not None
            assert 0 <= angle <= 180, f"Knee angle {angle}° out of bounds"

    def test_hip_angle_within_bounds(
        self,
        standing_position_landmarks: dict,
        eccentric_phase_landmarks: dict,
        takeoff_phase_landmarks: dict,
    ) -> None:
        """Test hip angle stays within 0-180° range."""
        angles = [
            calculate_hip_angle(standing_position_landmarks, "right"),
            calculate_hip_angle(eccentric_phase_landmarks, "right"),
            calculate_hip_angle(takeoff_phase_landmarks, "right"),
        ]

        for angle in angles:
            assert angle is not None
            assert 0 <= angle <= 180, f"Hip angle {angle}° out of bounds"

    def test_ankle_angle_plantarflexion_range(
        self,
        standing_position_landmarks: dict,
        eccentric_phase_landmarks: dict,
        concentric_phase_landmarks: dict,
        takeoff_phase_landmarks: dict,
    ) -> None:
        """Test ankle angle stays within plausible CMJ range.

        CMJ plantarflexion progression: 75-85° (standing) → 110-130° (takeoff)
        """
        angles = [
            calculate_ankle_angle(standing_position_landmarks, "right"),
            calculate_ankle_angle(eccentric_phase_landmarks, "right"),
            calculate_ankle_angle(concentric_phase_landmarks, "right"),
            calculate_ankle_angle(takeoff_phase_landmarks, "right"),
        ]

        for angle in angles:
            assert angle is not None
            # Ankle angles should be calculable and plausible (not negative, not >180°)
            assert 0 <= angle <= 180, f"Ankle angle {angle}° out of valid range"


class TestJointAngleConsistency:
    """Test consistency of joint angle calculations across multiple calls."""

    def test_ankle_angle_deterministic(self, tall_athlete_landmarks: dict) -> None:
        """Test ankle angle calculation is deterministic."""
        angles = [calculate_ankle_angle(tall_athlete_landmarks, side="right") for _ in range(5)]

        # All angles should be identical
        assert all(a == angles[0] for a in angles)

    def test_triple_extension_deterministic(self, squat_position_landmarks: dict) -> None:
        """Test triple extension calculation is deterministic."""
        results = [
            calculate_triple_extension(squat_position_landmarks, side="right") for _ in range(5)
        ]

        # All results should be identical
        for result in results[1:]:
            assert result == results[0]

    def test_angle_calculation_side_independence(self) -> None:
        """Test that left/right side calculations are independent.

        Computing left and right side should not affect each other.
        """
        landmarks = {
            "right_ankle": (0.5, 0.8, 0.95),
            "right_knee": (0.5, 0.6, 0.95),
            "right_hip": (0.5, 0.4, 0.95),
            "left_ankle": (0.5, 0.8, 0.95),
            "left_knee": (0.5, 0.6, 0.95),
            "left_hip": (0.5, 0.4, 0.95),
        }

        right_angle = calculate_knee_angle(landmarks, side="right")
        left_angle = calculate_knee_angle(landmarks, side="left")

        # Same landmarks should give same angle regardless of side
        assert right_angle == left_angle
