"""Drop jump metrics validation using physiological bounds.

Comprehensive validation of Drop Jump metrics against biomechanical bounds,
consistency checks, and cross-validation of RSI calculation.

Provides severity levels (ERROR, WARNING, INFO) for different categories
of metric issues.
"""

from dataclasses import dataclass

from kinemotion.core.types import MetricsDict
from kinemotion.core.validation import (
    MetricsValidator,
    ValidationResult,
)
from kinemotion.dropjump.validation_bounds import (
    DropJumpBounds,
    estimate_athlete_profile,
)


@dataclass
class DropJumpValidationResult(ValidationResult):
    """Drop jump-specific validation result."""

    rsi: float | None = None
    contact_flight_ratio: float | None = None
    height_kinematic_trajectory_consistency: float | None = None  # % error

    def to_dict(self) -> dict:
        """Convert validation result to JSON-serializable dictionary.

        Returns:
            Dictionary with status, issues, and consistency metrics.
        """
        return {
            "status": self.status,
            "issues": [
                {
                    "severity": issue.severity.value,
                    "metric": issue.metric,
                    "message": issue.message,
                    "value": issue.value,
                    "bounds": issue.bounds,
                }
                for issue in self.issues
            ],
            "athlete_profile": (self.athlete_profile.value if self.athlete_profile else None),
            "rsi": self.rsi,
            "contact_flight_ratio": self.contact_flight_ratio,
            "height_kinematic_trajectory_consistency_percent": (
                self.height_kinematic_trajectory_consistency
            ),
        }


