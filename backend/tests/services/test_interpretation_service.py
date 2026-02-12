"""Tests for the metrics interpretation service.

Validates that raw analysis metrics are correctly classified against normative
ranges and that coaching recommendations are generated for all supported jump
types (CMJ, Drop Jump, SJ).

Normative data sources:
    - docs/guides/coach-quick-start.md
    - src/kinemotion/*/validation_bounds.py
"""

from __future__ import annotations

import pytest

from kinemotion_backend.services.interpretation_service import (
    _build_metric_interpretation,
    _classify_value,
    interpret_cmj_metrics,
    interpret_dropjump_metrics,
    interpret_metrics,
    interpret_sj_metrics,
)

# ---------------------------------------------------------------------------
# Helper: shared assertion for interpretation dict structure
# ---------------------------------------------------------------------------


def _assert_interpretation_structure(
    interp: dict, expected_category: str, expected_unit: str
) -> None:
    """Verify that an interpretation dict has the correct shape and category."""
    assert "category" in interp
    assert "value" in interp
    assert "range" in interp
    assert "recommendation" in interp

    assert interp["category"] == expected_category
    assert isinstance(interp["value"], (int, float))

    range_dict = interp["range"]
    assert "low" in range_dict
    assert "high" in range_dict
    assert "unit" in range_dict
    assert range_dict["unit"] == expected_unit

    assert isinstance(range_dict["low"], (int, float))
    assert isinstance(range_dict["high"], (int, float))
    assert range_dict["low"] <= range_dict["high"]

    assert isinstance(interp["recommendation"], str)


# ===========================================================================
# _classify_value tests
# ===========================================================================


class TestClassifyValue:
    """Tests for the low-level _classify_value helper."""

    SAMPLE_NORMS = [
        ("low", 0.0, 10.0),
        ("mid", 10.0, 20.0),
        ("high", 20.0, 30.0),
    ]

    def test_value_in_first_range(self) -> None:
        """Value in the first normative range returns that category."""
        cat, low, high = _classify_value(5.0, self.SAMPLE_NORMS)
        assert cat == "low"
        assert low == 0.0
        assert high == 10.0

    def test_value_in_middle_range(self) -> None:
        """Value in the middle range returns the correct category."""
        cat, low, high = _classify_value(15.0, self.SAMPLE_NORMS)
        assert cat == "mid"
        assert low == 10.0
        assert high == 20.0

    def test_value_in_last_range(self) -> None:
        """Value in the last range returns the correct category."""
        cat, low, high = _classify_value(25.0, self.SAMPLE_NORMS)
        assert cat == "high"
        assert low == 20.0
        assert high == 30.0

    def test_value_at_range_boundary_low(self) -> None:
        """Value at the exact lower boundary is classified within the range."""
        cat, _, _ = _classify_value(0.0, self.SAMPLE_NORMS)
        assert cat == "low"

    def test_value_at_range_boundary_high(self) -> None:
        """Value at the exact upper boundary is classified within the range."""
        cat, _, _ = _classify_value(10.0, self.SAMPLE_NORMS)
        assert cat == "low"

    def test_value_at_overlap_boundary(self) -> None:
        """When ranges share a boundary, the first matching range wins."""
        # 10.0 is in both "low" (0-10) and "mid" (10-20); first match wins.
        cat, _, _ = _classify_value(10.0, self.SAMPLE_NORMS)
        assert cat == "low"

    def test_value_below_all_ranges(self) -> None:
        """Value below the lowest range falls back to the first category."""
        cat, low, high = _classify_value(-5.0, self.SAMPLE_NORMS)
        assert cat == "low"
        assert low == 0.0
        assert high == 10.0

    def test_value_above_all_ranges(self) -> None:
        """Value above the highest range falls back to the last category."""
        cat, low, high = _classify_value(999.0, self.SAMPLE_NORMS)
        assert cat == "high"
        assert low == 20.0
        assert high == 30.0

    def test_value_in_gap_closest_to_lower_range(self) -> None:
        """Value in a gap between ranges classifies to the closest range."""
        # Ranges with a gap: (0-10), (15-30) — value 12 is closer to 10 than 15
        gapped_norms = [
            ("low", 0.0, 10.0),
            ("high", 15.0, 30.0),
        ]
        cat, low, high = _classify_value(12.0, gapped_norms)
        assert cat == "low"
        assert low == 0.0
        assert high == 10.0

    def test_value_in_gap_closest_to_upper_range(self) -> None:
        """Value in a gap closer to the upper range classifies there."""
        gapped_norms = [
            ("low", 0.0, 10.0),
            ("high", 15.0, 30.0),
        ]
        cat, low, high = _classify_value(13.0, gapped_norms)
        assert cat == "high"
        assert low == 15.0
        assert high == 30.0

    def test_age_adjusted_gap_classifies_correctly(self) -> None:
        """Simulates the real bug: 24.7 in age-adjusted norms with gaps.

        After age factor 0.82, male jump height poor range is (17.2, 24.6)
        and below_average is (25.4, 32.8). Value 24.7 falls in the gap
        and should classify as "poor" (distance 0.1) not "excellent".
        """
        age_adjusted_norms = [
            ("poor", 17.2, 24.6),
            ("below_average", 25.4, 32.8),
            ("average", 33.6, 41.0),
            ("above_average", 41.8, 49.2),
            ("very_good", 50.0, 57.4),
            ("excellent", 57.4, 83.6),
        ]
        cat, _, _ = _classify_value(24.7, age_adjusted_norms)
        assert cat == "poor"


# ===========================================================================
# _build_metric_interpretation tests
# ===========================================================================


class TestBuildMetricInterpretation:
    """Tests for the _build_metric_interpretation helper."""

    def test_returns_correct_structure(self) -> None:
        """Output dict contains all required keys with correct values."""
        tips = {"good": "Keep it up!", "bad": "Try harder."}
        result = _build_metric_interpretation("good", 42.0, 30.0, 50.0, "cm", tips)

        assert result["category"] == "good"
        assert result["value"] == 42.0
        assert result["range"] == {"low": 30.0, "high": 50.0, "unit": "cm"}
        assert result["recommendation"] == "Keep it up!"

    def test_missing_coaching_tip_returns_empty_string(self) -> None:
        """When the category has no coaching tip, recommendation is empty."""
        tips = {"other_category": "Some tip."}
        result = _build_metric_interpretation("unknown_cat", 10.0, 0.0, 20.0, "m/s", tips)

        assert result["recommendation"] == ""

    def test_integer_value_preserved(self) -> None:
        """Integer input values are preserved (not coerced to float)."""
        tips = {}
        result = _build_metric_interpretation("cat", 42, 30, 50, "kg", tips)

        assert result["value"] == 42
        assert result["range"]["low"] == 30
        assert result["range"]["high"] == 50


