"""Tests for CMJ physiological bounds and validation.

Comprehensive test suite validating that metrics fall within realistic
physiological bounds for different athlete profiles.
"""

from typing import cast

from kinemotion.cmj.metrics_validator import (
    CMJMetricsValidator,
)
from kinemotion.cmj.validation_bounds import (
    ATHLETE_PROFILES,
    CMJBounds,
    MetricConsistency,
    RSIBounds,
    TripleExtensionBounds,
    estimate_athlete_profile,
)
from kinemotion.core.validation import (
    AthleteProfile,
    ValidationSeverity,
)


class TestAthleteProfileEstimation:
    """Test athlete profile estimation from jump height."""

    def test_estimate_elderly_profile(self) -> None:
        """Low jump height should estimate elderly profile."""
        metrics = {"jump_height": 0.12}
        profile = estimate_athlete_profile(metrics)
        assert profile == AthleteProfile.ELDERLY

    def test_estimate_untrained_profile(self) -> None:
        """25cm jump should estimate untrained."""
        metrics = {"jump_height": 0.25}
        profile = estimate_athlete_profile(metrics)
        assert profile == AthleteProfile.UNTRAINED

    def test_estimate_recreational_profile(self) -> None:
        """45cm jump should estimate recreational."""
        metrics = {"jump_height": 0.45}
        profile = estimate_athlete_profile(metrics)
        assert profile == AthleteProfile.RECREATIONAL

    def test_estimate_trained_profile(self) -> None:
        """75cm jump should estimate trained."""
        metrics = {"jump_height": 0.75}
        profile = estimate_athlete_profile(metrics)
        assert profile == AthleteProfile.TRAINED

    def test_estimate_elite_profile(self) -> None:
        """90cm jump should estimate elite."""
        metrics = {"jump_height": 0.90}
        profile = estimate_athlete_profile(metrics)
        assert profile == AthleteProfile.ELITE


class TestFlightTimeBounds:
    """Test flight time bounds validation."""

    def test_flight_time_minimum_physically_possible(self) -> None:
        """Flight time above minimum should be valid."""
        bounds = CMJBounds.FLIGHT_TIME
        assert bounds.is_physically_possible(0.15)

    def test_flight_time_maximum_physically_possible(self) -> None:
        """Flight time below maximum should be valid."""
        bounds = CMJBounds.FLIGHT_TIME
        assert bounds.is_physically_possible(1.0)

    def test_flight_time_below_absolute_minimum_fails(self) -> None:
        """Flight time below absolute minimum should fail."""
        bounds = CMJBounds.FLIGHT_TIME
        assert not bounds.is_physically_possible(0.05)

    def test_flight_time_above_absolute_maximum_fails(self) -> None:
        """Flight time above absolute maximum should fail."""
        bounds = CMJBounds.FLIGHT_TIME
        assert not bounds.is_physically_possible(1.5)

    def test_flight_time_recreational_range(self) -> None:
        """Flight time should be in recreational range for recreational athlete."""
        bounds = CMJBounds.FLIGHT_TIME
        assert bounds.contains(0.50, AthleteProfile.RECREATIONAL)

    def test_flight_time_elite_range(self) -> None:
        """Flight time should be in elite range for elite athlete."""
        bounds = CMJBounds.FLIGHT_TIME
        assert bounds.contains(0.80, AthleteProfile.ELITE)


class TestJumpHeightBounds:
    """Test jump height bounds validation."""

    def test_jump_height_minimum_physically_possible(self) -> None:
        """Jump height above minimum should be valid."""
        bounds = CMJBounds.JUMP_HEIGHT
        assert bounds.is_physically_possible(0.10)

    def test_jump_height_maximum_physically_possible(self) -> None:
        """Jump height below maximum should be valid."""
        bounds = CMJBounds.JUMP_HEIGHT
        assert bounds.is_physically_possible(1.0)

    def test_jump_height_below_absolute_minimum_fails(self) -> None:
        """Jump height below absolute minimum should fail."""
        bounds = CMJBounds.JUMP_HEIGHT
        assert not bounds.is_physically_possible(0.01)

    def test_jump_height_above_absolute_maximum_fails(self) -> None:
        """Jump height above absolute maximum should fail."""
        bounds = CMJBounds.JUMP_HEIGHT
        assert not bounds.is_physically_possible(1.5)


