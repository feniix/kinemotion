"""SJ metrics physiological bounds for validation testing.

This module defines realistic physiological bounds for Squat Jump (SJ)
metrics based on biomechanical literature and real-world athlete performance.

These bounds are used to:
1. Prevent false positives from measurement noise
2. Catch real errors in video processing and phase detection
3. Provide athlete-profile-appropriate validation
4. Enable cross-validation of metric consistency

Note: SJ metrics differ from CMJ as there is no eccentric phase.
Focus is on static squat hold duration and explosive concentric phase.
"""

from kinemotion.core.types import MetricsDict
from kinemotion.core.validation import AthleteProfile, MetricBounds


class SJBounds:
    """Collection of physiological bounds for all SJ metrics."""

    # FLIGHT TIME (seconds)
    FLIGHT_TIME = MetricBounds(
        absolute_min=0.08,  # Frame rate resolution limit
        practical_min=0.15,  # Minimum effort jump
        recreational_min=0.20,  # Untrained ~5-10cm
        recreational_max=0.50,  # Recreational ~20-35cm
        elite_min=0.55,  # Trained ~50cm
        elite_max=1.00,  # Elite >80cm
        absolute_max=1.20,
        unit="s",
    )

    # JUMP HEIGHT (meters) - SJ typically achieves less than CMJ
    JUMP_HEIGHT = MetricBounds(
        absolute_min=0.02,
        practical_min=0.05,
        recreational_min=0.10,  # Untrained with effort
        recreational_max=0.45,  # Good recreational
        elite_min=0.50,
        elite_max=0.85,
        absolute_max=1.20,
        unit="m",
    )

    # SQUAT HOLD DURATION (seconds) - Key SJ-specific metric
    SQUAT_HOLD_DURATION = MetricBounds(
        absolute_min=0.0,  # Can be very short
        practical_min=0.0,
        recreational_min=0.0,  # May not be detectable
        recreational_max=2.0,  # Very long static holds
        elite_min=0.0,
        elite_max=3.0,  # Elite athletes sometimes use long pauses
        absolute_max=5.0,  # Maximum reasonable squat hold
        unit="s",
    )

    # CONCENTRIC DURATION (seconds) - Similar to CMJ concentric phase
    CONCENTRIC_DURATION = MetricBounds(
        absolute_min=0.08,
        practical_min=0.15,  # Extreme plyometric
        recreational_min=0.30,  # Moderate propulsion
        recreational_max=0.70,  # Slow push-off
        elite_min=0.20,
        elite_max=0.45,
        absolute_max=1.50,
        unit="s",
    )

    # PEAK CONCENTRIC VELOCITY (m/s, upward) - Key SJ metric
    PEAK_CONCENTRIC_VELOCITY = MetricBounds(
        absolute_min=0.30,
        practical_min=0.50,
        recreational_min=1.60,
        recreational_max=2.60,
        elite_min=2.80,
        elite_max=4.00,
        absolute_max=5.00,
        unit="m/s",
    )

    # PEAK POWER (Watts) - Requires mass calculation
    PEAK_POWER = MetricBounds(
        absolute_min=1000,  # Minimum for adult
        practical_min=1500,
        recreational_min=3000,
        recreational_max=8000,
        elite_min=9000,
        elite_max=15000,
        absolute_max=20000,
        unit="W",
    )

    # MEAN POWER (Watts) - During concentric phase
    MEAN_POWER = MetricBounds(
        absolute_min=500,  # Minimum for adult
        practical_min=800,
        recreational_min=1500,
        recreational_max=5000,
        elite_min=6000,
        elite_max=10000,
        absolute_max=15000,
        unit="W",
    )

    # PEAK FORCE (Newtons) - During concentric phase
    PEAK_FORCE = MetricBounds(
        absolute_min=1000,  # Minimum for adult
        practical_min=1500,
        recreational_min=2000,
        recreational_max=4000,
        elite_min=4500,
        elite_max=6000,
        absolute_max=8000,
        unit="N",
    )


