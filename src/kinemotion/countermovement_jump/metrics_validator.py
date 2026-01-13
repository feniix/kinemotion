"""CMJ metrics validation using physiological bounds.

Comprehensive validation of Counter Movement Jump metrics against
biomechanical bounds, cross-validation checks, and consistency tests.

Provides severity levels (ERROR, WARNING, INFO) for different categories
of metric issues.
"""

from dataclasses import dataclass

from kinemotion.core.types import MetricsDict
from kinemotion.core.validation import (
    AthleteProfile,
    MetricBounds,
    MetricsValidator,
    ValidationResult,
)
from kinemotion.countermovement_jump.validation_bounds import (
    CMJBounds,
    MetricConsistency,
    RSIBounds,
    TripleExtensionBounds,
    estimate_athlete_profile,
)


@dataclass
class CMJValidationResult(ValidationResult):
    """CMJ-specific validation result."""

    rsi: float | None = None
    height_flight_time_consistency: float | None = None  # % error
    velocity_height_consistency: float | None = None  # % error
    depth_height_ratio: float | None = None
    contact_depth_ratio: float | None = None

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
            "height_flight_time_consistency_percent": (self.height_flight_time_consistency),
            "velocity_height_consistency_percent": self.velocity_height_consistency,
            "depth_height_ratio": self.depth_height_ratio,
            "contact_depth_ratio": self.contact_depth_ratio,
        }