# ===========================================================================
# CMJ interpretation tests
# ===========================================================================


class TestInterpretCmjMetrics:
    """Tests for interpret_cmj_metrics covering jump height, velocity, and CM depth."""

    # -- Jump height classification --

    @pytest.mark.parametrize(
        "height_m, expected_category",
        [
            (0.25, "poor"),  # 25 cm
            (0.35, "below_average"),  # 35 cm
            (0.45, "average"),  # 45 cm
            (0.55, "above_average"),  # 55 cm
            (0.65, "very_good"),  # 65 cm
            (0.80, "excellent"),  # 80 cm
        ],
    )
    def test_jump_height_classification(self, height_m: float, expected_category: str) -> None:
        """Jump height in meters is converted to cm and classified correctly."""
        data = {"jump_height_m": height_m}
        result = interpret_cmj_metrics(data)

        assert "jump_height" in result
        _assert_interpretation_structure(result["jump_height"], expected_category, "cm")
        assert abs(result["jump_height"]["value"] - height_m * 100) < 0.01

    def test_jump_height_has_recommendation(self) -> None:
        """Jump height interpretation includes a non-empty recommendation."""
        data = {"jump_height_m": 0.45}
        result = interpret_cmj_metrics(data)

        assert len(result["jump_height"]["recommendation"]) > 0

    # -- Peak concentric velocity --

    @pytest.mark.parametrize(
        "velocity, expected_category",
        [
            (1.0, "below_average"),
            (2.0, "average"),
            (2.7, "above_average"),
            (3.3, "very_good"),
            (4.0, "excellent"),
        ],
    )
    def test_velocity_classification(self, velocity: float, expected_category: str) -> None:
        """Peak concentric velocity is classified in m/s."""
        data = {"peak_concentric_velocity_m_s": velocity}
        result = interpret_cmj_metrics(data)

        assert "peak_concentric_velocity" in result
        _assert_interpretation_structure(
            result["peak_concentric_velocity"], expected_category, "m/s"
        )
        assert result["peak_concentric_velocity"]["value"] == velocity

    # -- Countermovement depth --

    @pytest.mark.parametrize(
        "depth_m, expected_category",
        [
            (0.10, "too_shallow"),  # 10 cm
            (0.25, "optimal"),  # 25 cm
            (0.37, "deep"),  # 37 cm
            (0.50, "too_deep"),  # 50 cm
        ],
    )
    def test_countermovement_depth_classification(
        self, depth_m: float, expected_category: str
    ) -> None:
        """Countermovement depth in meters is converted to cm and classified."""
        data = {"countermovement_depth_m": depth_m}
        result = interpret_cmj_metrics(data)

        assert "countermovement_depth" in result
        _assert_interpretation_structure(result["countermovement_depth"], expected_category, "cm")
        assert abs(result["countermovement_depth"]["value"] - depth_m * 100) < 0.01

    # -- Combined metrics --

    def test_all_metrics_present(self) -> None:
        """When all three CMJ metrics are provided, all three are interpreted."""
        data = {
            "jump_height_m": 0.45,
            "peak_concentric_velocity_m_s": 2.5,
            "countermovement_depth_m": 0.30,
        }
        result = interpret_cmj_metrics(data)

        assert "jump_height" in result
        assert "peak_concentric_velocity" in result
        assert "countermovement_depth" in result

    def test_partial_metrics(self) -> None:
        """Only provided metrics are interpreted; missing ones are omitted."""
        data = {"jump_height_m": 0.45}
        result = interpret_cmj_metrics(data)

        assert "jump_height" in result
        assert "peak_concentric_velocity" not in result
        assert "countermovement_depth" not in result


# ===========================================================================
# Drop Jump interpretation tests
# ===========================================================================


