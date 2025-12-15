"""Tests for core validation infrastructure.

Tests ValidationSeverity, ValidationIssue, ValidationResult, AthleteProfile,
MetricBounds, and MetricsValidator base classes.
"""

import pytest

from kinemotion.core.validation import (
    AthleteProfile,
    MetricBounds,
    MetricsValidator,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
)

pytestmark = [pytest.mark.unit, pytest.mark.core, pytest.mark.validation]

# ===== ValidationSeverity Tests =====


def test_validation_severity_enum_values() -> None:
    """Test ValidationSeverity enum has expected values."""
    assert ValidationSeverity.ERROR.value == "ERROR"
    assert ValidationSeverity.WARNING.value == "WARNING"
    assert ValidationSeverity.INFO.value == "INFO"


def test_validation_severity_comparison() -> None:
    """Test ValidationSeverity enum members are comparable."""
    error = ValidationSeverity.ERROR
    warning = ValidationSeverity.WARNING
    info = ValidationSeverity.INFO

    # Enum members should be equal to themselves
    assert error == ValidationSeverity.ERROR
    assert warning == ValidationSeverity.WARNING
    assert info == ValidationSeverity.INFO


# ===== ValidationIssue Tests =====


def test_validation_issue_creation_with_all_fields() -> None:
    """Test ValidationIssue dataclass creation with all fields."""
    issue = ValidationIssue(
        severity=ValidationSeverity.ERROR,
        metric="jump_height",
        message="Value exceeds maximum",
        value=2.5,
        bounds=(0.0, 1.5),
    )

    assert issue.severity == ValidationSeverity.ERROR
    assert issue.metric == "jump_height"
    assert issue.message == "Value exceeds maximum"
    assert issue.value == 2.5
    assert issue.bounds == (0.0, 1.5)


def test_validation_issue_creation_with_optional_fields() -> None:
    """Test ValidationIssue with optional fields None."""
    issue = ValidationIssue(
        severity=ValidationSeverity.INFO,
        metric="transition_time",
        message="Normal variation",
    )

    assert issue.severity == ValidationSeverity.INFO
    assert issue.metric == "transition_time"
    assert issue.message == "Normal variation"
    assert issue.value is None
    assert issue.bounds is None


def test_validation_issue_immutability() -> None:
    """Test ValidationIssue dataclass is mutable (default behavior)."""
    issue = ValidationIssue(
        severity=ValidationSeverity.WARNING,
        metric="test",
        message="test message",
    )

    # Dataclass is mutable by default
    issue.message = "updated message"
    assert issue.message == "updated message"


# ===== AthleteProfile Tests =====


def test_athlete_profile_enum_values() -> None:
    """Test AthleteProfile enum has expected values."""
    assert AthleteProfile.ELDERLY.value == "elderly"
    assert AthleteProfile.UNTRAINED.value == "untrained"
    assert AthleteProfile.RECREATIONAL.value == "recreational"
    assert AthleteProfile.TRAINED.value == "trained"
    assert AthleteProfile.ELITE.value == "elite"


def test_athlete_profile_ordering() -> None:
    """Test athlete profiles exist in expected progression."""
    profiles = [
        AthleteProfile.ELDERLY,
        AthleteProfile.UNTRAINED,
        AthleteProfile.RECREATIONAL,
        AthleteProfile.TRAINED,
        AthleteProfile.ELITE,
    ]

    # All profiles should be distinct
    assert len(set(profiles)) == 5


# ===== MetricBounds Tests =====


def test_metric_bounds_creation() -> None:
    """Test MetricBounds dataclass creation."""
    bounds = MetricBounds(
        absolute_min=0.0,
        practical_min=0.1,
        recreational_min=0.3,
        recreational_max=0.7,
        elite_min=0.5,
        elite_max=1.0,
        absolute_max=1.5,
        unit="m",
    )

    assert bounds.absolute_min == 0.0
    assert bounds.practical_min == 0.1
    assert bounds.recreational_min == 0.3
    assert bounds.recreational_max == 0.7
    assert bounds.elite_min == 0.5
    assert bounds.elite_max == 1.0
    assert bounds.absolute_max == 1.5
    assert bounds.unit == "m"