class TestCountermovementDepthBounds:
    """Test countermovement depth bounds."""

    def test_depth_minimum_physically_possible(self) -> None:
        """Depth above minimum should be valid."""
        bounds = CMJBounds.COUNTERMOVEMENT_DEPTH
        assert bounds.is_physically_possible(0.15)

    def test_depth_maximum_physically_possible(self) -> None:
        """Depth below maximum should be valid."""
        bounds = CMJBounds.COUNTERMOVEMENT_DEPTH
        assert bounds.is_physically_possible(0.80)

    def test_depth_below_absolute_minimum_fails(self) -> None:
        """Depth below absolute minimum should fail."""
        bounds = CMJBounds.COUNTERMOVEMENT_DEPTH
        assert not bounds.is_physically_possible(0.03)

    def test_depth_above_absolute_maximum_fails(self) -> None:
        """Depth above absolute maximum should fail."""
        bounds = CMJBounds.COUNTERMOVEMENT_DEPTH
        assert not bounds.is_physically_possible(1.2)

    def test_depth_elderly_range(self) -> None:
        """Depth should be shallow for elderly athlete."""
        bounds = CMJBounds.COUNTERMOVEMENT_DEPTH
        assert bounds.contains(0.15, AthleteProfile.ELDERLY)

    def test_depth_elite_range(self) -> None:
        """Depth should be deep for elite athlete."""
        bounds = CMJBounds.COUNTERMOVEMENT_DEPTH
        assert bounds.contains(0.55, AthleteProfile.ELITE)


class TestContactTimeBounds:
    """Test concentric duration (contact time) bounds."""

    def test_contact_time_minimum_physically_possible(self) -> None:
        """Contact time above minimum should be valid."""
        bounds = CMJBounds.CONCENTRIC_DURATION
        assert bounds.is_physically_possible(0.15)

    def test_contact_time_maximum_physically_possible(self) -> None:
        """Contact time below maximum should be valid."""
        bounds = CMJBounds.CONCENTRIC_DURATION
        assert bounds.is_physically_possible(1.5)

    def test_contact_time_below_absolute_minimum_fails(self) -> None:
        """Contact time below absolute minimum should fail."""
        bounds = CMJBounds.CONCENTRIC_DURATION
        assert not bounds.is_physically_possible(0.05)

    def test_contact_time_above_absolute_maximum_fails(self) -> None:
        """Contact time above absolute maximum should fail."""
        bounds = CMJBounds.CONCENTRIC_DURATION
        assert not bounds.is_physically_possible(2.0)

    def test_contact_time_elite_faster_than_recreational(self) -> None:
        """Elite athletes typically have shorter contact time than recreational."""
        elite_mid = (
            CMJBounds.CONCENTRIC_DURATION.elite_min + CMJBounds.CONCENTRIC_DURATION.elite_max
        ) / 2
        recreational_mid = (
            CMJBounds.CONCENTRIC_DURATION.recreational_min
            + CMJBounds.CONCENTRIC_DURATION.recreational_max
        ) / 2
        assert elite_mid < recreational_mid


class TestPeakVelocityBounds:
    """Test peak velocity bounds."""

    def test_eccentric_velocity_minimum_physically_possible(self) -> None:
        """Eccentric velocity above minimum should be valid."""
        bounds = CMJBounds.PEAK_ECCENTRIC_VELOCITY
        assert bounds.is_physically_possible(0.20)

    def test_eccentric_velocity_maximum_physically_possible(self) -> None:
        """Eccentric velocity below maximum should be valid."""
        bounds = CMJBounds.PEAK_ECCENTRIC_VELOCITY
        assert bounds.is_physically_possible(4.0)

    def test_concentric_velocity_minimum_physically_possible(self) -> None:
        """Concentric velocity above minimum should be valid."""
        bounds = CMJBounds.PEAK_CONCENTRIC_VELOCITY
        assert bounds.is_physically_possible(1.0)

    def test_concentric_velocity_maximum_physically_possible(self) -> None:
        """Concentric velocity below maximum should be valid."""
        bounds = CMJBounds.PEAK_CONCENTRIC_VELOCITY
        assert bounds.is_physically_possible(4.5)

    def test_concentric_velocity_below_absolute_minimum_fails(self) -> None:
        """Concentric velocity below 0.3 m/s cannot leave ground."""
        bounds = CMJBounds.PEAK_CONCENTRIC_VELOCITY
        assert not bounds.is_physically_possible(0.2)

    def test_concentric_velocity_above_absolute_maximum_fails(self) -> None:
        """Concentric velocity above 5.0 m/s exceeds elite capability."""
        bounds = CMJBounds.PEAK_CONCENTRIC_VELOCITY
        assert not bounds.is_physically_possible(5.5)


