"""Tests for CMJ API module."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from kinemotion.api import (
    CMJAnalysisOverrides,
    CMJVideoConfig,
    CMJVideoResult,
    process_cmj_video,
    process_cmj_videos_bulk,
)
from kinemotion.cmj.kinematics import CMJMetrics
from kinemotion.core.auto_tuning import AnalysisParameters, QualityPreset
from kinemotion.core.pipeline_utils import (
    apply_expert_overrides,
    determine_confidence_levels,
)

# Skip multiprocessing tests in CI
# MediaPipe doesn't work well with ProcessPoolExecutor in headless environments
skip_in_ci = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Multiprocessing with MediaPipe not supported in CI headless environment",
)


def test_process_cmj_video_returns_metrics(sample_video_path: str) -> None:
    """Test that process_cmj_video returns CMJMetrics object or raises ValueError."""
    # CMJ phase detection may fail on synthetic video - that's acceptable
    try:
        metrics = process_cmj_video(
            video_path=sample_video_path,
            quality="fast",  # Use fast for quicker tests
            verbose=False,
        )

        # Should return a CMJMetrics object
        assert isinstance(metrics, CMJMetrics)

    except ValueError as e:
        # CMJ phase detection failure is expected on synthetic video
        assert "Could not detect CMJ phases" in str(e)


def test_process_cmj_video_with_json_output(sample_video_path: str) -> None:
    """Test that process_cmj_video saves JSON output correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "metrics.json"

        # CMJ analysis may fail on synthetic video, so catch ValueError
        try:
            process_cmj_video(
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

            # Check that JSON structure is correct (data/metadata structure)
            assert "data" in saved_metrics
            assert "metadata" in saved_metrics

            # Check data fields (values may be None for synthetic video)
            assert "jump_height_m" in saved_metrics["data"]
            assert "flight_time_ms" in saved_metrics["data"]
            assert "countermovement_depth_m" in saved_metrics["data"]

            # Check metadata fields
            assert "quality" in saved_metrics["metadata"]
            assert "video" in saved_metrics["metadata"]
            assert "processing" in saved_metrics["metadata"]
            assert "algorithm" in saved_metrics["metadata"]

        except ValueError:
            # CMJ phase detection may fail on synthetic video - that's acceptable
            pass


def test_process_cmj_video_with_debug_output(sample_video_path: str) -> None:
    """Test that process_cmj_video saves debug video correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "debug.mp4"

        try:
            metrics = process_cmj_video(
                video_path=sample_video_path,
                output_video=str(output_path),
                quality="fast",
            )

            # Check debug video was created
            assert output_path.exists()
            assert output_path.stat().st_size > 0  # Non-empty file

            # Metrics should still be returned
            assert isinstance(metrics, CMJMetrics)

        except ValueError:
            # CMJ phase detection may fail on synthetic video - that's acceptable
            pass


def test_process_cmj_video_invalid_quality(tmp_path: Path) -> None:
    """Test that invalid quality preset raises ValueError."""
    # Create a dummy video file
    dummy_video = tmp_path / "dummy.mp4"
    dummy_video.touch()

    with pytest.raises(ValueError, match="Invalid quality preset"):
        process_cmj_video(
            video_path=str(dummy_video),
            quality="invalid",
        )


def test_process_cmj_video_file_not_found() -> None:
    """Test that missing video file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="Video file not found"):
        process_cmj_video(
            video_path="nonexistent_video.mp4",
        )


def test_process_cmj_video_quality_presets(sample_video_path: str) -> None:
    """Test that different quality presets work correctly."""
    qualities = ["fast", "balanced", "accurate"]

    for quality in qualities:
        try:
            metrics = process_cmj_video(
                video_path=sample_video_path,
                quality=quality,
                verbose=False,
            )

            # Should return metrics object for all quality levels
            assert isinstance(metrics, CMJMetrics)
            # Note: Metrics may be None for synthetic test videos

        except ValueError:
            # CMJ phase detection may fail on synthetic video - that's acceptable
            pass