def test_metric_bounds_contains_elderly() -> None:
    """Test MetricBounds.contains() for elderly profile."""
    bounds = MetricBounds(
        absolute_min=0.0,
        practical_min=0.1,
        recreational_min=0.3,
        recreational_max=0.7,
        elite_min=0.5,
        elite_max=1.0,
        absolute_max=1.5,
        unit="m",
    )

    # Elderly uses practical_min to recreational_max
    assert bounds.contains(0.1, AthleteProfile.ELDERLY)  # At practical_min
    assert bounds.contains(0.4, AthleteProfile.ELDERLY)  # Mid-range
    assert bounds.contains(0.7, AthleteProfile.ELDERLY)  # At recreational_max

    # Outside elderly bounds
    assert not bounds.contains(0.05, AthleteProfile.ELDERLY)  # Below practical_min
    assert not bounds.contains(0.8, AthleteProfile.ELDERLY)  # Above recreational_max


def test_metric_bounds_contains_untrained() -> None:
    """Test MetricBounds.contains() for untrained profile."""
    bounds = MetricBounds(
        absolute_min=0.0,
        practical_min=0.1,
        recreational_min=0.3,
        recreational_max=0.7,
        elite_min=0.5,
        elite_max=1.0,
        absolute_max=1.5,
        unit="m",
    )

    # Untrained uses same bounds as elderly
    assert bounds.contains(0.15, AthleteProfile.UNTRAINED)
    assert bounds.contains(0.6, AthleteProfile.UNTRAINED)
    assert not bounds.contains(0.0, AthleteProfile.UNTRAINED)


def test_metric_bounds_contains_recreational() -> None:
    """Test MetricBounds.contains() for recreational profile."""
    bounds = MetricBounds(
        absolute_min=0.0,
        practical_min=0.1,
        recreational_min=0.3,
        recreational_max=0.7,
        elite_min=0.5,
        elite_max=1.0,
        absolute_max=1.5,
        unit="m",
    )

    # Recreational uses recreational_min to recreational_max
    assert bounds.contains(0.3, AthleteProfile.RECREATIONAL)  # At min
    assert bounds.contains(0.5, AthleteProfile.RECREATIONAL)  # Mid-range
    assert bounds.contains(0.7, AthleteProfile.RECREATIONAL)  # At max

    # Outside recreational bounds
    assert not bounds.contains(0.2, AthleteProfile.RECREATIONAL)  # Below min
    assert not bounds.contains(0.8, AthleteProfile.RECREATIONAL)  # Above max


def test_metric_bounds_contains_trained() -> None:
    """Test MetricBounds.contains() for trained profile (midpoint logic)."""
    bounds = MetricBounds(
        absolute_min=0.0,
        practical_min=0.1,
        recreational_min=0.3,
        recreational_max=0.7,
        elite_min=0.5,
        elite_max=1.0,
        absolute_max=1.5,
        unit="m",
    )

    # Trained uses midpoint between recreational and elite
    # trained_min = (0.3 + 0.5) / 2 = 0.4
    # trained_max = (0.7 + 1.0) / 2 = 0.85

    assert bounds.contains(0.4, AthleteProfile.TRAINED)  # At trained_min
    assert bounds.contains(0.6, AthleteProfile.TRAINED)  # Mid-range
    assert bounds.contains(0.85, AthleteProfile.TRAINED)  # At trained_max

    # Outside trained bounds
    assert not bounds.contains(0.35, AthleteProfile.TRAINED)  # Below trained_min
    assert not bounds.contains(0.9, AthleteProfile.TRAINED)  # Above trained_max


def test_metric_bounds_contains_elite() -> None:
    """Test MetricBounds.contains() for elite profile."""
    bounds = MetricBounds(
        absolute_min=0.0,
        practical_min=0.1,
        recreational_min=0.3,
        recreational_max=0.7,
        elite_min=0.5,
        elite_max=1.0,
        absolute_max=1.5,
        unit="m",
    )

    # Elite uses elite_min to elite_max
    assert bounds.contains(0.5, AthleteProfile.ELITE)  # At elite_min
    assert bounds.contains(0.75, AthleteProfile.ELITE)  # Mid-range
    assert bounds.contains(1.0, AthleteProfile.ELITE)  # At elite_max

    # Outside elite bounds
    assert not bounds.contains(0.4, AthleteProfile.ELITE)  # Below elite_min
    assert not bounds.contains(1.1, AthleteProfile.ELITE)  # Above elite_max


