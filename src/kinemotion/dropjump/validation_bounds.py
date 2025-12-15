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

from kinemotion.core.types import MetricsDict
from kinemotion.core.validation import AthleteProfile, MetricBounds


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


def _score_jump_height(jump_height: float) -> float:
    """Convert jump height to athlete profile score (0-4).

    Args:
        jump_height: Jump height in meters

    Returns:
        Score from 0 (elderly) to 4 (elite)
    """
    thresholds = [(0.25, 0), (0.35, 1), (0.50, 2), (0.70, 3)]
    for threshold, score in thresholds:
        if jump_height < threshold:
            return float(score)
    return 4.0  # Elite


def _score_contact_time(contact_time_s: float) -> float:
    """Convert contact time to athlete profile score (0-4).

    Args:
        contact_time_s: Ground contact time in seconds

    Returns:
        Score from 0 (elderly) to 4 (elite)
    """
    thresholds = [(0.60, 0), (0.50, 1), (0.45, 2), (0.40, 3)]
    for threshold, score in thresholds:
        if contact_time_s > threshold:
            return float(score)
    return 4.0  # Elite


def _classify_combined_score(combined_score: float) -> AthleteProfile:
    """Classify combined score into athlete profile.

    Args:
        combined_score: Weighted score from height and contact time

    Returns:
        Athlete profile classification
    """
    thresholds = [
        (1.0, AthleteProfile.ELDERLY),
        (1.7, AthleteProfile.UNTRAINED),
        (2.7, AthleteProfile.RECREATIONAL),
        (3.7, AthleteProfile.TRAINED),
    ]
    for threshold, profile in thresholds:
        if combined_score < threshold:
            return profile
    return AthleteProfile.ELITE


def estimate_athlete_profile(metrics: MetricsDict, gender: str | None = None) -> AthleteProfile:
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
        return AthleteProfile.RECREATIONAL

    contact_time_s = contact_time / 1000.0

    # Calculate weighted combination: height (70%) + contact time (30%)
    # Height is more reliable indicator across populations
    height_score = _score_jump_height(jump_height)
    contact_score = _score_contact_time(contact_time_s)
    combined_score = (height_score * 0.70) + (contact_score * 0.30)

    return _classify_combined_score(combined_score)
