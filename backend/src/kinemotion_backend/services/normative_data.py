"""Sex-specific normative data with age adjustment factors.

Provides norm tables for coaching interpretation of jump metrics.
Each metric has either sex-specific or universal norms, with age-group
multipliers applied to boundary values.

References:
    - Meylan et al. (2009) CMJ norms by sex/age
    - Markovic & Jaric (2007) sex differences in jumping
    - Vanderburgh (2000) age-related performance decline
"""

from __future__ import annotations

NormTable = list[tuple[str, float, float]]

# ---------------------------------------------------------------------------
# Sex-specific base tables (adult reference values)
# ---------------------------------------------------------------------------

# Jump height norms (cm) - strong sex difference
JUMP_HEIGHT_NORMS: dict[str, NormTable] = {
    "male": [
        ("poor", 21.0, 30.0),
        ("below_average", 31.0, 40.0),
        ("average", 41.0, 50.0),
        ("above_average", 51.0, 60.0),
        ("very_good", 61.0, 70.0),
        ("excellent", 70.0, 102.0),
    ],
    "female": [
        ("poor", 11.0, 20.0),
        ("below_average", 21.0, 30.0),
        ("average", 31.0, 40.0),
        ("above_average", 41.0, 50.0),
        ("very_good", 51.0, 60.0),
        ("excellent", 60.0, 76.0),
    ],
}

# Peak concentric velocity norms (m/s) - sex-specific
PEAK_VELOCITY_NORMS: dict[str, NormTable] = {
    "male": [
        ("below_average", 0.5, 1.8),
        ("average", 1.8, 2.4),
        ("above_average", 2.4, 3.0),
        ("very_good", 3.0, 3.6),
        ("excellent", 3.6, 5.0),
    ],
    "female": [
        ("below_average", 0.4, 1.5),
        ("average", 1.5, 2.0),
        ("above_average", 2.0, 2.6),
        ("very_good", 2.6, 3.2),
        ("excellent", 3.2, 4.5),
    ],
}

# RSI norms (ratio) - sex-specific
RSI_NORMS: dict[str, NormTable] = {
    "male": [
        ("poor", 0.3, 0.8),
        ("below_average", 0.8, 1.0),
        ("average", 1.0, 1.5),
        ("good", 1.5, 2.0),
        ("very_good", 2.0, 2.5),
        ("excellent", 2.5, 4.0),
    ],
    "female": [
        ("poor", 0.2, 0.6),
        ("below_average", 0.6, 0.8),
        ("average", 0.8, 1.2),
        ("good", 1.2, 1.6),
        ("very_good", 1.6, 2.0),
        ("excellent", 2.0, 3.2),
    ],
}

# ---------------------------------------------------------------------------
# Universal tables (minimal sex difference)
# ---------------------------------------------------------------------------

# Ground contact time norms (ms) - minimal sex difference
GCT_NORMS: NormTable = [
    ("excellent", 140.0, 180.0),
    ("very_good", 180.0, 200.0),
    ("good", 200.0, 220.0),
    ("average", 220.0, 250.0),
    ("below_average", 250.0, 350.0),
]

# Countermovement depth norms (cm) - minimal sex difference
CM_DEPTH_NORMS: NormTable = [
    ("too_shallow", 5.0, 20.0),
    ("optimal", 20.0, 35.0),
    ("deep", 35.0, 40.0),
    ("too_deep", 40.0, 75.0),
]

# ---------------------------------------------------------------------------
# Age adjustment factors (multiplied against norm boundaries)
# ---------------------------------------------------------------------------

# Applied as multipliers: lower factor = lower expected performance.
# Reference group is adult (1.00). Based on cross-sectional decline data.
AGE_FACTORS: dict[str, float] = {
    "youth": 0.85,  # Still developing neuromuscular system
    "adult": 1.00,  # Reference group (18-34)
    "masters_35": 0.92,  # ~8% decline per decade after 30
    "masters_50": 0.82,  # Cumulative age-related decline
    "senior": 0.70,  # Significant but variable decline
}


def _apply_age_factor(
    norms: NormTable,
    age_group: str | None,
) -> NormTable:
    """Scale norm boundaries by the age-group factor.

    Args:
        norms: Base norm table (adult reference).
        age_group: AgeGroup value string, or None for default (adult).

    Returns:
        New NormTable with scaled boundaries.
    """
    if age_group is None or age_group == "adult":
        return norms

    factor = AGE_FACTORS.get(age_group, 1.0)
    return [
        (category, round(low * factor, 1), round(high * factor, 1))
        for category, low, high in norms
    ]


def get_norms(
    base_norms: NormTable | dict[str, NormTable],
    sex: str | None = None,
    age_group: str | None = None,
) -> NormTable:
    """Return age/sex-adjusted norm table.

    Args:
        base_norms: Either a sex-keyed dict or a universal NormTable.
        sex: "male" or "female", or None for male default.
        age_group: AgeGroup value string, or None for adult default.

    Returns:
        NormTable adjusted for the given demographics.
    """
    # Select sex-specific table or use universal
    if isinstance(base_norms, dict):
        sex_key = sex if sex in base_norms else "male"
        table = base_norms[sex_key]
    else:
        table = base_norms

    # Apply age adjustment
    return _apply_age_factor(table, age_group)