def test_metric_bounds_is_physically_possible() -> None:
    """Test MetricBounds.is_physically_possible() checks absolute limits."""
    bounds = MetricBounds(
        absolute_min=0.0,
        practical_min=0.1,
        recreational_min=0.3,
        recreational_max=0.7,
        elite_min=0.5,
        elite_max=1.0,
        absolute_max=1.5,
        unit="m",
    )

    # Within absolute bounds
    assert bounds.is_physically_possible(0.0)  # At absolute_min
    assert bounds.is_physically_possible(0.5)  # Mid-range
    assert bounds.is_physically_possible(1.5)  # At absolute_max

    # Outside absolute bounds
    assert not bounds.is_physically_possible(-0.1)  # Below absolute_min
    assert not bounds.is_physically_possible(2.0)  # Above absolute_max


def test_metric_bounds_edge_cases() -> None:
    """Test MetricBounds with edge case values."""
    # Narrow bounds (elite range equals recreational range)
    narrow_bounds = MetricBounds(
        absolute_min=0.0,
        practical_min=0.1,
        recreational_min=0.3,
        recreational_max=0.4,
        elite_min=0.3,
        elite_max=0.4,
        absolute_max=0.5,
        unit="m",
    )

    # Trained should still compute midpoint correctly
    # trained_min = (0.3 + 0.3) / 2 = 0.3
    # trained_max = (0.4 + 0.4) / 2 = 0.4
    assert narrow_bounds.contains(0.35, AthleteProfile.TRAINED)


# ===== ValidationResult Tests =====


def test_validation_result_creation() -> None:
    """Test ValidationResult dataclass creation with defaults."""
    result = ValidationResult()

    assert result.issues == []
    assert result.status == "PASS"
    assert result.athlete_profile is None


def test_validation_result_add_error() -> None:
    """Test ValidationResult.add_error() adds error-level issue."""
    result = ValidationResult()

    result.add_error(
        metric="jump_height",
        message="Exceeds maximum",
        value=2.0,
        bounds=(0.0, 1.5),
    )

    assert len(result.issues) == 1
    issue = result.issues[0]
    assert issue.severity == ValidationSeverity.ERROR
    assert issue.metric == "jump_height"
    assert issue.message == "Exceeds maximum"
    assert issue.value == 2.0
    assert issue.bounds == (0.0, 1.5)


def test_validation_result_add_warning() -> None:
    """Test ValidationResult.add_warning() adds warning-level issue."""
    result = ValidationResult()

    result.add_warning(
        metric="contact_time",
        message="Unusually short",
        value=0.15,
        bounds=(0.2, 0.8),
    )

    assert len(result.issues) == 1
    issue = result.issues[0]
    assert issue.severity == ValidationSeverity.WARNING
    assert issue.metric == "contact_time"
    assert issue.message == "Unusually short"
    assert issue.value == 0.15
    assert issue.bounds == (0.2, 0.8)


def test_validation_result_add_info() -> None:
    """Test ValidationResult.add_info() adds info-level issue."""
    result = ValidationResult()

    result.add_info(
        metric="transition_time",
        message="Normal variation",
        value=0.05,
    )

    assert len(result.issues) == 1
    issue = result.issues[0]
    assert issue.severity == ValidationSeverity.INFO
    assert issue.metric == "transition_time"
    assert issue.message == "Normal variation"
    assert issue.value == 0.05
    assert issue.bounds is None  # Info doesn't require bounds


def test_validation_result_finalize_status_pass() -> None:
    """Test finalize_status() sets PASS when no issues."""
    result = ValidationResult()
    result.finalize_status()

    assert result.status == "PASS"


def test_validation_result_finalize_status_pass_with_warnings() -> None:
    """Test finalize_status() sets PASS_WITH_WARNINGS when warnings present."""
    result = ValidationResult()
    result.add_warning("metric1", "Warning message")
    result.add_info("metric2", "Info message")
    result.finalize_status()

    assert result.status == "PASS_WITH_WARNINGS"


