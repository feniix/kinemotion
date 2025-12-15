"""CMJ metrics physiological bounds for validation testing.

This module defines realistic physiological bounds for Counter Movement Jump (CMJ)
metrics based on biomechanical literature and real-world athlete performance.

These bounds are used to:
1. Prevent false positives from measurement noise
2. Catch real errors in video processing and phase detection
3. Provide athlete-profile-appropriate validation
4. Enable cross-validation of metric consistency

References:
- Nordez et al. (2009): CMJ depth-height relationships
- Cormie et al. (2011): Power generation characteristics
- Bogdanis (2012): Plyometric training effects
"""

from kinemotion.core.types import MetricsDict
from kinemotion.core.validation import AthleteProfile, MetricBounds


class CMJBounds:
    """Collection of physiological bounds for all CMJ metrics."""

    # FLIGHT TIME (seconds)
    FLIGHT_TIME = MetricBounds(
        absolute_min=0.08,  # Frame rate resolution limit
        practical_min=0.15,  # Minimum effort jump
        recreational_min=0.25,  # Untrained ~10cm
        recreational_max=0.70,  # Recreational ~30-50cm
        elite_min=0.65,  # Trained ~60cm
        elite_max=1.10,  # Elite >100cm
        absolute_max=1.30,
        unit="s",
    )

    # JUMP HEIGHT (meters)
    JUMP_HEIGHT = MetricBounds(
        absolute_min=0.02,
        practical_min=0.05,
        recreational_min=0.15,  # Untrained with effort
        recreational_max=0.60,  # Good recreational
        elite_min=0.65,
        elite_max=1.00,
        absolute_max=1.30,
        unit="m",
    )

    # COUNTERMOVEMENT DEPTH (meters)
    COUNTERMOVEMENT_DEPTH = MetricBounds(
        absolute_min=0.05,
        practical_min=0.08,  # Minimal squat
        recreational_min=0.20,  # Shallow to parallel
        recreational_max=0.55,  # Normal to deep squat
        elite_min=0.40,
        elite_max=0.75,
        absolute_max=1.10,  # Only extreme tall athletes
        unit="m",
    )

    # CONCENTRIC DURATION / CONTACT TIME (seconds)
    CONCENTRIC_DURATION = MetricBounds(
        absolute_min=0.08,
        practical_min=0.10,  # Extreme plyometric
        recreational_min=0.40,  # Moderate propulsion
        recreational_max=0.90,  # Slow push-off
        elite_min=0.25,
        elite_max=0.50,
        absolute_max=1.80,
        unit="s",
    )

    # ECCENTRIC DURATION (seconds)
    ECCENTRIC_DURATION = MetricBounds(
        absolute_min=0.15,
        practical_min=0.25,
        recreational_min=0.35,
        recreational_max=0.75,
        elite_min=0.30,
        elite_max=0.65,
        absolute_max=1.30,
        unit="s",
    )

    # TOTAL MOVEMENT TIME (seconds)
    TOTAL_MOVEMENT_TIME = MetricBounds(
        absolute_min=0.25,
        practical_min=0.35,
        recreational_min=0.75,
        recreational_max=1.50,
        elite_min=0.55,
        elite_max=1.10,
        absolute_max=2.20,
        unit="s",
    )

    # PEAK ECCENTRIC VELOCITY (m/s, downward)
    PEAK_ECCENTRIC_VELOCITY = MetricBounds(
        absolute_min=0.10,
        practical_min=0.20,
        recreational_min=0.80,
        recreational_max=2.00,
        elite_min=2.00,
        elite_max=3.50,
        absolute_max=4.50,
        unit="m/s",
    )

    # PEAK CONCENTRIC VELOCITY (m/s, upward)
    PEAK_CONCENTRIC_VELOCITY = MetricBounds(
        absolute_min=0.30,
        practical_min=0.50,
        recreational_min=1.80,
        recreational_max=2.80,
        elite_min=3.00,
        elite_max=4.20,
        absolute_max=5.00,
        unit="m/s",
    )