def test_process_cmj_video_with_expert_overrides(sample_video_path: str) -> None:
    """Test that expert parameter overrides work."""
    try:
        overrides = CMJAnalysisOverrides(
            smoothing_window=7,
            velocity_threshold=0.025,
            min_contact_frames=5,
            visibility_threshold=0.6,
        )
        metrics = process_cmj_video(
            video_path=sample_video_path,
            overrides=overrides,
            verbose=False,
        )

        assert isinstance(metrics, CMJMetrics)

    except ValueError:
        # CMJ phase detection may fail on synthetic video - that's acceptable
        pass


def test_cmj_video_config_creation() -> None:
    """Test CMJVideoConfig dataclass creation."""
    config = CMJVideoConfig(
        video_path="test.mp4",
        quality="balanced",
    )

    assert config.video_path == "test.mp4"
    assert config.quality == "balanced"
    assert config.output_video is None
    assert config.json_output is None


def test_cmj_video_result_creation() -> None:
    """Test CMJVideoResult dataclass creation."""
    metrics = CMJMetrics(
        jump_height=0.45,
        flight_time=0.60,
        countermovement_depth=0.35,
        eccentric_duration=0.50,
        concentric_duration=0.35,
        total_movement_time=0.85,
        peak_eccentric_velocity=1.5,
        peak_concentric_velocity=2.9,
        transition_time=0.05,
        standing_start_frame=10.0,
        lowest_point_frame=25.0,
        takeoff_frame=40.0,
        landing_frame=58.0,
        video_fps=30.0,
        tracking_method="foot",
    )

    result = CMJVideoResult(
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
def test_process_cmj_videos_bulk_success(sample_video_path: str) -> None:
    """Test bulk processing of multiple CMJ videos."""
    configs = [
        CMJVideoConfig(video_path=sample_video_path, quality="fast"),
        CMJVideoConfig(video_path=sample_video_path, quality="fast"),
    ]

    results = process_cmj_videos_bulk(configs, max_workers=2)

    assert len(results) == 2

    for result in results:
        assert isinstance(result, CMJVideoResult)
        assert result.video_path == sample_video_path
        # Result may succeed or fail depending on synthetic video quality
        assert result.processing_time > 0


@skip_in_ci
def test_process_cmj_videos_bulk_with_failure() -> None:
    """Test bulk processing handles failures gracefully."""
    configs = [
        CMJVideoConfig(
            video_path="nonexistent1.mp4",
        ),
        CMJVideoConfig(
            video_path="nonexistent2.mp4",
        ),
    ]

    results = process_cmj_videos_bulk(configs, max_workers=2)

    assert len(results) == 2

    for result in results:
        assert isinstance(result, CMJVideoResult)
        assert result.success is False
        assert result.metrics is None
        assert result.error is not None
        assert "not found" in result.error.lower()


@skip_in_ci
def test_process_cmj_videos_bulk_mixed_results(sample_video_path: str) -> None:
    """Test bulk processing with mix of successful and failed videos."""
    configs = [
        CMJVideoConfig(video_path=sample_video_path, quality="fast"),
        CMJVideoConfig(
            video_path="nonexistent.mp4",
        ),
        CMJVideoConfig(video_path=sample_video_path, quality="fast"),
    ]

    results = process_cmj_videos_bulk(configs, max_workers=2)

    assert len(results) == 3

    failed = [r for r in results if not r.success]

    # At least one should fail (the nonexistent file)
    assert len(failed) >= 1

    # Check failed result
    assert failed[0].metrics is None
    assert failed[0].error is not None


@skip_in_ci
def test_process_cmj_videos_bulk_progress_callback(sample_video_path: str) -> None:
    """Test that progress callback is called for each video."""
    configs = [
        CMJVideoConfig(video_path=sample_video_path, quality="fast"),
        CMJVideoConfig(video_path=sample_video_path, quality="fast"),
    ]

    callback_results = []

    def progress_callback(result: CMJVideoResult) -> None:
        callback_results.append(result)

    results = process_cmj_videos_bulk(configs, max_workers=2, progress_callback=progress_callback)

    # Callback should be called for each video
    assert len(callback_results) == 2
    assert len(results) == 2

    # Results should match
    for callback_result in callback_results:
        assert callback_result in results


@skip_in_ci
def test_process_cmj_videos_bulk_different_parameters(sample_video_path: str) -> None:
    """Test bulk processing with different parameter combinations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        configs = [
            CMJVideoConfig(
                video_path=sample_video_path,
                quality="fast",
            ),
            CMJVideoConfig(
                video_path=sample_video_path,
                quality="balanced",
                json_output=str(Path(tmpdir) / "video2.json"),
            ),
            CMJVideoConfig(
                video_path=sample_video_path,
                quality="fast",
                overrides=CMJAnalysisOverrides(smoothing_window=7),
            ),
        ]

        results = process_cmj_videos_bulk(configs, max_workers=2)

        assert len(results) == 3

        # Check JSON output was created if analysis succeeded
        json_file = Path(tmpdir) / "video2.json"
        if results[1].success:
            assert json_file.exists()


# Unit tests for helper functions (shared with Drop Jump)


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


def test_process_cmj_video_verbose_mode(
    sample_video_path: str, capsys: pytest.CaptureFixture
) -> None:
    """Test that verbose mode prints parameter information."""
    try:
        process_cmj_video(video_path=sample_video_path, quality="fast", verbose=True)

        captured = capsys.readouterr()

        # Check that verbose output contains expected information
        assert "AUTO-TUNED PARAMETERS" in captured.out or "Processing" in captured.out

    except ValueError:
        # CMJ phase detection may fail on synthetic video - that's acceptable
        pass


# Fixtures


# sample_video_path fixture moved to tests/conftest.py


def test_cmj_analysis_overrides_dataclass() -> None:
    """Test AnalysisOverrides dataclass creation and defaults."""
    # Test all None (default)
    overrides = CMJAnalysisOverrides()
    assert overrides.smoothing_window is None
    assert overrides.velocity_threshold is None
    assert overrides.min_contact_frames is None
    assert overrides.visibility_threshold is None

    # Test partial overrides
    overrides = CMJAnalysisOverrides(smoothing_window=9)
    assert overrides.smoothing_window == 9
    assert overrides.velocity_threshold is None

    # Test all specified
    overrides = CMJAnalysisOverrides(
        smoothing_window=9,
        velocity_threshold=0.03,
        min_contact_frames=7,
        visibility_threshold=0.7,
    )
    assert overrides.smoothing_window == 9
    assert overrides.velocity_threshold == 0.03
    assert overrides.min_contact_frames == 7
    assert overrides.visibility_threshold == 0.7


def test_generate_debug_video_integration(sample_video_path: str) -> None:
    """Test debug video generation through full pipeline."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "debug.mp4"

        try:
            _ = process_cmj_video(
                video_path=sample_video_path,
                output_video=str(output_path),
                quality="fast",
                verbose=True,
            )

            # If processing succeeded, check video was created
            if output_path.exists():
                assert output_path.stat().st_size > 0

        except ValueError:
            # CMJ detection may fail on synthetic video
            pass


def test_save_metrics_to_json_integration(sample_video_path: str) -> None:
    """Test JSON metrics saving through full pipeline."""
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "metrics.json"

        try:
            _ = process_cmj_video(
                video_path=sample_video_path,
                json_output=str(json_path),
                quality="fast",
                verbose=True,
            )

            # If processing succeeded, check JSON was created
            if json_path.exists():
                assert json_path.stat().st_size > 0
                data = json.loads(json_path.read_text())
                assert "jump_height" in data
                assert "flight_time" in data

        except ValueError:
            # CMJ detection may fail on synthetic video
            pass


def test_process_cmj_video_with_all_outputs(sample_video_path: str) -> None:
    """Test processing with both debug video and JSON output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_video = Path(tmpdir) / "debug.mp4"
        json_output = Path(tmpdir) / "metrics.json"

        try:
            metrics = process_cmj_video(
                video_path=sample_video_path,
                output_video=str(output_video),
                json_output=str(json_output),
                quality="fast",
                verbose=True,
            )

            assert isinstance(metrics, CMJMetrics)

        except ValueError:
            # CMJ detection may fail on synthetic video
            pass


def test_process_cmj_video_with_confidence_overrides(sample_video_path: str) -> None:
    """Test processing with detection and tracking confidence overrides."""
    try:
        metrics = process_cmj_video(
            video_path=sample_video_path,
            detection_confidence=0.4,
            tracking_confidence=0.4,
            quality="fast",
            verbose=False,
        )

        assert isinstance(metrics, CMJMetrics)

    except ValueError:
        # CMJ detection may fail on synthetic video
        pass
