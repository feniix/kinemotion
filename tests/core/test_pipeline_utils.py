"""Tests for pipeline utilities."""

from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from kinemotion.core.auto_tuning import AnalysisParameters, QualityPreset
from kinemotion.core.pipeline_utils import (
    apply_expert_overrides,
    apply_smoothing,
    calculate_foot_visibility,
    convert_timer_to_stage_names,
    determine_confidence_levels,
    extract_vertical_positions,
    parse_quality_preset,
    print_verbose_parameters,
    process_all_frames,
    process_videos_bulk_generic,
)
from kinemotion.core.timing import PerformanceTimer


def _create_default_params() -> AnalysisParameters:
    return AnalysisParameters(
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

    # Partial overrides
    d, t = determine_confidence_levels(QualityPreset.ACCURATE, 0.9, None)
    assert d == 0.9
    assert t == 0.6  # Default for ACCURATE

    d, t = determine_confidence_levels(QualityPreset.ACCURATE, None, 0.9)
    assert d == 0.6
    assert t == 0.9


def test_apply_expert_overrides() -> None:
    params = _create_default_params()

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


def test_print_verbose_parameters(capsys: pytest.CaptureFixture) -> None:
    video = MagicMock(fps=30.0)
    chars = MagicMock(tracking_quality="good", avg_visibility=0.9)
    params = _create_default_params()
    print_verbose_parameters(video, chars, QualityPreset.BALANCED, params)
    captured = capsys.readouterr()
    assert "AUTO-TUNED PARAMETERS" in captured.out
    assert "Video FPS: 30.00" in captured.out


def test_process_all_frames_basic() -> None:
    video = MagicMock()
    # Return one valid frame, then None to stop
    video.read_frame.side_effect = [np.zeros((100, 100, 3), dtype=np.uint8), None]
    video.fps = 30.0
    video.display_width = 100
    video.display_height = 100
    video.width = 100
    video.height = 100

    tracker = MagicMock()
    tracker.process_frame.return_value = {}

    debug_frames, landmarks, indices = process_all_frames(video, tracker, verbose=False)

    assert len(debug_frames) == 1
    assert len(landmarks) == 1
    assert indices == [0]
    tracker.close.assert_called_once()


def test_process_all_frames_with_timer() -> None:
    video = MagicMock()
    video.read_frame.side_effect = [np.zeros((100, 100, 3), dtype=np.uint8), None]
    video.fps = 30.0
    video.display_width = 100
    video.display_height = 100
    video.width = 100
    video.height = 100

    tracker = MagicMock()
    tracker.process_frame.return_value = {}
    timer = PerformanceTimer()

    debug_frames, landmarks, indices = process_all_frames(
        video, tracker, verbose=False, timer=timer
    )

    assert len(debug_frames) == 1
    assert "pose_tracking" in timer.get_metrics()


def test_process_all_frames_resizing() -> None:
    video = MagicMock()
    video.read_frame.side_effect = [np.zeros((1000, 1000, 3), dtype=np.uint8), None]
    video.fps = 30.0
    video.display_width = 1000
    video.display_height = 1000
    video.width = 1000
    video.height = 1000

    tracker = MagicMock()
    tracker.process_frame.return_value = {}

    # max_debug_dim=500 -> should resize to 500x500
    debug_frames, _, _ = process_all_frames(video, tracker, verbose=False, max_debug_dim=500)

    assert debug_frames[0].shape == (500, 500, 3)


def test_apply_smoothing_options() -> None:
    landmarks = [{}, {}]
    params = _create_default_params()
    params.outlier_rejection = True
    params.bilateral_filter = True

    with patch("kinemotion.core.pipeline_utils.smooth_landmarks_advanced") as mock_smooth:
        apply_smoothing(landmarks, params, verbose=True)
        mock_smooth.assert_called_once()


def test_apply_smoothing_with_timer() -> None:
    landmarks = [{}, {}]
    params = _create_default_params()
    # Simple smoothing
    params.outlier_rejection = False
    params.bilateral_filter = False
    timer = PerformanceTimer()

    with patch("kinemotion.core.pipeline_utils.smooth_landmarks") as mock_smooth:
        apply_smoothing(landmarks, params, verbose=False, timer=timer)
        mock_smooth.assert_called_once()
        assert "smoothing" in timer.get_metrics()


def test_calculate_foot_visibility() -> None:
    # All feet points present
    landmarks = {
        "left_ankle": (0, 0, 0.9),
        "right_ankle": (0, 0, 0.8),
        "left_heel": (0, 0, 0.7),
        "right_heel": (0, 0, 0.6),
    }
    vis = calculate_foot_visibility(landmarks)
    assert vis == (0.9 + 0.8 + 0.7 + 0.6) / 4

    # Empty
    assert calculate_foot_visibility({}) == 0.0


@dataclass
class MockConfig:
    video_path: str


# Module-level functions for multiprocessing pickling
def _mock_processor(conf: MockConfig) -> str:
    if conf.video_path == "v2":
        raise ValueError("fail")
    return "success"


def _mock_error_factory(path: str, msg: str) -> str:
    return f"error: {path} {msg}"


def test_process_videos_bulk_generic_error() -> None:
    config1 = MockConfig(video_path="v1")
    config2 = MockConfig(video_path="v2")  # This one will fail
    configs = [config1, config2]

    # We use module-level functions which are picklable
    results = process_videos_bulk_generic(
        configs, _mock_processor, _mock_error_factory, max_workers=2
    )

    assert "success" in results
    # The order is not guaranteed
    errors = [r for r in results if isinstance(r, str) and r.startswith("error")]
    assert len(errors) == 1
    assert "error: v2" in errors[0]