class CMJMetricsValidator(MetricsValidator):
    """Comprehensive CMJ metrics validator."""

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
        This heuristic works because no CMJ duration metric is between 10ms and 10s.

        Args:
            value_raw: Raw duration value (may be seconds or milliseconds)

        Returns:
            Duration in seconds
        """
        if value_raw < 10:  # Likely in seconds
            return value_raw
        return value_raw / 1000.0

    def validate(self, metrics: MetricsDict) -> CMJValidationResult:
        """Validate CMJ metrics comprehensively.

        Args:
            metrics: Dictionary with CMJ metric values

        Returns:
            CMJValidationResult with all issues and status
        """
        result = CMJValidationResult()

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
        self._check_countermovement_depth(data, result, profile)
        self._check_concentric_duration(data, result, profile)
        self._check_eccentric_duration(data, result, profile)
        self._check_peak_velocities(data, result, profile)

        # CROSS-VALIDATION CHECKS
        self._check_flight_time_height_consistency(data, result)
        self._check_velocity_height_consistency(data, result)
        self._check_rsi_validity(data, result, profile)

        # CONSISTENCY CHECKS
        self._check_depth_height_ratio(data, result)
        self._check_contact_depth_ratio(data, result)

        # TRIPLE EXTENSION ANGLES
        self._check_triple_extension(data, result, profile)

        # Finalize status
        result.finalize_status()

        return result

    def _check_flight_time(
        self, metrics: MetricsDict, result: CMJValidationResult, profile: AthleteProfile
    ) -> None:
        """Validate flight time."""
        flight_time_raw = self._get_metric_value(metrics, "flight_time_ms", "flight_time")
        if flight_time_raw is None:
            return

        flight_time = self._convert_raw_duration_to_seconds(flight_time_raw)
        bounds = CMJBounds.FLIGHT_TIME
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
        self, metrics: MetricsDict, result: CMJValidationResult, profile: AthleteProfile
    ) -> None:
        """Validate jump height."""
        jump_height = self._get_metric_value(metrics, "jump_height_m", "jump_height")
        if jump_height is None:
            return

        bounds = CMJBounds.JUMP_HEIGHT
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

    def _check_countermovement_depth(
        self, metrics: MetricsDict, result: CMJValidationResult, profile: AthleteProfile
    ) -> None:
        """Validate countermovement depth."""
        depth = self._get_metric_value(metrics, "countermovement_depth_m", "countermovement_depth")
        if depth is None:
            return

        bounds = CMJBounds.COUNTERMOVEMENT_DEPTH
        error_label = (
            "essentially no squat" if depth < bounds.absolute_min else "exceeds physical limit"
        )

        self._validate_metric_with_bounds(
            "countermovement_depth",
            depth,
            bounds,
            profile,
            result,
            error_suffix=error_label,
            format_str="{value:.3f}m",
        )

    def _validate_metric_with_bounds(
        self,
        name: str,
        value: float,
        bounds: MetricBounds,
        profile: AthleteProfile,
        result: CMJValidationResult,
        error_suffix: str,
        format_str: str = "{value}",
    ) -> None:
        """Generic validation for metrics with physical and profile bounds.

        Args:
            name: Metric name for messages
            value: Metric value
            bounds: Bounds definition
            profile: Athlete profile for expected ranges
            result: Validation result to add issues to
            error_suffix: Description for out-of-bounds errors
            format_str: Format string for value display
        """
        if not bounds.is_physically_possible(value):
            formatted_value = format_str.format(value=value)
            result.add_error(
                name,
                f"{name.replace('_', ' ').title()} {formatted_value} {error_suffix}",
                value=value,
                bounds=(bounds.absolute_min, bounds.absolute_max),
            )
        elif bounds.contains(value, profile):
            formatted_value = format_str.format(value=value)
            result.add_info(
                name,
                f"{name.replace('_', ' ').title()} {formatted_value} "
                f"within expected range for {profile.value}",
                value=value,
            )
        else:
            expected_min, expected_max = self._get_profile_range(profile, bounds)
            formatted_value = format_str.format(value=value)
            result.add_warning(
                name,
                f"{name.replace('_', ' ').title()} {formatted_value} "
                f"outside typical range [{expected_min:.3f}-{expected_max:.3f}] "
                f"for {profile.value}",
                value=value,
                bounds=(expected_min, expected_max),
            )

    def _check_concentric_duration(
        self, metrics: MetricsDict, result: CMJValidationResult, profile: AthleteProfile
    ) -> None:
        """Validate concentric duration (contact time)."""
        duration_raw = self._get_metric_value(
            metrics, "concentric_duration_ms", "concentric_duration"
        )
        if duration_raw is None:
            return

        duration = self._convert_raw_duration_to_seconds(duration_raw)
        bounds = CMJBounds.CONCENTRIC_DURATION

        if not bounds.is_physically_possible(duration):
            if duration < bounds.absolute_min:
                result.add_error(
                    "concentric_duration",
                    f"Concentric duration {duration:.3f}s likely phase detection error",
                    value=duration,
                    bounds=(bounds.absolute_min, bounds.absolute_max),
                )
            else:
                result.add_error(
                    "concentric_duration",
                    f"Concentric duration {duration:.3f}s likely includes standing phase",
                    value=duration,
                    bounds=(bounds.absolute_min, bounds.absolute_max),
                )
        else:
            # NOTE: Downgraded from WARNING to INFO - standing end detection has
            # ~117ms offset causing misleading warnings. See issue #16.
            result.add_info(
                "concentric_duration",
                f"Concentric duration {duration:.3f}s",
                value=duration,
            )

    def _check_eccentric_duration(
        self, metrics: MetricsDict, result: CMJValidationResult, profile: AthleteProfile
    ) -> None:
        """Validate eccentric duration."""
        duration_raw = self._get_metric_value(
            metrics, "eccentric_duration_ms", "eccentric_duration"
        )
        if duration_raw is None:
            return

        duration = self._convert_raw_duration_to_seconds(duration_raw)
        bounds = CMJBounds.ECCENTRIC_DURATION

        if not bounds.is_physically_possible(duration):
            result.add_error(
                "eccentric_duration",
                f"Eccentric duration {duration:.3f}s outside physical limits",
                value=duration,
                bounds=(bounds.absolute_min, bounds.absolute_max),
            )
        else:
            # NOTE: Downgraded from WARNING to INFO - standing end detection has
            # ~117ms offset causing misleading warnings. See issue #16.
            result.add_info(
                "eccentric_duration",
                f"Eccentric duration {duration:.3f}s",
                value=duration,
            )

    def _check_peak_velocities(
        self, metrics: MetricsDict, result: CMJValidationResult, profile: AthleteProfile
    ) -> None:
        """Validate peak eccentric and concentric velocities."""
        velocity_checks = [
            (
                "peak_eccentric_velocity",
                "peak_eccentric_velocity_m_s",
                CMJBounds.PEAK_ECCENTRIC_VELOCITY,
                "",
            ),
            (
                "peak_concentric_velocity",
                "peak_concentric_velocity_m_s",
                CMJBounds.PEAK_CONCENTRIC_VELOCITY,
                "insufficient to leave ground",
            ),
        ]

        for metric_name, key_name, bounds, error_suffix in velocity_checks:
            velocity = self._get_metric_value(metrics, key_name, metric_name)
            if velocity is None:
                continue

            self._validate_velocity_metric(
                metric_name, velocity, bounds, profile, result, error_suffix
            )

    def _validate_velocity_metric(
        self,
        name: str,
        velocity: float,
        bounds: MetricBounds,
        profile: AthleteProfile,
        result: CMJValidationResult,
        error_suffix: str,
    ) -> None:
        """Validate a velocity metric against bounds."""
        if not bounds.is_physically_possible(velocity):
            if velocity < bounds.absolute_min and error_suffix:
                error_msg = (
                    f"Peak {name.replace('peak_', '')} velocity {velocity:.2f} m/s {error_suffix}"
                )
            else:
                error_msg = (
                    f"Peak {name.replace('peak_', '')} velocity {velocity:.2f} m/s outside limits"
                )
            result.add_error(
                name,
                error_msg,
                value=velocity,
                bounds=(bounds.absolute_min, bounds.absolute_max),
            )
        elif bounds.contains(velocity, profile):
            velocity_type = name.replace("peak_", "").replace("_", " ")
            result.add_info(
                name,
                f"Peak {velocity_type} velocity {velocity:.2f} m/s "
                f"within range for {profile.value}",
                value=velocity,
            )
        else:
            expected_min, expected_max = self._get_profile_range(profile, bounds)
            velocity_type = name.replace("peak_", "").replace("_", " ")
            result.add_warning(
                name,
                f"Peak {velocity_type} velocity {velocity:.2f} m/s "
                f"outside typical range [{expected_min:.2f}-{expected_max:.2f}] "
                f"for {profile.value}",
                value=velocity,
                bounds=(expected_min, expected_max),
            )

    def _check_flight_time_height_consistency(
        self, metrics: MetricsDict, result: CMJValidationResult
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

        result.height_flight_time_consistency = error_pct

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

    def _check_velocity_height_consistency(
        self, metrics: MetricsDict, result: CMJValidationResult
    ) -> None:
        """Verify peak velocity is consistent with jump height."""
        velocity = metrics.get("peak_concentric_velocity_m_s")
        jump_height = metrics.get("jump_height_m")

        if velocity is None or jump_height is None:
            return

        # Calculate expected velocity using kinematic formula: v² = 2*g*h
        g = 9.81
        expected_velocity = (2 * g * jump_height) ** 0.5
        error_pct = abs(velocity - expected_velocity) / expected_velocity

        result.velocity_height_consistency = error_pct

        if error_pct > MetricConsistency.VELOCITY_HEIGHT_TOLERANCE:
            error_msg = (
                f"Peak velocity {velocity:.2f} m/s inconsistent with "
                f"jump height {jump_height:.3f}m (expected {expected_velocity:.2f} "
                f"m/s, error {error_pct * 100:.1f}%)"
            )
            result.add_warning(
                "velocity_height_consistency",
                error_msg,
                value=error_pct,
                bounds=(0, MetricConsistency.VELOCITY_HEIGHT_TOLERANCE),
            )
        else:
            result.add_info(
                "velocity_height_consistency",
                f"Peak velocity and jump height consistent (error {error_pct * 100:.1f}%)",
                value=error_pct,
            )

    def _check_rsi_validity(
        self, metrics: MetricsDict, result: CMJValidationResult, profile: AthleteProfile
    ) -> None:
        """Validate Reactive Strength Index."""
        flight_time_raw = self._get_metric_value(metrics, "flight_time_ms", "flight_time")
        concentric_duration_raw = self._get_metric_value(
            metrics, "concentric_duration_ms", "concentric_duration"
        )

        if (
            flight_time_raw is None
            or concentric_duration_raw is None
            or concentric_duration_raw == 0
        ):
            return

        flight_time = self._convert_raw_duration_to_seconds(flight_time_raw)
        concentric_duration = self._convert_raw_duration_to_seconds(concentric_duration_raw)

        rsi = flight_time / concentric_duration
        result.rsi = rsi

        if not RSIBounds.is_valid(rsi):
            if rsi < RSIBounds.MIN_VALID:
                result.add_error(
                    "rsi",
                    f"RSI {rsi:.2f} below physiological minimum (likely error)",
                    value=rsi,
                    bounds=(RSIBounds.MIN_VALID, RSIBounds.MAX_VALID),
                )
            else:
                result.add_error(
                    "rsi",
                    f"RSI {rsi:.2f} exceeds physiological maximum (likely error)",
                    value=rsi,
                    bounds=(RSIBounds.MIN_VALID, RSIBounds.MAX_VALID),
                )
        else:
            expected_min, expected_max = RSIBounds.get_rsi_range(profile)
            if expected_min <= rsi <= expected_max:
                result.add_info(
                    "rsi",
                    f"RSI {rsi:.2f} within expected range "
                    f"[{expected_min:.2f}-{expected_max:.2f}] "
                    f"for {profile.value}",
                    value=rsi,
                )
            else:
                result.add_warning(
                    "rsi",
                    f"RSI {rsi:.2f} outside typical range "
                    f"[{expected_min:.2f}-{expected_max:.2f}] "
                    f"for {profile.value}",
                    value=rsi,
                    bounds=(expected_min, expected_max),
                )

    def _check_depth_height_ratio(self, metrics: MetricsDict, result: CMJValidationResult) -> None:
        """Check countermovement depth to jump height ratio."""
        depth = metrics.get("countermovement_depth_m")
        jump_height = metrics.get("jump_height_m")

        if depth is None or jump_height is None or depth < 0.05:  # Skip if depth minimal
            return

        ratio = jump_height / depth
        result.depth_height_ratio = ratio

        if ratio < MetricConsistency.DEPTH_HEIGHT_RATIO_MIN:
            result.add_warning(
                "depth_height_ratio",
                f"Jump height {ratio:.2f}x countermovement depth: "
                f"May indicate incomplete squat or standing position detection error",
                value=ratio,
                bounds=(
                    MetricConsistency.DEPTH_HEIGHT_RATIO_MIN,
                    MetricConsistency.DEPTH_HEIGHT_RATIO_MAX,
                ),
            )
        elif ratio > MetricConsistency.DEPTH_HEIGHT_RATIO_MAX:
            result.add_warning(
                "depth_height_ratio",
                f"Jump height only {ratio:.2f}x countermovement depth: "
                f"Unusually inefficient (verify lowest point detection)",
                value=ratio,
                bounds=(
                    MetricConsistency.DEPTH_HEIGHT_RATIO_MIN,
                    MetricConsistency.DEPTH_HEIGHT_RATIO_MAX,
                ),
            )
        else:
            result.add_info(
                "depth_height_ratio",
                f"Depth-to-height ratio {ratio:.2f} within expected range",
                value=ratio,
            )

    def _check_contact_depth_ratio(
        self, metrics: MetricsDict, result: CMJValidationResult
    ) -> None:
        """Check contact time to countermovement depth ratio."""
        contact_ms = metrics.get("concentric_duration_ms")
        depth = metrics.get("countermovement_depth_m")

        if contact_ms is None or depth is None or depth < 0.05:
            return

        # Convert ms to seconds for ratio calculation
        contact = contact_ms / 1000.0
        ratio = contact / depth
        result.contact_depth_ratio = ratio

        if ratio < MetricConsistency.CONTACT_DEPTH_RATIO_MIN:
            result.add_warning(
                "contact_depth_ratio",
                f"Contact time {ratio:.2f}s/m to depth ratio: Very fast for depth traversed",
                value=ratio,
                bounds=(
                    MetricConsistency.CONTACT_DEPTH_RATIO_MIN,
                    MetricConsistency.CONTACT_DEPTH_RATIO_MAX,
                ),
            )
        elif ratio > MetricConsistency.CONTACT_DEPTH_RATIO_MAX:
            result.add_warning(
                "contact_depth_ratio",
                f"Contact time {ratio:.2f}s/m to depth ratio: Slow for depth traversed",
                value=ratio,
                bounds=(
                    MetricConsistency.CONTACT_DEPTH_RATIO_MIN,
                    MetricConsistency.CONTACT_DEPTH_RATIO_MAX,
                ),
            )
        else:
            result.add_info(
                "contact_depth_ratio",
                f"Contact-depth ratio {ratio:.2f} s/m within expected range",
                value=ratio,
            )

    def _check_triple_extension(
        self, metrics: MetricsDict, result: CMJValidationResult, profile: AthleteProfile
    ) -> None:
        """Validate triple extension angles."""
        angles = metrics.get("triple_extension")
        if angles is None:
            return

        joint_definitions = [
            ("hip_angle", TripleExtensionBounds.hip_angle_valid, "Hip"),
            ("knee_angle", TripleExtensionBounds.knee_angle_valid, "Knee"),
            ("ankle_angle", TripleExtensionBounds.ankle_angle_valid, "Ankle"),
        ]

        for metric_name, validator, joint_name in joint_definitions:
            angle = angles.get(metric_name)
            if angle is None:
                continue

            if not validator(angle, profile):
                result.add_warning(
                    metric_name,
                    f"{joint_name} angle {angle:.1f}° outside expected range for {profile.value}",
                    value=angle,
                )
            else:
                result.add_info(
                    metric_name,
                    f"{joint_name} angle {angle:.1f}° within expected range for {profile.value}",
                    value=angle,
                )

        # Detect joint compensation patterns
        self._check_joint_compensation_pattern(angles, result, profile)

    def _check_joint_compensation_pattern(
        self, angles: dict, result: CMJValidationResult, profile: AthleteProfile
    ) -> None:
        """Detect compensatory joint patterns in triple extension.

        When one joint cannot achieve full extension, others may compensate.
        Example: Limited hip extension (160°) with excessive knee extension (185°+)
        suggests compensation rather than balanced movement quality.

        This is a biomechanical quality indicator, not an error.
        """
        hip = angles.get("hip_angle")
        knee = angles.get("knee_angle")
        ankle = angles.get("ankle_angle")

        if hip is None or knee is None or ankle is None:
            return  # Need all three to detect patterns

        # Profile-specific bounds lookup
        profile_bounds = {
            AthleteProfile.ELDERLY: (150, 175, 155, 175, 100, 125),
            AthleteProfile.UNTRAINED: (160, 180, 165, 182, 110, 140),
            AthleteProfile.RECREATIONAL: (160, 180, 165, 182, 110, 140),
            AthleteProfile.TRAINED: (170, 185, 173, 190, 125, 155),
            AthleteProfile.ELITE: (170, 185, 173, 190, 125, 155),
        }

        bounds_tuple = profile_bounds.get(profile)
        if not bounds_tuple:
            return

        hip_min, hip_max, knee_min, knee_max, ankle_min, ankle_max = bounds_tuple

        # Count joints at boundaries
        boundary_threshold = 3.0  # degrees from limit
        joints_at_boundary = sum(
            1
            for val, min_val, max_val in [
                (hip, hip_min, hip_max),
                (knee, knee_min, knee_max),
                (ankle, ankle_min, ankle_max),
            ]
            if val <= min_val + boundary_threshold or val >= max_val - boundary_threshold
        )

        # If 2+ joints at boundaries, likely compensation pattern
        if joints_at_boundary >= 2:
            result.add_info(
                "joint_compensation",
                f"Multiple joints near extension limits (hip={hip:.0f}°, "
                f"knee={knee:.0f}°, ankle={ankle:.0f}°). "
                f"May indicate compensatory movement pattern.",
                value=float(joints_at_boundary),
            )

    @staticmethod
    def _get_profile_range(profile: AthleteProfile, bounds: MetricBounds) -> tuple[float, float]:
        """Get min/max bounds for specific profile."""
        profile_ranges = {
            AthleteProfile.ELDERLY: (bounds.practical_min, bounds.recreational_max),
            AthleteProfile.UNTRAINED: (bounds.practical_min, bounds.recreational_max),
            AthleteProfile.RECREATIONAL: (bounds.recreational_min, bounds.recreational_max),
            AthleteProfile.TRAINED: (
                (bounds.recreational_min + bounds.elite_min) / 2,
                (bounds.recreational_max + bounds.elite_max) / 2,
            ),
            AthleteProfile.ELITE: (bounds.elite_min, bounds.elite_max),
        }
        return profile_ranges.get(profile, (bounds.absolute_min, bounds.absolute_max))
