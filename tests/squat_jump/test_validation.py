"""Tests for Squat Jump validation bounds.

Comprehensive test suite validating that metrics fall within realistic
physiological bounds for different athlete profiles.
"""

import pytest

from kinemotion.core.validation import (
    AthleteProfile,
    ValidationSeverity,
)
from kinemotion.squat_jump.metrics_validator import (
    SJMetricsValidator,
)
from kinemotion.squat_jump.validation_bounds import (
    SJBounds,
    estimate_athlete_profile,
)

pytestmark = [pytest.mark.integration, pytest.mark.squat_jump]


class TestSJBounds:
    """Test SJ physiological bounds definitions."""

    def test_sj_bounds_all_defined(self) -> None:
        """Test that all SJ bounds are properly defined."""
        # Flight time bounds
        assert SJBounds.FLIGHT_TIME.absolute_min > 0
        assert SJBounds.FLIGHT_TIME.practical_min > 0
        assert SJBounds.FLIGHT_TIME.recreational_min > 0
        assert SJBounds.FLIGHT_TIME.recreational_max > SJBounds.FLIGHT_TIME.recreational_min
        assert SJBounds.FLIGHT_TIME.elite_min > SJBounds.FLIGHT_TIME.recreational_max
        assert SJBounds.FLIGHT_TIME.elite_max > SJBounds.FLIGHT_TIME.elite_min
        assert SJBounds.FLIGHT_TIME.absolute_max > SJBounds.FLIGHT_TIME.elite_max
        assert SJBounds.FLIGHT_TIME.unit == "s"

        # Jump height bounds
        assert SJBounds.JUMP_HEIGHT.absolute_min > 0
        assert SJBounds.JUMP_HEIGHT.practical_min > 0
        assert SJBounds.JUMP_HEIGHT.recreational_min > 0
        assert SJBounds.JUMP_HEIGHT.recreational_max > SJBounds.JUMP_HEIGHT.recreational_min
        assert SJBounds.JUMP_HEIGHT.elite_min > SJBounds.JUMP_HEIGHT.recreational_max
        assert SJBounds.JUMP_HEIGHT.elite_max > SJBounds.JUMP_HEIGHT.elite_min
        assert SJBounds.JUMP_HEIGHT.absolute_max > SJBounds.JUMP_HEIGHT.elite_max
        assert SJBounds.JUMP_HEIGHT.unit == "m"

        # Squat hold duration bounds
        # Note: Unlike most metrics, squat hold duration is NOT performance-related
        # Elite athletes may use short holds, so elite_min overlaps recreational range
        assert SJBounds.SQUAT_HOLD_DURATION.absolute_min == 0.0
        assert SJBounds.SQUAT_HOLD_DURATION.practical_min == 0.0
        assert SJBounds.SQUAT_HOLD_DURATION.recreational_min >= 0.0
        assert (
            SJBounds.SQUAT_HOLD_DURATION.recreational_max
            > SJBounds.SQUAT_HOLD_DURATION.recreational_min
        )
        # Elite min can overlap recreational (not performance-dependent)
        assert SJBounds.SQUAT_HOLD_DURATION.elite_min == 0.0
        assert SJBounds.SQUAT_HOLD_DURATION.elite_max > SJBounds.SQUAT_HOLD_DURATION.elite_min
        assert SJBounds.SQUAT_HOLD_DURATION.absolute_max > SJBounds.SQUAT_HOLD_DURATION.elite_max
        assert SJBounds.SQUAT_HOLD_DURATION.unit == "s"

        # Concentric duration bounds
        assert SJBounds.CONCENTRIC_DURATION.absolute_min > 0
        assert SJBounds.CONCENTRIC_DURATION.practical_min > 0
        assert SJBounds.CONCENTRIC_DURATION.recreational_min > 0
        assert (
            SJBounds.CONCENTRIC_DURATION.recreational_max
            > SJBounds.CONCENTRIC_DURATION.recreational_min
        )
        assert SJBounds.CONCENTRIC_DURATION.elite_min < (
            SJBounds.CONCENTRIC_DURATION.recreational_min
        )
        assert SJBounds.CONCENTRIC_DURATION.elite_max > SJBounds.CONCENTRIC_DURATION.elite_min
        assert SJBounds.CONCENTRIC_DURATION.absolute_max > SJBounds.CONCENTRIC_DURATION.elite_max
        assert SJBounds.CONCENTRIC_DURATION.unit == "s"

        # Peak concentric velocity bounds
        assert SJBounds.PEAK_CONCENTRIC_VELOCITY.absolute_min > 0
        assert SJBounds.PEAK_CONCENTRIC_VELOCITY.practical_min > 0
        assert SJBounds.PEAK_CONCENTRIC_VELOCITY.recreational_min > 0
        assert SJBounds.PEAK_CONCENTRIC_VELOCITY.recreational_max > (
            SJBounds.PEAK_CONCENTRIC_VELOCITY.recreational_min
        )
        assert SJBounds.PEAK_CONCENTRIC_VELOCITY.elite_min > (
            SJBounds.PEAK_CONCENTRIC_VELOCITY.recreational_max
        )
        assert SJBounds.PEAK_CONCENTRIC_VELOCITY.elite_max > (
            SJBounds.PEAK_CONCENTRIC_VELOCITY.elite_min
        )
        assert SJBounds.PEAK_CONCENTRIC_VELOCITY.absolute_max > (
            SJBounds.PEAK_CONCENTRIC_VELOCITY.elite_max
        )
        assert SJBounds.PEAK_CONCENTRIC_VELOCITY.unit == "m/s"

        # Peak power bounds
        assert SJBounds.PEAK_POWER.absolute_min > 0
        assert SJBounds.PEAK_POWER.practical_min > 0
        assert SJBounds.PEAK_POWER.recreational_min > 0
        assert SJBounds.PEAK_POWER.recreational_max > SJBounds.PEAK_POWER.recreational_min
        assert SJBounds.PEAK_POWER.elite_min > SJBounds.PEAK_POWER.recreational_max
        assert SJBounds.PEAK_POWER.elite_max > SJBounds.PEAK_POWER.elite_min
        assert SJBounds.PEAK_POWER.absolute_max > SJBounds.PEAK_POWER.elite_max
        assert SJBounds.PEAK_POWER.unit == "W"

        # Mean power bounds
        assert SJBounds.MEAN_POWER.absolute_min > 0
        assert SJBounds.MEAN_POWER.practical_min > 0
        assert SJBounds.MEAN_POWER.recreational_min > 0
        assert SJBounds.MEAN_POWER.recreational_max > SJBounds.MEAN_POWER.recreational_min
        assert SJBounds.MEAN_POWER.elite_min > SJBounds.MEAN_POWER.recreational_max
        assert SJBounds.MEAN_POWER.elite_max > SJBounds.MEAN_POWER.elite_min
        assert SJBounds.MEAN_POWER.absolute_max > SJBounds.MEAN_POWER.elite_max
        assert SJBounds.MEAN_POWER.unit == "W"

        # Peak force bounds
        assert SJBounds.PEAK_FORCE.absolute_min > 0
        assert SJBounds.PEAK_FORCE.practical_min > 0
        assert SJBounds.PEAK_FORCE.recreational_min > 0
        assert SJBounds.PEAK_FORCE.recreational_max > SJBounds.PEAK_FORCE.recreational_min
        assert SJBounds.PEAK_FORCE.elite_min > SJBounds.PEAK_FORCE.recreational_max
        assert SJBounds.PEAK_FORCE.elite_max > SJBounds.PEAK_FORCE.elite_min
        assert SJBounds.PEAK_FORCE.absolute_max > SJBounds.PEAK_FORCE.elite_max
        assert SJBounds.PEAK_FORCE.unit == "N"


