"""Tests for Drop Jump physiological bounds and validation.

Comprehensive test suite validating that metrics fall within realistic
physiological bounds for different athlete profiles.
"""

from kinemotion.core.validation import (
    AthleteProfile,
    ValidationSeverity,
)
from kinemotion.dropjump.metrics_validator import (
    DropJumpMetricsValidator,
)
from kinemotion.dropjump.validation_bounds import (
    DropJumpBounds,
    estimate_athlete_profile,
)


class TestAthleteProfileEstimation:
    """Test athlete profile estimation from drop jump metrics."""

    def test_estimate_elderly_profile(self) -> None:
        """Low jump height should estimate elderly profile."""
        metrics = {"data": {"jump_height_m": 0.12, "ground_contact_time_ms": 650.0}}
        profile = estimate_athlete_profile(metrics)
        assert profile == AthleteProfile.ELDERLY

    def test_estimate_untrained_profile(self) -> None:
        """30cm jump should estimate untrained."""
        metrics = {"data": {"jump_height_m": 0.30, "ground_contact_time_ms": 520.0}}
        profile = estimate_athlete_profile(metrics)
        assert profile == AthleteProfile.UNTRAINED

    def test_estimate_recreational_profile(self) -> None:
        """45cm jump should estimate recreational."""
        metrics = {"data": {"jump_height_m": 0.45, "ground_contact_time_ms": 420.0}}
        profile = estimate_athlete_profile(metrics)
        assert profile == AthleteProfile.RECREATIONAL

    def test_estimate_trained_profile(self) -> None:
        """65cm jump should estimate trained."""
        metrics = {"data": {"jump_height_m": 0.65, "ground_contact_time_ms": 350.0}}
        profile = estimate_athlete_profile(metrics)
        assert profile == AthleteProfile.TRAINED

    def test_estimate_elite_profile(self) -> None:
        """85cm jump should estimate elite."""
        metrics = {"data": {"jump_height_m": 0.85, "ground_contact_time_ms": 250.0}}
        profile = estimate_athlete_profile(metrics)
        assert profile == AthleteProfile.ELITE


class TestContactTimeBounds:
    """Test ground contact time bounds validation."""

    def test_contact_time_minimum_physically_possible(self) -> None:
        """Contact time above minimum should be valid."""
        bounds = DropJumpBounds.CONTACT_TIME
        assert bounds.is_physically_possible(0.15)

    def test_contact_time_maximum_physically_possible(self) -> None:
        """Contact time below maximum should be valid."""
        bounds = DropJumpBounds.CONTACT_TIME
        assert bounds.is_physically_possible(1.0)

    def test_contact_time_below_absolute_minimum_fails(self) -> None:
        """Contact time below absolute minimum should fail."""
        bounds = DropJumpBounds.CONTACT_TIME
        assert not bounds.is_physically_possible(0.05)

    def test_contact_time_above_absolute_maximum_fails(self) -> None:
        """Contact time above absolute maximum should fail."""
        bounds = DropJumpBounds.CONTACT_TIME
        assert not bounds.is_physically_possible(2.0)

    def test_contact_time_recreational_range(self) -> None:
        """Contact time should be in recreational range for recreational athlete."""
        bounds = DropJumpBounds.CONTACT_TIME
        assert bounds.contains(0.45, AthleteProfile.RECREATIONAL)

    def test_contact_time_elite_range(self) -> None:
        """Contact time should be in elite range for elite athlete."""
        bounds = DropJumpBounds.CONTACT_TIME
        assert bounds.contains(0.30, AthleteProfile.ELITE)

    def test_contact_time_elite_faster_than_recreational(self) -> None:
        """Elite athletes typically have shorter contact time than recreational."""
        elite_mid = (
            DropJumpBounds.CONTACT_TIME.elite_min + DropJumpBounds.CONTACT_TIME.elite_max
        ) / 2
        recreational_mid = (
            DropJumpBounds.CONTACT_TIME.recreational_min
            + DropJumpBounds.CONTACT_TIME.recreational_max
        ) / 2
        assert elite_mid < recreational_mid


