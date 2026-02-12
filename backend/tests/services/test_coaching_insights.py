"""Tests for the cross-metric coaching insights module.

Validates that rule-based coaching insights are correctly generated from
per-metric classifications for all supported jump types (Drop Jump, CMJ, SJ).
"""

from __future__ import annotations

import pytest

from kinemotion_backend.services.coaching_insights import (
    generate_cmj_insights,
    generate_dropjump_insights,
    generate_sj_insights,
)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _assert_insight_structure(insight: dict[str, object]) -> None:
    """Verify that an insight dict has the correct shape."""
    assert "type" in insight
    assert insight["type"] in {"strength", "limiter", "observation"}
    assert "key" in insight
    assert isinstance(insight["key"], str)
    assert "related_metrics" in insight
    assert isinstance(insight["related_metrics"], list)
    assert len(insight["related_metrics"]) > 0
    assert "priority" in insight
    assert isinstance(insight["priority"], int)


def _has_insight(insights: list[dict[str, object]], key: str) -> bool:
    """Check if an insight with the given key exists in the list."""
    return any(i["key"] == key for i in insights)


def _get_insight(insights: list[dict[str, object]], key: str) -> dict[str, object]:
    """Get a specific insight by key."""
    for i in insights:
        if i["key"] == key:
            return i
    raise AssertionError(f"Insight '{key}' not found in {[i['key'] for i in insights]}")


# ===========================================================================
# Drop Jump insight tests
# ===========================================================================


class TestDropJumpInsights:
    """Tests for generate_dropjump_insights."""

    def test_height_limiter_rsi_strong_height_weak(self) -> None:
        """RSI strong + height weak -> dj_height_limiter."""
        categories = {"rsi": "very_good", "jump_height": "poor", "ground_contact_time": "average"}
        insights = generate_dropjump_insights(categories)

        assert _has_insight(insights, "dj_height_limiter")
        insight = _get_insight(insights, "dj_height_limiter")
        assert insight["type"] == "limiter"
        assert insight["priority"] == 1
        assert "rsi" in insight["related_metrics"]
        assert "jump_height" in insight["related_metrics"]

    def test_rsi_limiter_rsi_weak_height_strong(self) -> None:
        """RSI weak + height strong -> dj_rsi_limiter."""
        categories = {"rsi": "poor", "jump_height": "good", "ground_contact_time": "average"}
        insights = generate_dropjump_insights(categories)

        assert _has_insight(insights, "dj_rsi_limiter")
        insight = _get_insight(insights, "dj_rsi_limiter")
        assert insight["type"] == "limiter"

    def test_both_weak(self) -> None:
        """RSI weak + height weak -> dj_both_weak."""
        categories = {
            "rsi": "below_average",
            "jump_height": "poor",
            "ground_contact_time": "average",
        }
        insights = generate_dropjump_insights(categories)

        assert _has_insight(insights, "dj_both_weak")
        insight = _get_insight(insights, "dj_both_weak")
        assert insight["type"] == "limiter"

    def test_rsi_strength_standalone(self) -> None:
        """RSI strong -> dj_rsi_strength (any height)."""
        categories = {"rsi": "excellent", "jump_height": "average"}
        insights = generate_dropjump_insights(categories)

        assert _has_insight(insights, "dj_rsi_strength")
        insight = _get_insight(insights, "dj_rsi_strength")
        assert insight["type"] == "strength"
        assert insight["priority"] == 3

    def test_gct_strength(self) -> None:
        """GCT excellent/very_good -> dj_gct_strength."""
        for gct_cat in ("excellent", "very_good"):
            categories = {
                "rsi": "average",
                "jump_height": "average",
                "ground_contact_time": gct_cat,
            }
            insights = generate_dropjump_insights(categories)

            assert _has_insight(insights, "dj_gct_strength"), f"Failed for {gct_cat}"
            insight = _get_insight(insights, "dj_gct_strength")
            assert insight["type"] == "strength"

    def test_gct_limiter(self) -> None:
        """GCT below_average -> dj_gct_limiter."""
        categories = {
            "rsi": "average",
            "jump_height": "average",
            "ground_contact_time": "below_average",
        }
        insights = generate_dropjump_insights(categories)

        assert _has_insight(insights, "dj_gct_limiter")
        insight = _get_insight(insights, "dj_gct_limiter")
        assert insight["type"] == "limiter"

    def test_gct_observation(self) -> None:
        """GCT average -> dj_gct_observation."""
        categories = {"rsi": "average", "jump_height": "average", "ground_contact_time": "average"}
        insights = generate_dropjump_insights(categories)

        assert _has_insight(insights, "dj_gct_observation")
        insight = _get_insight(insights, "dj_gct_observation")
        assert insight["type"] == "observation"
        assert insight["priority"] == 2

    def test_strong_rsi_and_weak_height_gives_both_limiter_and_strength(self) -> None:
        """When RSI is strong and height weak, both height_limiter AND rsi_strength fire."""
        categories = {"rsi": "good", "jump_height": "below_average", "ground_contact_time": "good"}
        insights = generate_dropjump_insights(categories)

        assert _has_insight(insights, "dj_height_limiter")
        assert _has_insight(insights, "dj_rsi_strength")

    @pytest.mark.parametrize("strong_cat", ["good", "very_good", "excellent", "above_average"])
    def test_all_strong_rsi_categories_trigger_strength(self, strong_cat: str) -> None:
        """All STRONG_CATS values for RSI trigger dj_rsi_strength."""
        categories = {"rsi": strong_cat, "jump_height": "average"}
        insights = generate_dropjump_insights(categories)

        assert _has_insight(insights, "dj_rsi_strength")