class TestInterpretDropjumpMetrics:
    """Tests for interpret_dropjump_metrics covering RSI, height, and GCT."""

    # -- RSI classification --

    @pytest.mark.parametrize(
        "rsi_value, expected_category",
        [
            (0.5, "poor"),
            (0.9, "below_average"),
            (1.2, "average"),
            (1.7, "good"),
            (2.3, "very_good"),
            (3.0, "excellent"),
        ],
    )
    def test_rsi_classification(self, rsi_value: float, expected_category: str) -> None:
        """Reactive strength index is classified correctly."""
        data = {"reactive_strength_index": rsi_value}
        result = interpret_dropjump_metrics(data)

        assert "rsi" in result
        _assert_interpretation_structure(result["rsi"], expected_category, "ratio")
        assert result["rsi"]["value"] == rsi_value

    def test_rsi_has_recommendation(self) -> None:
        """RSI interpretation includes a non-empty coaching recommendation."""
        data = {"reactive_strength_index": 1.2}
        result = interpret_dropjump_metrics(data)

        assert len(result["rsi"]["recommendation"]) > 0

    # -- Jump height in drop jump context --

    def test_dropjump_jump_height(self) -> None:
        """Drop jump jump height uses the same male norms as CMJ."""
        data = {"jump_height_m": 0.55}
        result = interpret_dropjump_metrics(data)

        assert "jump_height" in result
        _assert_interpretation_structure(result["jump_height"], "above_average", "cm")

    # -- Ground contact time --

    @pytest.mark.parametrize(
        "gct_ms, expected_category",
        [
            (160.0, "excellent"),
            (190.0, "very_good"),
            (210.0, "good"),
            (235.0, "average"),
            (300.0, "below_average"),
        ],
    )
    def test_gct_classification(self, gct_ms: float, expected_category: str) -> None:
        """Ground contact time in ms is classified correctly."""
        data = {"ground_contact_time_ms": gct_ms}
        result = interpret_dropjump_metrics(data)

        assert "ground_contact_time" in result
        _assert_interpretation_structure(result["ground_contact_time"], expected_category, "ms")
        assert result["ground_contact_time"]["value"] == gct_ms

    def test_gct_has_recommendation(self) -> None:
        """GCT interpretation includes a non-empty coaching recommendation."""
        data = {"ground_contact_time_ms": 235.0}
        result = interpret_dropjump_metrics(data)

        assert len(result["ground_contact_time"]["recommendation"]) > 0

    # -- GCT age adjustment (inverse metric) --

    def test_gct_masters_50_ranges_more_lenient(self) -> None:
        """Masters 50 GCT ranges should be MORE lenient (higher ms) than adult.

        GCT is an inverse metric: lower = better. For older athletes, the
        thresholds should shift upward (divide by age factor), making it
        easier to achieve a given category.
        """
        # Adult: below_average is 250-350 ms
        adult = interpret_dropjump_metrics({"ground_contact_time_ms": 300.0}, age_group=None)
        assert adult["ground_contact_time"]["category"] == "below_average"

        # Masters 50: 300 ms should rate BETTER than below_average
        # because thresholds shift up (÷0.82 → below_average becomes ~305-427)
        masters = interpret_dropjump_metrics(
            {"ground_contact_time_ms": 300.0}, age_group="masters_50"
        )
        cat_order = ["excellent", "very_good", "good", "average", "below_average"]
        adult_idx = cat_order.index(adult["ground_contact_time"]["category"])
        masters_idx = cat_order.index(masters["ground_contact_time"]["category"])
        assert masters_idx <= adult_idx  # lower index = better category

    def test_gct_276_masters_50_not_below_average(self) -> None:
        """276 ms GCT for Masters 50 should NOT be below_average.

        This was the reported bug: with inverse adjustment, 276 ms should
        classify better since the thresholds are more lenient.
        """
        result = interpret_dropjump_metrics(
            {"ground_contact_time_ms": 276.1}, age_group="masters_50"
        )
        assert result["ground_contact_time"]["category"] != "below_average"

    # -- Combined --

    def test_all_dropjump_metrics_present(self) -> None:
        """When all three drop jump metrics are provided, all three are interpreted."""
        data = {
            "reactive_strength_index": 1.5,
            "jump_height_m": 0.45,
            "ground_contact_time_ms": 200.0,
        }
        result = interpret_dropjump_metrics(data)

        assert "rsi" in result
        assert "jump_height" in result
        assert "ground_contact_time" in result


# ===========================================================================
# Squat Jump interpretation tests
# ===========================================================================


class TestInterpretSjMetrics:
    """Tests for interpret_sj_metrics covering jump height and velocity."""

    @pytest.mark.parametrize(
        "height_m, expected_category",
        [
            (0.25, "poor"),
            (0.45, "average"),
            (0.65, "very_good"),
        ],
    )
    def test_sj_jump_height_classification(self, height_m: float, expected_category: str) -> None:
        """SJ jump height uses the same male norms and cm conversion."""
        data = {"jump_height_m": height_m}
        result = interpret_sj_metrics(data)

        assert "jump_height" in result
        _assert_interpretation_structure(result["jump_height"], expected_category, "cm")

    @pytest.mark.parametrize(
        "velocity, expected_category",
        [
            (1.0, "below_average"),
            (2.0, "average"),
            (3.3, "very_good"),
        ],
    )
    def test_sj_velocity_classification(self, velocity: float, expected_category: str) -> None:
        """SJ velocity uses the same peak velocity norms."""
        data = {"peak_concentric_velocity_m_s": velocity}
        result = interpret_sj_metrics(data)

        assert "peak_concentric_velocity" in result
        _assert_interpretation_structure(
            result["peak_concentric_velocity"], expected_category, "m/s"
        )

    def test_both_sj_metrics_present(self) -> None:
        """Both SJ metrics are returned when provided."""
        data = {
            "jump_height_m": 0.40,
            "peak_concentric_velocity_m_s": 2.5,
        }
        result = interpret_sj_metrics(data)

        assert "jump_height" in result
        assert "peak_concentric_velocity" in result


# ===========================================================================
# Main router: interpret_metrics
# ===========================================================================


class TestInterpretMetrics:
    """Tests for the top-level interpret_metrics router function."""

    # -- Valid jump types --

    def test_routes_to_cmj(self) -> None:
        """The 'cmj' jump type routes to interpret_cmj_metrics."""
        data = {"jump_height_m": 0.45}
        result = interpret_metrics("cmj", data)

        assert "interpretations" in result
        assert "jump_height" in result["interpretations"]

    def test_routes_to_drop_jump(self) -> None:
        """The 'drop_jump' jump type routes to interpret_dropjump_metrics."""
        data = {"reactive_strength_index": 1.5}
        result = interpret_metrics("drop_jump", data)

        assert "interpretations" in result
        assert "rsi" in result["interpretations"]

    def test_routes_to_sj(self) -> None:
        """The 'sj' jump type routes to interpret_sj_metrics."""
        data = {"jump_height_m": 0.40}
        result = interpret_metrics("sj", data)

        assert "interpretations" in result
        assert "jump_height" in result["interpretations"]

    def test_squat_jump_alias_not_handled_at_dispatch(self) -> None:
        """The 'squat_jump' alias is normalized to 'sj' at validation, not here.

        After validate_jump_type() normalizes 'squat_jump' -> 'sj', only
        canonical forms reach interpret_metrics. Passing 'squat_jump' directly
        returns empty because dispatch only handles canonical forms.
        """
        data = {"jump_height_m": 0.40}
        result = interpret_metrics("squat_jump", data)

        assert result == {}

    # -- Invalid / unknown jump types --

    def test_unknown_jump_type_returns_empty(self) -> None:
        """An unrecognized jump type returns an empty dict."""
        data = {"jump_height_m": 0.45}
        result = interpret_metrics("unknown_type", data)

        assert result == {}

    def test_empty_string_jump_type_returns_empty(self) -> None:
        """An empty string jump type returns an empty dict."""
        data = {"jump_height_m": 0.45}
        result = interpret_metrics("", data)

        assert result == {}

    # -- Empty / None metrics data --

    def test_empty_dict_returns_empty(self) -> None:
        """Empty metrics dict returns empty result."""
        result = interpret_metrics("cmj", {})

        assert result == {}

    def test_none_metrics_returns_empty(self) -> None:
        """None metrics data returns empty result (falsy check)."""
        result = interpret_metrics("cmj", None)  # type: ignore[arg-type]

        assert result == {}

    # -- Wrapper structure --

    def test_result_wrapped_in_interpretations_key(self) -> None:
        """Valid result is wrapped in an 'interpretations' top-level key."""
        data = {"jump_height_m": 0.45}
        result = interpret_metrics("cmj", data)

        assert set(result.keys()) == {"interpretations"}
        assert isinstance(result["interpretations"], dict)

    def test_no_interpretable_metrics_returns_empty(self) -> None:
        """When metrics_data has keys but none are interpretable, returns empty."""
        data = {"some_unrelated_key": 42.0}
        result = interpret_metrics("cmj", data)

        assert result == {}


