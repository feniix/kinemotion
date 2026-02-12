"""Cross-metric coaching insights for holistic jump analysis.

Synthesizes per-metric classifications into actionable coaching narratives
by identifying limiters, strengths, and cross-metric observations. This is
a rule-based system (deterministic, no LLM) consistent with the BiomechAgent
Tier 1 approach.

Separation of concerns:
    - interpretation_service.py: per-metric classification against norms
    - coaching_insights.py: cross-metric synthesis into coaching narratives
"""

from __future__ import annotations

# Category groupings used in rules
STRONG_CATS = frozenset({"good", "very_good", "excellent", "above_average"})
WEAK_CATS = frozenset({"poor", "below_average"})
AVERAGE_OR_BETTER = frozenset({"average", "above_average", "good", "very_good", "excellent"})


def _insight(
    type_: str,
    key: str,
    related_metrics: list[str],
    priority: int,
) -> dict[str, object]:
    """Build a single coaching insight dict."""
    return {
        "type": type_,
        "key": key,
        "related_metrics": related_metrics,
        "priority": priority,
    }


def generate_dropjump_insights(
    categories: dict[str, str],
) -> list[dict[str, object]]:
    """Generate cross-metric coaching insights for Drop Jump.

    Args:
        categories: Map of metric name to performance category string,
            e.g. {"rsi": "very_good", "jump_height": "poor", "ground_contact_time": "average"}.

    Returns:
        List of insight dicts sorted by priority (lower = more important).
    """
    insights: list[dict[str, object]] = []

    rsi_cat = categories.get("rsi", "")
    height_cat = categories.get("jump_height", "")
    gct_cat = categories.get("ground_contact_time", "")

    # RSI + Jump Height cross-metric rules
    if rsi_cat in STRONG_CATS and height_cat in WEAK_CATS:
        insights.append(_insight("limiter", "dj_height_limiter", ["rsi", "jump_height"], 1))
    elif rsi_cat in WEAK_CATS and height_cat in STRONG_CATS:
        insights.append(_insight("limiter", "dj_rsi_limiter", ["rsi", "jump_height"], 1))
    elif rsi_cat in WEAK_CATS and height_cat in WEAK_CATS:
        insights.append(_insight("limiter", "dj_both_weak", ["rsi", "jump_height"], 1))

    # RSI standalone strength
    if rsi_cat in STRONG_CATS:
        insights.append(_insight("strength", "dj_rsi_strength", ["rsi"], 3))

    # GCT rules
    if gct_cat in {"excellent", "very_good"}:
        insights.append(_insight("strength", "dj_gct_strength", ["ground_contact_time"], 3))
    elif gct_cat == "below_average":
        insights.append(_insight("limiter", "dj_gct_limiter", ["ground_contact_time"], 1))
    elif gct_cat == "average":
        insights.append(_insight("observation", "dj_gct_observation", ["ground_contact_time"], 2))

    insights.sort(key=lambda x: (x["priority"], str(x["key"])))
    return insights


def generate_cmj_insights(
    categories: dict[str, str],
) -> list[dict[str, object]]:
    """Generate cross-metric coaching insights for CMJ.

    Args:
        categories: Map of metric name to performance category string,
            e.g. {"jump_height": "poor", "peak_concentric_velocity": "average",
                   "countermovement_depth": "optimal"}.

    Returns:
        List of insight dicts sorted by priority.
    """
    insights: list[dict[str, object]] = []

    height_cat = categories.get("jump_height", "")
    velocity_cat = categories.get("peak_concentric_velocity", "")
    depth_cat = categories.get("countermovement_depth", "")

    # Height + Velocity cross-metric rules
    if height_cat in WEAK_CATS and velocity_cat in AVERAGE_OR_BETTER:
        insights.append(
            _insight(
                "limiter",
                "cmj_height_limiter",
                ["jump_height", "peak_concentric_velocity"],
                1,
            )
        )
    elif height_cat in AVERAGE_OR_BETTER and velocity_cat in WEAK_CATS:
        insights.append(
            _insight(
                "limiter",
                "cmj_velocity_limiter",
                ["jump_height", "peak_concentric_velocity"],
                1,
            )
        )

    # Depth + Height rules
    if depth_cat == "too_deep" and height_cat in WEAK_CATS:
        insights.append(
            _insight(
                "limiter",
                "cmj_depth_too_deep",
                ["countermovement_depth", "jump_height"],
                1,
            )
        )
    elif depth_cat == "too_shallow" and height_cat in WEAK_CATS:
        insights.append(
            _insight(
                "limiter",
                "cmj_depth_too_shallow",
                ["countermovement_depth", "jump_height"],
                1,
            )
        )

    # Depth optimal standalone
    if depth_cat == "optimal":
        insights.append(_insight("strength", "cmj_depth_optimal", ["countermovement_depth"], 3))

    # Both height + velocity strong
    if height_cat in STRONG_CATS and velocity_cat in STRONG_CATS:
        insights.append(
            _insight(
                "strength",
                "cmj_power_strength",
                ["jump_height", "peak_concentric_velocity"],
                3,
            )
        )

    insights.sort(key=lambda x: (x["priority"], str(x["key"])))
    return insights


def generate_sj_insights(
    categories: dict[str, str],
) -> list[dict[str, object]]:
    """Generate cross-metric coaching insights for Squat Jump.

    Args:
        categories: Map of metric name to performance category string,
            e.g. {"jump_height": "poor", "peak_concentric_velocity": "average"}.

    Returns:
        List of insight dicts sorted by priority.
    """
    insights: list[dict[str, object]] = []

    height_cat = categories.get("jump_height", "")
    velocity_cat = categories.get("peak_concentric_velocity", "")

    # Height + Velocity cross-metric rules
    if height_cat in WEAK_CATS and velocity_cat in AVERAGE_OR_BETTER:
        insights.append(
            _insight(
                "observation",
                "sj_height_limiter",
                ["jump_height", "peak_concentric_velocity"],
                2,
            )
        )
    elif height_cat in AVERAGE_OR_BETTER and velocity_cat in WEAK_CATS:
        insights.append(
            _insight(
                "limiter",
                "sj_velocity_limiter",
                ["jump_height", "peak_concentric_velocity"],
                1,
            )
        )

    # Both strong
    if height_cat in STRONG_CATS and velocity_cat in STRONG_CATS:
        insights.append(
            _insight(
                "strength",
                "sj_power_strength",
                ["jump_height", "peak_concentric_velocity"],
                3,
            )
        )

    insights.sort(key=lambda x: (x["priority"], str(x["key"])))
    return insights