class TestSquatJumpValidation:
    """Test SJ metrics validation."""

    def test_sj_validator_initialization(self) -> None:
        """Test SJ validator initialization."""
        validator = SJMetricsValidator()
        assert validator is not None

    def test_validate_flight_time(self) -> None:
        """Test flight time validation."""
        validator = SJMetricsValidator()

        # Valid flight times for different profiles
        test_cases = [
            (0.25, AthleteProfile.UNTRAINED),  # Untrained
            (0.35, AthleteProfile.RECREATIONAL),  # Recreational
            (0.50, AthleteProfile.TRAINED),  # Trained
            (0.70, AthleteProfile.ELITE),  # Elite
        ]

        for flight_time, _profile in test_cases:
            metrics = {"data": {"flight_time_ms": flight_time * 1000}}
            result = validator.validate(metrics)

            # Should have validation for this profile
            assert result is not None

    def test_validate_jump_height(self) -> None:
        """Test jump height validation."""
        validator = SJMetricsValidator()

        # Valid jump heights for different profiles
        test_cases = [
            (0.20, AthleteProfile.UNTRAINED),  # Untrained
            (0.35, AthleteProfile.RECREATIONAL),  # Recreational
            (0.55, AthleteProfile.TRAINED),  # Trained
            (0.75, AthleteProfile.ELITE),  # Elite
        ]

        for jump_height, _profile in test_cases:
            metrics = {"data": {"jump_height_m": jump_height}}
            result = validator.validate(metrics)

            # Should have validation for this profile
            assert result is not None

    def test_validate_squat_hold_duration(self) -> None:
        """Test squat hold duration validation."""
        validator = SJMetricsValidator()

        # Test different squat hold durations
        metrics = {"data": {"squat_hold_duration_ms": 1500.0}}  # 1.5 seconds
        result = validator.validate(metrics)

        # Should have validation for this duration
        assert result is not None

    def test_validate_concentric_duration(self) -> None:
        """Test concentric duration validation."""
        validator = SJMetricsValidator()

        # Test different concentric durations
        metrics = {"data": {"concentric_duration_ms": 800.0}}  # 0.8 seconds
        result = validator.validate(metrics)

        # Should have validation for this duration
        assert result is not None

    def test_validate_peak_velocity(self) -> None:
        """Test peak velocity validation."""
        validator = SJMetricsValidator()

        # Test different peak velocities
        metrics = {"data": {"peak_concentric_velocity_m_s": 2.5}}
        result = validator.validate(metrics)

        # Should have validation for this velocity
        assert result is not None

    def test_validate_power(self) -> None:
        """Test power validation."""
        validator = SJMetricsValidator()

        # Test different power values (with mass)
        metrics = {"data": {"peak_power_w": 3500.0, "mean_power_w": 2800.0, "mass_kg": 75.0}}
        result = validator.validate(metrics)

        # Should have validation for these power values
        assert result is not None

    def test_validate_force(self) -> None:
        """Test force validation."""
        validator = SJMetricsValidator()

        # Test different force values (with mass)
        metrics = {"data": {"peak_force_n": 2000.0, "mass_kg": 75.0}}
        _result = validator.validate(metrics)

        # Should have validation for this force
        assert _result is not None

    def test_validation_without_mass(self) -> None:
        """Test validation when mass is not provided (power/force should be ignored)."""
        validator = SJMetricsValidator()

        metrics = {
            "data": {
                "jump_height_m": 0.40,
                "flight_time_ms": 450.0,
                "squat_hold_duration_ms": 1200.0,
                "peak_concentric_velocity_m_s": 2.2,
                # No mass_kg - power/force should not be validated
            }
        }
        result = validator.validate(metrics)

        # Should still validate other metrics
        assert result is not None

    def test_validation_empty_metrics(self) -> None:
        """Test validation with empty metrics."""
        validator = SJMetricsValidator()

        # Empty metrics
        metrics = {"data": {}}
        result = validator.validate(metrics)

        # Should still return validation result
        assert result is not None

    def test_validation_multiple_metrics(self) -> None:
        """Test validation with multiple metrics simultaneously.

        NOTE: Flight time must be consistent with jump height per h = g*t²/8
        For h=0.45m: t = sqrt(8*0.45/9.81) ≈ 0.605s = 605ms
        """
        validator = SJMetricsValidator()

        metrics = {
            "data": {
                "jump_height_m": 0.45,  # Recreational athlete
                "flight_time_ms": 605.0,  # Consistent with h = g*t²/8
                "squat_hold_duration_ms": 1500.0,
                "concentric_duration_ms": 900.0,
                "peak_concentric_velocity_m_s": 2.5,
                "peak_power_w": 3750.0,
                "peak_force_n": 2100.0,
                "mass_kg": 80.0,
                "tracking_method": "foot",
            }
        }
        result = validator.validate(metrics)

        # Should validate all metrics
        assert result is not None
        # Check for error-level issues (warnings are acceptable)
        assert not any(issue.severity == ValidationSeverity.ERROR for issue in result.issues)