# ===========================================================================
# Edge cases and boundary conditions
# ===========================================================================


class TestEdgeCases:
    """Edge cases: missing metrics, non-numeric values, boundary values, extremes."""

    # -- Non-numeric metric values --

    def test_string_value_ignored(self) -> None:
        """A string metric value is silently skipped (isinstance check)."""
        data = {"jump_height_m": "not_a_number"}
        result = interpret_cmj_metrics(data)

        assert "jump_height" not in result

    def test_none_value_ignored(self) -> None:
        """A None metric value is silently skipped."""
        data = {"jump_height_m": None}
        result = interpret_cmj_metrics(data)

        assert "jump_height" not in result

    def test_boolean_value_accepted(self) -> None:
        """Booleans are instances of int in Python, so they pass the isinstance check.

        This is a known edge case. True == 1, False == 0. The function will
        classify them as numeric, which is technically correct for isinstance
        but semantically odd. This test documents the behavior.
        """
        data = {"jump_height_m": True}
        result = interpret_cmj_metrics(data)

        # True == 1 => 100 cm => excellent range (70-102)
        assert "jump_height" in result

    def test_list_value_ignored(self) -> None:
        """A list metric value is silently skipped."""
        data = {"jump_height_m": [0.45]}
        result = interpret_cmj_metrics(data)

        assert "jump_height" not in result

    # -- Extreme values --

    def test_very_large_jump_height(self) -> None:
        """Extremely large jump height falls back to the last (excellent) range."""
        data = {"jump_height_m": 5.0}  # 500 cm - superhuman
        result = interpret_cmj_metrics(data)

        assert result["jump_height"]["category"] == "excellent"
        assert result["jump_height"]["range"]["low"] == 70.0
        assert result["jump_height"]["range"]["high"] == 102.0

    def test_very_small_jump_height(self) -> None:
        """Extremely small jump height falls back to the first (poor) range."""
        data = {"jump_height_m": 0.01}  # 1 cm
        result = interpret_cmj_metrics(data)

        assert result["jump_height"]["category"] == "poor"
        assert result["jump_height"]["range"]["low"] == 21.0
        assert result["jump_height"]["range"]["high"] == 30.0

    def test_negative_jump_height(self) -> None:
        """Negative jump height falls back to the first (poor) range."""
        data = {"jump_height_m": -0.10}
        result = interpret_cmj_metrics(data)

        assert result["jump_height"]["category"] == "poor"

    def test_zero_jump_height(self) -> None:
        """Zero jump height falls back to the first (poor) range."""
        data = {"jump_height_m": 0.0}
        result = interpret_cmj_metrics(data)

        assert result["jump_height"]["category"] == "poor"

    def test_zero_velocity(self) -> None:
        """Zero velocity falls back to the first (below_average) range."""
        data = {"peak_concentric_velocity_m_s": 0.0}
        result = interpret_cmj_metrics(data)

        assert result["peak_concentric_velocity"]["category"] == "below_average"

    def test_very_large_rsi(self) -> None:
        """RSI well above norms falls back to the last (excellent) range."""
        data = {"reactive_strength_index": 10.0}
        result = interpret_dropjump_metrics(data)

        assert result["rsi"]["category"] == "excellent"

    def test_very_small_rsi(self) -> None:
        """RSI below all norms falls back to the first (poor) range."""
        data = {"reactive_strength_index": 0.1}
        result = interpret_dropjump_metrics(data)

        assert result["rsi"]["category"] == "poor"

    def test_very_small_gct(self) -> None:
        """GCT well below norms falls back to the first category (excellent)."""
        data = {"ground_contact_time_ms": 50.0}
        result = interpret_dropjump_metrics(data)

        # GCT norms are ordered excellent first, so below-all returns excellent
        assert result["ground_contact_time"]["category"] == "excellent"

    def test_very_large_gct(self) -> None:
        """GCT well above norms falls back to the last category (below_average)."""
        data = {"ground_contact_time_ms": 500.0}
        result = interpret_dropjump_metrics(data)

        assert result["ground_contact_time"]["category"] == "below_average"

    def test_negative_countermovement_depth(self) -> None:
        """Negative CM depth falls back to the first category (too_shallow)."""
        data = {"countermovement_depth_m": -0.05}
        result = interpret_cmj_metrics(data)

        assert result["countermovement_depth"]["category"] == "too_shallow"

    # -- Integer metric values --

    def test_integer_height_value(self) -> None:
        """Integer metric values are accepted (isinstance check includes int)."""
        data = {"jump_height_m": 1}  # 100 cm
        result = interpret_cmj_metrics(data)

        assert "jump_height" in result
        assert result["jump_height"]["value"] == 100

    def test_integer_rsi_value(self) -> None:
        """Integer RSI is classified correctly.

        RSI=2 is at the boundary of good (1.5-2.0) and very_good (2.0-2.5).
        First matching range wins, so 2.0 falls into 'good'.
        """
        data = {"reactive_strength_index": 2}
        result = interpret_dropjump_metrics(data)

        assert result["rsi"]["category"] == "good"

    # -- Empty interpreter results --

    def test_cmj_empty_data_returns_empty(self) -> None:
        """Empty dict to CMJ interpreter returns empty dict."""
        assert interpret_cmj_metrics({}) == {}

    def test_dropjump_empty_data_returns_empty(self) -> None:
        """Empty dict to drop jump interpreter returns empty dict."""
        assert interpret_dropjump_metrics({}) == {}

    def test_sj_empty_data_returns_empty(self) -> None:
        """Empty dict to SJ interpreter returns empty dict."""
        assert interpret_sj_metrics({}) == {}

    # -- Unrelated keys --

    def test_extra_keys_ignored(self) -> None:
        """Unrecognized metric keys are silently ignored."""
        data = {
            "jump_height_m": 0.45,
            "some_random_metric": 999.0,
            "another_thing": "hello",
        }
        result = interpret_cmj_metrics(data)

        assert set(result.keys()) == {"jump_height"}