# ===========================================================================
# CMJ insight tests
# ===========================================================================


class TestCmjInsights:
    """Tests for generate_cmj_insights."""

    def test_height_limiter(self) -> None:
        """Height weak + velocity avg+ -> cmj_height_limiter."""
        categories = {"jump_height": "poor", "peak_concentric_velocity": "average"}
        insights = generate_cmj_insights(categories)

        assert _has_insight(insights, "cmj_height_limiter")
        insight = _get_insight(insights, "cmj_height_limiter")
        assert insight["type"] == "limiter"
        assert "jump_height" in insight["related_metrics"]
        assert "peak_concentric_velocity" in insight["related_metrics"]

    def test_velocity_limiter(self) -> None:
        """Height avg+ + velocity weak -> cmj_velocity_limiter."""
        categories = {"jump_height": "average", "peak_concentric_velocity": "below_average"}
        insights = generate_cmj_insights(categories)

        assert _has_insight(insights, "cmj_velocity_limiter")
        insight = _get_insight(insights, "cmj_velocity_limiter")
        assert insight["type"] == "limiter"

    def test_depth_too_deep_and_height_weak(self) -> None:
        """Depth too_deep + height weak -> cmj_depth_too_deep."""
        categories = {
            "jump_height": "poor",
            "peak_concentric_velocity": "average",
            "countermovement_depth": "too_deep",
        }
        insights = generate_cmj_insights(categories)

        assert _has_insight(insights, "cmj_depth_too_deep")
        insight = _get_insight(insights, "cmj_depth_too_deep")
        assert insight["type"] == "limiter"
        assert "countermovement_depth" in insight["related_metrics"]

    def test_depth_too_shallow_and_height_weak(self) -> None:
        """Depth too_shallow + height weak -> cmj_depth_too_shallow."""
        categories = {
            "jump_height": "below_average",
            "peak_concentric_velocity": "below_average",
            "countermovement_depth": "too_shallow",
        }
        insights = generate_cmj_insights(categories)

        assert _has_insight(insights, "cmj_depth_too_shallow")

    def test_depth_optimal(self) -> None:
        """Depth optimal -> cmj_depth_optimal."""
        categories = {
            "jump_height": "average",
            "peak_concentric_velocity": "average",
            "countermovement_depth": "optimal",
        }
        insights = generate_cmj_insights(categories)

        assert _has_insight(insights, "cmj_depth_optimal")
        insight = _get_insight(insights, "cmj_depth_optimal")
        assert insight["type"] == "strength"

    def test_power_strength(self) -> None:
        """Height strong + velocity strong -> cmj_power_strength."""
        categories = {
            "jump_height": "excellent",
            "peak_concentric_velocity": "very_good",
        }
        insights = generate_cmj_insights(categories)

        assert _has_insight(insights, "cmj_power_strength")
        insight = _get_insight(insights, "cmj_power_strength")
        assert insight["type"] == "strength"

    def test_depth_too_deep_not_triggered_when_height_not_weak(self) -> None:
        """Depth too_deep does NOT trigger cmj_depth_too_deep if height is average+."""
        categories = {
            "jump_height": "average",
            "peak_concentric_velocity": "average",
            "countermovement_depth": "too_deep",
        }
        insights = generate_cmj_insights(categories)

        assert not _has_insight(insights, "cmj_depth_too_deep")


# ===========================================================================
# Squat Jump insight tests
# ===========================================================================


class TestSjInsights:
    """Tests for generate_sj_insights."""

    def test_height_limiter(self) -> None:
        """Height weak + velocity avg+ -> sj_height_limiter (observation)."""
        categories = {"jump_height": "poor", "peak_concentric_velocity": "average"}
        insights = generate_sj_insights(categories)

        assert _has_insight(insights, "sj_height_limiter")
        insight = _get_insight(insights, "sj_height_limiter")
        assert insight["type"] == "observation"
        assert insight["priority"] == 2

    def test_velocity_limiter(self) -> None:
        """Height avg+ + velocity weak -> sj_velocity_limiter."""
        categories = {"jump_height": "good", "peak_concentric_velocity": "poor"}
        insights = generate_sj_insights(categories)

        assert _has_insight(insights, "sj_velocity_limiter")
        insight = _get_insight(insights, "sj_velocity_limiter")
        assert insight["type"] == "limiter"
        assert insight["priority"] == 1

    def test_power_strength(self) -> None:
        """Height strong + velocity strong -> sj_power_strength."""
        categories = {"jump_height": "very_good", "peak_concentric_velocity": "good"}
        insights = generate_sj_insights(categories)

        assert _has_insight(insights, "sj_power_strength")
        insight = _get_insight(insights, "sj_power_strength")
        assert insight["type"] == "strength"
        assert insight["priority"] == 3


