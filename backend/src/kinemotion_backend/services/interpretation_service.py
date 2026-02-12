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

from .coaching_insights import (
    generate_cmj_insights,
    generate_dropjump_insights,
    generate_sj_insights,
)
from .normative_data import (
    CM_DEPTH_NORMS,
    GCT_NORMS,
    JUMP_HEIGHT_NORMS,
    PEAK_VELOCITY_NORMS,
    RSI_NORMS,
    NormTable,
    get_norms,
)

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


def _classify_value(
    value: float,
    norms: NormTable,
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

    # Value below all ranges → first category
    if value < norms[0][1]:
        return norms[0][0], norms[0][1], norms[0][2]
    # Value above all ranges → last category
    if value > norms[-1][2]:
        return norms[-1][0], norms[-1][1], norms[-1][2]
    # Value in a gap between ranges → find closest range
    best_entry = norms[0]
    best_dist = min(abs(value - norms[0][1]), abs(value - norms[0][2]))
    for entry in norms[1:]:
        dist = min(abs(value - entry[1]), abs(value - entry[2]))
        if dist < best_dist:
            best_dist = dist
            best_entry = entry
    return best_entry[0], best_entry[1], best_entry[2]


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


def interpret_cmj_metrics(
    metrics_data: dict[str, Any],
    sex: str | None = None,
    age_group: str | None = None,
    training_level: str | None = None,
) -> dict[str, Any]:
    """Generate coaching interpretations for CMJ metrics.

    Args:
        metrics_data: The 'data' dict from the analysis response.
        sex: Biological sex for norm selection (None defaults to male).
        age_group: Age group for norm adjustment (None defaults to adult).
        training_level: Training level for norm adjustment (None defaults to trained).

    Returns:
        Dictionary of metric interpretations keyed by metric name.
    """
    interpretations: dict[str, Any] = {}

    # Jump height (sex-specific + age-adjusted + training-adjusted)
    height_m = metrics_data.get("jump_height_m")
    if isinstance(height_m, (int, float)):
        height_cm = height_m * 100
        norms = get_norms(
            JUMP_HEIGHT_NORMS,
            sex,
            age_group,
            training_level=training_level,
            metric_key="jump_height",
        )
        cat, low, high = _classify_value(height_cm, norms)
        interpretations["jump_height"] = _build_metric_interpretation(
            cat, height_cm, low, high, "cm", _JUMP_HEIGHT_TIPS
        )

    # Peak concentric velocity (sex-specific + age-adjusted + training-adjusted)
    velocity = metrics_data.get("peak_concentric_velocity_m_s")
    if isinstance(velocity, (int, float)):
        norms = get_norms(
            PEAK_VELOCITY_NORMS,
            sex,
            age_group,
            training_level=training_level,
            metric_key="peak_velocity",
        )
        cat, low, high = _classify_value(velocity, norms)
        interpretations["peak_concentric_velocity"] = _build_metric_interpretation(
            cat, velocity, low, high, "m/s", _VELOCITY_TIPS
        )

    # Countermovement depth (universal, age-adjusted only, no training factor)
    depth_m = metrics_data.get("countermovement_depth_m")
    if isinstance(depth_m, (int, float)):
        depth_cm = depth_m * 100
        norms = get_norms(CM_DEPTH_NORMS, age_group=age_group)
        cat, low, high = _classify_value(depth_cm, norms)
        interpretations["countermovement_depth"] = _build_metric_interpretation(
            cat, depth_cm, low, high, "cm", _CM_DEPTH_TIPS
        )

    return interpretations


def interpret_dropjump_metrics(
    metrics_data: dict[str, Any],
    sex: str | None = None,
    age_group: str | None = None,
    training_level: str | None = None,
) -> dict[str, Any]:
    """Generate coaching interpretations for Drop Jump metrics.

    Args:
        metrics_data: The 'data' dict from the analysis response.
        sex: Biological sex for norm selection (None defaults to male).
        age_group: Age group for norm adjustment (None defaults to adult).
        training_level: Training level for norm adjustment (None defaults to trained).

    Returns:
        Dictionary of metric interpretations keyed by metric name.
    """
    interpretations: dict[str, Any] = {}

    # RSI (sex-specific + age-adjusted + training-adjusted)
    rsi = metrics_data.get("reactive_strength_index")
    if isinstance(rsi, (int, float)):
        norms = get_norms(
            RSI_NORMS,
            sex,
            age_group,
            training_level=training_level,
            metric_key="rsi",
        )
        cat, low, high = _classify_value(rsi, norms)
        interpretations["rsi"] = _build_metric_interpretation(
            cat, rsi, low, high, "ratio", _RSI_TIPS
        )

    # Jump height (sex-specific + age-adjusted + training-adjusted)
    height_m = metrics_data.get("jump_height_m")
    if isinstance(height_m, (int, float)):
        height_cm = height_m * 100
        norms = get_norms(
            JUMP_HEIGHT_NORMS,
            sex,
            age_group,
            training_level=training_level,
            metric_key="jump_height",
        )
        cat, low, high = _classify_value(height_cm, norms)
        interpretations["jump_height"] = _build_metric_interpretation(
            cat, height_cm, low, high, "cm", _JUMP_HEIGHT_TIPS
        )

    # Ground contact time (universal, age-adjusted + training-adjusted, inverse metric)
    gct_ms = metrics_data.get("ground_contact_time_ms")
    if isinstance(gct_ms, (int, float)):
        norms = get_norms(
            GCT_NORMS,
            age_group=age_group,
            inverse=True,
            training_level=training_level,
            metric_key="ground_contact_time",
        )
        cat, low, high = _classify_value(gct_ms, norms)
        interpretations["ground_contact_time"] = _build_metric_interpretation(
            cat, gct_ms, low, high, "ms", _GCT_TIPS
        )

    return interpretations


def interpret_sj_metrics(
    metrics_data: dict[str, Any],
    sex: str | None = None,
    age_group: str | None = None,
    training_level: str | None = None,
) -> dict[str, Any]:
    """Generate coaching interpretations for Squat Jump metrics.

    Args:
        metrics_data: The 'data' dict from the analysis response.
        sex: Biological sex for norm selection (None defaults to male).
        age_group: Age group for norm adjustment (None defaults to adult).
        training_level: Training level for norm adjustment (None defaults to trained).

    Returns:
        Dictionary of metric interpretations keyed by metric name.
    """
    interpretations: dict[str, Any] = {}

    # Jump height (sex-specific + age-adjusted + training-adjusted)
    height_m = metrics_data.get("jump_height_m")
    if isinstance(height_m, (int, float)):
        height_cm = height_m * 100
        norms = get_norms(
            JUMP_HEIGHT_NORMS,
            sex,
            age_group,
            training_level=training_level,
            metric_key="jump_height",
        )
        cat, low, high = _classify_value(height_cm, norms)
        interpretations["jump_height"] = _build_metric_interpretation(
            cat, height_cm, low, high, "cm", _JUMP_HEIGHT_TIPS
        )

    # Peak concentric velocity (sex-specific + age-adjusted + training-adjusted)
    velocity = metrics_data.get("peak_concentric_velocity_m_s")
    if isinstance(velocity, (int, float)):
        norms = get_norms(
            PEAK_VELOCITY_NORMS,
            sex,
            age_group,
            training_level=training_level,
            metric_key="peak_velocity",
        )
        cat, low, high = _classify_value(velocity, norms)
        interpretations["peak_concentric_velocity"] = _build_metric_interpretation(
            cat, velocity, low, high, "m/s", _VELOCITY_TIPS
        )

    return interpretations


# Dispatch map from canonical jump type to interpreter function.
# Input is already normalized by validate_jump_type() so only canonical
# forms are needed here (aliases like "squat_jump" are resolved to "sj").
_INTERPRETERS: dict[str, Any] = {
    "cmj": interpret_cmj_metrics,
    "drop_jump": interpret_dropjump_metrics,
    "sj": interpret_sj_metrics,
}

# Dispatch map from jump type to insight generator function.
_INSIGHT_GENERATORS: dict[str, Any] = {
    "cmj": generate_cmj_insights,
    "drop_jump": generate_dropjump_insights,
    "sj": generate_sj_insights,
}


def interpret_metrics(
    jump_type: str,
    metrics_data: dict[str, Any],
    sex: str | None = None,
    age: int | None = None,
    training_level: str | None = None,
) -> dict[str, Any]:
    """Generate coaching interpretations for analysis metrics.

    Routes to the appropriate jump-type interpreter and returns structured
    interpretation data suitable for the frontend.

    Args:
        jump_type: Normalized jump type string (cmj, drop_jump, sj).
        metrics_data: The 'data' dict from the analysis response.
        sex: Biological sex string ("male" or "female"), or None for male default.
        age: Athlete age in years, or None for adult default.
        training_level: Training level string, or None for trained default.

    Returns:
        Dictionary with 'interpretations' key containing per-metric analysis.
        If demographics were provided, also includes 'demographic_context'.
        Returns empty dict if metrics_data is empty or None.
    """
    if not metrics_data:
        return {}

    # Derive age_group from age
    age_group: str | None = None
    if age is not None:
        if age < 18:
            age_group = "youth"
        elif age < 35:
            age_group = "adult"
        elif age < 50:
            age_group = "masters_35"
        elif age < 65:
            age_group = "masters_50"
        else:
            age_group = "senior"

    interpreter = _INTERPRETERS.get(jump_type)
    if interpreter is None:
        return {}

    metric_interpretations = interpreter(
        metrics_data,
        sex=sex,
        age_group=age_group,
        training_level=training_level,
    )

    if not metric_interpretations:
        return {}

    result: dict[str, Any] = {"interpretations": metric_interpretations}

    # Generate cross-metric coaching insights
    insight_generator = _INSIGHT_GENERATORS.get(jump_type)
    if insight_generator is not None:
        categories = {key: interp["category"] for key, interp in metric_interpretations.items()}
        insights: list[dict[str, object]] = insight_generator(categories)
        if insights:
            result["coaching_insights"] = insights

    # Include demographic context when demographics were provided
    if sex is not None or age is not None or training_level is not None:
        context: dict[str, Any] = {}
        if sex is not None:
            context["sex"] = sex
        if age_group is not None:
            context["age_group"] = age_group
        if training_level is not None:
            context["training_level"] = training_level
        result["demographic_context"] = context

    return result
