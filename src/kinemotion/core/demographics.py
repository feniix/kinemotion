"""Athlete demographics for normative comparison.

Demographics affect only the interpretation/normative layer (how results
compare to peers), NOT the measurement layer (how metrics are calculated
from video). Video processing, pose estimation, and metric calculations
remain unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .validation import AthleteProfile


class BiologicalSex(str, Enum):
    """Biological sex for normative reference group selection."""

    MALE = "male"
    FEMALE = "female"


class AgeGroup(str, Enum):
    """Age group categories for normative adjustments."""

    YOUTH = "youth"  # <18
    ADULT = "adult"  # 18-34
    MASTERS_35 = "masters_35"  # 35-49
    MASTERS_50 = "masters_50"  # 50-64
    SENIOR = "senior"  # 65+


class TrainingLevel(str, Enum):
    """Training level for normative reference group selection."""

    UNTRAINED = "untrained"
    RECREATIONAL = "recreational"
    TRAINED = "trained"
    COMPETITIVE = "competitive"
    ELITE = "elite"


_TRAINING_LEVEL_TO_PROFILE: dict[TrainingLevel, AthleteProfile] = {
    TrainingLevel.UNTRAINED: AthleteProfile.UNTRAINED,
    TrainingLevel.RECREATIONAL: AthleteProfile.RECREATIONAL,
    TrainingLevel.TRAINED: AthleteProfile.TRAINED,
    TrainingLevel.COMPETITIVE: AthleteProfile.COMPETITIVE,
    TrainingLevel.ELITE: AthleteProfile.ELITE,
}


def training_level_to_profile(level: TrainingLevel) -> AthleteProfile:
    """Map a TrainingLevel to the corresponding AthleteProfile for validation."""
    return _TRAINING_LEVEL_TO_PROFILE[level]


def age_to_group(age: int) -> AgeGroup:
    """Convert an exact age to an age group category.

    Args:
        age: Athlete age in years (must be positive).

    Returns:
        The corresponding AgeGroup.

    Raises:
        ValueError: If age is not a positive integer.
    """
    if age < 1:
        raise ValueError(f"Age must be positive, got {age}")
    if age < 18:
        return AgeGroup.YOUTH
    if age < 35:
        return AgeGroup.ADULT
    if age < 50:
        return AgeGroup.MASTERS_35
    if age < 65:
        return AgeGroup.MASTERS_50
    return AgeGroup.SENIOR


@dataclass(frozen=True)
class AthleteDemographics:
    """Optional athlete demographics for normative comparison.

    All fields are optional. When None, the interpretation layer
    defaults to male adult norms (backward-compatible behavior).

    Attributes:
        sex: Biological sex for sex-specific norm selection.
        age: Exact age in years; used to derive age_group.
        training_level: Self-reported training level.
    """

    sex: BiologicalSex | None = None
    age: int | None = None
    training_level: TrainingLevel | None = None

    @property
    def age_group(self) -> AgeGroup | None:
        """Derive age group from exact age, or None if age not provided."""
        if self.age is None:
            return None
        return age_to_group(self.age)

    def to_dict(self) -> dict[str, str | int | None]:
        """Serialize to a plain dict for JSON output."""
        result: dict[str, str | int | None] = {}
        if self.sex is not None:
            result["sex"] = self.sex.value
        if self.age is not None:
            result["age"] = self.age
            result["age_group"] = self.age_group.value if self.age_group else None
        if self.training_level is not None:
            result["training_level"] = self.training_level.value
        return result

    def has_any(self) -> bool:
        """Return True if any demographic field is provided."""
        return self.sex is not None or self.age is not None or self.training_level is not None