class TestRSIBounds:
    """Test Reactive Strength Index bounds."""

    def test_rsi_minimum_valid(self) -> None:
        """RSI at minimum should be valid."""
        assert RSIBounds.is_valid(0.30)

    def test_rsi_maximum_valid(self) -> None:
        """RSI at maximum should be valid."""
        assert RSIBounds.is_valid(4.0)

    def test_rsi_below_minimum_invalid(self) -> None:
        """RSI below minimum should be invalid."""
        assert not RSIBounds.is_valid(0.2)

    def test_rsi_above_maximum_invalid(self) -> None:
        """RSI above maximum should be invalid."""
        assert not RSIBounds.is_valid(4.5)

    def test_rsi_elderly_range(self) -> None:
        """Elderly athlete RSI should be low."""
        rsi_min, rsi_max = RSIBounds.get_rsi_range(AthleteProfile.ELDERLY)
        assert rsi_min < rsi_max < RSIBounds.RECREATIONAL_RANGE[0]

    def test_rsi_elite_range(self) -> None:
        """Elite athlete RSI should be high."""
        rsi_min, _ = RSIBounds.get_rsi_range(AthleteProfile.ELITE)
        assert rsi_min > RSIBounds.RECREATIONAL_RANGE[1]


class TestTripleExtensionBounds:
    """Test triple extension angle bounds."""

    def test_hip_angle_full_extension_valid(self) -> None:
        """Hip angle near 180° should be valid for all profiles."""
        assert TripleExtensionBounds.hip_angle_valid(175, AthleteProfile.ELDERLY)
        assert TripleExtensionBounds.hip_angle_valid(180, AthleteProfile.RECREATIONAL)
        assert TripleExtensionBounds.hip_angle_valid(182, AthleteProfile.ELITE)

    def test_hip_angle_incomplete_extension_weak(self) -> None:
        """Hip angle 150° is acceptable for elderly but not elite."""
        assert TripleExtensionBounds.hip_angle_valid(150, AthleteProfile.ELDERLY)
        assert not TripleExtensionBounds.hip_angle_valid(150, AthleteProfile.ELITE)

    def test_hip_angle_out_of_bounds_fails(self) -> None:
        """Hip angle <120° indicates wrong phase."""
        assert not TripleExtensionBounds.hip_angle_valid(100, AthleteProfile.RECREATIONAL)

    def test_knee_angle_full_extension_valid(self) -> None:
        """Knee angle near 180° should be valid."""
        assert TripleExtensionBounds.knee_angle_valid(175, AthleteProfile.RECREATIONAL)
        assert TripleExtensionBounds.knee_angle_valid(185, AthleteProfile.ELITE)

    def test_ankle_angle_plantarflexion_valid(self) -> None:
        """Ankle angle 120-150° should be valid."""
        assert TripleExtensionBounds.ankle_angle_valid(130, AthleteProfile.RECREATIONAL)
        assert TripleExtensionBounds.ankle_angle_valid(140, AthleteProfile.ELITE)

    def test_ankle_angle_dorsiflexion_invalid(self) -> None:
        """Ankle angle <90° indicates dorsiflexion, wrong phase."""
        assert not TripleExtensionBounds.ankle_angle_valid(80, AthleteProfile.RECREATIONAL)


