"""Shared validation infrastructure for jump metrics.

Provides base classes and enums for validating Counter Movement Jump (CMJ)
and Drop Jump metrics against physiological bounds.

Contains:
- ValidationSeverity: Severity levels for issues (ERROR, WARNING, INFO)
- ValidationIssue: Single validation issue dataclass
- ValidationResult: Aggregated validation results
- AthleteProfile: Athlete performance categories
- MetricBounds: Physiological bounds for any metric
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class ValidationSeverity(Enum):
    """Severity level for validation issues."""

    ERROR = "ERROR"  # Metrics invalid, likely data corruption
    WARNING = "WARNING"  # Metrics valid but unusual, needs review
    INFO = "INFO"  # Normal variation, informational only


@dataclass
class ValidationIssue:
    """Single validation issue."""

    severity: ValidationSeverity
    metric: str
    message: str
    value: float | None = None
    bounds: tuple[float, float] | None = None


class AthleteProfile(Enum):
    """Athlete performance categories for metric bounds."""

    ELDERLY = "elderly"  # 70+, deconditioned
    UNTRAINED = "untrained"  # Sedentary, no training
    RECREATIONAL = "recreational"  # Fitness class, moderate activity
    TRAINED = "trained"  # Regular athlete, 3-5 years training
    COMPETITIVE = "competitive"  # Regular competition, club/regional level
    ELITE = "elite"  # Competitive athlete, college/professional level


@dataclass
class MetricBounds:
    """Physiological bounds for a single metric across athlete performance levels.

    Defines nested ranges for validating metrics: absolute limits mark impossible
    values (likely data corruption), while performance-level ranges assess whether
    results are typical for an athlete's training background.

    Bounds are ordered: absolute_min < practical_min < recreational_min < elite_min
    and elite_max < recreational_max < absolute_max (symmetric about typical values).

    Attributes:
        absolute_min: Absolute minimum (error threshold, marks data corruption)
        practical_min: Minimum for untrained/elderly athletes
        recreational_min: Minimum for recreational athletes (moderate activity)
        recreational_max: Maximum for recreational athletes
        elite_min: Minimum for elite athletes (competitive level)
        elite_max: Maximum for elite athletes
        absolute_max: Absolute maximum (error threshold, marks data corruption)
        unit: Unit of measurement (e.g., "m", "s", "m/s", "degrees")
    """

    absolute_min: float
    practical_min: float
    recreational_min: float
    recreational_max: float
    elite_min: float
    elite_max: float
    absolute_max: float
    unit: str

    def contains(self, value: float, profile: AthleteProfile) -> bool:
        """Check if value is within bounds for athlete profile."""
        # ELDERLY and UNTRAINED use same bounds (practical to recreational)
        if profile in (AthleteProfile.ELDERLY, AthleteProfile.UNTRAINED):
            return self.practical_min <= value <= self.recreational_max
        if profile == AthleteProfile.RECREATIONAL:
            return self.recreational_min <= value <= self.recreational_max
        if profile == AthleteProfile.ELITE:
            return self.elite_min <= value <= self.elite_max
        if profile == AthleteProfile.TRAINED:
            # Trained athletes: midpoint between recreational and elite
            trained_min = (self.recreational_min + self.elite_min) / 2
            trained_max = (self.recreational_max + self.elite_max) / 2
            return trained_min <= value <= trained_max
        # Competitive: midpoint between trained and elite
        trained_min = (self.recreational_min + self.elite_min) / 2
        trained_max = (self.recreational_max + self.elite_max) / 2
        competitive_min = (trained_min + self.elite_min) / 2
        competitive_max = (trained_max + self.elite_max) / 2
        return competitive_min <= value <= competitive_max

    def is_physically_possible(self, value: float) -> bool:
        """Check if value is within absolute physiological limits."""
        return self.absolute_min <= value <= self.absolute_max


@dataclass
class ValidationResult:
    """Base validation result for jump metrics."""

    issues: list[ValidationIssue] = field(default_factory=list)
    status: str = "PASS"  # "PASS", "PASS_WITH_WARNINGS", "FAIL"
    athlete_profile: AthleteProfile | None = None

    def add_error(
        self,
        metric: str,
        message: str,
        value: float | None = None,
        bounds: tuple[float, float] | None = None,
    ) -> None:
        """Add error-level issue."""
        self.issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR,
                metric=metric,
                message=message,
                value=value,
                bounds=bounds,
            )
        )

    def add_warning(
        self,
        metric: str,
        message: str,
        value: float | None = None,
        bounds: tuple[float, float] | None = None,
    ) -> None:
        """Add warning-level issue."""
        self.issues.append(
            ValidationIssue(
                severity=ValidationSeverity.WARNING,
                metric=metric,
                message=message,
                value=value,
                bounds=bounds,
            )
        )

    def add_info(
        self,
        metric: str,
        message: str,
        value: float | None = None,
    ) -> None:
        """Add info-level issue."""
        self.issues.append(
            ValidationIssue(
                severity=ValidationSeverity.INFO,
                metric=metric,
                message=message,
                value=value,
            )
        )

    def finalize_status(self) -> None:
        """Determine final pass/fail status based on issues."""
        has_errors = any(issue.severity == ValidationSeverity.ERROR for issue in self.issues)
        has_warnings = any(issue.severity == ValidationSeverity.WARNING for issue in self.issues)

        if has_errors:
            self.status = "FAIL"
        elif has_warnings:
            self.status = "PASS_WITH_WARNINGS"
        else:
            self.status = "PASS"

    @abstractmethod
    def to_dict(self) -> dict:
        """Convert validation result to JSON-serializable dictionary."""
        pass


class MetricsValidator(ABC):
    """Base validator for jump metrics."""

    def __init__(self, assumed_profile: AthleteProfile | None = None):
        """Initialize validator.

        Args:
            assumed_profile: If provided, validate against this specific profile.
                            Otherwise, estimate from metrics.
        """
        self.assumed_profile = assumed_profile

    @abstractmethod
    def validate(self, metrics: dict) -> ValidationResult:
        """Validate metrics comprehensively.

        Args:
            metrics: Dictionary with metric values

        Returns:
            ValidationResult with all issues and status
        """
        pass

    def _validate_metric_with_bounds(
        self,
        name: str,
        value: float,
        bounds: MetricBounds,
        profile: AthleteProfile | None,
        result: ValidationResult,
        error_suffix: str = "physically impossible",
        format_str: str = "{value}",
    ) -> None:
        """Generic validation for metrics with physical and profile bounds.

        Args:
            name: Metric name for messages
            value: Metric value
            bounds: Bounds definition
            profile: Athlete profile for expected ranges (can be None)
            result: Validation result to add issues to
            error_suffix: Description for out-of-bounds errors
            format_str: Format string for value display
        """
        formatted_value = format_str.format(value=value)
        display_name = name.replace("_", " ").title()

        if not bounds.is_physically_possible(value):
            result.add_error(
                name,
                f"{display_name} {formatted_value} {error_suffix}",
                value=value,
                bounds=(bounds.absolute_min, bounds.absolute_max),
            )
        elif profile is not None and bounds.contains(value, profile):
            result.add_info(
                name,
                f"{display_name} {formatted_value} within expected range for {profile.value}",
                value=value,
            )
        elif profile is not None:
            expected_min, expected_max = self._get_profile_range(profile, bounds)
            result.add_warning(
                name,
                f"{display_name} {formatted_value} outside typical range "
                f"[{expected_min:.3f}-{expected_max:.3f}] for {profile.value}",
                value=value,
                bounds=(expected_min, expected_max),
            )

    @staticmethod
    def _get_profile_range(profile: AthleteProfile, bounds: MetricBounds) -> tuple[float, float]:
        """Get min/max bounds for specific profile.

        Args:
            profile: Athlete profile
            bounds: Metric bounds definition

        Returns:
            Tuple of (min, max) bounds for the profile
        """
        profile_ranges = {
            AthleteProfile.ELDERLY: (bounds.practical_min, bounds.recreational_max),
            AthleteProfile.UNTRAINED: (bounds.practical_min, bounds.recreational_max),
            AthleteProfile.RECREATIONAL: (bounds.recreational_min, bounds.recreational_max),
            AthleteProfile.TRAINED: (
                (bounds.recreational_min + bounds.elite_min) / 2,
                (bounds.recreational_max + bounds.elite_max) / 2,
            ),
            AthleteProfile.COMPETITIVE: (
                ((bounds.recreational_min + bounds.elite_min) / 2 + bounds.elite_min) / 2,
                ((bounds.recreational_max + bounds.elite_max) / 2 + bounds.elite_max) / 2,
            ),
            AthleteProfile.ELITE: (bounds.elite_min, bounds.elite_max),
        }
        return profile_ranges.get(profile, (bounds.absolute_min, bounds.absolute_max))