class TripleExtensionBounds:
    """Physiological bounds for triple extension angles (degrees)."""

    # HIP ANGLE at takeoff (close to 180° = full extension)
    @staticmethod
    def hip_angle_valid(angle: float | None, profile: AthleteProfile) -> bool:
        """Check if hip angle is valid for profile."""
        if angle is None:
            return True  # May not be detectable
        if angle < 120 or angle > 195:
            return False  # Outside physiological limits
        if profile == AthleteProfile.ELDERLY:
            return 150 <= angle <= 175
        elif profile in (AthleteProfile.UNTRAINED, AthleteProfile.RECREATIONAL):
            return 160 <= angle <= 180
        elif profile in (AthleteProfile.TRAINED, AthleteProfile.ELITE):
            return 170 <= angle <= 185
        return True

    # KNEE ANGLE at takeoff (close to 180° = full extension)
    @staticmethod
    def knee_angle_valid(angle: float | None, profile: AthleteProfile) -> bool:
        """Check if knee angle is valid for profile."""
        if angle is None:
            return True
        if angle < 130 or angle > 200:
            return False  # Outside physiological limits
        if profile == AthleteProfile.ELDERLY:
            return 155 <= angle <= 175
        elif profile in (AthleteProfile.UNTRAINED, AthleteProfile.RECREATIONAL):
            return 165 <= angle <= 182
        elif profile in (AthleteProfile.TRAINED, AthleteProfile.ELITE):
            return 173 <= angle <= 190
        return True

    # ANKLE ANGLE at takeoff (120-155° = plantarflexion, 90° = neutral)
    @staticmethod
    def ankle_angle_valid(angle: float | None, profile: AthleteProfile) -> bool:
        """Check if ankle angle is valid for profile."""
        if angle is None:
            return True  # Often not detectable in side view
        if angle < 90 or angle > 165:
            return False  # Outside physiological limits
        if profile == AthleteProfile.ELDERLY:
            return 100 <= angle <= 125
        elif profile in (AthleteProfile.UNTRAINED, AthleteProfile.RECREATIONAL):
            return 110 <= angle <= 140
        elif profile in (AthleteProfile.TRAINED, AthleteProfile.ELITE):
            return 125 <= angle <= 155
        return True

    # TRUNK TILT (forward lean from vertical, degrees)
    @staticmethod
    def trunk_tilt_valid(angle: float | None, profile: AthleteProfile) -> bool:
        """Check if trunk tilt is valid for profile."""
        if angle is None:
            return True
        if angle < -15 or angle > 60:
            return False  # Outside reasonable range
        # Most athletes show 10-30° forward lean during takeoff
        return -10 <= angle <= 45


class RSIBounds:
    """Reactive Strength Index bounds."""

    # Calculated as: RSI = flight_time / contact_time
    MIN_VALID = 0.30  # Below this: invalid metrics
    MAX_VALID = 4.00  # Above this: invalid metrics

    ELDERLY_RANGE = (0.15, 0.30)
    UNTRAINED_RANGE = (0.30, 0.80)
    RECREATIONAL_RANGE = (0.80, 1.50)
    TRAINED_RANGE = (1.50, 2.40)
    ELITE_RANGE = (2.20, 3.50)

    @staticmethod
    def get_rsi_range(profile: AthleteProfile) -> tuple[float, float]:
        """Get expected RSI range for athlete profile."""
        if profile == AthleteProfile.ELDERLY:
            return RSIBounds.ELDERLY_RANGE
        elif profile == AthleteProfile.UNTRAINED:
            return RSIBounds.UNTRAINED_RANGE
        elif profile == AthleteProfile.RECREATIONAL:
            return RSIBounds.RECREATIONAL_RANGE
        elif profile == AthleteProfile.TRAINED:
            return RSIBounds.TRAINED_RANGE
        elif profile == AthleteProfile.ELITE:
            return RSIBounds.ELITE_RANGE
        return (RSIBounds.MIN_VALID, RSIBounds.MAX_VALID)

    @staticmethod
    def is_valid(rsi: float) -> bool:
        """Check if RSI is within physiological bounds."""
        return RSIBounds.MIN_VALID <= rsi <= RSIBounds.MAX_VALID

    @staticmethod
    def in_range_for_profile(rsi: float, profile: AthleteProfile) -> bool:
        """Check if RSI is in expected range for profile."""
        min_rsi, max_rsi = RSIBounds.get_rsi_range(profile)
        return min_rsi <= rsi <= max_rsi