class TestMetricsConsistency:
    """Test cross-metric consistency validation."""

    def test_flight_time_height_consistency_perfect(self) -> None:
        """0.60s flight time should give ~0.45m jump height."""
        flight_time = 0.60
        expected_height = (9.81 * flight_time**2) / 8
        assert 0.43 < expected_height < 0.47

    def test_velocity_height_consistency_perfect(self) -> None:
        """2.9 m/s velocity should give ~0.43m jump height."""
        velocity = 2.9
        expected_height = velocity**2 / (2 * 9.81)
        assert 0.41 < expected_height < 0.45

    def test_depth_height_ratio_normal(self) -> None:
        """Normal depth-to-height ratio should be 0.7-1.2."""
        depth = 0.40
        height = 0.45
        ratio = height / depth
        assert (
            MetricConsistency.DEPTH_HEIGHT_RATIO_MIN
            < ratio
            < MetricConsistency.DEPTH_HEIGHT_RATIO_MAX
        )

    def test_depth_height_ratio_too_shallow_warning(self) -> None:
        """Depth only 25% of height suggests incomplete squat."""
        depth = 0.10
        height = 0.45
        ratio = height / depth
        assert ratio > MetricConsistency.DEPTH_HEIGHT_RATIO_MAX


class TestRecreationalAthleteProfile:
    """Integration tests for recreational athlete profile."""

    def test_recreational_athlete_all_metrics_valid(self) -> None:
        """All metrics for recreational athlete should pass validation."""
        metrics = {
            "jump_height": 0.45,
            "flight_time": 0.60,
            "countermovement_depth": 0.35,
            "concentric_duration": 0.55,
            "eccentric_duration": 0.50,
            "peak_eccentric_velocity": 1.5,
            "peak_concentric_velocity": 2.9,
        }

        validator = CMJMetricsValidator(assumed_profile=AthleteProfile.RECREATIONAL)
        result = validator.validate(metrics)

        # Should have info/warning issues but not errors
        errors = [issue for issue in result.issues if issue.severity == ValidationSeverity.ERROR]
        assert len(errors) == 0

    def test_recreational_rsi_in_expected_range(self) -> None:
        """RSI for recreational athlete should be 0.8-1.5."""
        flight_time = 0.60
        contact_time = 0.55
        rsi = flight_time / contact_time
        rsi_min, rsi_max = RSIBounds.get_rsi_range(AthleteProfile.RECREATIONAL)
        assert rsi_min <= rsi <= rsi_max