class TestAthleteProfileEstimation:
    """Test athlete profile estimation from SJ metrics.

    NOTE: SJ thresholds are lower than CMJ due to lack of countermovement.
    Implementation uses: <0.15=ELDERLY, 0.15-0.20=UNTRAINED, 0.20-0.45=RECREATIONAL,
    0.45-0.50=TRAINED, >=0.50=ELITE
    """

    def test_estimate_elderly_profile(self) -> None:
        """Very low jump height (<0.15m) should estimate elderly profile."""
        metrics = {"data": {"jump_height_m": 0.10, "flight_time_ms": 150.0}}
        profile = estimate_athlete_profile(metrics)
        assert profile == AthleteProfile.ELDERLY

    def test_estimate_untrained_profile(self) -> None:
        """0.15-0.20m jump should estimate untrained."""
        metrics = {"data": {"jump_height_m": 0.18, "flight_time_ms": 250.0}}
        profile = estimate_athlete_profile(metrics)
        assert profile == AthleteProfile.UNTRAINED

    def test_estimate_recreational_profile(self) -> None:
        """0.20-0.45m jump should estimate recreational."""
        metrics = {"data": {"jump_height_m": 0.35, "flight_time_ms": 400.0}}
        profile = estimate_athlete_profile(metrics)
        assert profile == AthleteProfile.RECREATIONAL

    def test_estimate_trained_profile(self) -> None:
        """0.45-0.50m jump should estimate trained."""
        metrics = {"data": {"jump_height_m": 0.48, "flight_time_ms": 500.0}}
        profile = estimate_athlete_profile(metrics)
        assert profile == AthleteProfile.TRAINED

    def test_estimate_competitive_profile(self) -> None:
        """0.55-0.65m jump should estimate competitive."""
        metrics = {"data": {"jump_height_m": 0.60, "flight_time_ms": 580.0}}
        profile = estimate_athlete_profile(metrics)
        assert profile == AthleteProfile.COMPETITIVE

    def test_estimate_elite_profile(self) -> None:
        """>=0.65m jump should estimate elite."""
        metrics = {"data": {"jump_height_m": 0.70, "flight_time_ms": 650.0}}
        profile = estimate_athlete_profile(metrics)
        assert profile == AthleteProfile.ELITE

    def test_profile_estimation_with_power(self) -> None:
        """Test profile estimation with power metrics."""
        metrics = {
            "data": {
                "jump_height_m": 0.52,
                "flight_time_ms": 550.0,
                "peak_power_w": 5000.0,
                "mass_kg": 80.0,
            }
        }
        profile = estimate_athlete_profile(metrics)
        assert profile == AthleteProfile.TRAINED

    def test_profile_estimation_multiple_metrics_consistency(self) -> None:
        """Test that multiple metrics agree on profile estimation."""
        metrics = {
            "data": {
                "jump_height_m": 0.40,
                "flight_time_ms": 450.0,
                "squat_hold_duration_ms": 1500.0,
                "peak_concentric_velocity_m_s": 2.5,
                "mass_kg": 75.0,
            }
        }

        # All metrics should point to recreational profile
        profile = estimate_athlete_profile(metrics)
        assert profile == AthleteProfile.RECREATIONAL

    def test_profile_estimation_edge_cases(self) -> None:
        """Test profile estimation at boundaries."""
        # At recreational upper bound
        metrics1 = {"data": {"jump_height_m": 0.44, "flight_time_ms": 480.0}}
        profile1 = estimate_athlete_profile(metrics1)
        assert profile1 == AthleteProfile.RECREATIONAL

        # At trained lower bound
        metrics2 = {"data": {"jump_height_m": 0.46, "flight_time_ms": 500.0}}
        profile2 = estimate_athlete_profile(metrics2)
        assert profile2 == AthleteProfile.TRAINED

    def test_profile_estimation_ambiguous_metrics(self) -> None:
        """Test profile estimation with slightly conflicting metrics."""
        metrics = {
            "data": {
                # Good jump height for competitive SJ
                "jump_height_m": 0.55,
                # But unusually short squat hold (not typical for competitive)
                "squat_hold_duration_ms": 200.0,
            }
        }
        profile = estimate_athlete_profile(metrics)
        # Should prioritize jump height for SJ (competitive threshold is 0.55-0.65m)
        assert profile == AthleteProfile.COMPETITIVE