# ===========================================================================
# Boundary value tests at exact normative edges
# ===========================================================================


class TestBoundaryValues:
    """Tests at exact normative range boundaries."""

    # -- Jump height boundaries (cm, male norms) --

    def test_jump_height_at_poor_low(self) -> None:
        """21 cm is exactly at the low end of 'poor'."""
        data = {"jump_height_m": 0.21}
        result = interpret_cmj_metrics(data)
        assert result["jump_height"]["category"] == "poor"

    def test_jump_height_at_poor_high(self) -> None:
        """30 cm is exactly at the high end of 'poor'."""
        data = {"jump_height_m": 0.30}
        result = interpret_cmj_metrics(data)
        assert result["jump_height"]["category"] == "poor"

    def test_jump_height_at_below_average_low(self) -> None:
        """31 cm is at the low end of 'below_average'."""
        data = {"jump_height_m": 0.31}
        result = interpret_cmj_metrics(data)
        assert result["jump_height"]["category"] == "below_average"

    def test_jump_height_at_excellent_high(self) -> None:
        """102 cm is at the high end of 'excellent'."""
        data = {"jump_height_m": 1.02}
        result = interpret_cmj_metrics(data)
        assert result["jump_height"]["category"] == "excellent"

    # -- RSI boundaries --

    def test_rsi_at_poor_low(self) -> None:
        """RSI 0.3 is at the low end of 'poor'."""
        data = {"reactive_strength_index": 0.3}
        result = interpret_dropjump_metrics(data)
        assert result["rsi"]["category"] == "poor"

    def test_rsi_at_excellent_high(self) -> None:
        """RSI 4.0 is at the high end of 'excellent'."""
        data = {"reactive_strength_index": 4.0}
        result = interpret_dropjump_metrics(data)
        assert result["rsi"]["category"] == "excellent"

    # -- GCT boundaries --

    def test_gct_at_excellent_low(self) -> None:
        """GCT 140 ms is at the low end of 'excellent'."""
        data = {"ground_contact_time_ms": 140.0}
        result = interpret_dropjump_metrics(data)
        assert result["ground_contact_time"]["category"] == "excellent"

    def test_gct_at_below_average_high(self) -> None:
        """GCT 350 ms is at the high end of 'below_average'."""
        data = {"ground_contact_time_ms": 350.0}
        result = interpret_dropjump_metrics(data)
        assert result["ground_contact_time"]["category"] == "below_average"

    # -- CM depth boundaries --

    def test_cm_depth_at_too_shallow_low(self) -> None:
        """5 cm is at the low end of 'too_shallow'."""
        data = {"countermovement_depth_m": 0.05}
        result = interpret_cmj_metrics(data)
        assert result["countermovement_depth"]["category"] == "too_shallow"

    def test_cm_depth_at_optimal_low(self) -> None:
        """20 cm is at the boundary of 'too_shallow' and 'optimal'.

        Because 20.0 matches both too_shallow (5-20) and optimal (20-35),
        the first match in the norms list wins, which is too_shallow.
        """
        data = {"countermovement_depth_m": 0.20}
        result = interpret_cmj_metrics(data)
        assert result["countermovement_depth"]["category"] == "too_shallow"

    def test_cm_depth_at_too_deep_high(self) -> None:
        """75 cm is at the high end of 'too_deep'."""
        data = {"countermovement_depth_m": 0.75}
        result = interpret_cmj_metrics(data)
        assert result["countermovement_depth"]["category"] == "too_deep"

    # -- Velocity boundaries --

    def test_velocity_at_below_average_low(self) -> None:
        """0.5 m/s is at the low end of 'below_average'."""
        data = {"peak_concentric_velocity_m_s": 0.5}
        result = interpret_cmj_metrics(data)
        assert result["peak_concentric_velocity"]["category"] == "below_average"

    def test_velocity_at_excellent_high(self) -> None:
        """5.0 m/s is at the high end of 'excellent'."""
        data = {"peak_concentric_velocity_m_s": 5.0}
        result = interpret_cmj_metrics(data)
        assert result["peak_concentric_velocity"]["category"] == "excellent"


# ===========================================================================
# Coaching recommendations content tests
# ===========================================================================


class TestCoachingRecommendations:
    """Verify that recommendations contain meaningful coaching content."""

    def test_poor_jump_height_mentions_strength(self) -> None:
        """Poor jump height recommendation references strength training."""
        data = {"jump_height_m": 0.25}
        result = interpret_cmj_metrics(data)

        rec = result["jump_height"]["recommendation"].lower()
        assert "strength" in rec

    def test_excellent_jump_height_mentions_elite(self) -> None:
        """Excellent jump height recommendation references elite level."""
        data = {"jump_height_m": 0.80}
        result = interpret_cmj_metrics(data)

        rec = result["jump_height"]["recommendation"].lower()
        assert "elite" in rec

    def test_poor_rsi_mentions_landing(self) -> None:
        """Poor RSI recommendation references landing mechanics."""
        data = {"reactive_strength_index": 0.5}
        result = interpret_dropjump_metrics(data)

        rec = result["rsi"]["recommendation"].lower()
        assert "landing" in rec

    def test_too_deep_cm_mentions_depth(self) -> None:
        """Too-deep CM recommendation references excessive depth."""
        data = {"countermovement_depth_m": 0.50}
        result = interpret_cmj_metrics(data)

        rec = result["countermovement_depth"]["recommendation"].lower()
        assert "deep" in rec

    def test_below_average_velocity_mentions_force(self) -> None:
        """Below-average velocity recommendation references force development."""
        data = {"peak_concentric_velocity_m_s": 1.0}
        result = interpret_cmj_metrics(data)

        rec = result["peak_concentric_velocity"]["recommendation"].lower()
        assert "force" in rec

    def test_excellent_gct_mentions_fast(self) -> None:
        """Excellent GCT recommendation references fast ground contact."""
        data = {"ground_contact_time_ms": 160.0}
        result = interpret_dropjump_metrics(data)

        rec = result["ground_contact_time"]["recommendation"].lower()
        assert "fast" in rec