class MetricConsistency:
    """Cross-validation tolerance for metric consistency checks."""

    # Jump height from flight time: h = g*t²/8
    # Allow 10% deviation for measurement noise
    HEIGHT_FLIGHT_TIME_TOLERANCE = 0.10

    # Peak velocity from jump height: v = sqrt(2*g*h)
    # Allow 15% deviation (velocity harder to detect precisely)
    VELOCITY_HEIGHT_TOLERANCE = 0.15

    # Countermovement depth to jump height ratio
    # Typically 0.5-1.2, flag if outside 0.3-1.5
    DEPTH_HEIGHT_RATIO_MIN = 0.30
    DEPTH_HEIGHT_RATIO_MAX = 1.50

    # Contact time to countermovement depth ratio
    # Should be roughly 1.0-1.5 s/m
    CONTACT_DEPTH_RATIO_MIN = 0.50
    CONTACT_DEPTH_RATIO_MAX = 2.50


# Athlete profile examples with expected metric ranges
ATHLETE_PROFILES = {
    "elderly_deconditioned": {
        "label": "Elderly/Deconditioned (70+, sedentary)",
        "profile": AthleteProfile.ELDERLY,
        "expected": {
            "jump_height_m": (0.10, 0.18),
            "flight_time_s": (0.14, 0.19),
            "countermovement_depth_m": (0.12, 0.20),
            "concentric_duration_s": (0.80, 1.20),
            "eccentric_duration_s": (0.60, 0.95),
            "peak_eccentric_velocity_ms": (0.4, 0.7),
            "peak_concentric_velocity_ms": (1.0, 1.5),
            "rsi": (0.15, 0.25),
            "hip_angle_deg": (150, 165),
            "knee_angle_deg": (155, 170),
            "ankle_angle_deg": (105, 125),
        },
    },
    "recreational": {
        "label": "Recreational Athlete (fitness participant, 30-45 yrs)",
        "profile": AthleteProfile.RECREATIONAL,
        "expected": {
            "jump_height_m": (0.35, 0.55),
            "flight_time_s": (0.53, 0.67),
            "countermovement_depth_m": (0.28, 0.45),
            "concentric_duration_s": (0.45, 0.65),
            "eccentric_duration_s": (0.40, 0.65),
            "peak_eccentric_velocity_ms": (1.3, 1.9),
            "peak_concentric_velocity_ms": (2.6, 3.3),
            "rsi": (0.85, 1.25),
            "hip_angle_deg": (168, 178),
            "knee_angle_deg": (170, 182),
            "ankle_angle_deg": (120, 138),
        },
    },
    "elite_male": {
        "label": "Elite Male Athlete (college/pro volleyball/basketball)",
        "profile": AthleteProfile.ELITE,
        "expected": {
            "jump_height_m": (0.68, 0.88),
            "flight_time_s": (0.74, 0.84),
            "countermovement_depth_m": (0.42, 0.62),
            "concentric_duration_s": (0.28, 0.42),
            "eccentric_duration_s": (0.35, 0.55),
            "peak_eccentric_velocity_ms": (2.1, 3.2),
            "peak_concentric_velocity_ms": (3.6, 4.2),
            "rsi": (1.85, 2.80),
            "hip_angle_deg": (173, 185),
            "knee_angle_deg": (176, 188),
            "ankle_angle_deg": (132, 148),
        },
    },
}


def estimate_athlete_profile(
    metrics_dict: MetricsDict, gender: str | None = None
) -> AthleteProfile:
    """Estimate athlete profile from metrics.

    Uses jump height as primary classifier:
    - <0.20m: Elderly
    - 0.20-0.35m: Untrained
    - 0.35-0.65m: Recreational
    - 0.65-0.85m: Trained
    - >0.85m: Elite

    NOTE: Bounds are calibrated for adult males. Female athletes typically achieve
    60-70% of male heights due to lower muscle mass and strength. If analyzing
    female athletes, interpret results one level lower than classification suggests.
    Example: Female athlete with 0.45m jump = Recreational male = Trained female.

    Args:
        metrics_dict: Dictionary with CMJ metric values
        gender: Optional gender for context ("M"/"F"). Currently informational only.

    Returns:
        Estimated AthleteProfile
    """
    # Support both nested "data" structure and flat structure
    # Extract with unit suffix as used in serialization, or without suffix (legacy)
    data = metrics_dict.get("data", metrics_dict)
    jump_height = data.get("jump_height_m") or data.get("jump_height", 0)

    if jump_height < 0.20:
        return AthleteProfile.ELDERLY
    elif jump_height < 0.35:
        return AthleteProfile.UNTRAINED
    elif jump_height < 0.65:
        return AthleteProfile.RECREATIONAL
    elif jump_height < 0.85:
        return AthleteProfile.TRAINED
    else:
        return AthleteProfile.ELITE