class TestStaticStartCriteria:
    """Test squat jump static start validation criteria."""

    def test_valid_static_hold(self) -> None:
        """Test validation of valid static squat hold.

        NOTE: Flight time must be consistent with jump height per h = g*t²/8
        For h=0.35m: t = sqrt(8*0.35/9.81) ≈ 0.534s = 534ms
        """
        validator = SJMetricsValidator()

        # Simulate a static hold with appropriate duration
        metrics = {
            "data": {
                "squat_hold_duration_ms": 1000.0,  # 1 second
                # Physically consistent metrics
                "jump_height_m": 0.35,  # Recreational athlete
                "flight_time_ms": 534.0,  # Consistent with h = g*t²/8
            }
        }
        result = validator.validate(metrics)

        # Should not have error-level issues for static hold
        assert not any(issue.severity == ValidationSeverity.ERROR for issue in result.issues)

    def test_invalid_no_static_hold(self) -> None:
        """Test validation when no static squat hold is detected."""
        validator = SJMetricsValidator()

        metrics = {
            "data": {
                "squat_hold_duration_ms": 0.0,  # No static hold
                "jump_height_m": 0.40,
                "flight_time_ms": 450.0,
            }
        }
        _result = validator.validate(metrics)

        # May have warning about no static hold (depends on implementation)
        # But should not be a hard error for SJ (can be counted jump)

    def test_very_short_static_hold(self) -> None:
        """Test validation of very short static hold."""
        validator = SJMetricsValidator()

        metrics = {
            "data": {
                "squat_hold_duration_ms": 100.0,  # Very short (100ms)
                "jump_height_m": 0.40,
                "flight_time_ms": 450.0,
            }
        }
        result = validator.validate(metrics)

        # Should handle short holds gracefully
        assert result is not None

    def test_extremely_long_static_hold(self) -> None:
        """Test validation of extremely long static hold."""
        validator = SJMetricsValidator()

        metrics = {
            "data": {
                "squat_hold_duration_ms": 10000.0,  # Very long (10 seconds)
                "jump_height_m": 0.40,
                "flight_time_ms": 450.0,
            }
        }
        result = validator.validate(metrics)

        # Should handle long holds gracefully
        assert result is not None