# ===========================================================================
# Sex-specific norm tests
# ===========================================================================


class TestSexSpecificInterpretation:
    """Tests that sex parameter changes normative ranges."""

    def test_female_jump_height_different_category_than_male(self) -> None:
        """A 35cm jump is 'below_average' for male but 'average' for female."""
        data = {"jump_height_m": 0.35}  # 35 cm

        male_result = interpret_cmj_metrics(data, sex=None)  # defaults to male
        female_result = interpret_cmj_metrics(data, sex="female")

        assert male_result["jump_height"]["category"] == "below_average"
        assert female_result["jump_height"]["category"] == "average"

    def test_female_rsi_different_category_than_male(self) -> None:
        """RSI 0.7 is 'poor' for male but 'below_average' for female."""
        data = {"reactive_strength_index": 0.7}

        male_result = interpret_dropjump_metrics(data, sex=None)
        female_result = interpret_dropjump_metrics(data, sex="female")

        assert male_result["rsi"]["category"] == "poor"
        assert female_result["rsi"]["category"] == "below_average"

    def test_female_velocity_different_ranges(self) -> None:
        """Female velocity norms have lower boundaries than male."""
        data = {"peak_concentric_velocity_m_s": 1.6}

        male_result = interpret_cmj_metrics(data, sex="male")
        female_result = interpret_cmj_metrics(data, sex="female")

        assert male_result["peak_concentric_velocity"]["category"] == "below_average"
        assert female_result["peak_concentric_velocity"]["category"] == "average"

    def test_cm_depth_universal_same_for_both_sexes(self) -> None:
        """Countermovement depth norms are universal (minimal sex difference)."""
        data = {"countermovement_depth_m": 0.25}

        male_result = interpret_cmj_metrics(data, sex="male")
        female_result = interpret_cmj_metrics(data, sex="female")

        assert (
            male_result["countermovement_depth"]["category"]
            == female_result["countermovement_depth"]["category"]
        )

    def test_gct_universal_same_for_both_sexes(self) -> None:
        """Ground contact time norms are universal."""
        data = {"ground_contact_time_ms": 190.0}

        male_result = interpret_dropjump_metrics(data, sex="male")
        female_result = interpret_dropjump_metrics(data, sex="female")

        assert (
            male_result["ground_contact_time"]["category"]
            == female_result["ground_contact_time"]["category"]
        )


# ===========================================================================
# Age-adjusted norm tests
# ===========================================================================


class TestAgeAdjustedInterpretation:
    """Tests that age_group parameter adjusts normative ranges."""

    def test_youth_jump_height_higher_category(self) -> None:
        """A moderate jump is classified higher for youth (lower norms)."""
        data = {"jump_height_m": 0.35}  # 35 cm

        adult_result = interpret_cmj_metrics(data)
        youth_result = interpret_cmj_metrics(data, age_group="youth")

        # Youth norms are scaled down by 0.85, so 35cm rates better
        adult_cat_idx = [
            "poor",
            "below_average",
            "average",
            "above_average",
            "very_good",
            "excellent",
        ].index(adult_result["jump_height"]["category"])
        youth_cat_idx = [
            "poor",
            "below_average",
            "average",
            "above_average",
            "very_good",
            "excellent",
        ].index(youth_result["jump_height"]["category"])
        assert youth_cat_idx >= adult_cat_idx

    def test_senior_rsi_higher_category(self) -> None:
        """A moderate RSI rates better for seniors (lower norms)."""
        data = {"reactive_strength_index": 0.9}

        adult_result = interpret_dropjump_metrics(data)
        senior_result = interpret_dropjump_metrics(data, age_group="senior")

        # Senior norms are scaled down by 0.70
        adult_cat = adult_result["rsi"]["category"]
        senior_cat = senior_result["rsi"]["category"]
        # 0.9 is below_average for adults, should be at least average for seniors
        assert adult_cat == "below_average"
        assert senior_cat != "poor"

    def test_adult_age_group_matches_default(self) -> None:
        """Explicit 'adult' age group gives same results as None."""
        data = {"jump_height_m": 0.45}

        default_result = interpret_cmj_metrics(data)
        adult_result = interpret_cmj_metrics(data, age_group="adult")

        assert default_result == adult_result

    def test_masters_50_jump_height_24_7_not_excellent(self) -> None:
        """24.7 cm jump for Masters 50 male must NOT be 'excellent'.

        This was the reported bug: 24.7 cm fell in a gap between
        age-adjusted ranges and the old fallback returned 'excellent'.
        Should classify as 'poor' (closest range).
        """
        data = {"jump_height_m": 0.247}  # 24.7 cm
        result = interpret_cmj_metrics(data, age_group="masters_50")

        assert result["jump_height"]["category"] == "poor"


# ===========================================================================
# interpret_metrics demographic context tests
# ===========================================================================