# ===========================================================================
# Priority ordering tests
# ===========================================================================


class TestPriorityOrdering:
    """Tests that insights are sorted by priority (limiters first)."""

    def test_limiters_before_observations_before_strengths(self) -> None:
        """Limiters (1) come before observations (2) before strengths (3)."""
        categories = {
            "rsi": "good",
            "jump_height": "below_average",
            "ground_contact_time": "average",
        }
        insights = generate_dropjump_insights(categories)

        # Should have: dj_height_limiter (1), dj_gct_observation (2), dj_rsi_strength (3)
        assert len(insights) >= 3
        priorities = [i["priority"] for i in insights]
        assert priorities == sorted(priorities)

    def test_multiple_limiters_grouped_together(self) -> None:
        """When multiple limiters exist, they're all at priority 1."""
        categories = {
            "rsi": "below_average",
            "jump_height": "poor",
            "ground_contact_time": "below_average",
        }
        insights = generate_dropjump_insights(categories)

        limiters = [i for i in insights if i["type"] == "limiter"]
        assert len(limiters) >= 2
        assert all(i["priority"] == 1 for i in limiters)


# ===========================================================================
# Empty / partial metric scenarios
# ===========================================================================


class TestEmptyAndPartialMetrics:
    """Tests for edge cases with missing or partial metrics."""

    def test_empty_categories_returns_empty(self) -> None:
        """Empty categories dict returns no insights."""
        assert generate_dropjump_insights({}) == []
        assert generate_cmj_insights({}) == []
        assert generate_sj_insights({}) == []

    def test_single_metric_dj(self) -> None:
        """Only RSI provided for drop jump - no cross-metric rules fire for RSI+height."""
        categories = {"rsi": "excellent"}
        insights = generate_dropjump_insights(categories)

        # Only rsi_strength should fire (standalone)
        assert _has_insight(insights, "dj_rsi_strength")
        assert not _has_insight(insights, "dj_height_limiter")

    def test_single_metric_cmj(self) -> None:
        """Only depth provided for CMJ - only depth rules apply."""
        categories = {"countermovement_depth": "optimal"}
        insights = generate_cmj_insights(categories)

        assert _has_insight(insights, "cmj_depth_optimal")
        assert not _has_insight(insights, "cmj_height_limiter")

    def test_unknown_category_value_no_match(self) -> None:
        """Unknown category values don't match any rule sets."""
        categories = {"rsi": "unknown_cat", "jump_height": "unknown_cat"}
        insights = generate_dropjump_insights(categories)

        # No cross-metric rules should fire
        assert not _has_insight(insights, "dj_height_limiter")
        assert not _has_insight(insights, "dj_rsi_limiter")
        assert not _has_insight(insights, "dj_both_weak")
        assert not _has_insight(insights, "dj_rsi_strength")

    def test_insight_structure_valid(self) -> None:
        """All generated insights have the correct structure."""
        categories = {
            "rsi": "excellent",
            "jump_height": "poor",
            "ground_contact_time": "very_good",
        }
        insights = generate_dropjump_insights(categories)

        assert len(insights) > 0
        for insight in insights:
            _assert_insight_structure(insight)

    def test_both_metrics_average_dj(self) -> None:
        """When RSI and height are both average, no cross-metric limiter/strength fires."""
        categories = {"rsi": "average", "jump_height": "average", "ground_contact_time": "good"}
        insights = generate_dropjump_insights(categories)

        # No RSI+height limiters/strengths, only GCT-based rules
        assert not _has_insight(insights, "dj_height_limiter")
        assert not _has_insight(insights, "dj_rsi_limiter")
        assert not _has_insight(insights, "dj_both_weak")
        assert not _has_insight(insights, "dj_rsi_strength")
        # GCT good doesn't trigger any GCT rules either
        assert not _has_insight(insights, "dj_gct_strength")
        assert not _has_insight(insights, "dj_gct_limiter")
        assert not _has_insight(insights, "dj_gct_observation")

    def test_both_metrics_weak_sj(self) -> None:
        """When both SJ metrics are weak, no rule fires (not in AVERAGE_OR_BETTER)."""
        categories = {"jump_height": "poor", "peak_concentric_velocity": "poor"}
        insights = generate_sj_insights(categories)

        assert not _has_insight(insights, "sj_height_limiter")
        assert not _has_insight(insights, "sj_velocity_limiter")
        assert not _has_insight(insights, "sj_power_strength")
