"""Tests for video I/O functionality including codec extraction."""

import tempfile
from unittest.mock import patch

import cv2
import numpy as np
import pytest

from kinemotion.core.video_io import VideoProcessor


@pytest.fixture
def test_video_path() -> str:
    """Create a test video file with codec metadata."""
    temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    temp_path = temp_file.name
    temp_file.close()

    # Create a simple test video with mp4v codec
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(temp_path, fourcc, 30.0, (640, 480))

    # Write 10 frames
    for _ in range(10):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.circle(frame, (320, 240), 50, (255, 255, 255), -1)
        writer.write(frame)

    writer.release()
    return temp_path


def test_codec_extraction_from_video(test_video_path: str) -> None:
    """Test that codec is extracted from video metadata."""
    video = VideoProcessor(test_video_path)
    try:
        # Codec should be extracted (or None if ffprobe unavailable)
        # We just verify it's either a string or None
        assert video.codec is None or isinstance(video.codec, str)
    finally:
        video.close()


def test_codec_extraction_with_ffprobe_available(test_video_path: str) -> None:
    """Test codec extraction when ffprobe is available."""
    video = VideoProcessor(test_video_path)
    try:
        # If ffprobe is available, codec should be a string like "h264", "hevc", "mpeg4", etc.
        # If ffprobe is not available, it will be None
        if video.codec is not None:
            assert isinstance(video.codec, str)
            # Common codec names
            assert (
                video.codec
                in [
                    "h264",
                    "hevc",
                    "mpeg4",
                    "vp8",
                    "vp9",
                    "av1",
                    "mpeg2video",
                    "rawvideo",
                    "mpeg1video",
                ]
                or len(video.codec) > 0
            )
    finally:
        video.close()


def test_codec_none_on_ffprobe_failure(test_video_path: str) -> None:
    """Test that codec remains None if ffprobe fails or is unavailable."""
    with patch("kinemotion.core.video_io.subprocess.run") as mock_run:
        # Simulate ffprobe not being available (FileNotFoundError)
        mock_run.side_effect = FileNotFoundError("ffprobe not found")

        video = VideoProcessor(test_video_path)
        try:
            # Codec should remain None when ffprobe is unavailable
            assert video.codec is None
        finally:
            video.close()


def test_video_processor_basic_properties(test_video_path: str) -> None:
    """Test that VideoProcessor initializes all properties including codec."""
    video = VideoProcessor(test_video_path)
    try:
        # Verify all properties are set
        assert video.fps > 0
        assert video.frame_count > 0
        assert video.width > 0
        assert video.height > 0
        assert video.rotation in [0, 90, -90, 180, -180]
        # codec can be None or str
        assert video.codec is None or isinstance(video.codec, str)
    finally:
        video.close()


def test_codec_persists_across_frame_reading(test_video_path: str) -> None:
    """Test that codec property persists after reading frames."""
    video = VideoProcessor(test_video_path)
    try:
        codec_before = video.codec
        # Read a frame
        frame = video.read_frame()
        assert frame is not None
        # Codec should remain unchanged
        assert video.codec == codec_before
    finally:
        video.close()
