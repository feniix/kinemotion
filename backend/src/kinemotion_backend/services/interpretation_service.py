"""Metrics interpretation service for coaching insights.

Transforms raw analysis metrics into coaching-friendly interpretations with
normative benchmarks, performance categories, and actionable recommendations.
Uses rule-based logic grounded in validated physiological data from
kinemotion's existing validation bounds and published normative tables.

References:
    - docs/guides/coach-quick-start.md (normative tables)
    - src/kinemotion/*/validation_bounds.py (MetricBounds)
    - Cotton & Leonard (2026) BiomechAgent paper (architecture rationale)
"""

from __future__ import annotations

from typing import Any

# Performance categories ordered from worst to best
CATEGORIES = (
    "poor",
    "below_average",
    "average",
    "above_average",
    "good",
    "very_good",
    "excellent",
)

# --- Normative Data ---
# Sources: coach-quick-start.md, published literature, validation_bounds.py

# Jump height norms (cm) - adult general population
_JUMP_HEIGHT_NORMS_MALE: list[tuple[str, float, float]] = [
    ("poor", 21.0, 30.0),
    ("below_average", 31.0, 40.0),
    ("average", 41.0, 50.0),
    ("above_average", 51.0, 60.0),
    ("very_good", 61.0, 70.0),
    ("excellent", 70.0, 102.0),
]

_JUMP_HEIGHT_NORMS_FEMALE: list[tuple[str, float, float]] = [
    ("poor", 11.0, 20.0),
    ("below_average", 21.0, 30.0),
    ("average", 31.0, 40.0),
    ("above_average", 41.0, 50.0),
    ("very_good", 51.0, 60.0),
    ("excellent", 60.0, 76.0),
]

# RSI norms (drop jump from 30-40cm box)
_RSI_NORMS: list[tuple[str, float, float]] = [
    ("poor", 0.3, 0.8),
    ("below_average", 0.8, 1.0),
    ("average", 1.0, 1.5),
    ("good", 1.5, 2.0),
    ("very_good", 2.0, 2.5),
    ("excellent", 2.5, 4.0),
]

# Ground contact time norms (ms)
_GCT_NORMS: list[tuple[str, float, float]] = [
    ("excellent", 140.0, 180.0),
    ("very_good", 180.0, 200.0),
    ("good", 200.0, 220.0),
    ("average", 220.0, 250.0),
    ("below_average", 250.0, 350.0),
]

# Countermovement depth norms (cm)
_CM_DEPTH_NORMS: list[tuple[str, float, float]] = [
    ("too_shallow", 5.0, 20.0),
    ("optimal", 20.0, 35.0),
    ("deep", 35.0, 40.0),
    ("too_deep", 40.0, 75.0),
]

# Peak concentric velocity norms (m/s)
_PEAK_VELOCITY_NORMS: list[tuple[str, float, float]] = [
    ("below_average", 0.5, 1.8),
    ("average", 1.8, 2.4),
    ("above_average", 2.4, 3.0),
    ("very_good", 3.0, 3.6),
    ("excellent", 3.6, 5.0),
]


def _classify_value(
    value: float,
    norms: list[tuple[str, float, float]],
) -> tuple[str, float, float]:
    """Classify a value against normative ranges.

    Args:
        value: The metric value to classify.
        norms: List of (category, low, high) tuples.

    Returns:
        Tuple of (category, range_low, range_high). Falls back to closest
        category if value is outside all ranges.
    """
    for category, low, high in norms:
        if low <= value <= high:
            return category, low, high

    # Value outside all ranges - return closest boundary category
    if value < norms[0][1]:
        return norms[0][0], norms[0][1], norms[0][2]
    return norms[-1][0], norms[-1][1], norms[-1][2]


def _build_metric_interpretation(
    category: str,
    value: float,
    range_low: float,
    range_high: float,
    unit: str,
    coaching_tips: dict[str, str],
) -> dict[str, Any]:
    """Build a single metric interpretation dict.

    Args:
        category: Performance category name.
        value: Actual metric value.
        range_low: Low end of the matched range.
        range_high: High end of the matched range.
        unit: Measurement unit string.
        coaching_tips: Map of category to coaching recommendation.

    Returns:
        Interpretation dictionary with category, range, and recommendation.
    """
    return {
        "category": category,
        "value": value,
        "range": {"low": range_low, "high": range_high, "unit": unit},
        "recommendation": coaching_tips.get(category, ""),
    }