class DropJumpMetricsValidator(MetricsValidator):
    """Comprehensive drop jump metrics validator."""

    def validate(self, metrics: MetricsDict) -> DropJumpValidationResult:
        """Validate drop jump metrics comprehensively.

        Args:
            metrics: Dictionary with drop jump metric values

        Returns:
            DropJumpValidationResult with all issues and status
        """
        result = DropJumpValidationResult()

        # Estimate athlete profile if not provided
        if self.assumed_profile:
            result.athlete_profile = self.assumed_profile
        else:
            result.athlete_profile = estimate_athlete_profile(metrics)

        # Extract metric values (handle nested "data" structure)
        data = metrics.get("data", metrics)  # Support both structures

        contact_time_ms = data.get("ground_contact_time_ms")
        flight_time_ms = data.get("flight_time_ms")
        jump_height_m = data.get("jump_height_m")
        jump_height_kinematic_m = data.get("jump_height_kinematic_m")
        jump_height_trajectory_m = data.get("jump_height_trajectory_m")

        # Validate individual metrics
        if contact_time_ms is not None:
            self._check_contact_time(contact_time_ms, result)

        if flight_time_ms is not None:
            self._check_flight_time(flight_time_ms, result)

        if jump_height_m is not None:
            self._check_jump_height(jump_height_m, result)

        # Cross-validation
        if contact_time_ms is not None and flight_time_ms is not None:
            self._check_rsi(contact_time_ms, flight_time_ms, result)

        # Dual height validation (kinematic vs trajectory)
        if jump_height_kinematic_m is not None and jump_height_trajectory_m is not None:
            self._check_dual_height_consistency(
                jump_height_kinematic_m, jump_height_trajectory_m, result
            )

        # Finalize status
        result.finalize_status()

        return result

    def _check_contact_time(
        self, contact_time_ms: float, result: DropJumpValidationResult
    ) -> None:
        """Validate contact time."""
        contact_time_s = contact_time_ms / 1000.0
        bounds = DropJumpBounds.CONTACT_TIME

        if not bounds.is_physically_possible(contact_time_s):
            result.add_error(
                "contact_time",
                f"Contact time {contact_time_s:.3f}s physically impossible",
                value=contact_time_s,
                bounds=(bounds.absolute_min, bounds.absolute_max),
            )
        elif result.athlete_profile and not bounds.contains(
            contact_time_s, result.athlete_profile
        ):
            profile_name = result.athlete_profile.value
            result.add_warning(
                "contact_time",
                f"Contact time {contact_time_s:.3f}s unusual for {profile_name} athlete",
                value=contact_time_s,
            )

    def _check_flight_time(self, flight_time_ms: float, result: DropJumpValidationResult) -> None:
        """Validate flight time."""
        flight_time_s = flight_time_ms / 1000.0
        bounds = DropJumpBounds.FLIGHT_TIME

        if not bounds.is_physically_possible(flight_time_s):
            result.add_error(
                "flight_time",
                f"Flight time {flight_time_s:.3f}s physically impossible",
                value=flight_time_s,
                bounds=(bounds.absolute_min, bounds.absolute_max),
            )
        elif result.athlete_profile and not bounds.contains(flight_time_s, result.athlete_profile):
            profile_name = result.athlete_profile.value
            result.add_warning(
                "flight_time",
                f"Flight time {flight_time_s:.3f}s unusual for {profile_name} athlete",
                value=flight_time_s,
            )

    def _check_jump_height(self, jump_height_m: float, result: DropJumpValidationResult) -> None:
        """Validate jump height."""
        bounds = DropJumpBounds.JUMP_HEIGHT

        if not bounds.is_physically_possible(jump_height_m):
            result.add_error(
                "jump_height",
                f"Jump height {jump_height_m:.3f}m physically impossible",
                value=jump_height_m,
                bounds=(bounds.absolute_min, bounds.absolute_max),
            )
        elif result.athlete_profile and not bounds.contains(jump_height_m, result.athlete_profile):
            profile_name = result.athlete_profile.value
            result.add_warning(
                "jump_height",
                f"Jump height {jump_height_m:.3f}m unusual for {profile_name} athlete",
                value=jump_height_m,
            )

    def _check_rsi(
        self,
        contact_time_ms: float,
        flight_time_ms: float,
        result: DropJumpValidationResult,
    ) -> None:
        """Validate RSI and cross-check consistency."""
        contact_time_s = contact_time_ms / 1000.0
        flight_time_s = flight_time_ms / 1000.0

        if contact_time_s > 0 and flight_time_s > 0:
            rsi = flight_time_s / contact_time_s
            result.rsi = rsi
            result.contact_flight_ratio = contact_time_s / flight_time_s

            bounds = DropJumpBounds.RSI

            if not bounds.is_physically_possible(rsi):
                result.add_error(
                    "rsi",
                    f"RSI {rsi:.2f} physically impossible",
                    value=rsi,
                    bounds=(bounds.absolute_min, bounds.absolute_max),
                )
            elif result.athlete_profile and not bounds.contains(rsi, result.athlete_profile):
                result.add_warning(
                    "rsi",
                    f"RSI {rsi:.2f} unusual for {result.athlete_profile.value} athlete",
                    value=rsi,
                )

    def _check_dual_height_consistency(
        self,
        jump_height_kinematic_m: float,
        jump_height_trajectory_m: float,
        result: DropJumpValidationResult,
    ) -> None:
        """Validate consistency between kinematic and trajectory-based heights.

        Kinematic height (h = g*t²/8) comes from flight time (objective).
        Trajectory height comes from position tracking (subject to landmark
        detection noise).

        Expected correlation: r > 0.95, absolute difference < 5% for quality video.
        """
        if jump_height_kinematic_m <= 0 or jump_height_trajectory_m <= 0:
            return  # Skip if either value is missing or invalid

        # Calculate percentage difference
        avg_height = (jump_height_kinematic_m + jump_height_trajectory_m) / 2.0
        if avg_height > 0:
            abs_diff = abs(jump_height_kinematic_m - jump_height_trajectory_m)
            percent_error = (abs_diff / avg_height) * 100.0
            result.height_kinematic_trajectory_consistency = percent_error

            # Allow 10% tolerance for typical video processing noise
            if percent_error > 10.0:
                result.add_warning(
                    "height_consistency",
                    f"Kinematic ({jump_height_kinematic_m:.3f}m) and trajectory "
                    f"({jump_height_trajectory_m:.3f}m) heights differ by "
                    f"{percent_error:.1f}%. May indicate landmark detection "
                    "issues or video quality problems.",
                    value=percent_error,
                    bounds=(0, 10),
                )
