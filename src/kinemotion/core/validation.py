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
        if profile == AthleteProfile.ELDERLY:
            return self.practical_min <= value <= self.recreational_max
        elif profile == AthleteProfile.UNTRAINED:
            return self.practical_min <= value <= self.recreational_max
        elif profile == AthleteProfile.RECREATIONAL:
            return self.recreational_min <= value <= self.recreational_max
        elif profile == AthleteProfile.TRAINED:
            # Trained athletes: midpoint between recreational and elite
            trained_min = (self.recreational_min + self.elite_min) / 2
            trained_max = (self.recreational_max + self.elite_max) / 2
            return trained_min <= value <= trained_max
        elif profile == AthleteProfile.ELITE:
            return self.elite_min <= value <= self.elite_max
        return False

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
