"""Integration tests for drop jump validation."""

import json
from typing import cast

from kinemotion.dropjump.kinematics import DropJumpMetrics
from kinemotion.dropjump.metrics_validator import (
    DropJumpMetricsValidator,
)


def test_dropjump_metrics_validation_integration() -> None:
    """Test that validation results are attached to drop jump metrics.

    Verifies validation runs during analysis and results are available
    in metrics object.
    """
    # Create synthetic drop jump metrics
    metrics = DropJumpMetrics()
    metrics.ground_contact_time = 0.40  # seconds, recreational
    metrics.flight_time = 0.65  # seconds, recreational
    metrics.jump_height = 0.50  # meters
    metrics.jump_height_kinematic = 0.50
    metrics.contact_start_frame = 10
    metrics.contact_end_frame = 22
    metrics.flight_start_frame = 22
    metrics.flight_end_frame = 41
    metrics.peak_height_frame = 31

    # Validate metrics
    validator = DropJumpMetricsValidator()
    validation_result = validator.validate(cast(dict, metrics.to_dict()))
    metrics.validation_result = validation_result

    # Assert: Validation result exists and has expected structure
    assert metrics.validation_result is not None
    assert hasattr(metrics.validation_result, "status")
    assert hasattr(metrics.validation_result, "issues")
    assert metrics.validation_result.status in ["PASS", "PASS_WITH_WARNINGS", "FAIL"]
    assert metrics.validation_result.rsi is not None


def test_dropjump_metrics_validation_in_json_output() -> None:
    """Test that validation results appear in JSON export.

    Verifies that when metrics.to_dict() is called, validation
    results are included in the output.
    """
    # Create elite drop jump metrics
    metrics = DropJumpMetrics()
    metrics.ground_contact_time = 0.25  # seconds, elite
    metrics.flight_time = 0.85  # seconds, elite
    metrics.jump_height = 0.75  # meters, elite
    metrics.jump_height_kinematic = 0.75
    metrics.contact_start_frame = 8
    metrics.contact_end_frame = 15
    metrics.flight_start_frame = 15
    metrics.flight_end_frame = 41
    metrics.peak_height_frame = 28

    # Add validation result
    validator = DropJumpMetricsValidator()
    validation_result = validator.validate(cast(dict, metrics.to_dict()))
    metrics.validation_result = validation_result

    # Export to dict
    result_dict = metrics.to_dict()

    # Assert: Validation appears in JSON output
    assert "validation" in result_dict
    assert "status" in result_dict["validation"]
    assert "issues" in result_dict["validation"]
    assert isinstance(result_dict["validation"]["issues"], list)
    assert "rsi" in result_dict["validation"]


def test_dropjump_validation_result_serialization() -> None:
    """Test that ValidationResult can be serialized to JSON.

    Verifies to_dict() method produces JSON-compatible output.
    """
    # Create metrics that will trigger warnings (impossible RSI)
    metrics_dict = {
        "data": {
            "ground_contact_time_ms": 1500.0,  # Excessive contact time
            "flight_time_ms": 400.0,  # Short flight
            "jump_height_m": 0.20,  # Low height
        }
    }

    # Validate
    validator = DropJumpMetricsValidator()
    validation_result = validator.validate(metrics_dict)

    # Serialize to dict
    result_dict = validation_result.to_dict()

    # Assert: Can be serialized to JSON
    assert isinstance(result_dict, dict)
    json_str = json.dumps(result_dict)
    assert isinstance(json_str, str)

    # Assert: Contains expected keys
    assert "status" in result_dict
    assert "issues" in result_dict
    assert isinstance(result_dict["issues"], list)
    assert "rsi" in result_dict

    # Assert: Issues are JSON-serializable
    for issue in result_dict["issues"]:
        assert "severity" in issue
        assert "metric" in issue
        assert "message" in issue


def test_dropjump_rsi_calculation() -> None:
    """Test RSI (Reactive Strength Index) calculation during validation.

    RSI = flight_time / contact_time, key metric for drop jump assessment.
    """
    # Create metrics for elite athlete with high RSI
    metrics = DropJumpMetrics()
    metrics.ground_contact_time = 0.20  # Very fast contact
    metrics.flight_time = 0.80  # Long flight
    metrics.jump_height = 0.80  # High jump

    validator = DropJumpMetricsValidator()
    validation_result = validator.validate(cast(dict, metrics.to_dict()))

    # Assert: RSI calculated correctly
    expected_rsi = 0.80 / 0.20  # Should be 4.0
    assert validation_result.rsi is not None
    assert abs(validation_result.rsi - expected_rsi) < 0.01  # Allow small rounding error


def test_dropjump_validation_athlete_profile_estimation() -> None:
    """Test that drop jump validator estimates athlete profile correctly."""
    # Recreational athlete
    recreational_metrics = DropJumpMetrics()
    recreational_metrics.ground_contact_time = 0.45
    recreational_metrics.flight_time = 0.65
    recreational_metrics.jump_height = 0.45

    validator = DropJumpMetricsValidator()
    result = validator.validate(cast(dict, recreational_metrics.to_dict()))

    assert result.athlete_profile is not None
    assert result.athlete_profile.value in ["recreational", "trained", "untrained"]

    # Elite athlete
    elite_metrics = DropJumpMetrics()
    elite_metrics.ground_contact_time = 0.20
    elite_metrics.flight_time = 0.95
    elite_metrics.jump_height = 0.90

    result_elite = validator.validate(cast(dict, elite_metrics.to_dict()))
    assert result_elite.athlete_profile is not None


def test_dropjump_dual_height_validation_consistency() -> None:
    """Test validation of dual height methods (kinematic vs trajectory).

    Validates consistency between:
    - jump_height_kinematic_m (from flight time: h = g*t²/8)
    - jump_height_trajectory_normalized (from position tracking)
    """
    metrics = DropJumpMetrics()
    metrics.ground_contact_time = 0.25
    metrics.flight_time = 0.70
    metrics.jump_height_kinematic = 0.60  # From flight time
    # From position tracking (3% difference)
    metrics.jump_height_trajectory_m = 0.62
    metrics.jump_height_trajectory = 0.15  # Normalized (doesn't matter here)

    validator = DropJumpMetricsValidator()
    result = validator.validate(cast(dict, metrics.to_dict()))

    # Should detect consistency with tolerance
    assert result.height_kinematic_trajectory_consistency is not None
    assert result.height_kinematic_trajectory_consistency < 10.0
    # Should not raise warning for <10% difference
    consistency_issues = [issue for issue in result.issues if issue.metric == "height_consistency"]
    assert len(consistency_issues) == 0


def test_dropjump_dual_height_validation_poor_quality() -> None:
    """Test detection of poor agreement between height calculation methods.

    When kinematic and trajectory heights differ significantly, suggests
    video quality or landmark detection issues.
    """
    metrics = DropJumpMetrics()
    metrics.ground_contact_time = 0.30
    metrics.flight_time = 0.75
    metrics.jump_height_kinematic = 0.70  # From flight time
    metrics.jump_height_trajectory_m = 0.55  # From position tracking (20% difference)
    metrics.jump_height_trajectory = 0.12  # Normalized

    validator = DropJumpMetricsValidator()
    result = validator.validate(cast(dict, metrics.to_dict()))

    # Should detect large inconsistency and warn
    assert result.height_kinematic_trajectory_consistency is not None
    assert result.height_kinematic_trajectory_consistency > 10.0
    consistency_issues = [issue for issue in result.issues if issue.metric == "height_consistency"]
    assert len(consistency_issues) > 0
    assert consistency_issues[0].severity.value == "WARNING"