class TestInterpretMetricsDemographicContext:
    """Tests for the demographic_context in interpret_metrics output."""

    def test_no_demographics_no_context(self) -> None:
        """When no demographics are provided, no demographic_context key exists."""
        data = {"jump_height_m": 0.45}
        result = interpret_metrics("cmj", data)

        assert "demographic_context" not in result
        assert "interpretations" in result

    def test_sex_only_includes_context(self) -> None:
        """When sex is provided, demographic_context includes sex."""
        data = {"jump_height_m": 0.45}
        result = interpret_metrics("cmj", data, sex="female")

        assert "demographic_context" in result
        assert result["demographic_context"]["sex"] == "female"

    def test_age_only_includes_context(self) -> None:
        """When age is provided, demographic_context includes age_group."""
        data = {"jump_height_m": 0.45}
        result = interpret_metrics("cmj", data, age=25)

        assert "demographic_context" in result
        assert result["demographic_context"]["age_group"] == "adult"

    def test_both_sex_and_age_includes_full_context(self) -> None:
        """When both sex and age are provided, context includes both."""
        data = {"jump_height_m": 0.45}
        result = interpret_metrics("cmj", data, sex="female", age=16)

        assert "demographic_context" in result
        ctx = result["demographic_context"]
        assert ctx["sex"] == "female"
        assert ctx["age_group"] == "youth"

    @pytest.mark.parametrize(
        "age, expected_group",
        [
            (10, "youth"),
            (17, "youth"),
            (18, "adult"),
            (34, "adult"),
            (35, "masters_35"),
            (49, "masters_35"),
            (50, "masters_50"),
            (64, "masters_50"),
            (65, "senior"),
            (80, "senior"),
        ],
    )
    def test_age_to_group_mapping(self, age: int, expected_group: str) -> None:
        """Age values map to correct age groups in interpret_metrics."""
        data = {"jump_height_m": 0.45}
        result = interpret_metrics("cmj", data, age=age)

        assert result["demographic_context"]["age_group"] == expected_group


# ===========================================================================
# Backward compatibility tests
# ===========================================================================


class TestBackwardCompatibility:
    """Ensure that None demographics produce identical output to original behavior."""

    def test_cmj_none_demographics_same_as_original(self) -> None:
        """CMJ with None sex/age_group matches the original male adult norms."""
        data = {
            "jump_height_m": 0.45,
            "peak_concentric_velocity_m_s": 2.5,
            "countermovement_depth_m": 0.30,
        }
        result_default = interpret_cmj_metrics(data)
        result_explicit = interpret_cmj_metrics(data, sex=None, age_group=None)

        assert result_default == result_explicit

    def test_dropjump_none_demographics_same_as_original(self) -> None:
        """Drop jump with None sex/age_group matches the original male adult norms."""
        data = {
            "reactive_strength_index": 1.5,
            "jump_height_m": 0.45,
            "ground_contact_time_ms": 200.0,
        }
        result_default = interpret_dropjump_metrics(data)
        result_explicit = interpret_dropjump_metrics(data, sex=None, age_group=None)

        assert result_default == result_explicit

    def test_sj_none_demographics_same_as_original(self) -> None:
        """SJ with None sex/age_group matches the original male adult norms."""
        data = {
            "jump_height_m": 0.40,
            "peak_concentric_velocity_m_s": 2.5,
        }
        result_default = interpret_sj_metrics(data)
        result_explicit = interpret_sj_metrics(data, sex=None, age_group=None)

        assert result_default == result_explicit

    def test_interpret_metrics_wrapper_backward_compat(self) -> None:
        """interpret_metrics with no demographics returns interpretations and possibly insights."""
        data = {"jump_height_m": 0.45}
        result = interpret_metrics("cmj", data)

        assert "interpretations" in result
        assert "jump_height" in result["interpretations"]


# ===========================================================================
# Coaching insights integration tests
# ===========================================================================


class TestCoachingInsightsIntegration:
    """Integration tests: verify coaching_insights appear in interpret_metrics output."""

    def test_dropjump_cross_metric_insights_present(self) -> None:
        """Drop jump with strong RSI + weak height produces coaching insights."""
        data = {
            "reactive_strength_index": 2.5,  # very_good
            "jump_height_m": 0.25,  # poor (25 cm)
            "ground_contact_time_ms": 160.0,  # excellent
        }
        result = interpret_metrics("drop_jump", data)

        assert "coaching_insights" in result
        insights = result["coaching_insights"]
        assert isinstance(insights, list)
        assert len(insights) > 0

        # Should identify height as limiter
        keys = [i["key"] for i in insights]
        assert "dj_height_limiter" in keys
        assert "dj_rsi_strength" in keys

    def test_cmj_cross_metric_insights_present(self) -> None:
        """CMJ with optimal depth and strong metrics produces coaching insights."""
        data = {
            "jump_height_m": 0.70,  # excellent (70 cm)
            "peak_concentric_velocity_m_s": 3.5,  # very_good/excellent
            "countermovement_depth_m": 0.25,  # optimal (25 cm)
        }
        result = interpret_metrics("cmj", data)

        assert "coaching_insights" in result
        insights = result["coaching_insights"]
        keys = [i["key"] for i in insights]
        assert "cmj_depth_optimal" in keys
        assert "cmj_power_strength" in keys

    def test_sj_cross_metric_insights_present(self) -> None:
        """SJ with weak height and average velocity produces insights."""
        data = {
            "jump_height_m": 0.25,  # poor (25 cm)
            "peak_concentric_velocity_m_s": 2.0,  # average
        }
        result = interpret_metrics("sj", data)

        assert "coaching_insights" in result
        insights = result["coaching_insights"]
        keys = [i["key"] for i in insights]
        assert "sj_height_limiter" in keys

    def test_no_insights_when_metrics_are_all_average(self) -> None:
        """When all metrics are average, no cross-metric insights may fire."""
        data = {
            "jump_height_m": 0.45,  # average (45 cm)
            "peak_concentric_velocity_m_s": 2.0,  # average
        }
        result = interpret_metrics("sj", data)

        # Both metrics average: no cross-metric rules fire
        assert "coaching_insights" not in result

    def test_insights_sorted_by_priority(self) -> None:
        """Insights in the result are sorted by priority."""
        data = {
            "reactive_strength_index": 2.3,  # very_good
            "jump_height_m": 0.25,  # poor
            "ground_contact_time_ms": 235.0,  # average
        }
        result = interpret_metrics("drop_jump", data)

        assert "coaching_insights" in result
        insights = result["coaching_insights"]
        priorities = [i["priority"] for i in insights]
        assert priorities == sorted(priorities)

    def test_insights_coexist_with_demographic_context(self) -> None:
        """coaching_insights and demographic_context both appear when applicable."""
        data = {
            "reactive_strength_index": 2.5,
            "jump_height_m": 0.25,
            "ground_contact_time_ms": 160.0,
        }
        result = interpret_metrics("drop_jump", data, sex="male", age=50)

        assert "interpretations" in result
        assert "coaching_insights" in result
        assert "demographic_context" in result