class MetricConsistency:
    """Cross-validation tolerance for metric consistency checks."""

    # Jump height from flight time: h = g*t²/8
    # Allow 10% deviation for measurement noise
    HEIGHT_FLIGHT_TIME_TOLERANCE = 0.10

    # Power from velocity and mass: P = F × v
    # Allow 25% deviation (power calculations are complex)
    POWER_VELOCITY_TOLERANCE = 0.25

    # Squat hold to concentric duration ratio
    # Typically 0-2.0, flag if outside 0-3.0
    SQUAT_CONCENTRIC_RATIO_MIN = 0.0
    SQUAT_CONCENTRIC_RATIO_MAX = 3.0


# Athlete profile examples with expected metric ranges
ATHLETE_PROFILES = {
    "elderly_deconditioned": {
        "label": "Elderly/Deconditioned (70+, sedentary)",
        "profile": AthleteProfile.ELDERLY,
        "expected": {
            "jump_height_m": (0.05, 0.15),
            "flight_time_s": (0.10, 0.18),
            "squat_hold_duration_s": (0.0, 1.5),
            "concentric_duration_s": (0.40, 0.90),
            "peak_concentric_velocity_ms": (0.8, 1.4),
            "peak_power_w": (1500, 3000),
            "mean_power_w": (800, 2000),
            "peak_force_n": (1500, 3000),
        },
    },
    "recreational": {
        "label": "Recreational Athlete (fitness participant, 30-45 yrs)",
        "profile": AthleteProfile.RECREATIONAL,
        "expected": {
            "jump_height_m": (0.20, 0.45),
            "flight_time_s": (0.25, 0.50),
            "squat_hold_duration_s": (0.0, 1.0),
            "concentric_duration_s": (0.35, 0.65),
            "peak_concentric_velocity_ms": (1.8, 2.5),
            "peak_power_w": (4000, 7000),
            "mean_power_w": (2000, 4500),
            "peak_force_n": (2500, 3500),
        },
    },
    "elite_male": {
        "label": "Elite Male Athlete (college/pro volleyball/basketball)",
        "profile": AthleteProfile.ELITE,
        "expected": {
            "jump_height_m": (0.60, 0.85),
            "flight_time_s": (0.70, 0.80),
            "squat_hold_duration_s": (0.0, 1.5),
            "concentric_duration_s": (0.25, 0.40),
            "peak_concentric_velocity_ms": (3.2, 3.8),
            "peak_power_w": (10000, 14000),
            "mean_power_w": (6000, 9000),
            "peak_force_n": (4500, 5500),
        },
    },
}


def estimate_athlete_profile(
    metrics_dict: MetricsDict, _gender: str | None = None
) -> AthleteProfile:
    """Estimate athlete profile from SJ metrics.

    Uses jump height as primary classifier (similar to CMJ):
    - <0.15m: Elderly
    - 0.15-0.20m: Untrained
    - 0.20-0.45m: Recreational
    - 0.45-0.50m: Trained
    - >0.50m: Elite

    NOTE: Squat Jump typically achieves lower heights than CMJ due to
    the lack of pre-stretch (no countermovement). Adjust expectations
    accordingly when analyzing results.

    Args:
        metrics_dict: Dictionary with SJ metric values
        gender: Optional gender for context ("M"/"F"). Currently informational only.

    Returns:
        Estimated AthleteProfile
    """
    # Support both nested "data" structure and flat structure
    # Extract with unit suffix as used in serialization, or without suffix (legacy)
    data = metrics_dict.get("data", metrics_dict)
    jump_height = data.get("jump_height_m") or data.get("jump_height", 0)

    if jump_height < 0.15:
        return AthleteProfile.ELDERLY
    elif jump_height < 0.20:
        return AthleteProfile.UNTRAINED
    elif jump_height < 0.45:
        return AthleteProfile.RECREATIONAL
    elif jump_height < 0.50:
        return AthleteProfile.TRAINED
    else:
        return AthleteProfile.ELITE