# --- Coaching recommendation text per metric per category ---

_JUMP_HEIGHT_TIPS: dict[str, str] = {
    "poor": ("Focus on lower-body strength with squats and lunges before jump training."),
    "below_average": (
        "Add basic plyometric drills and strength training to improve power output."
    ),
    "average": ("Good foundation. Progress to moderate plyometrics and Olympic lift variations."),
    "above_average": (
        "Strong performance. Refine technique and add sport-specific power exercises."
    ),
    "very_good": ("Excellent. Maintain power while adding advanced plyometric complexes."),
    "excellent": ("Elite level. Optimize movement efficiency and sport-specific application."),
}

_RSI_TIPS: dict[str, str] = {
    "poor": (
        "Not ready for high-intensity plyometrics. Focus on landing mechanics and strength base."
    ),
    "below_average": (
        "Build reactive strength with low-intensity plyometrics (ankle hops, skipping)."
    ),
    "average": ("Ready for moderate plyometrics. Progress box height gradually."),
    "good": ("Good reactive capacity. Increase plyometric intensity and add depth jumps."),
    "very_good": ("Strong plyometric capacity. Progress to sport-specific reactive drills."),
    "excellent": (
        "Elite reactive ability. Maintain with sport-specific power and high-intensity plyo."
    ),
}

_GCT_TIPS: dict[str, str] = {
    "excellent": ("Outstanding ground contact efficiency. Fast stretch-shortening cycle."),
    "very_good": ("Fast SSC utilization. Maintain with reactive training."),
    "good": ("Adequate reactive ability. Focus on faster ground contacts in drills."),
    "average": ("Room for improvement. Practice quick-response drills and ankle stiffness."),
    "below_average": (
        "Slow ground contact suggests weak SSC. Focus on technique and ankle stiffness."
    ),
}

_CM_DEPTH_TIPS: dict[str, str] = {
    "too_shallow": ("Countermovement too shallow. Cue deeper squat for full range of motion."),
    "optimal": ("Good countermovement depth. Balanced trade-off between depth and speed."),
    "deep": ("Slightly deep countermovement. May slow the transition \u2014 try shallower."),
    "too_deep": ("Countermovement too deep. Excessive depth slows the stretch-shortening cycle."),
}

_VELOCITY_TIPS: dict[str, str] = {
    "below_average": (
        "Low takeoff velocity. Focus on rate of force development and explosive strength."
    ),
    "average": (
        "Moderate velocity. Add contrast training (heavy sets followed by explosive jumps)."
    ),
    "above_average": ("Good velocity. Refine technique for more efficient force application."),
    "very_good": ("Strong velocity. Focus on sport-specific transfer of this power."),
    "excellent": ("Elite velocity. Optimize movement efficiency and reactive training."),
}


def interpret_cmj_metrics(metrics_data: dict[str, Any]) -> dict[str, Any]:
    """Generate coaching interpretations for CMJ metrics.

    Args:
        metrics_data: The 'data' dict from the analysis response.

    Returns:
        Dictionary of metric interpretations keyed by metric name.
    """
    interpretations: dict[str, Any] = {}

    # Jump height
    height_m = metrics_data.get("jump_height_m")
    if isinstance(height_m, (int, float)):
        height_cm = height_m * 100
        cat, low, high = _classify_value(height_cm, _JUMP_HEIGHT_NORMS_MALE)
        interpretations["jump_height"] = _build_metric_interpretation(
            cat, height_cm, low, high, "cm", _JUMP_HEIGHT_TIPS
        )

    # Peak concentric velocity
    velocity = metrics_data.get("peak_concentric_velocity_m_s")
    if isinstance(velocity, (int, float)):
        cat, low, high = _classify_value(velocity, _PEAK_VELOCITY_NORMS)
        interpretations["peak_concentric_velocity"] = _build_metric_interpretation(
            cat, velocity, low, high, "m/s", _VELOCITY_TIPS
        )

    # Countermovement depth
    depth_m = metrics_data.get("countermovement_depth_m")
    if isinstance(depth_m, (int, float)):
        depth_cm = depth_m * 100
        cat, low, high = _classify_value(depth_cm, _CM_DEPTH_NORMS)
        interpretations["countermovement_depth"] = _build_metric_interpretation(
            cat, depth_cm, low, high, "cm", _CM_DEPTH_TIPS
        )

    return interpretations