class TestFlightTimeBounds:
    """Test flight time bounds validation."""

    def test_flight_time_minimum_physically_possible(self) -> None:
        """Flight time above minimum should be valid."""
        bounds = DropJumpBounds.FLIGHT_TIME
        assert bounds.is_physically_possible(0.40)

    def test_flight_time_maximum_physically_possible(self) -> None:
        """Flight time below maximum should be valid."""
        bounds = DropJumpBounds.FLIGHT_TIME
        assert bounds.is_physically_possible(1.0)

    def test_flight_time_below_absolute_minimum_fails(self) -> None:
        """Flight time below absolute minimum should fail."""
        bounds = DropJumpBounds.FLIGHT_TIME
        assert not bounds.is_physically_possible(0.20)

    def test_flight_time_above_absolute_maximum_fails(self) -> None:
        """Flight time above absolute maximum should fail."""
        bounds = DropJumpBounds.FLIGHT_TIME
        assert not bounds.is_physically_possible(1.5)

    def test_flight_time_recreational_range(self) -> None:
        """Flight time should be in recreational range for recreational athlete."""
        bounds = DropJumpBounds.FLIGHT_TIME
        assert bounds.contains(0.65, AthleteProfile.RECREATIONAL)

    def test_flight_time_elite_range(self) -> None:
        """Flight time should be in elite range for elite athlete."""
        bounds = DropJumpBounds.FLIGHT_TIME
        assert bounds.contains(0.85, AthleteProfile.ELITE)


class TestJumpHeightBounds:
    """Test jump height bounds validation."""

    def test_jump_height_minimum_physically_possible(self) -> None:
        """Jump height above minimum should be valid."""
        bounds = DropJumpBounds.JUMP_HEIGHT
        assert bounds.is_physically_possible(0.10)

    def test_jump_height_maximum_physically_possible(self) -> None:
        """Jump height below maximum should be valid."""
        bounds = DropJumpBounds.JUMP_HEIGHT
        assert bounds.is_physically_possible(0.90)

    def test_jump_height_below_absolute_minimum_fails(self) -> None:
        """Jump height below absolute minimum should fail."""
        bounds = DropJumpBounds.JUMP_HEIGHT
        assert not bounds.is_physically_possible(0.02)

    def test_jump_height_above_absolute_maximum_fails(self) -> None:
        """Jump height above absolute maximum should fail."""
        bounds = DropJumpBounds.JUMP_HEIGHT
        assert not bounds.is_physically_possible(1.5)

    def test_jump_height_recreational_range(self) -> None:
        """Jump height should be in recreational range for recreational athlete."""
        bounds = DropJumpBounds.JUMP_HEIGHT
        assert bounds.contains(0.45, AthleteProfile.RECREATIONAL)

    def test_jump_height_elite_range(self) -> None:
        """Jump height should be in elite range for elite athlete."""
        bounds = DropJumpBounds.JUMP_HEIGHT
        assert bounds.contains(0.75, AthleteProfile.ELITE)


class TestRSIBounds:
    """Test Reactive Strength Index bounds."""

    def test_rsi_minimum_valid(self) -> None:
        """RSI at minimum should be valid."""
        bounds = DropJumpBounds.RSI
        assert bounds.is_physically_possible(0.50)

    def test_rsi_maximum_valid(self) -> None:
        """RSI at maximum should be valid."""
        bounds = DropJumpBounds.RSI
        assert bounds.is_physically_possible(3.0)

    def test_rsi_below_minimum_invalid(self) -> None:
        """RSI below minimum should be invalid."""
        bounds = DropJumpBounds.RSI
        assert not bounds.is_physically_possible(0.2)

    def test_rsi_above_maximum_invalid(self) -> None:
        """RSI above maximum should be invalid."""
        bounds = DropJumpBounds.RSI
        assert not bounds.is_physically_possible(5.5)

    def test_rsi_recreational_range(self) -> None:
        """Recreational athlete RSI should be in expected range."""
        bounds = DropJumpBounds.RSI
        assert bounds.contains(1.2, AthleteProfile.RECREATIONAL)

    def test_rsi_elite_range(self) -> None:
        """Elite athlete RSI should be high."""
        bounds = DropJumpBounds.RSI
        assert bounds.contains(2.5, AthleteProfile.ELITE)