class TestEliteAthleteProfile:
    """Integration tests for elite athlete profile."""

    def test_elite_athlete_all_metrics_valid(self) -> None:
        """All metrics for elite athlete should pass validation."""
        profile = ATHLETE_PROFILES["elite_male"]

        metrics = {
            "jump_height": 0.78,
            "flight_time": 0.79,
            "countermovement_depth": 0.52,
            "concentric_duration": 0.35,
            "eccentric_duration": 0.48,
            "peak_eccentric_velocity": 2.8,
            "peak_concentric_velocity": 3.9,
        }

        validator = CMJMetricsValidator(assumed_profile=cast(AthleteProfile, profile["profile"]))
        result = validator.validate(metrics)

        errors = [issue for issue in result.issues if issue.severity == ValidationSeverity.ERROR]
        assert len(errors) == 0

    def test_elite_rsi_in_expected_range(self) -> None:
        """RSI for elite athlete should be 1.85-2.80."""
        flight_time = 0.80
        contact_time = 0.33
        rsi = flight_time / contact_time
        rsi_min, rsi_max = RSIBounds.get_rsi_range(AthleteProfile.ELITE)
        assert rsi_min <= rsi <= rsi_max

    def test_elite_contact_time_faster_than_recreational(self) -> None:
        """Elite athlete contact time should be noticeably shorter."""
        elite_contact = 0.35
        recreational_contact = 0.55
        assert elite_contact < recreational_contact


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_minimal_countermovement_jump(self) -> None:
        """Minimal squat CMJ should still be valid if internally consistent."""
        metrics = {
            "jump_height": 0.25,
            "flight_time": 0.45,
            "countermovement_depth": 0.12,  # Very shallow
            "concentric_duration": 0.30,
            "eccentric_duration": 0.25,
            "peak_eccentric_velocity": 0.6,
            "peak_concentric_velocity": 2.2,
        }

        validator = CMJMetricsValidator()
        result = validator.validate(metrics)
        # Should have warnings but not errors
        errors = [issue for issue in result.issues if issue.severity == ValidationSeverity.ERROR]
        assert len(errors) == 0

    def test_very_deep_squat(self) -> None:
        """Deep squat from tall athlete should be valid."""
        metrics = {
            "jump_height": 0.72,
            "flight_time": 0.77,
            "countermovement_depth": 0.65,  # Very deep
            "concentric_duration": 0.50,
            "eccentric_duration": 0.65,
            "peak_eccentric_velocity": 3.2,
            "peak_concentric_velocity": 3.8,
        }

        validator = CMJMetricsValidator()
        result = validator.validate(metrics)
        errors = [issue for issue in result.issues if issue.severity == ValidationSeverity.ERROR]
        assert len(errors) == 0

    def test_error_detected_contact_time_too_short(self) -> None:
        """Contact time <0.08s should flag as error."""
        metrics = {
            "jump_height": 0.50,
            "flight_time": 0.63,
            "countermovement_depth": 0.35,
            "concentric_duration": 0.06,  # TOO SHORT
            "eccentric_duration": 0.40,
            "peak_eccentric_velocity": 1.5,
            "peak_concentric_velocity": 3.1,
        }

        validator = CMJMetricsValidator()
        result = validator.validate(metrics)
        errors = [
            issue
            for issue in result.issues
            if issue.severity == ValidationSeverity.ERROR and "concentric_duration" in issue.metric
        ]
        assert len(errors) > 0

    def test_error_detected_rsi_too_high(self) -> None:
        """RSI >4.0 should flag as error."""
        metrics = {
            "jump_height": 0.60,
            "flight_time": 0.78,
            "countermovement_depth": 0.40,
            "concentric_duration": 0.15,  # Very short
            "eccentric_duration": 0.40,
            "peak_eccentric_velocity": 2.0,
            "peak_concentric_velocity": 3.4,
        }

        validator = CMJMetricsValidator()
        result = validator.validate(metrics)
        # RSI = 0.78 / 0.15 = 5.2 (too high)
        rsi_errors = [
            issue
            for issue in result.issues
            if issue.severity == ValidationSeverity.ERROR and "rsi" in issue.metric
        ]
        assert len(rsi_errors) > 0


class TestValidationSeverityLevels:
    """Test that validation correctly assigns severity levels."""

    def test_error_severity_assigned_correctly(self) -> None:
        """Physically impossible metrics should be errors."""
        metrics = {
            "jump_height": 2.0,  # Impossibly high
            "flight_time": 2.0,
            "countermovement_depth": 0.40,
            "concentric_duration": 0.50,
            "eccentric_duration": 0.50,
            "peak_eccentric_velocity": 1.5,
            "peak_concentric_velocity": 6.0,  # Impossibly high
        }

        validator = CMJMetricsValidator()
        result = validator.validate(metrics)
        errors = [issue for issue in result.issues if issue.severity == ValidationSeverity.ERROR]
        assert len(errors) > 0

    def test_warning_severity_for_unusual_but_possible(self) -> None:
        """Unusual but physically possible should be warnings."""
        metrics = {
            "jump_height": 0.95,  # Elite range
            "flight_time": 0.88,
            "countermovement_depth": 0.25,  # Shallow for this height
            "concentric_duration": 0.40,
            "eccentric_duration": 0.35,
            "peak_eccentric_velocity": 2.0,
            "peak_concentric_velocity": 4.3,
        }

        validator = CMJMetricsValidator()
        result = validator.validate(metrics)
        # Should have warnings about unusual patterns
        warnings = [
            issue for issue in result.issues if issue.severity == ValidationSeverity.WARNING
        ]
        assert len(warnings) > 0

    def test_info_severity_for_normal_performance(self) -> None:
        """Normal performance should have info messages."""
        metrics = {
            "jump_height": 0.45,
            "flight_time": 0.60,
            "countermovement_depth": 0.35,
            "concentric_duration": 0.55,
            "eccentric_duration": 0.50,
            "peak_eccentric_velocity": 1.5,
            "peak_concentric_velocity": 2.9,
        }

        validator = CMJMetricsValidator()
        result = validator.validate(metrics)
        infos = [issue for issue in result.issues if issue.severity == ValidationSeverity.INFO]
        assert len(infos) > 0
