"""Tests for the public API module."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from kinemotion.api import (
    VideoConfig,
    VideoResult,
    process_video,
    process_videos_bulk,
)
from kinemotion.dropjump.kinematics import DropJumpMetrics


def test_process_video_returns_metrics(sample_video_path: str) -> None:
    """Test that process_video returns DropJumpMetrics object."""
    metrics = process_video(
        video_path=sample_video_path,
        drop_height=0.40,
        quality="fast",  # Use fast for quicker tests
        verbose=False,
    )

    # Should always return a DropJumpMetrics object even if analysis fails
    assert isinstance(metrics, DropJumpMetrics)
    # Note: Synthetic test videos won't produce valid results, so metrics may be None
    # In real usage with actual jump videos, these would be populated


def test_process_video_with_json_output(sample_video_path: str) -> None:
    """Test that process_video saves JSON output correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "metrics.json"

        process_video(
            video_path=sample_video_path,
            drop_height=0.40,
            json_output=str(json_path),
            quality="fast",
        )

        # Check JSON file was created
        assert json_path.exists()

        # Verify JSON content exists and is valid
        import json

        with open(json_path) as f:
            saved_metrics = json.load(f)

        # Check that JSON structure is correct (values may be None for synthetic video)
        assert "ground_contact_time_ms" in saved_metrics
        assert "flight_time_ms" in saved_metrics
        assert "jump_height_m" in saved_metrics


def test_process_video_with_debug_output(sample_video_path: str) -> None:
    """Test that process_video saves debug video correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "debug.mp4"

        metrics = process_video(
            video_path=sample_video_path,
            drop_height=0.40,
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
        process_video(
            video_path=str(dummy_video),
            drop_height=0.40,
            quality="invalid",
        )


def test_process_video_file_not_found() -> None:
    """Test that missing video file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="Video file not found"):
        process_video(
            video_path="nonexistent_video.mp4",
            drop_height=0.40,
        )


def test_process_video_quality_presets(sample_video_path: str) -> None:
    """Test that different quality presets work correctly."""
    qualities = ["fast", "balanced", "accurate"]

    for quality in qualities:
        metrics = process_video(
            video_path=sample_video_path,
            drop_height=0.40,
            quality=quality,
            verbose=False,
        )

        # Should return metrics object for all quality levels
        assert isinstance(metrics, DropJumpMetrics)
        # Note: Metrics may be None for synthetic test videos


def test_process_video_with_expert_overrides(sample_video_path: str) -> None:
    """Test that expert parameter overrides work."""
    metrics = process_video(
        video_path=sample_video_path,
        drop_height=0.40,
        smoothing_window=7,
        velocity_threshold=0.025,
        min_contact_frames=5,
        visibility_threshold=0.6,
        verbose=False,
    )

    assert isinstance(metrics, DropJumpMetrics)


def test_video_config_creation() -> None:
    """Test VideoConfig dataclass creation."""
    config = VideoConfig(
        video_path="test.mp4",
        drop_height=0.40,
        quality="balanced",
    )

    assert config.video_path == "test.mp4"
    assert config.drop_height == 0.40
    assert config.quality == "balanced"
    assert config.output_video is None
    assert config.json_output is None


def test_video_result_creation() -> None:
    """Test VideoResult dataclass creation."""
    metrics = DropJumpMetrics()
    metrics.ground_contact_time = 0.250  # 250ms in seconds
    metrics.flight_time = 0.500  # 500ms in seconds
    metrics.jump_height = 0.35

    result = VideoResult(
        video_path="test.mp4",
        success=True,
        metrics=metrics,
        processing_time=5.5,
    )

    assert result.video_path == "test.mp4"
    assert result.success is True
    assert result.metrics == metrics
    assert result.processing_time == 5.5
    assert result.error is None


def test_process_videos_bulk_success(sample_video_path: str) -> None:
    """Test bulk processing of multiple videos."""
    configs = [
        VideoConfig(video_path=sample_video_path, drop_height=0.40, quality="fast"),
        VideoConfig(video_path=sample_video_path, drop_height=0.30, quality="fast"),
    ]

    results = process_videos_bulk(configs, max_workers=2)

    assert len(results) == 2

    for result in results:
        assert isinstance(result, VideoResult)
        assert result.video_path == sample_video_path
        assert result.success is True
        assert result.metrics is not None
        assert result.error is None
        assert result.processing_time > 0


def test_process_videos_bulk_with_failure() -> None:
    """Test bulk processing handles failures gracefully."""
    configs = [
        VideoConfig(video_path="nonexistent1.mp4", drop_height=0.40),
        VideoConfig(video_path="nonexistent2.mp4", drop_height=0.40),
    ]

    results = process_videos_bulk(configs, max_workers=2)

    assert len(results) == 2

    for result in results:
        assert isinstance(result, VideoResult)
        assert result.success is False
        assert result.metrics is None
        assert result.error is not None
        assert "not found" in result.error.lower()


def test_process_videos_bulk_mixed_results(sample_video_path: str) -> None:
    """Test bulk processing with mix of successful and failed videos."""
    configs = [
        VideoConfig(video_path=sample_video_path, drop_height=0.40, quality="fast"),
        VideoConfig(video_path="nonexistent.mp4", drop_height=0.40),
        VideoConfig(video_path=sample_video_path, drop_height=0.30, quality="fast"),
    ]

    results = process_videos_bulk(configs, max_workers=2)

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


def test_process_videos_bulk_progress_callback(sample_video_path: str) -> None:
    """Test that progress callback is called for each video."""
    configs = [
        VideoConfig(video_path=sample_video_path, drop_height=0.40, quality="fast"),
        VideoConfig(video_path=sample_video_path, drop_height=0.30, quality="fast"),
    ]

    callback_results = []

    def progress_callback(result: VideoResult) -> None:
        callback_results.append(result)

    results = process_videos_bulk(
        configs, max_workers=2, progress_callback=progress_callback
    )

    # Callback should be called for each video
    assert len(callback_results) == 2
    assert len(results) == 2

    # Results should match
    for callback_result in callback_results:
        assert callback_result in results


def test_process_videos_bulk_different_parameters(sample_video_path: str) -> None:
    """Test bulk processing with different parameter combinations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        configs = [
            VideoConfig(
                video_path=sample_video_path,
                drop_height=0.40,
                quality="fast",
            ),
            VideoConfig(
                video_path=sample_video_path,
                drop_height=0.40,
                quality="balanced",
                json_output=str(Path(tmpdir) / "video2.json"),
            ),
            VideoConfig(
                video_path=sample_video_path,
                drop_height=0.40,
                quality="fast",
                smoothing_window=7,
            ),
        ]

        results = process_videos_bulk(configs, max_workers=2)

        assert len(results) == 3
        assert all(r.success for r in results)

        # Check JSON output was created
        json_file = Path(tmpdir) / "video2.json"
        assert json_file.exists()


# Fixtures


@pytest.fixture
def sample_video_path(tmp_path: Path) -> str:
    """Create a minimal synthetic video for testing."""
    import cv2

    video_path = tmp_path / "test_video.mp4"

    # Create a simple test video (30 frames at 30fps = 1 second)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(video_path), fourcc, 30.0, (640, 480))

    # Generate frames with a simple moving pattern
    for i in range(30):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add some pattern to make pose detection possible (though it will likely fail)
        cv2.circle(frame, (320, 240 + i * 5), 50, (255, 255, 255), -1)
        out.write(frame)

    out.release()

    return str(video_path)
