"""Tests for pipeline utilities."""

import pytest

from kinemotion.core.auto_tuning import AnalysisParameters, QualityPreset
from kinemotion.core.pipeline_utils import (
    apply_expert_overrides,
    convert_timer_to_stage_names,
    determine_confidence_levels,
    extract_vertical_positions,
    parse_quality_preset,
)


def test_parse_quality_preset_valid() -> None:
    assert parse_quality_preset("fast") == QualityPreset.FAST
    assert parse_quality_preset("BALANCED") == QualityPreset.BALANCED
    assert parse_quality_preset("Accurate") == QualityPreset.ACCURATE


def test_parse_quality_preset_invalid() -> None:
    with pytest.raises(ValueError, match="Invalid quality preset"):
        parse_quality_preset("invalid")


def test_determine_confidence_levels() -> None:
    d, t = determine_confidence_levels(QualityPreset.FAST, None, None)
    assert d == 0.3
    assert t == 0.3

    d, t = determine_confidence_levels(QualityPreset.BALANCED, 0.8, 0.9)
    assert d == 0.8
    assert t == 0.9


def test_apply_expert_overrides() -> None:
    params = AnalysisParameters(
        smoothing_window=5,
        velocity_threshold=0.01,
        min_contact_frames=3,
        visibility_threshold=0.5,
        polyorder=2,
        detection_confidence=0.5,
        tracking_confidence=0.5,
        outlier_rejection=False,
        bilateral_filter=False,
        use_curvature=True,
    )

    new_params = apply_expert_overrides(params, 7, None, None, None)
    assert new_params.smoothing_window == 7
    assert new_params.velocity_threshold == 0.01


def test_extract_vertical_positions_foot() -> None:
    # Mock smoothed landmarks: list of dicts or None
    # frame 1: present, frame 2: missing
    landmarks = [
        {"left_ankle": (0.5, 0.8, 0.9), "right_ankle": (0.6, 0.8, 0.9)},
        None,
    ]

    # average y for frame 1: 0.8
    # frame 2: repeats previous (0.8)

    positions, visibilities = extract_vertical_positions(landmarks, target="foot")

    assert len(positions) == 2
    assert positions[0] == 0.8
    assert positions[1] == 0.8
    assert visibilities[0] > 0
    assert visibilities[1] == 0.0


def test_convert_timer_to_stage_names() -> None:
    metrics = {"pose_tracking": 1.5, "unknown_stage": 0.5}
    names = convert_timer_to_stage_names(metrics)

    assert names["Pose tracking"] == 1.5
    assert names["unknown_stage"] == 0.5