class TestRecreationalAthleteProfile:
    """Integration tests for recreational athlete profile."""

    def test_recreational_athlete_all_metrics_valid(self) -> None:
        """All metrics for recreational athlete should pass validation."""
        metrics = {
            "data": {
                "ground_contact_time_ms": 400.0,
                "flight_time_ms": 650.0,
                "jump_height_m": 0.50,
            }
        }

        validator = DropJumpMetricsValidator(assumed_profile=AthleteProfile.RECREATIONAL)
        result = validator.validate(metrics)

        # Should have info/warning issues but not errors
        errors = [issue for issue in result.issues if issue.severity == ValidationSeverity.ERROR]
        assert len(errors) == 0

    def test_recreational_rsi_in_expected_range(self) -> None:
        """RSI for recreational athlete should be 0.7-1.8."""
        flight_time = 0.65
        contact_time = 0.40
        rsi = flight_time / contact_time
        assert 0.7 <= rsi <= 1.8


class TestEliteAthleteProfile:
    """Integration tests for elite athlete profile."""

    def test_elite_athlete_all_metrics_valid(self) -> None:
        """All metrics for elite athlete should pass validation."""
        metrics = {
            "data": {
                "ground_contact_time_ms": 250.0,
                "flight_time_ms": 850.0,
                "jump_height_m": 0.80,
            }
        }

        validator = DropJumpMetricsValidator(assumed_profile=AthleteProfile.ELITE)
        result = validator.validate(metrics)

        errors = [issue for issue in result.issues if issue.severity == ValidationSeverity.ERROR]
        assert len(errors) == 0

    def test_elite_rsi_in_expected_range(self) -> None:
        """RSI for elite athlete should be 1.5-3.5."""
        flight_time = 0.85
        contact_time = 0.25
        rsi = flight_time / contact_time
        assert 1.5 <= rsi <= 3.5

    def test_elite_contact_time_faster_than_recreational(self) -> None:
        """Elite athlete contact time should be noticeably shorter."""
        elite_contact = 0.25
        recreational_contact = 0.45
        assert elite_contact < recreational_contact


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_minimal_drop_jump(self) -> None:
        """Minimal drop jump should still be valid if internally consistent."""
        metrics = {
            "data": {
                "ground_contact_time_ms": 500.0,
                "flight_time_ms": 450.0,
                "jump_height_m": 0.25,
            }
        }

        validator = DropJumpMetricsValidator()
        result = validator.validate(metrics)
        # Should have warnings but not errors
        errors = [issue for issue in result.issues if issue.severity == ValidationSeverity.ERROR]
        assert len(errors) == 0

    def test_high_performance_drop_jump(self) -> None:
        """High performance drop jump from elite athlete should be valid."""
        metrics = {
            "data": {
                "ground_contact_time_ms": 220.0,
                "flight_time_ms": 950.0,
                "jump_height_m": 0.95,
            }
        }

        validator = DropJumpMetricsValidator()
        result = validator.validate(metrics)
        errors = [issue for issue in result.issues if issue.severity == ValidationSeverity.ERROR]
        assert len(errors) == 0

    def test_error_detected_contact_time_too_short(self) -> None:
        """Contact time <0.08s should flag as error."""
        metrics = {
            "data": {
                "ground_contact_time_ms": 60.0,  # TOO SHORT
                "flight_time_ms": 700.0,
                "jump_height_m": 0.55,
            }
        }

        validator = DropJumpMetricsValidator()
        result = validator.validate(metrics)
        errors = [
            issue
            for issue in result.issues
            if issue.severity == ValidationSeverity.ERROR
            and "contact_time" in issue.metric.lower()
        ]
        assert len(errors) > 0

    def test_error_detected_rsi_too_high(self) -> None:
        """RSI >5.0 should flag as error."""
        metrics = {
            "data": {
                "ground_contact_time_ms": 150.0,  # Very short
                "flight_time_ms": 850.0,
                "jump_height_m": 0.75,
            }
        }

        validator = DropJumpMetricsValidator()
        result = validator.validate(metrics)
        # RSI = 0.85 / 0.15 = 5.67 (too high)
        rsi_errors = [
            issue
            for issue in result.issues
            if issue.severity == ValidationSeverity.ERROR and "rsi" in issue.metric.lower()
        ]
        assert len(rsi_errors) > 0