def interpret_dropjump_metrics(metrics_data: dict[str, Any]) -> dict[str, Any]:
    """Generate coaching interpretations for Drop Jump metrics.

    Args:
        metrics_data: The 'data' dict from the analysis response.

    Returns:
        Dictionary of metric interpretations keyed by metric name.
    """
    interpretations: dict[str, Any] = {}

    # RSI
    rsi = metrics_data.get("reactive_strength_index")
    if isinstance(rsi, (int, float)):
        cat, low, high = _classify_value(rsi, _RSI_NORMS)
        interpretations["rsi"] = _build_metric_interpretation(
            cat, rsi, low, high, "ratio", _RSI_TIPS
        )

    # Jump height
    height_m = metrics_data.get("jump_height_m")
    if isinstance(height_m, (int, float)):
        height_cm = height_m * 100
        cat, low, high = _classify_value(height_cm, _JUMP_HEIGHT_NORMS_MALE)
        interpretations["jump_height"] = _build_metric_interpretation(
            cat, height_cm, low, high, "cm", _JUMP_HEIGHT_TIPS
        )

    # Ground contact time
    gct_ms = metrics_data.get("ground_contact_time_ms")
    if isinstance(gct_ms, (int, float)):
        cat, low, high = _classify_value(gct_ms, _GCT_NORMS)
        interpretations["ground_contact_time"] = _build_metric_interpretation(
            cat, gct_ms, low, high, "ms", _GCT_TIPS
        )

    return interpretations


def interpret_sj_metrics(metrics_data: dict[str, Any]) -> dict[str, Any]:
    """Generate coaching interpretations for Squat Jump metrics.

    Args:
        metrics_data: The 'data' dict from the analysis response.

    Returns:
        Dictionary of metric interpretations keyed by metric name.
    """
    interpretations: dict[str, Any] = {}

    # Jump height (SJ typically lower than CMJ)
    height_m = metrics_data.get("jump_height_m")
    if isinstance(height_m, (int, float)):
        height_cm = height_m * 100
        cat, low, high = _classify_value(height_cm, _JUMP_HEIGHT_NORMS_MALE)
        interpretations["jump_height"] = _build_metric_interpretation(
            cat, height_cm, low, high, "cm", _JUMP_HEIGHT_TIPS
        )

    # Peak concentric velocity
    velocity = metrics_data.get("peak_concentric_velocity_m_s")
    if isinstance(velocity, (int, float)):
        cat, low, high = _classify_value(velocity, _PEAK_VELOCITY_NORMS)
        interpretations["peak_concentric_velocity"] = _build_metric_interpretation(
            cat, velocity, low, high, "m/s", _VELOCITY_TIPS
        )

    return interpretations


def interpret_metrics(
    jump_type: str,
    metrics_data: dict[str, Any],
) -> dict[str, Any]:
    """Generate coaching interpretations for analysis metrics.

    Routes to the appropriate jump-type interpreter and returns structured
    interpretation data suitable for the frontend.

    Args:
        jump_type: Normalized jump type string (cmj, drop_jump, sj).
        metrics_data: The 'data' dict from the analysis response.

    Returns:
        Dictionary with 'interpretations' key containing per-metric analysis.
        Returns empty dict if metrics_data is empty or None.
    """
    if not metrics_data:
        return {}

    interpreters = {
        "cmj": interpret_cmj_metrics,
        "drop_jump": interpret_dropjump_metrics,
        "sj": interpret_sj_metrics,
        "squat_jump": interpret_sj_metrics,
    }

    interpreter = interpreters.get(jump_type)
    if interpreter is None:
        return {}

    metric_interpretations = interpreter(metrics_data)

    if not metric_interpretations:
        return {}

    return {"interpretations": metric_interpretations}
