"""Tests for Drop Jump API module."""

import os
import tempfile
from pathlib import Path

import pytest

from kinemotion.api import (
    DropJumpVideoConfig,
    DropJumpVideoResult,
    process_dropjump_video,
    process_dropjump_videos_bulk,
)
from kinemotion.core.auto_tuning import AnalysisParameters, QualityPreset
from kinemotion.core.pipeline_utils import (
    apply_expert_overrides,
    determine_confidence_levels,
)
from kinemotion.dropjump.kinematics import DropJumpMetrics

# Skip multiprocessing tests in CI
# MediaPipe doesn't work well with ProcessPoolExecutor in headless environments
skip_in_ci = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Multiprocessing with MediaPipe not supported in CI headless environment",
)


def test_process_video_returns_metrics(sample_video_path: str) -> None:
    """Test that process_dropjump_video returns DropJumpMetrics object."""
    metrics = process_dropjump_video(
        video_path=sample_video_path,
        quality="fast",  # Use fast for quicker tests
        verbose=False,
    )

    # Should always return a DropJumpMetrics object even if analysis fails
    assert isinstance(metrics, DropJumpMetrics)
    # Note: Synthetic test videos won't produce valid results, so metrics may be None
    # In real usage with actual jump videos, these would be populated


def test_process_video_with_json_output(sample_video_path: str) -> None:
    """Test that process_dropjump_video saves JSON output correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "metrics.json"

        process_dropjump_video(
            video_path=sample_video_path,
            json_output=str(json_path),
            quality="fast",
        )

        # Check JSON file was created
        assert json_path.exists()

        # Verify JSON content exists and is valid
        import json

        with open(json_path) as f:
            saved_metrics = json.load(f)

        # Check that JSON structure is correct (new data/metadata structure)
        assert "data" in saved_metrics
        assert "metadata" in saved_metrics

        # Check data fields (values may be None for synthetic video)
        assert "ground_contact_time_ms" in saved_metrics["data"]
        assert "flight_time_ms" in saved_metrics["data"]
        assert "jump_height_m" in saved_metrics["data"]

        # Check metadata fields
        assert "quality" in saved_metrics["metadata"]
        assert "video" in saved_metrics["metadata"]
        assert "processing" in saved_metrics["metadata"]
        assert "algorithm" in saved_metrics["metadata"]


def test_process_video_with_debug_output(sample_video_path: str) -> None:
    """Test that process_dropjump_video saves debug video correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "debug.mp4"

        metrics = process_dropjump_video(
            video_path=sample_video_path,
            output_video=str(output_path),
            quality="fast",
        )

        # Check debug video was created
        assert output_path.exists()
        assert output_path.stat().st_size > 0  # Non-empty file

        # Metrics should still be returned
        assert isinstance(metrics, DropJumpMetrics)


def test_process_video_invalid_quality(tmp_path: Path) -> None:
    """Test that invalid quality preset raises ValueError."""
    # Create a dummy video file
    dummy_video = tmp_path / "dummy.mp4"
    dummy_video.touch()

    with pytest.raises(ValueError, match="Invalid quality preset"):
        process_dropjump_video(
            video_path=str(dummy_video),
            quality="invalid",
        )