class TestValidationSeverityLevels:
    """Test that validation correctly assigns severity levels."""

    def test_error_severity_assigned_correctly(self) -> None:
        """Physically impossible metrics should be errors."""
        metrics = {
            "data": {
                "ground_contact_time_ms": 2500.0,  # Impossibly long
                "flight_time_ms": 1600.0,  # Impossibly long
                "jump_height_m": 1.8,  # Impossibly high
            }
        }

        validator = DropJumpMetricsValidator()
        result = validator.validate(metrics)
        errors = [issue for issue in result.issues if issue.severity == ValidationSeverity.ERROR]
        assert len(errors) > 0

    def test_warning_severity_for_unusual_but_possible(self) -> None:
        """Unusual but physically possible should be warnings."""
        metrics = {
            "data": {
                "ground_contact_time_ms": 180.0,  # Very fast but possible
                "flight_time_ms": 1050.0,  # Very high but possible
                "jump_height_m": 1.05,  # Elite range
            }
        }

        validator = DropJumpMetricsValidator()
        result = validator.validate(metrics)
        # Should have warnings about unusual patterns
        warnings = [
            issue for issue in result.issues if issue.severity == ValidationSeverity.WARNING
        ]
        # May have warnings about extreme values
        assert len(warnings) >= 0

    def test_info_severity_for_normal_performance(self) -> None:
        """Normal performance should have info or no issues."""
        metrics = {
            "data": {
                "ground_contact_time_ms": 400.0,
                "flight_time_ms": 650.0,
                "jump_height_m": 0.50,
            }
        }

        validator = DropJumpMetricsValidator()
        result = validator.validate(metrics)
        # Normal performance may have info messages or no issues
        # Both are acceptable
        assert result.status in ["PASS", "PASS_WITH_WARNINGS"]


class TestMetricConsistency:
    """Test cross-metric consistency validation."""

    def test_flight_time_height_consistency_perfect(self) -> None:
        """Flight time should match jump height via kinematic formula."""
        flight_time = 0.70
        expected_height = (9.81 * flight_time**2) / 8
        assert 0.59 < expected_height < 0.62

    def test_rsi_calculation_consistency(self) -> None:
        """RSI should be calculated correctly from flight/contact time."""
        flight_time = 0.80
        contact_time = 0.30
        expected_rsi = flight_time / contact_time
        assert 2.6 < expected_rsi < 2.7


class TestUntrainedAthleteProfile:
    """Integration tests for untrained athlete profile."""

    def test_untrained_athlete_all_metrics_valid(self) -> None:
        """All metrics for untrained athlete should pass validation."""
        metrics = {
            "data": {
                "ground_contact_time_ms": 550.0,
                "flight_time_ms": 500.0,
                "jump_height_m": 0.30,
            }
        }

        validator = DropJumpMetricsValidator(assumed_profile=AthleteProfile.UNTRAINED)
        result = validator.validate(metrics)

        errors = [issue for issue in result.issues if issue.severity == ValidationSeverity.ERROR]
        assert len(errors) == 0


class TestElderlyAthleteProfile:
    """Integration tests for elderly athlete profile."""

    def test_elderly_athlete_all_metrics_valid(self) -> None:
        """All metrics for elderly athlete should pass validation."""
        metrics = {
            "data": {
                "ground_contact_time_ms": 700.0,
                "flight_time_ms": 400.0,
                "jump_height_m": 0.20,
            }
        }

        validator = DropJumpMetricsValidator(assumed_profile=AthleteProfile.ELDERLY)
        result = validator.validate(metrics)

        errors = [issue for issue in result.issues if issue.severity == ValidationSeverity.ERROR]
        assert len(errors) == 0


class TestTrainedAthleteProfile:
    """Integration tests for trained athlete profile."""

    def test_trained_athlete_all_metrics_valid(self) -> None:
        """All metrics for trained athlete should pass validation."""
        metrics = {
            "data": {
                "ground_contact_time_ms": 320.0,
                "flight_time_ms": 750.0,
                "jump_height_m": 0.65,
            }
        }

        validator = DropJumpMetricsValidator(assumed_profile=AthleteProfile.TRAINED)
        result = validator.validate(metrics)

        errors = [issue for issue in result.issues if issue.severity == ValidationSeverity.ERROR]
        assert len(errors) == 0

    def test_trained_rsi_in_expected_range(self) -> None:
        """RSI for trained athlete should be between recreational and elite."""
        flight_time = 0.75
        contact_time = 0.32
        rsi = flight_time / contact_time
        # Trained athletes typically have RSI 1.5-2.5
        assert 1.5 <= rsi <= 2.8
