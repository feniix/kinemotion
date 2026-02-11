"""Tests for the normative data module.

Validates sex-specific norm tables, age adjustment factors, and the
get_norms() function that combines both.
"""

from __future__ import annotations

import pytest

from kinemotion_backend.services.normative_data import (
    AGE_FACTORS,
    CM_DEPTH_NORMS,
    GCT_NORMS,
    JUMP_HEIGHT_NORMS,
    PEAK_VELOCITY_NORMS,
    RSI_NORMS,
    NormTable,
    _apply_age_factor,
    get_norms,
)

# ===========================================================================
# Table structure validation
# ===========================================================================

ALL_NORM_TABLES = [
    ("JUMP_HEIGHT_NORMS_male", JUMP_HEIGHT_NORMS["male"]),
    ("JUMP_HEIGHT_NORMS_female", JUMP_HEIGHT_NORMS["female"]),
    ("PEAK_VELOCITY_NORMS_male", PEAK_VELOCITY_NORMS["male"]),
    ("PEAK_VELOCITY_NORMS_female", PEAK_VELOCITY_NORMS["female"]),
    ("RSI_NORMS_male", RSI_NORMS["male"]),
    ("RSI_NORMS_female", RSI_NORMS["female"]),
    ("GCT_NORMS", GCT_NORMS),
    ("CM_DEPTH_NORMS", CM_DEPTH_NORMS),
]


class TestTableStructure:
    """Validate that all norm tables have correct structure."""

    @pytest.mark.parametrize("table_name, table", ALL_NORM_TABLES)
    def test_table_is_non_empty_list(self, table_name: str, table: NormTable) -> None:
        """Each norm table is a non-empty list of tuples."""
        assert isinstance(table, list)
        assert len(table) > 0

    @pytest.mark.parametrize("table_name, table", ALL_NORM_TABLES)
    def test_table_entries_are_valid_tuples(self, table_name: str, table: NormTable) -> None:
        """Each entry is (str, float, float) with low <= high."""
        for category, low, high in table:
            assert isinstance(category, str), f"{table_name}: category must be str"
            assert isinstance(low, (int, float)), f"{table_name}: low must be numeric"
            assert isinstance(high, (int, float)), f"{table_name}: high must be numeric"
            assert low <= high, f"{table_name}: low ({low}) must be <= high ({high})"

    def test_sex_specific_tables_have_both_sexes(self) -> None:
        """Sex-specific tables have both 'male' and 'female' keys."""
        for name, table in [
            ("JUMP_HEIGHT_NORMS", JUMP_HEIGHT_NORMS),
            ("PEAK_VELOCITY_NORMS", PEAK_VELOCITY_NORMS),
            ("RSI_NORMS", RSI_NORMS),
        ]:
            assert "male" in table, f"{name} missing 'male' key"
            assert "female" in table, f"{name} missing 'female' key"

    def test_female_norms_lower_than_male_for_jump_height(self) -> None:
        """Female jump height norms have lower values than male (physiological)."""
        male_max = max(high for _, _, high in JUMP_HEIGHT_NORMS["male"])
        female_max = max(high for _, _, high in JUMP_HEIGHT_NORMS["female"])
        assert female_max < male_max

    def test_female_norms_lower_than_male_for_rsi(self) -> None:
        """Female RSI norms have lower values than male."""
        male_max = max(high for _, _, high in RSI_NORMS["male"])
        female_max = max(high for _, _, high in RSI_NORMS["female"])
        assert female_max < male_max


# ===========================================================================
# Age factors
# ===========================================================================


class TestAgeFactors:
    """Tests for the AGE_FACTORS dictionary."""

    def test_adult_factor_is_reference(self) -> None:
        """Adult age group is the reference group with factor 1.00."""
        assert AGE_FACTORS["adult"] == 1.0

    def test_youth_factor_below_adult(self) -> None:
        """Youth factor is below adult (still developing)."""
        assert AGE_FACTORS["youth"] < AGE_FACTORS["adult"]

    def test_factors_decrease_with_age(self) -> None:
        """Age factors decrease progressively: adult > masters_35 > masters_50 > senior."""
        assert AGE_FACTORS["adult"] > AGE_FACTORS["masters_35"]
        assert AGE_FACTORS["masters_35"] > AGE_FACTORS["masters_50"]
        assert AGE_FACTORS["masters_50"] > AGE_FACTORS["senior"]

    def test_all_factors_positive(self) -> None:
        """All age factors are positive (performance never zero)."""
        for group, factor in AGE_FACTORS.items():
            assert factor > 0, f"Factor for {group} must be positive"

    def test_all_factors_at_most_one(self) -> None:
        """No age factor exceeds 1.0 (adult is the reference max)."""
        for group, factor in AGE_FACTORS.items():
            assert factor <= 1.0, f"Factor for {group} must be <= 1.0"

    def test_expected_age_groups_present(self) -> None:
        """All expected age groups are in AGE_FACTORS."""
        expected = {"youth", "adult", "masters_35", "masters_50", "senior"}
        assert set(AGE_FACTORS.keys()) == expected


# ===========================================================================
# _apply_age_factor
# ===========================================================================