def test_validation_result_finalize_status_fail() -> None:
    """Test finalize_status() sets FAIL when errors present."""
    result = ValidationResult()
    result.add_error("metric1", "Error message")
    result.add_warning("metric2", "Warning message")
    result.finalize_status()

    assert result.status == "FAIL"


def test_validation_result_finalize_status_multiple_calls() -> None:
    """Test finalize_status() can be called multiple times."""
    result = ValidationResult()
    result.finalize_status()
    assert result.status == "PASS"

    # Add error and re-finalize
    result.add_error("metric1", "Error added")
    result.finalize_status()
    assert result.status == "FAIL"


def test_validation_result_with_athlete_profile() -> None:
    """Test ValidationResult with athlete profile specified."""
    result = ValidationResult(athlete_profile=AthleteProfile.ELITE)

    assert result.athlete_profile == AthleteProfile.ELITE
    assert result.status == "PASS"
    assert result.issues == []


def test_validation_result_to_dict_implementation() -> None:
    """Test ValidationResult.to_dict() must be implemented by subclasses.

    Note: ValidationResult uses @abstractmethod but is also a dataclass,
    which allows instantiation but requires subclasses to implement to_dict().
    """
    # Verify the method exists on base class
    assert hasattr(ValidationResult, "to_dict")

    # Verify that a proper implementation works
    class ConcreteValidationResult(ValidationResult):
        def to_dict(self) -> dict:
            return {
                "status": self.status,
                "issues": [
                    {
                        "severity": issue.severity.value,
                        "metric": issue.metric,
                        "message": issue.message,
                    }
                    for issue in self.issues
                ],
                "athlete_profile": (self.athlete_profile.value if self.athlete_profile else None),
            }

    # Create instance and test serialization
    result = ConcreteValidationResult()
    result.add_error("test_metric", "Test error")
    result.finalize_status()

    result_dict = result.to_dict()
    assert isinstance(result_dict, dict)
    assert result_dict["status"] == "FAIL"
    assert len(result_dict["issues"]) == 1
    assert result_dict["issues"][0]["metric"] == "test_metric"


# ===== MetricsValidator Tests =====


def test_metrics_validator_abstract() -> None:
    """Test MetricsValidator is abstract and cannot be instantiated."""
    # Should raise TypeError for abstract class
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        MetricsValidator()  # type: ignore[abstract]


def test_metrics_validator_with_assumed_profile() -> None:
    """Test MetricsValidator initialization with assumed profile."""

    # Create concrete implementation
    class ConcreteValidator(MetricsValidator):
        def validate(self, metrics: dict) -> ValidationResult:
            result = ValidationResult()
            result.athlete_profile = self.assumed_profile
            return result

    validator = ConcreteValidator(assumed_profile=AthleteProfile.ELITE)

    assert validator.assumed_profile == AthleteProfile.ELITE

    # Test validation uses assumed profile
    result = validator.validate({})
    assert result.athlete_profile == AthleteProfile.ELITE


def test_metrics_validator_without_assumed_profile() -> None:
    """Test MetricsValidator initialization without assumed profile."""

    class ConcreteValidator(MetricsValidator):
        def validate(self, metrics: dict) -> ValidationResult:
            return ValidationResult()

    validator = ConcreteValidator()

    assert validator.assumed_profile is None


def test_metrics_validator_validate_abstract() -> None:
    """Test MetricsValidator.validate() must be implemented by subclasses."""

    # Attempt to create validator without implementing validate()
    class IncompleteValidator(MetricsValidator):
        pass

    # Should raise TypeError for missing abstract method
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        IncompleteValidator()  # type: ignore[abstract]


