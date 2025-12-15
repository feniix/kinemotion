"""CMJ metrics validation using physiological bounds.

Comprehensive validation of Counter Movement Jump metrics against
biomechanical bounds, cross-validation checks, and consistency tests.

Provides severity levels (ERROR, WARNING, INFO) for different categories
of metric issues.
"""

from dataclasses import dataclass

from kinemotion.cmj.validation_bounds import (
    CMJBounds,
    MetricConsistency,
    RSIBounds,
    TripleExtensionBounds,
    estimate_athlete_profile,
)
from kinemotion.core.types import MetricsDict
from kinemotion.core.validation import (
    AthleteProfile,
    MetricBounds,
    MetricsValidator,
    ValidationResult,
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

        # If value is in seconds (legacy), use as-is; if in ms, convert
        if flight_time_raw < 10:  # Likely in seconds
            flight_time = flight_time_raw
        else:  # In milliseconds
            flight_time = flight_time_raw / 1000.0

        bounds = CMJBounds.FLIGHT_TIME

        if not bounds.is_physically_possible(flight_time):
            if flight_time < bounds.absolute_min:
                result.add_error(
                    "flight_time",
                    f"Flight time {flight_time:.3f}s below frame rate resolution limit",
                    value=flight_time,
                    bounds=(bounds.absolute_min, bounds.absolute_max),
                )
            else:
                result.add_error(
                    "flight_time",
                    f"Flight time {flight_time:.3f}s exceeds elite human capability",
                    value=flight_time,
                    bounds=(bounds.absolute_min, bounds.absolute_max),
                )
        elif bounds.contains(flight_time, profile):
            result.add_info(
                "flight_time",
                f"Flight time {flight_time:.3f}s within expected range for {profile.value}",
                value=flight_time,
            )
        else:
            # Outside expected range but physically possible
            expected_min, expected_max = self._get_profile_range(profile, bounds)
            result.add_warning(
                "flight_time",
                f"Flight time {flight_time:.3f}s outside typical range "
                f"[{expected_min:.3f}-{expected_max:.3f}]s for {profile.value}",
                value=flight_time,
                bounds=(expected_min, expected_max),
            )

    def _check_jump_height(
        self, metrics: MetricsDict, result: CMJValidationResult, profile: AthleteProfile
    ) -> None:
        """Validate jump height."""
        jump_height = self._get_metric_value(metrics, "jump_height_m", "jump_height")
        if jump_height is None:
            return

        bounds = CMJBounds.JUMP_HEIGHT

        if not bounds.is_physically_possible(jump_height):
            if jump_height < bounds.absolute_min:
                result.add_error(
                    "jump_height",
                    f"Jump height {jump_height:.3f}m essentially no jump (noise)",
                    value=jump_height,
                    bounds=(bounds.absolute_min, bounds.absolute_max),
                )
            else:
                result.add_error(
                    "jump_height",
                    f"Jump height {jump_height:.3f}m exceeds human capability",
                    value=jump_height,
                    bounds=(bounds.absolute_min, bounds.absolute_max),
                )
        elif bounds.contains(jump_height, profile):
            result.add_info(
                "jump_height",
                f"Jump height {jump_height:.3f}m within expected range for {profile.value}",
                value=jump_height,
            )
        else:
            expected_min, expected_max = self._get_profile_range(profile, bounds)
            result.add_warning(
                "jump_height",
                f"Jump height {jump_height:.3f}m outside typical range "
                f"[{expected_min:.3f}-{expected_max:.3f}]m for {profile.value}",
                value=jump_height,
                bounds=(expected_min, expected_max),
            )

    def _check_countermovement_depth(
        self, metrics: MetricsDict, result: CMJValidationResult, profile: AthleteProfile
    ) -> None:
        """Validate countermovement depth."""
        depth = self._get_metric_value(metrics, "countermovement_depth_m", "countermovement_depth")
        if depth is None:
            return

        bounds = CMJBounds.COUNTERMOVEMENT_DEPTH

        if not bounds.is_physically_possible(depth):
            if depth < bounds.absolute_min:
                result.add_error(
                    "countermovement_depth",
                    f"Countermovement depth {depth:.3f}m essentially no squat",
                    value=depth,
                    bounds=(bounds.absolute_min, bounds.absolute_max),
                )
            else:
                result.add_error(
                    "countermovement_depth",
                    f"Countermovement depth {depth:.3f}m exceeds physical limit",
                    value=depth,
                    bounds=(bounds.absolute_min, bounds.absolute_max),
                )
        elif bounds.contains(depth, profile):
            result.add_info(
                "countermovement_depth",
                f"Countermovement depth {depth:.3f}m within expected range for {profile.value}",
                value=depth,
            )
        else:
            expected_min, expected_max = self._get_profile_range(profile, bounds)
            result.add_warning(
                "countermovement_depth",
                f"Countermovement depth {depth:.3f}m outside typical range "
                f"[{expected_min:.3f}-{expected_max:.3f}]m for {profile.value}",
                value=depth,
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

        # If value is in seconds (legacy), convert to ms first
        # Values >10 are assumed to be in ms, <10 assumed to be in seconds
        if duration_raw < 10:  # Likely in seconds
            duration = duration_raw
        else:  # In milliseconds
            duration = duration_raw / 1000.0

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
        elif bounds.contains(duration, profile):
            result.add_info(
                "concentric_duration",
                f"Concentric duration {duration:.3f}s within expected range for {profile.value}",
                value=duration,
            )
        else:
            expected_min, expected_max = self._get_profile_range(profile, bounds)
            result.add_warning(
                "concentric_duration",
                f"Concentric duration {duration:.3f}s outside typical range "
                f"[{expected_min:.3f}-{expected_max:.3f}]s for {profile.value}",
                value=duration,
                bounds=(expected_min, expected_max),
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

        # If value is in seconds (legacy), use as-is; if in ms, convert
        if duration_raw < 10:  # Likely in seconds
            duration = duration_raw
        else:  # In milliseconds
            duration = duration_raw / 1000.0

        bounds = CMJBounds.ECCENTRIC_DURATION

        if not bounds.is_physically_possible(duration):
            result.add_error(
                "eccentric_duration",
                f"Eccentric duration {duration:.3f}s outside physical limits",
                value=duration,
                bounds=(bounds.absolute_min, bounds.absolute_max),
            )
        elif bounds.contains(duration, profile):
            result.add_info(
                "eccentric_duration",
                f"Eccentric duration {duration:.3f}s within expected range for {profile.value}",
                value=duration,
            )
        else:
            expected_min, expected_max = self._get_profile_range(profile, bounds)
            result.add_warning(
                "eccentric_duration",
                f"Eccentric duration {duration:.3f}s outside typical range "
                f"[{expected_min:.3f}-{expected_max:.3f}]s for {profile.value}",
                value=duration,
                bounds=(expected_min, expected_max),
            )

    def _check_peak_velocities(
        self, metrics: MetricsDict, result: CMJValidationResult, profile: AthleteProfile
    ) -> None:
        """Validate peak eccentric and concentric velocities."""
        # Eccentric
        ecc_vel = self._get_metric_value(
            metrics, "peak_eccentric_velocity_m_s", "peak_eccentric_velocity"
        )
        if ecc_vel is not None:
            bounds = CMJBounds.PEAK_ECCENTRIC_VELOCITY
            if not bounds.is_physically_possible(ecc_vel):
                result.add_error(
                    "peak_eccentric_velocity",
                    f"Peak eccentric velocity {ecc_vel:.2f} m/s outside limits",
                    value=ecc_vel,
                    bounds=(bounds.absolute_min, bounds.absolute_max),
                )
            elif bounds.contains(ecc_vel, profile):
                result.add_info(
                    "peak_eccentric_velocity",
                    f"Peak eccentric velocity {ecc_vel:.2f} m/s within range for {profile.value}",
                    value=ecc_vel,
                )
            else:
                expected_min, expected_max = self._get_profile_range(profile, bounds)
                result.add_warning(
                    "peak_eccentric_velocity",
                    f"Peak eccentric velocity {ecc_vel:.2f} m/s outside typical range "
                    f"[{expected_min:.2f}-{expected_max:.2f}] for {profile.value}",
                    value=ecc_vel,
                    bounds=(expected_min, expected_max),
                )

        # Concentric
        con_vel = self._get_metric_value(
            metrics, "peak_concentric_velocity_m_s", "peak_concentric_velocity"
        )
        if con_vel is not None:
            bounds = CMJBounds.PEAK_CONCENTRIC_VELOCITY
            if not bounds.is_physically_possible(con_vel):
                if con_vel < bounds.absolute_min:
                    result.add_error(
                        "peak_concentric_velocity",
                        f"Peak concentric velocity {con_vel:.2f} m/s insufficient to leave ground",
                        value=con_vel,
                        bounds=(bounds.absolute_min, bounds.absolute_max),
                    )
                else:
                    result.add_error(
                        "peak_concentric_velocity",
                        f"Peak concentric velocity {con_vel:.2f} m/s exceeds elite capability",
                        value=con_vel,
                        bounds=(bounds.absolute_min, bounds.absolute_max),
                    )
            elif bounds.contains(con_vel, profile):
                result.add_info(
                    "peak_concentric_velocity",
                    f"Peak concentric velocity {con_vel:.2f} m/s within range for {profile.value}",
                    value=con_vel,
                )
            else:
                expected_min, expected_max = self._get_profile_range(profile, bounds)
                result.add_warning(
                    "peak_concentric_velocity",
                    f"Peak concentric velocity {con_vel:.2f} m/s outside typical range "
                    f"[{expected_min:.2f}-{expected_max:.2f}] for {profile.value}",
                    value=con_vel,
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

        # Convert to seconds if needed
        if flight_time_raw < 10:  # Likely in seconds
            flight_time = flight_time_raw
        else:  # In milliseconds
            flight_time = flight_time_raw / 1000.0

        if concentric_duration_raw < 10:  # Likely in seconds
            concentric_duration = concentric_duration_raw
        else:  # In milliseconds
            concentric_duration = concentric_duration_raw / 1000.0

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

        hip = angles.get("hip_angle")
        if hip is not None:
            if not TripleExtensionBounds.hip_angle_valid(hip, profile):
                result.add_warning(
                    "hip_angle",
                    f"Hip angle {hip:.1f}° outside expected range for {profile.value}",
                    value=hip,
                )
            else:
                result.add_info(
                    "hip_angle",
                    f"Hip angle {hip:.1f}° within expected range for {profile.value}",
                    value=hip,
                )

        knee = angles.get("knee_angle")
        if knee is not None:
            if not TripleExtensionBounds.knee_angle_valid(knee, profile):
                result.add_warning(
                    "knee_angle",
                    f"Knee angle {knee:.1f}° outside expected range for {profile.value}",
                    value=knee,
                )
            else:
                result.add_info(
                    "knee_angle",
                    f"Knee angle {knee:.1f}° within expected range for {profile.value}",
                    value=knee,
                )

        ankle = angles.get("ankle_angle")
        if ankle is not None:
            if not TripleExtensionBounds.ankle_angle_valid(ankle, profile):
                result.add_warning(
                    "ankle_angle",
                    f"Ankle angle {ankle:.1f}° outside expected range for {profile.value}",
                    value=ankle,
                )
            else:
                result.add_info(
                    "ankle_angle",
                    f"Ankle angle {ankle:.1f}° within expected range for {profile.value}",
                    value=ankle,
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

        # Get profile-specific bounds
        if profile == AthleteProfile.ELDERLY:
            hip_min, hip_max = 150, 175
            knee_min, knee_max = 155, 175
            ankle_min, ankle_max = 100, 125
        elif profile in (AthleteProfile.UNTRAINED, AthleteProfile.RECREATIONAL):
            hip_min, hip_max = 160, 180
            knee_min, knee_max = 165, 182
            ankle_min, ankle_max = 110, 140
        elif profile in (AthleteProfile.TRAINED, AthleteProfile.ELITE):
            hip_min, hip_max = 170, 185
            knee_min, knee_max = 173, 190
            ankle_min, ankle_max = 125, 155
        else:
            return

        # Count how many joints are near their boundaries
        joints_at_boundary = 0
        boundary_threshold = 3.0  # degrees from limit

        if hip <= hip_min + boundary_threshold or hip >= hip_max - boundary_threshold:
            joints_at_boundary += 1
        if knee <= knee_min + boundary_threshold or knee >= knee_max - boundary_threshold:
            joints_at_boundary += 1
        if ankle <= ankle_min + boundary_threshold or ankle >= ankle_max - boundary_threshold:
            joints_at_boundary += 1

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
        if profile == AthleteProfile.ELDERLY:
            return (bounds.practical_min, bounds.recreational_max)
        elif profile == AthleteProfile.UNTRAINED:
            return (bounds.practical_min, bounds.recreational_max)
        elif profile == AthleteProfile.RECREATIONAL:
            return (bounds.recreational_min, bounds.recreational_max)
        elif profile == AthleteProfile.TRAINED:
            trained_min = (bounds.recreational_min + bounds.elite_min) / 2
            trained_max = (bounds.recreational_max + bounds.elite_max) / 2
            return (trained_min, trained_max)
        elif profile == AthleteProfile.ELITE:
            return (bounds.elite_min, bounds.elite_max)
        return (bounds.absolute_min, bounds.absolute_max)