# ===========================================================================
# Training level interpretation tests
# ===========================================================================


class TestTrainingLevelInterpretation:
    """Tests that training_level parameter adjusts normative ranges."""

    def test_recreational_gets_higher_category_for_same_height(self) -> None:
        """A moderate jump rates better for recreational (lower norms).

        35cm is below_average for male adult trained; with recreational
        training level, norms are lowered so the category should be higher.
        """
        data = {"jump_height_m": 0.35}  # 35 cm

        default_result = interpret_cmj_metrics(data)
        rec_result = interpret_cmj_metrics(data, training_level="recreational")

        cat_order = [
            "poor",
            "below_average",
            "average",
            "above_average",
            "very_good",
            "excellent",
        ]
        default_idx = cat_order.index(default_result["jump_height"]["category"])
        rec_idx = cat_order.index(rec_result["jump_height"]["category"])
        assert rec_idx >= default_idx

    def test_elite_gets_lower_category_for_same_height(self) -> None:
        """A good jump rates worse for elite (higher norms).

        55cm is above_average for male adult trained; with elite
        training level, norms are raised so the category should be lower.
        """
        data = {"jump_height_m": 0.55}  # 55 cm

        default_result = interpret_cmj_metrics(data)
        elite_result = interpret_cmj_metrics(data, training_level="elite")

        cat_order = [
            "poor",
            "below_average",
            "average",
            "above_average",
            "very_good",
            "excellent",
        ]
        default_idx = cat_order.index(default_result["jump_height"]["category"])
        elite_idx = cat_order.index(elite_result["jump_height"]["category"])
        assert elite_idx <= default_idx

    def test_trained_matches_default(self) -> None:
        """Trained level produces identical results to default (factor 1.0)."""
        data = {"jump_height_m": 0.45}

        default_result = interpret_cmj_metrics(data)
        trained_result = interpret_cmj_metrics(data, training_level="trained")

        assert default_result == trained_result

    def test_none_training_level_backward_compatible(self) -> None:
        """None training_level produces identical results to no arg."""
        data = {
            "jump_height_m": 0.45,
            "peak_concentric_velocity_m_s": 2.5,
            "countermovement_depth_m": 0.30,
        }
        result_default = interpret_cmj_metrics(data)
        result_explicit = interpret_cmj_metrics(data, training_level=None)

        assert result_default == result_explicit

    def test_training_level_in_demographic_context(self) -> None:
        """training_level appears in demographic_context when provided."""
        data = {"jump_height_m": 0.45}
        result = interpret_metrics("cmj", data, training_level="recreational")

        assert "demographic_context" in result
        assert result["demographic_context"]["training_level"] == "recreational"

    def test_training_level_absent_from_context_when_not_provided(self) -> None:
        """training_level absent from demographic_context when not provided."""
        data = {"jump_height_m": 0.45}
        result = interpret_metrics("cmj", data, sex="male")

        assert "demographic_context" in result
        assert "training_level" not in result["demographic_context"]

    def test_dropjump_recreational_rsi_higher_category(self) -> None:
        """Recreational athlete gets better RSI category for same value."""
        data = {"reactive_strength_index": 0.9}

        default_result = interpret_dropjump_metrics(data)
        rec_result = interpret_dropjump_metrics(data, training_level="recreational")

        cat_order = [
            "poor",
            "below_average",
            "average",
            "good",
            "very_good",
            "excellent",
        ]
        default_idx = cat_order.index(default_result["rsi"]["category"])
        rec_idx = cat_order.index(rec_result["rsi"]["category"])
        assert rec_idx >= default_idx

    def test_sj_elite_lower_category_for_velocity(self) -> None:
        """Elite athlete gets worse velocity category for same value."""
        data = {"peak_concentric_velocity_m_s": 2.5}

        default_result = interpret_sj_metrics(data)
        elite_result = interpret_sj_metrics(data, training_level="elite")

        cat_order = [
            "below_average",
            "average",
            "above_average",
            "very_good",
            "excellent",
        ]
        default_idx = cat_order.index(default_result["peak_concentric_velocity"]["category"])
        elite_idx = cat_order.index(elite_result["peak_concentric_velocity"]["category"])
        assert elite_idx <= default_idx

    def test_countermovement_depth_unaffected_by_training_level(self) -> None:
        """CM depth has no training factor — category unchanged by training level."""
        data = {"countermovement_depth_m": 0.25}

        default_result = interpret_cmj_metrics(data)
        elite_result = interpret_cmj_metrics(data, training_level="elite")

        assert (
            default_result["countermovement_depth"]["category"]
            == elite_result["countermovement_depth"]["category"]
        )

    def test_all_demographics_combined(self) -> None:
        """Sex + age + training_level all appear in demographic_context."""
        data = {"jump_height_m": 0.45}
        result = interpret_metrics(
            "cmj",
            data,
            sex="female",
            age=40,
            training_level="competitive",
        )

        ctx = result["demographic_context"]
        assert ctx["sex"] == "female"
        assert ctx["age_group"] == "masters_35"
        assert ctx["training_level"] == "competitive"

    def test_competitive_519cm_jump_is_average(self) -> None:
        """Regression: 51.9cm competitive male must be 'average', not 'below_average'.

        A competitive male jumping 51.9cm with RSI 3.42 (very_good) and GCT 190ms
        (good) should not receive 'below_average' jump height feedback.
        """
        data = {"jump_height_m": 0.519}
        result = interpret_cmj_metrics(data, sex="male", training_level="competitive")

        category = result["jump_height"]["category"]
        assert category == "average", (
            f"51.9cm competitive male should be 'average', got '{category}'"
        )

    def test_competitive_jump_height_boundaries_consistent(self) -> None:
        """Competitive male jump height boundaries align with performance tiers.

        Values at the low end of 'average' and high end of 'below_average' must
        be in the expected categories.
        """
        # Just below average boundary should be below_average
        low = interpret_cmj_metrics(
            {"jump_height_m": 0.48}, sex="male", training_level="competitive"
        )
        assert low["jump_height"]["category"] == "below_average"

        # Solidly in average range should be average
        mid = interpret_cmj_metrics(
            {"jump_height_m": 0.55}, sex="male", training_level="competitive"
        )
        assert mid["jump_height"]["category"] == "average"