class TestApplyAgeFactor:
    """Tests for the internal _apply_age_factor helper."""

    SAMPLE_NORMS: NormTable = [
        ("low", 10.0, 20.0),
        ("high", 20.0, 30.0),
    ]

    def test_adult_returns_unmodified(self) -> None:
        """Adult age group returns the original norms unchanged."""
        result = _apply_age_factor(self.SAMPLE_NORMS, "adult")
        assert result == self.SAMPLE_NORMS

    def test_none_returns_unmodified(self) -> None:
        """None age group returns the original norms unchanged (default)."""
        result = _apply_age_factor(self.SAMPLE_NORMS, None)
        assert result == self.SAMPLE_NORMS

    def test_youth_scales_boundaries(self) -> None:
        """Youth factor (0.85) scales all boundaries down."""
        result = _apply_age_factor(self.SAMPLE_NORMS, "youth")
        factor = AGE_FACTORS["youth"]
        assert result[0] == ("low", round(10.0 * factor, 1), round(20.0 * factor, 1))
        assert result[1] == ("high", round(20.0 * factor, 1), round(30.0 * factor, 1))

    def test_senior_scales_boundaries(self) -> None:
        """Senior factor (0.70) scales all boundaries down significantly."""
        result = _apply_age_factor(self.SAMPLE_NORMS, "senior")
        factor = AGE_FACTORS["senior"]
        assert result[0] == ("low", round(10.0 * factor, 1), round(20.0 * factor, 1))

    def test_unknown_age_group_uses_factor_one(self) -> None:
        """Unknown age group uses factor 1.0 (no change)."""
        result = _apply_age_factor(self.SAMPLE_NORMS, "unknown_group")
        # factor = 1.0 from AGE_FACTORS.get("unknown_group", 1.0)
        assert result == [
            ("low", 10.0, 20.0),
            ("high", 20.0, 30.0),
        ]

    def test_categories_preserved(self) -> None:
        """Category names are not affected by age scaling."""
        result = _apply_age_factor(self.SAMPLE_NORMS, "masters_50")
        assert result[0][0] == "low"
        assert result[1][0] == "high"


# ===========================================================================
# get_norms
# ===========================================================================


class TestGetNorms:
    """Tests for the main get_norms function."""

    # -- Sex-specific tables --

    def test_none_sex_defaults_to_male(self) -> None:
        """None sex returns male norms (default)."""
        result = get_norms(JUMP_HEIGHT_NORMS, sex=None, age_group=None)
        assert result == JUMP_HEIGHT_NORMS["male"]

    def test_male_sex_returns_male_table(self) -> None:
        """Explicit 'male' returns male norms."""
        result = get_norms(JUMP_HEIGHT_NORMS, sex="male", age_group=None)
        assert result == JUMP_HEIGHT_NORMS["male"]

    def test_female_sex_returns_female_table(self) -> None:
        """Explicit 'female' returns female norms."""
        result = get_norms(JUMP_HEIGHT_NORMS, sex="female", age_group=None)
        assert result == JUMP_HEIGHT_NORMS["female"]

    def test_unknown_sex_falls_back_to_male(self) -> None:
        """Unknown sex value falls back to male norms."""
        result = get_norms(JUMP_HEIGHT_NORMS, sex="other", age_group=None)
        assert result == JUMP_HEIGHT_NORMS["male"]

    # -- Universal tables --

    def test_universal_table_ignores_sex(self) -> None:
        """Universal norms (GCT) are the same regardless of sex."""
        result_none = get_norms(GCT_NORMS, sex=None, age_group=None)
        result_male = get_norms(GCT_NORMS, sex="male", age_group=None)
        result_female = get_norms(GCT_NORMS, sex="female", age_group=None)
        assert result_none == result_male == result_female == GCT_NORMS

    # -- Age adjustment --

    def test_age_adjustment_applied_to_sex_specific(self) -> None:
        """Age factor scales sex-specific norms."""
        adult_norms = get_norms(JUMP_HEIGHT_NORMS, sex="male", age_group=None)
        youth_norms = get_norms(JUMP_HEIGHT_NORMS, sex="male", age_group="youth")

        # Youth boundaries should be lower
        for (_, adult_low, _), (_, youth_low, _) in zip(adult_norms, youth_norms, strict=True):
            assert youth_low < adult_low

    def test_age_adjustment_applied_to_universal(self) -> None:
        """Age factor scales universal norms."""
        adult_norms = get_norms(CM_DEPTH_NORMS, age_group=None)
        senior_norms = get_norms(CM_DEPTH_NORMS, age_group="senior")

        for (_, adult_low, _), (_, senior_low, _) in zip(adult_norms, senior_norms, strict=True):
            assert senior_low < adult_low

    # -- Combined sex + age --

    def test_female_youth_norms(self) -> None:
        """Female + youth gives doubly reduced norms."""
        male_adult = get_norms(JUMP_HEIGHT_NORMS, sex="male", age_group=None)
        female_youth = get_norms(JUMP_HEIGHT_NORMS, sex="female", age_group="youth")

        # Female youth should be much lower than male adult
        assert female_youth[0][1] < male_adult[0][1]

    def test_male_adult_is_default_baseline(self) -> None:
        """get_norms(table, None, None) equals table['male'] for sex-specific."""
        result = get_norms(RSI_NORMS, sex=None, age_group=None)
        assert result == RSI_NORMS["male"]
