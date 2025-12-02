"""Tests for metadata structures and serialization."""

import pytest

from kinemotion.core.metadata import (
    ProcessingInfo,
    SmoothingConfig,
    VideoInfo,
    create_timestamp,
    get_kinemotion_version,
)

pytestmark = [pytest.mark.unit, pytest.mark.core]


# ===== VideoInfo Tests =====


def test_video_info_creation() -> None:
    """Test VideoInfo dataclass creation."""
    video_info = VideoInfo(
        source_path="/path/to/video.mp4",
        fps=30.0,
        width=1920,
        height=1080,
        duration_s=10.5,
        frame_count=315,
        codec="h264",
    )

    assert video_info.source_path == "/path/to/video.mp4"
    assert video_info.fps == 30.0
    assert video_info.width == 1920
    assert video_info.height == 1080
    assert video_info.duration_s == 10.5
    assert video_info.frame_count == 315
    assert video_info.codec == "h264"


def test_video_info_to_dict() -> None:
    """Test VideoInfo.to_dict() serialization."""
    video_info = VideoInfo(
        source_path="test.mp4",
        fps=29.97,
        width=1280,
        height=720,
        duration_s=5.234,
        frame_count=157,
        codec="hevc",
    )

    result = video_info.to_dict()

    assert isinstance(result, dict)
    assert result["source_path"] == "test.mp4"
    assert result["fps"] == pytest.approx(29.97, abs=0.01)  # Rounded to 2 decimals
    assert result["resolution"] == {"width": 1280, "height": 720}
    assert result["duration_s"] == 5.23  # Rounded
    assert result["frame_count"] == 157
    assert result["codec"] == "hevc"


def test_video_info_without_codec() -> None:
    """Test VideoInfo with codec as None."""
    video_info = VideoInfo(
        source_path="test.mp4",
        fps=30.0,
        width=640,
        height=480,
        duration_s=10.0,
        frame_count=300,
        codec=None,
    )

    result = video_info.to_dict()
    assert result["codec"] is None


# ===== ProcessingInfo Tests =====


def test_processing_info_creation() -> None:
    """Test ProcessingInfo dataclass creation."""
    proc_info = ProcessingInfo(
        version="0.34.0",
        timestamp="2025-12-02T12:00:00Z",
        quality_preset="balanced",
        processing_time_s=5.234,
    )

    assert proc_info.version == "0.34.0"
    assert proc_info.timestamp == "2025-12-02T12:00:00Z"
    assert proc_info.quality_preset == "balanced"
    assert proc_info.processing_time_s == 5.234


def test_processing_info_to_dict() -> None:
    """Test ProcessingInfo.to_dict() serialization."""
    proc_info = ProcessingInfo(
        version="0.34.0",
        timestamp="2025-12-02T12:00:00Z",
        quality_preset="accurate",
        processing_time_s=12.5678,
    )

    result = proc_info.to_dict()

    assert isinstance(result, dict)
    assert result["version"] == "0.34.0"
    assert result["timestamp"] == "2025-12-02T12:00:00Z"
    assert result["quality_preset"] == "accurate"
    assert result["processing_time_s"] == 12.568  # Rounded to 3 decimals


# ===== SmoothingConfig Tests =====


def test_smoothing_config_creation() -> None:
    """Test SmoothingConfig dataclass creation."""
    config = SmoothingConfig(
        window_size=7,
        polynomial_order=2,
        use_bilateral_filter=True,
        use_outlier_rejection=True,
    )

    assert config.window_size == 7
    assert config.polynomial_order == 2
    assert config.use_bilateral_filter is True
    assert config.use_outlier_rejection is True


def test_smoothing_config_to_dict() -> None:
    """Test SmoothingConfig.to_dict() serialization."""
    config = SmoothingConfig(
        window_size=5,
        polynomial_order=3,
        use_bilateral_filter=False,
        use_outlier_rejection=True,
    )

    result = config.to_dict()

    assert isinstance(result, dict)
    assert result["window_size"] == 5
    assert result["polynomial_order"] == 3
    assert result["use_bilateral_filter"] is False
    assert result["use_outlier_rejection"] is True


# ===== Helper Function Tests =====


def test_create_timestamp() -> None:
    """Test create_timestamp returns valid ISO 8601 timestamp."""
    timestamp = create_timestamp()

    assert isinstance(timestamp, str)
    assert "T" in timestamp  # ISO 8601 format has T separator
    assert len(timestamp) > 10  # Should have date + time


def test_get_kinemotion_version() -> None:
    """Test get_kinemotion_version returns version string."""
    version = get_kinemotion_version()

    assert isinstance(version, str)
    # Should be either a version number or "unknown"
    assert version != ""
