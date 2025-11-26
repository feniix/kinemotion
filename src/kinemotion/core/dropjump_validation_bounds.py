"""Drop jump metrics physiological bounds for validation testing.

This module defines realistic physiological bounds for Drop Jump metrics
based on biomechanical literature and real-world athlete performance.

Drop jump metrics differ from CMJ:
- Contact time (ground interaction during landing)
- Flight time (time in air after landing)
- RSI (Reactive Strength Index) = flight_time / contact_time
- Jump height (calculated from flight time)

References:
- Komi & Bosco (1978): Drop jump RSI and elastic properties
- Flanagan & Comyns (2008): RSI reliability and athlete assessment
- Covens et al. (2019): Drop jump kinetics across athletes
"""

from dataclasses import dataclass
from enum import Enum


class AthleteProfile(Enum):
    """Athlete performance categories for metric bounds."""

    ELDERLY = "elderly"  # 70+, deconditioned
    UNTRAINED = "untrained"  # Sedentary, no training
    RECREATIONAL = "recreational"  # Fitness class, moderate activity
    TRAINED = "trained"  # Regular athlete, 3-5 years training
    ELITE = "elite"  # Competitive athlete, college/professional level


@dataclass
class MetricBounds:
    """Physiological bounds for a single metric.

    Attributes:
        absolute_min: Absolute minimum value (error threshold)
        practical_min: Practical minimum for weakest athletes
        recreational_min: Minimum for recreational athletes
        recreational_max: Maximum for recreational athletes
        elite_min: Minimum for elite athletes
        elite_max: Maximum for elite athletes
        absolute_max: Absolute maximum value (error threshold)
        unit: Unit of measurement (e.g., "s", "m", "ratio")
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


class DropJumpBounds:
    """Collection of physiological bounds for all drop jump metrics."""

    # GROUND CONTACT TIME (seconds, landing interaction)
    CONTACT_TIME = MetricBounds(
        absolute_min=0.08,  # Physiological minimum: neural delay + deceleration
        practical_min=0.15,  # Extreme plyometric
        recreational_min=0.35,  # Typical landing
        recreational_max=0.70,  # Slower absorption
        elite_min=0.20,
        elite_max=0.50,
        absolute_max=1.50,
        unit="s",
    )

    # FLIGHT TIME (seconds, after landing)
    FLIGHT_TIME = MetricBounds(
        absolute_min=0.30,
        practical_min=0.40,  # Minimal jump
        recreational_min=0.50,
        recreational_max=0.85,
        elite_min=0.65,
        elite_max=1.10,
        absolute_max=1.40,
        unit="s",
    )

    # JUMP HEIGHT (meters, calculated from flight time)
    JUMP_HEIGHT = MetricBounds(
        absolute_min=0.05,
        practical_min=0.10,
        recreational_min=0.25,
        recreational_max=0.65,
        elite_min=0.50,
        elite_max=1.00,
        absolute_max=1.30,
        unit="m",
    )

    # REACTIVE STRENGTH INDEX (RSI) = flight_time / contact_time (ratio, no unit)
    RSI = MetricBounds(
        absolute_min=0.30,  # Very poor reactive ability
        practical_min=0.50,
        recreational_min=0.70,
        recreational_max=1.80,
        elite_min=1.50,  # Elite: fast contact, long flight
        elite_max=3.50,
        absolute_max=5.00,
        unit="ratio",
    )


def estimate_athlete_profile(
    metrics: dict, gender: str | None = None
) -> AthleteProfile:
    """Estimate athlete profile from drop jump metrics.

    Uses jump_height and contact_time to classify athlete level.

    NOTE: Bounds are calibrated for adult males. Female athletes typically achieve
    60-70% of male heights due to lower muscle mass and strength. If analyzing
    female athletes, interpret results one level lower than classification suggests.

    Args:
        metrics: Dictionary with drop jump metric values
        gender: Optional gender for context ("M"/"F"). Currently informational only.

    Returns:
        Estimated AthleteProfile (ELDERLY, UNTRAINED, RECREATIONAL, TRAINED, or ELITE)
    """
    jump_height = metrics.get("data", {}).get("jump_height_m")
    contact_time = metrics.get("data", {}).get("ground_contact_time_ms")

    if jump_height is None or contact_time is None:
        return AthleteProfile.RECREATIONAL  # Default

    # Convert contact_time from ms to seconds
    contact_time_s = contact_time / 1000.0

    # Decision logic: Use weighted combination to avoid over-weighting single metrics
    # Calculate profile scores based on each metric
    height_score = 0.0
    if jump_height < 0.25:
        height_score = 0  # Elderly
    elif jump_height < 0.35:
        height_score = 1  # Untrained
    elif jump_height < 0.50:
        height_score = 2  # Recreational
    elif jump_height < 0.70:
        height_score = 3  # Trained
    else:
        height_score = 4  # Elite

    contact_score = 0.0
    if contact_time_s > 0.60:
        contact_score = 0  # Elderly
    elif contact_time_s > 0.50:
        contact_score = 1  # Untrained
    elif contact_time_s > 0.45:
        contact_score = 2  # Recreational
    elif contact_time_s > 0.40:
        contact_score = 3  # Trained
    else:
        contact_score = 4  # Elite

    # Weight height more heavily (70%) than contact time (30%)
    # Height is more reliable indicator across populations
    combined_score = (height_score * 0.70) + (contact_score * 0.30)

    if combined_score < 1.0:
        return AthleteProfile.ELDERLY
    elif combined_score < 1.7:
        return AthleteProfile.UNTRAINED
    elif combined_score < 2.7:
        return AthleteProfile.RECREATIONAL
    elif combined_score < 3.7:
        return AthleteProfile.TRAINED
    else:
        return AthleteProfile.ELITE
