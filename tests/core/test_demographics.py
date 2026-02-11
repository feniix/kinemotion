"""Tests for athlete demographics module."""

import pytest

from kinemotion.core.demographics import (
    AgeGroup,
    AthleteDemographics,
    BiologicalSex,
    TrainingLevel,
    age_to_group,
)

# ---------------------------------------------------------------------------
# Enum serialization
# ---------------------------------------------------------------------------


class TestBiologicalSex:
    """Tests for BiologicalSex enum."""

    def test_values(self) -> None:
        assert BiologicalSex.MALE.value == "male"
        assert BiologicalSex.FEMALE.value == "female"

    def test_str_serialization(self) -> None:
        assert str(BiologicalSex.MALE) == "BiologicalSex.MALE"
        assert BiologicalSex.MALE == "male"

    def test_from_string(self) -> None:
        assert BiologicalSex("male") is BiologicalSex.MALE
        assert BiologicalSex("female") is BiologicalSex.FEMALE

    def test_invalid_value(self) -> None:
        with pytest.raises(ValueError):
            BiologicalSex("other")


class TestAgeGroup:
    """Tests for AgeGroup enum."""

    def test_all_values(self) -> None:
        assert AgeGroup.YOUTH.value == "youth"
        assert AgeGroup.ADULT.value == "adult"
        assert AgeGroup.MASTERS_35.value == "masters_35"
        assert AgeGroup.MASTERS_50.value == "masters_50"
        assert AgeGroup.SENIOR.value == "senior"

    def test_from_string(self) -> None:
        assert AgeGroup("adult") is AgeGroup.ADULT

    def test_member_count(self) -> None:
        assert len(AgeGroup) == 5


class TestTrainingLevel:
    """Tests for TrainingLevel enum."""

    def test_all_values(self) -> None:
        assert TrainingLevel.UNTRAINED.value == "untrained"
        assert TrainingLevel.RECREATIONAL.value == "recreational"
        assert TrainingLevel.TRAINED.value == "trained"
        assert TrainingLevel.COMPETITIVE.value == "competitive"
        assert TrainingLevel.ELITE.value == "elite"

    def test_from_string(self) -> None:
        assert TrainingLevel("elite") is TrainingLevel.ELITE

    def test_member_count(self) -> None:
        assert len(TrainingLevel) == 5


# ---------------------------------------------------------------------------
# age_to_group boundary tests
# ---------------------------------------------------------------------------


class TestAgeToGroup:
    """Tests for age_to_group() with boundary values."""

    @pytest.mark.parametrize(
        ("age", "expected"),
        [
            # Youth: <18
            (1, AgeGroup.YOUTH),
            (10, AgeGroup.YOUTH),
            (17, AgeGroup.YOUTH),
            # Adult: 18-34
            (18, AgeGroup.ADULT),
            (25, AgeGroup.ADULT),
            (34, AgeGroup.ADULT),
            # Masters 35: 35-49
            (35, AgeGroup.MASTERS_35),
            (42, AgeGroup.MASTERS_35),
            (49, AgeGroup.MASTERS_35),
            # Masters 50: 50-64
            (50, AgeGroup.MASTERS_50),
            (57, AgeGroup.MASTERS_50),
            (64, AgeGroup.MASTERS_50),
            # Senior: 65+
            (65, AgeGroup.SENIOR),
            (80, AgeGroup.SENIOR),
            (100, AgeGroup.SENIOR),
        ],
    )
    def test_boundary_values(self, age: int, expected: AgeGroup) -> None:
        assert age_to_group(age) == expected

    def test_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            age_to_group(0)

    def test_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            age_to_group(-5)


# ---------------------------------------------------------------------------
# AthleteDemographics dataclass
# ---------------------------------------------------------------------------


class TestAthleteDemographics:
    """Tests for AthleteDemographics dataclass."""

    def test_defaults_all_none(self) -> None:
        d = AthleteDemographics()
        assert d.sex is None
        assert d.age is None
        assert d.training_level is None

    def test_frozen(self) -> None:
        d = AthleteDemographics()
        with pytest.raises(AttributeError):
            d.sex = BiologicalSex.MALE  # type: ignore[misc]

    def test_with_all_fields(self) -> None:
        d = AthleteDemographics(
            sex=BiologicalSex.FEMALE,
            age=28,
            training_level=TrainingLevel.TRAINED,
        )
        assert d.sex is BiologicalSex.FEMALE
        assert d.age == 28
        assert d.training_level is TrainingLevel.TRAINED

    def test_age_group_property(self) -> None:
        d = AthleteDemographics(age=28)
        assert d.age_group is AgeGroup.ADULT

    def test_age_group_none_when_no_age(self) -> None:
        d = AthleteDemographics()
        assert d.age_group is None

    def test_age_group_youth(self) -> None:
        d = AthleteDemographics(age=15)
        assert d.age_group is AgeGroup.YOUTH

    def test_age_group_senior(self) -> None:
        d = AthleteDemographics(age=70)
        assert d.age_group is AgeGroup.SENIOR

    def test_equality(self) -> None:
        a = AthleteDemographics(sex=BiologicalSex.MALE, age=30)
        b = AthleteDemographics(sex=BiologicalSex.MALE, age=30)
        assert a == b

    def test_inequality(self) -> None:
        a = AthleteDemographics(sex=BiologicalSex.MALE)
        b = AthleteDemographics(sex=BiologicalSex.FEMALE)
        assert a != b


class TestAthleteDemographicsToDict:
    """Tests for to_dict() serialization."""

    def test_empty_returns_empty(self) -> None:
        d = AthleteDemographics()
        assert d.to_dict() == {}

    def test_sex_only(self) -> None:
        d = AthleteDemographics(sex=BiologicalSex.FEMALE)
        assert d.to_dict() == {"sex": "female"}

    def test_age_includes_age_group(self) -> None:
        d = AthleteDemographics(age=25)
        result = d.to_dict()
        assert result == {"age": 25, "age_group": "adult"}

    def test_training_level_only(self) -> None:
        d = AthleteDemographics(training_level=TrainingLevel.ELITE)
        assert d.to_dict() == {"training_level": "elite"}

    def test_all_fields(self) -> None:
        d = AthleteDemographics(
            sex=BiologicalSex.MALE,
            age=45,
            training_level=TrainingLevel.COMPETITIVE,
        )
        result = d.to_dict()
        assert result == {
            "sex": "male",
            "age": 45,
            "age_group": "masters_35",
            "training_level": "competitive",
        }


class TestAthleteDemographicsHasAny:
    """Tests for has_any() method."""

    def test_empty_is_false(self) -> None:
        assert not AthleteDemographics().has_any()

    def test_sex_only(self) -> None:
        assert AthleteDemographics(sex=BiologicalSex.MALE).has_any()

    def test_age_only(self) -> None:
        assert AthleteDemographics(age=30).has_any()

    def test_training_only(self) -> None:
        assert AthleteDemographics(training_level=TrainingLevel.TRAINED).has_any()

    def test_all_fields(self) -> None:
        d = AthleteDemographics(
            sex=BiologicalSex.FEMALE,
            age=22,
            training_level=TrainingLevel.ELITE,
        )
        assert d.has_any()
