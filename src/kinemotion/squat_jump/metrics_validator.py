"""SJ metrics validation using physiological bounds.

Comprehensive validation of Squat Jump metrics against
biomechanical bounds and consistency tests.

Provides severity levels (ERROR, WARNING, INFO) for different categories
of metric issues.
"""

from dataclasses import dataclass

from kinemotion.core.types import MetricsDict
from kinemotion.core.validation import (
    AthleteProfile,
    MetricsValidator,
    ValidationResult,
)
from kinemotion.squat_jump.validation_bounds import (
    MetricConsistency,
    SJBounds,
    estimate_athlete_profile,
)


@dataclass
class SJValidationResult(ValidationResult):
    """SJ-specific validation result."""

    peak_power_consistency: float | None = None
    force_height_consistency: float | None = None

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
            "peak_power_consistency_percent": self.peak_power_consistency,
            "force_height_consistency_percent": self.force_height_consistency,
        }


class SJMetricsValidator(MetricsValidator):
    """Comprehensive SJ metrics validator."""

    @staticmethod
    def _get_metric_value(
        data: dict, key_with_suffix: str, key_without_suffix: str
    ) -> float | None:
        """Get metric value, supporting both suffixed and legacy key formats.

        Args:
            data: Dictionary containing metrics
            key_with_suffix: Key with unit suffix (e.g., "flight_time_ms")
            key_without_suffix: Legacy key without suffix (e.g., "flight_time")

        Returns:
            Metric value or None if not found
        """
        return data.get(key_with_suffix) or data.get(key_without_suffix)

    @staticmethod
    def _convert_raw_duration_to_seconds(value_raw: float) -> float:
        """Convert raw duration value to seconds.

        Handles legacy values that may be in seconds (<10) vs milliseconds (>10).
        This heuristic works because no SJ duration metric is between 10ms and 10s.

        Args:
            value_raw: Raw duration value (may be seconds or milliseconds)

        Returns:
            Duration in seconds
        """
        if value_raw < 10:  # Likely in seconds
            return value_raw
        return value_raw / 1000.0

    def validate(self, metrics: MetricsDict) -> SJValidationResult:
        """Validate SJ metrics comprehensively.

        Args:
            metrics: Dictionary with SJ metric values

        Returns:
            SJValidationResult with all issues and status
        """
        result = SJValidationResult()

        # Estimate athlete profile if not provided
        if self.assumed_profile:
            result.athlete_profile = self.assumed_profile
        else:
            result.athlete_profile = estimate_athlete_profile(metrics)

        profile = result.athlete_profile

        # Extract metric values (handle nested "data" structure)
        data = metrics.get("data", metrics)  # Support both structures

        # PRIMARY BOUNDS CHECKS
        self._check_flight_time(data, result, profile)
        self._check_jump_height(data, result, profile)
        self._check_squat_hold_duration(data, result, profile)
        self._check_concentric_duration(data, result, profile)
        self._check_peak_concentric_velocity(data, result, profile)
        self._check_power_metrics(data, result, profile)
        self._check_force_metrics(data, result, profile)

        # CROSS-VALIDATION CHECKS
        self._check_flight_time_height_consistency(data, result)
        self._check_power_velocity_consistency(data, result)

        # CONSISTENCY CHECKS
        self._check_squat_concentric_ratio(data, result)

        # Finalize status
        result.finalize_status()

        return result

    def _check_flight_time(
        self, metrics: MetricsDict, result: SJValidationResult, profile: AthleteProfile
    ) -> None:
        """Validate flight time."""
        flight_time_raw = self._get_metric_value(metrics, "flight_time_ms", "flight_time")
        if flight_time_raw is None:
            return

        flight_time = self._convert_raw_duration_to_seconds(flight_time_raw)
        bounds = SJBounds.FLIGHT_TIME
        error_label = (
            "below frame rate resolution limit"
            if flight_time < bounds.absolute_min
            else "exceeds elite human capability"
        )

        self._validate_metric_with_bounds(
            "flight_time",
            flight_time,
            bounds,
            profile,
            result,
            error_suffix=error_label,
            format_str="{value:.3f}s",
        )

    def _check_jump_height(
        self, metrics: MetricsDict, result: SJValidationResult, profile: AthleteProfile
    ) -> None:
        """Validate jump height."""
        jump_height = self._get_metric_value(metrics, "jump_height_m", "jump_height")
        if jump_height is None:
            return

        bounds = SJBounds.JUMP_HEIGHT
        error_label = (
            "essentially no jump (noise)"
            if jump_height < bounds.absolute_min
            else "exceeds human capability"
        )

        self._validate_metric_with_bounds(
            "jump_height",
            jump_height,
            bounds,
            profile,
            result,
            error_suffix=error_label,
            format_str="{value:.3f}m",
        )

    def _check_squat_hold_duration(
        self, metrics: MetricsDict, result: SJValidationResult, profile: AthleteProfile
    ) -> None:
        """Validate squat hold duration."""
        duration_raw = self._get_metric_value(
            metrics, "squat_hold_duration_ms", "squat_hold_duration"
        )
        if duration_raw is None:
            return

        duration = self._convert_raw_duration_to_seconds(duration_raw)
        bounds = SJBounds.SQUAT_HOLD_DURATION

        if not bounds.is_physically_possible(duration):
            result.add_error(
                "squat_hold_duration",
                f"Squat hold duration {duration:.3f}s outside physical limits",
                value=duration,
                bounds=(bounds.absolute_min, bounds.absolute_max),
            )
        else:
            result.add_info(
                "squat_hold_duration",
                f"Squat hold duration {duration:.3f}s",
                value=duration,
            )

    def _check_concentric_duration(
        self, metrics: MetricsDict, result: SJValidationResult, profile: AthleteProfile
    ) -> None:
        """Validate concentric duration."""
        duration_raw = self._get_metric_value(
            metrics, "concentric_duration_ms", "concentric_duration"
        )
        if duration_raw is None:
            return

        duration = self._convert_raw_duration_to_seconds(duration_raw)
        bounds = SJBounds.CONCENTRIC_DURATION

        if not bounds.is_physically_possible(duration):
            if duration < bounds.absolute_min:
                result.add_error(
                    "concentric_duration",
                    f"Concentric duration {duration:.3f}s likely detection error",
                    value=duration,
                    bounds=(bounds.absolute_min, bounds.absolute_max),
                )
            else:
                result.add_error(
                    "concentric_duration",
                    f"Concentric duration {duration:.3f}s includes pre-takeoff phase",
                    value=duration,
                    bounds=(bounds.absolute_min, bounds.absolute_max),
                )
        else:
            result.add_info(
                "concentric_duration",
                f"Concentric duration {duration:.3f}s",
                value=duration,
            )

    def _check_peak_concentric_velocity(
        self, metrics: MetricsDict, result: SJValidationResult, profile: AthleteProfile
    ) -> None:
        """Validate peak concentric velocity."""
        velocity = self._get_metric_value(
            metrics, "peak_concentric_velocity_m_s", "peak_concentric_velocity"
        )
        if velocity is None:
            return

        bounds = SJBounds.PEAK_CONCENTRIC_VELOCITY
        error_suffix = "insufficient to leave ground" if velocity < bounds.absolute_min else ""

        self._validate_metric_with_bounds(
            "peak_concentric_velocity",
            velocity,
            bounds,
            profile,
            result,
            error_suffix=error_suffix,
            format_str="{value:.3f} m/s",
        )

    def _check_power_metrics(
        self, metrics: MetricsDict, result: SJValidationResult, profile: AthleteProfile
    ) -> None:
        """Validate power metrics (peak and mean)."""
        power_checks = [
            ("peak_power", "peak_power_w", SJBounds.PEAK_POWER, ""),
            ("mean_power", "mean_power_w", SJBounds.MEAN_POWER, ""),
        ]

        for metric_name, key_name, bounds, _error_suffix in power_checks:
            power = self._get_metric_value(metrics, key_name, metric_name)
            if power is None:
                continue

            # Skip validation if mass wasn't provided (power calculations require mass)
            if power == 0 and metrics.get("mass_kg") is None:
                result.add_info(
                    metric_name,
                    f"{metric_name.replace('_', ' ').title()} not calculated (mass not provided)",
                    value=power,
                )
                continue

            if not bounds.is_physically_possible(power):
                result.add_error(
                    metric_name,
                    f"Peak {metric_name.replace('_', ' ')} {power:.0f} W outside physical limits",
                    value=power,
                    bounds=(bounds.absolute_min, bounds.absolute_max),
                )
            else:
                result.add_info(
                    metric_name,
                    f"{metric_name.replace('_', ' ').title()} {power:.0f} W",
                    value=power,
                )

    def _check_force_metrics(
        self, metrics: MetricsDict, result: SJValidationResult, profile: AthleteProfile
    ) -> None:
        """Validate force metrics."""
        peak_force = self._get_metric_value(metrics, "peak_force_n", "peak_force")
        if peak_force is None:
            return

        # Skip validation if mass wasn't provided
        if peak_force == 0 and metrics.get("mass_kg") is None:
            result.add_info(
                "peak_force",
                "Peak force not calculated (mass not provided)",
                value=peak_force,
            )
            return

        bounds = SJBounds.PEAK_FORCE

        if not bounds.is_physically_possible(peak_force):
            result.add_error(
                "peak_force",
                f"Peak force {peak_force:.0f} N outside physical limits",
                value=peak_force,
                bounds=(bounds.absolute_min, bounds.absolute_max),
            )
        else:
            result.add_info(
                "peak_force",
                f"Peak force {peak_force:.0f} N",
                value=peak_force,
            )

    def _check_flight_time_height_consistency(
        self, metrics: MetricsDict, result: SJValidationResult
    ) -> None:
        """Verify jump height is consistent with flight time."""
        flight_time_ms = metrics.get("flight_time_ms")
        jump_height = metrics.get("jump_height_m")

        if flight_time_ms is None or jump_height is None:
            return

        # Convert ms to seconds
        flight_time = flight_time_ms / 1000.0

        # Calculate expected height using kinematic formula: h = g*t²/8
        g = 9.81
        expected_height = (g * flight_time**2) / 8
        error_pct = abs(jump_height - expected_height) / expected_height

        result.force_height_consistency = error_pct

        if error_pct > MetricConsistency.HEIGHT_FLIGHT_TIME_TOLERANCE:
            result.add_error(
                "height_flight_time_consistency",
                f"Jump height {jump_height:.3f}m inconsistent with flight "
                f"time {flight_time:.3f}s (expected {expected_height:.3f}m, "
                f"error {error_pct * 100:.1f}%)",
                value=error_pct,
                bounds=(0, MetricConsistency.HEIGHT_FLIGHT_TIME_TOLERANCE),
            )
        else:
            result.add_info(
                "height_flight_time_consistency",
                f"Jump height and flight time consistent (error {error_pct * 100:.1f}%)",
                value=error_pct,
            )

    def _check_power_velocity_consistency(
        self, metrics: MetricsDict, result: SJValidationResult
    ) -> None:
        """Verify power is consistent with velocity and mass."""
        velocity = metrics.get("peak_concentric_velocity_m_s")
        peak_power = metrics.get("peak_power_w")
        mass_kg = metrics.get("mass_kg")

        if velocity is None or peak_power is None or mass_kg is None:
            return

        # Calculate expected power: P = F × v = (m × a) × v
        # For simplicity, assume peak acceleration occurs at peak velocity
        # TODO: This needs biomechanical validation by specialist
        g = 9.81
        # Estimate force during concentric phase (simplified)
        expected_force = mass_kg * g * 2  # Assume 2x bodyweight force
        expected_power = expected_force * velocity
        error_pct = abs(peak_power - expected_power) / expected_power

        result.peak_power_consistency = error_pct

        if error_pct > MetricConsistency.POWER_VELOCITY_TOLERANCE:
            result.add_warning(
                "power_velocity_consistency",
                f"Peak power {peak_power:.0f} W inconsistent with velocity "
                f"{velocity:.2f} m/s and mass {mass_kg:.1f} kg "
                f"(expected ~{expected_power:.0f} W, error {error_pct * 100:.1f}%)",
                value=error_pct,
                bounds=(0, MetricConsistency.POWER_VELOCITY_TOLERANCE),
            )
        else:
            result.add_info(
                "power_velocity_consistency",
                f"Power and velocity consistent (error {error_pct * 100:.1f}%)",
                value=error_pct,
            )

    def _check_squat_concentric_ratio(
        self, metrics: MetricsDict, result: SJValidationResult
    ) -> None:
        """Check squat hold duration to concentric duration ratio."""
        squat_ms = metrics.get("squat_hold_duration_ms")
        concentric_ms = metrics.get("concentric_duration_ms")

        if squat_ms is None or concentric_ms is None or concentric_ms < 50:
            return

        # Convert to seconds for ratio calculation
        squat = squat_ms / 1000.0
        concentric = concentric_ms / 1000.0
        ratio = squat / concentric

        if ratio > MetricConsistency.SQUAT_CONCENTRIC_RATIO_MAX:
            result.add_warning(
                "squat_concentric_ratio",
                f"Squat hold {ratio:.2f}x concentric duration: "
                f"Unusually long static phase, verify squat detection",
                value=ratio,
                bounds=(
                    MetricConsistency.SQUAT_CONCENTRIC_RATIO_MIN,
                    MetricConsistency.SQUAT_CONCENTRIC_RATIO_MAX,
                ),
            )
        else:
            result.add_info(
                "squat_concentric_ratio",
                f"Squat-to-concentric ratio {ratio:.2f} within expected range",
                value=ratio,
            )