def test_metrics_validator_concrete_implementation() -> None:
    """Test complete concrete MetricsValidator implementation."""

    class TestValidator(MetricsValidator):
        def validate(self, metrics: dict) -> ValidationResult:
            result = ValidationResult()

            # Example validation logic
            if "jump_height" in metrics:
                height = metrics["jump_height"]
                if height < 0:
                    result.add_error("jump_height", "Height cannot be negative", value=height)
                elif height > 2.0:
                    result.add_error("jump_height", "Height exceeds maximum", value=height)
                elif height > 1.5:
                    result.add_warning("jump_height", "Unusually high", value=height)

            result.finalize_status()
            return result

    validator = TestValidator()

    # Test with valid data
    result = validator.validate({"jump_height": 0.5})
    assert result.status == "PASS"
    assert len(result.issues) == 0

    # Test with warning data
    result = validator.validate({"jump_height": 1.6})
    assert result.status == "PASS_WITH_WARNINGS"
    assert len(result.issues) == 1
    assert result.issues[0].severity == ValidationSeverity.WARNING

    # Test with error data
    result = validator.validate({"jump_height": 2.5})
    assert result.status == "FAIL"
    assert len(result.issues) == 1
    assert result.issues[0].severity == ValidationSeverity.ERROR


# ===== Integration Tests =====


def test_validation_workflow_complete() -> None:
    """Test complete validation workflow with all components."""
    # Create metric bounds
    height_bounds = MetricBounds(
        absolute_min=0.0,
        practical_min=0.1,
        recreational_min=0.3,
        recreational_max=0.7,
        elite_min=0.5,
        elite_max=1.0,
        absolute_max=1.5,
        unit="m",
    )

    # Create validator
    class JumpValidator(MetricsValidator):
        def validate(self, metrics: dict) -> ValidationResult:
            result = ValidationResult()

            height = metrics.get("jump_height")
            if height is None:
                result.add_error("jump_height", "Missing required metric")
                result.finalize_status()
                return result

            # Check physical possibility
            if not height_bounds.is_physically_possible(height):
                result.add_error(
                    "jump_height",
                    "Physically impossible",
                    value=height,
                    bounds=(height_bounds.absolute_min, height_bounds.absolute_max),
                )

            # Check profile-specific bounds
            profile = self.assumed_profile or AthleteProfile.RECREATIONAL
            if not height_bounds.contains(height, profile):
                result.add_warning(
                    "jump_height",
                    f"Outside expected range for {profile.value} athlete",
                    value=height,
                )

            result.athlete_profile = profile
            result.finalize_status()
            return result

    # Test with various scenarios
    validator = JumpValidator(assumed_profile=AthleteProfile.RECREATIONAL)

    # Valid height for recreational athlete
    result = validator.validate({"jump_height": 0.5})
    assert result.status == "PASS"
    assert result.athlete_profile == AthleteProfile.RECREATIONAL

    # Height outside recreational bounds (too high)
    result = validator.validate({"jump_height": 0.9})
    assert result.status == "PASS_WITH_WARNINGS"

    # Physically impossible height
    result = validator.validate({"jump_height": 2.0})
    assert result.status == "FAIL"
    assert any(issue.severity == ValidationSeverity.ERROR for issue in result.issues)


def test_validation_severity_in_different_contexts() -> None:
    """Test ValidationSeverity usage across different validation scenarios."""
    result = ValidationResult()

    # Add issues of different severities
    result.add_error("metric1", "Critical error")
    result.add_warning("metric2", "Minor warning")
    result.add_info("metric3", "FYI")

    # Verify all severities present
    severities = {issue.severity for issue in result.issues}
    assert ValidationSeverity.ERROR in severities
    assert ValidationSeverity.WARNING in severities
    assert ValidationSeverity.INFO in severities

    # Verify status determined by highest severity
    result.finalize_status()
    assert result.status == "FAIL"  # Due to ERROR


def test_metric_bounds_boundary_values() -> None:
    """Test MetricBounds with boundary values at limits."""
    bounds = MetricBounds(
        absolute_min=0.0,
        practical_min=0.1,
        recreational_min=0.3,
        recreational_max=0.7,
        elite_min=0.5,
        elite_max=1.0,
        absolute_max=1.5,
        unit="m",
    )

    # Test exact boundary values
    assert bounds.is_physically_possible(0.0)  # Exactly at absolute_min
    assert bounds.is_physically_possible(1.5)  # Exactly at absolute_max

    # Test boundary for contains()
    # Exactly at recreational_min
    assert bounds.contains(0.3, AthleteProfile.RECREATIONAL)
    # Exactly at recreational_max
    assert bounds.contains(0.7, AthleteProfile.RECREATIONAL)