def test_process_video_file_not_found() -> None:
    """Test that missing video file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="Video file not found"):
        process_dropjump_video(
            video_path="nonexistent_video.mp4",
        )


def test_process_video_quality_presets(sample_video_path: str) -> None:
    """Test that different quality presets work correctly."""
    qualities = ["fast", "balanced", "accurate"]

    for quality in qualities:
        metrics = process_dropjump_video(
            video_path=sample_video_path,
            quality=quality,
            verbose=False,
        )

        # Should return metrics object for all quality levels
        assert isinstance(metrics, DropJumpMetrics)
        # Note: Metrics may be None for synthetic test videos


def test_process_video_with_expert_overrides(sample_video_path: str) -> None:
    """Test that expert parameter overrides work."""
    from kinemotion.dropjump.api import AnalysisOverrides

    overrides = AnalysisOverrides(
        smoothing_window=7,
        velocity_threshold=0.025,
        min_contact_frames=5,
        visibility_threshold=0.6,
    )

    metrics = process_dropjump_video(
        video_path=sample_video_path,
        overrides=overrides,
        verbose=False,
    )

    assert isinstance(metrics, DropJumpMetrics)


def test_video_config_creation() -> None:
    """Test DropJumpVideoConfig dataclass creation."""
    config = DropJumpVideoConfig(
        video_path="test.mp4",
        quality="balanced",
    )

    assert config.video_path == "test.mp4"
    assert config.quality == "balanced"
    assert config.output_video is None
    assert config.json_output is None


def test_video_result_creation() -> None:
    """Test DropJumpVideoResult dataclass creation."""
    metrics = DropJumpMetrics()
    metrics.ground_contact_time = 0.250  # 250ms in seconds
    metrics.flight_time = 0.500  # 500ms in seconds
    metrics.jump_height = 0.35

    result = DropJumpVideoResult(
        video_path="test.mp4",
        success=True,
        metrics=metrics,
        processing_time=5.5,
    )

    assert result.video_path == "test.mp4"
    assert result.success is True
    assert result.metrics == metrics
    assert result.processing_time == pytest.approx(5.5)
    assert result.error is None


@skip_in_ci
def test_process_videos_bulk_success(sample_video_path: str) -> None:
    """Test bulk processing of multiple videos."""
    configs = [
        DropJumpVideoConfig(video_path=sample_video_path, quality="fast"),
        DropJumpVideoConfig(video_path=sample_video_path, quality="fast"),
    ]

    results = process_dropjump_videos_bulk(configs, max_workers=2)

    assert len(results) == 2

    for result in results:
        assert isinstance(result, DropJumpVideoResult)
        assert result.video_path == sample_video_path
        assert result.success is True
        assert result.metrics is not None
        assert result.error is None
        assert result.processing_time > 0


@skip_in_ci
def test_process_videos_bulk_with_failure() -> None:
    """Test bulk processing handles failures gracefully."""
    configs = [
        DropJumpVideoConfig(
            video_path="nonexistent1.mp4",
        ),
        DropJumpVideoConfig(
            video_path="nonexistent2.mp4",
        ),
    ]

    results = process_dropjump_videos_bulk(configs, max_workers=2)

    assert len(results) == 2

    for result in results:
        assert isinstance(result, DropJumpVideoResult)
        assert result.success is False
        assert result.metrics is None
        assert result.error is not None
        assert "not found" in result.error.lower()


@skip_in_ci
def test_process_videos_bulk_mixed_results(sample_video_path: str) -> None:
    """Test bulk processing with mix of successful and failed videos."""
    configs = [
        DropJumpVideoConfig(video_path=sample_video_path, quality="fast"),
        DropJumpVideoConfig(
            video_path="nonexistent.mp4",
        ),
        DropJumpVideoConfig(video_path=sample_video_path, quality="fast"),
    ]

    results = process_dropjump_videos_bulk(configs, max_workers=2)

    assert len(results) == 3

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    assert len(successful) == 2
    assert len(failed) == 1

    # Check successful results
    for result in successful:
        assert result.metrics is not None
        assert result.error is None

    # Check failed result
    assert failed[0].metrics is None
    assert failed[0].error is not None


@skip_in_ci
def test_process_videos_bulk_progress_callback(sample_video_path: str) -> None:
    """Test that progress callback is called for each video."""
    configs = [
        DropJumpVideoConfig(video_path=sample_video_path, quality="fast"),
        DropJumpVideoConfig(video_path=sample_video_path, quality="fast"),
    ]

    callback_results = []

    def progress_callback(result: DropJumpVideoResult) -> None:
        callback_results.append(result)

    results = process_dropjump_videos_bulk(
        configs, max_workers=2, progress_callback=progress_callback
    )

    # Callback should be called for each video
    assert len(callback_results) == 2
    assert len(results) == 2

    # Results should match
    for callback_result in callback_results:
        assert callback_result in results


@skip_in_ci
def test_process_videos_bulk_different_parameters(sample_video_path: str) -> None:
    """Test bulk processing with different parameter combinations."""
    from kinemotion.dropjump.api import AnalysisOverrides

    with tempfile.TemporaryDirectory() as tmpdir:
        configs = [
            DropJumpVideoConfig(
                video_path=sample_video_path,
                quality="fast",
            ),
            DropJumpVideoConfig(
                video_path=sample_video_path,
                quality="balanced",
                json_output=str(Path(tmpdir) / "video2.json"),
            ),
            DropJumpVideoConfig(
                video_path=sample_video_path,
                quality="fast",
                overrides=AnalysisOverrides(smoothing_window=7),
            ),
        ]

        results = process_dropjump_videos_bulk(configs, max_workers=2)

        assert len(results) == 3
        assert all(r.success for r in results)

        # Check JSON output was created for second video
        json_file = Path(tmpdir) / "video2.json"
        assert json_file.exists(), "JSON output should be created for video2"


# Unit tests for helper functions


def test_determine_confidence_levels_default() -> None:
    """Test determine_confidence_levels with default values."""
    detection, tracking = determine_confidence_levels(
        quality_preset=QualityPreset.BALANCED,
        detection_confidence=None,
        tracking_confidence=None,
    )

    assert detection == 0.5
    assert tracking == 0.5


def test_determine_confidence_levels_with_overrides() -> None:
    """Test determine_confidence_levels with custom confidence values."""
    detection, tracking = determine_confidence_levels(
        quality_preset=QualityPreset.BALANCED,
        detection_confidence=0.8,
        tracking_confidence=0.7,
    )

    assert detection == 0.8
    assert tracking == 0.7


def test_apply_expert_overrides_all_parameters() -> None:
    """Test apply_expert_overrides with all parameters specified."""
    params = AnalysisParameters(
        smoothing_window=5,
        velocity_threshold=0.02,
        min_contact_frames=3,
        visibility_threshold=0.5,
        polyorder=2,
        detection_confidence=0.5,
        tracking_confidence=0.5,
        outlier_rejection=False,
        bilateral_filter=False,
        use_curvature=True,
    )

    result = apply_expert_overrides(
        params,
        smoothing_window=7,
        velocity_threshold=0.03,
        min_contact_frames=5,
        visibility_threshold=0.6,
    )

    assert result.smoothing_window == 7
    assert result.velocity_threshold == 0.03
    assert result.min_contact_frames == 5
    assert result.visibility_threshold == 0.6


def test_apply_expert_overrides_partial() -> None:
    """Test apply_expert_overrides with only some parameters."""
    params = AnalysisParameters(
        smoothing_window=5,
        velocity_threshold=0.02,
        min_contact_frames=3,
        visibility_threshold=0.5,
        polyorder=2,
        detection_confidence=0.5,
        tracking_confidence=0.5,
        outlier_rejection=False,
        bilateral_filter=False,
        use_curvature=True,
    )

    result = apply_expert_overrides(
        params,
        smoothing_window=9,
        velocity_threshold=None,
        min_contact_frames=None,
        visibility_threshold=None,
    )

    # Only smoothing_window should change
    assert result.smoothing_window == 9
    assert result.velocity_threshold == 0.02  # Unchanged
    assert result.min_contact_frames == 3  # Unchanged
    assert result.visibility_threshold == 0.5  # Unchanged


def test_process_video_verbose_mode(sample_video_path: str, capsys: pytest.CaptureFixture) -> None:
    """Test that verbose mode prints parameter information."""
    process_dropjump_video(video_path=sample_video_path, quality="fast", verbose=True)

    captured = capsys.readouterr()

    # Check that verbose output contains expected information
    assert "AUTO-TUNED PARAMETERS" in captured.out or "Processing" in captured.out


# Fixtures


# sample_video_path fixture moved to tests/conftest.py
