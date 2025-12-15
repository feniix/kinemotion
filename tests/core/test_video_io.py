"""Tests for video I/O functionality including codec extraction."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
import pytest

from kinemotion.core.video_io import VideoProcessor
from kinemotion.dropjump.debug_overlay import DebugOverlayRenderer


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
        # If ffprobe is available, codec should be a string like "h264",
        # "hevc", "mpeg4", etc. If ffprobe is not available, it will be None
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


"""Test that aspect ratio is preserved from source video."""


def create_test_video(width: int, height: int, fps: float = 30.0, num_frames: int = 10) -> str:
    """Create a test video with specified dimensions."""
    temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    temp_path = temp_file.name
    temp_file.close()

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))

    rng = np.random.default_rng(42)
    for _ in range(num_frames):
        # Create a random frame
        frame = rng.integers(0, 255, (height, width, 3), dtype=np.uint8)
        writer.write(frame)

    writer.release()
    return temp_path


def test_aspect_ratio_16_9():
    """Test 16:9 aspect ratio video."""
    # Create test video with 16:9 aspect ratio
    test_video = create_test_video(1920, 1080)

    try:
        # Read video
        video = VideoProcessor(test_video)
        assert video.width == 1920
        assert video.height == 1080
        video.close()

        # Create output video
        output_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
        renderer = DebugOverlayRenderer(output_path, 1920, 1080, 1920, 1080, 30.0)

        # Write test frame
        test_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        renderer.write_frame(test_frame)
        renderer.close()

        # Verify output dimensions
        cap = cv2.VideoCapture(output_path)
        ret, frame = cap.read()
        assert ret
        # Dimensions are downscaled to max 720p and even numbers
        # 1920x1080 -> scale 0.375 -> 720x405 -> 720x404 (even)
        assert frame.shape[0] == 404  # height
        assert frame.shape[1] == 720  # width
        cap.release()

        Path(output_path).unlink()

    finally:
        Path(test_video).unlink()


def test_aspect_ratio_4_3():
    """Test 4:3 aspect ratio video."""
    # Create test video with 4:3 aspect ratio
    test_video = create_test_video(640, 480)

    try:
        video = VideoProcessor(test_video)
        assert video.width == 640
        assert video.height == 480
        video.close()

    finally:
        Path(test_video).unlink()


def test_aspect_ratio_9_16_portrait():
    """Test 9:16 portrait aspect ratio video."""
    # Create test video with portrait aspect ratio
    test_video = create_test_video(1080, 1920)

    try:
        video = VideoProcessor(test_video)
        assert video.width == 1080
        assert video.height == 1920
        video.close()

        # Create output video
        output_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
        renderer = DebugOverlayRenderer(output_path, 1080, 1920, 1080, 1920, 30.0)

        # Write test frame
        test_frame = np.zeros((1920, 1080, 3), dtype=np.uint8)
        renderer.write_frame(test_frame)
        renderer.close()

        # Verify output dimensions
        cap = cv2.VideoCapture(output_path)
        ret, frame = cap.read()
        assert ret
        # Dimensions are downscaled to max 720p and even numbers
        # 1080x1920 -> scale 0.375 -> 405x720 -> 404x720 (even)
        assert frame.shape[0] == 720  # height
        assert frame.shape[1] == 404  # width
        cap.release()

        Path(output_path).unlink()

    finally:
        Path(test_video).unlink()


def test_frame_dimension_validation():
    """Test that mismatched frame dimensions raise an error."""
    output_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

    try:
        renderer = DebugOverlayRenderer(output_path, 1920, 1080, 1920, 1080, 30.0)

        # Try to write frame with wrong dimensions
        wrong_frame = np.zeros((1080, 1080, 3), dtype=np.uint8)  # Square instead of 16:9

        with pytest.raises(ValueError, match="don't match"):
            renderer.write_frame(wrong_frame)

        renderer.close()

    finally:
        Path(output_path).unlink(missing_ok=True)


def test_ffprobe_not_found_warning():
    """Test that warning is shown when ffprobe is not available."""
    test_video = create_test_video(640, 480)

    try:
        # Mock subprocess.run to raise FileNotFoundError (ffprobe not found)
        with patch("subprocess.run", side_effect=FileNotFoundError("ffprobe not found")):
            with pytest.warns(UserWarning, match="ffprobe not found.*rotation and aspect ratio"):
                video = VideoProcessor(test_video)
                video.close()

    finally:
        Path(test_video).unlink()


def test_ffprobe_timeout_silent():
    """Test that ffprobe timeout is handled silently."""
    import subprocess

    test_video = create_test_video(640, 480)

    try:
        # Mock subprocess.run to raise TimeoutExpired
        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired("ffprobe", timeout=5),
        ):
            # Should not raise exception or warning, just continue
            video = VideoProcessor(test_video)
            assert video.rotation == 0  # Default rotation
            video.close()

    finally:
        Path(test_video).unlink()


def test_ffprobe_json_decode_error_silent():
    """Test that ffprobe JSON decode error is handled silently."""
    import json

    test_video = create_test_video(640, 480)

    try:
        # Mock subprocess.run to raise JSONDecodeError
        with patch(
            "subprocess.run",
            side_effect=json.JSONDecodeError("Invalid JSON", "", 0),
        ):
            # Should not raise exception or warning, just continue
            video = VideoProcessor(test_video)
            assert video.rotation == 0  # Default rotation
            video.close()

    finally:
        Path(test_video).unlink()


def test_video_not_found():
    """Test that VideoProcessor raises ValueError for non-existent video."""
    with pytest.raises(ValueError, match="Could not open video"):
        VideoProcessor("/nonexistent/path/to/video.mp4")


def test_ffprobe_returncode_error():
    """Test that ffprobe non-zero returncode is handled silently."""
    from unittest.mock import MagicMock

    test_video = create_test_video(640, 480)

    try:
        # Mock subprocess.run to return non-zero returncode
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        with patch("subprocess.run", return_value=mock_result):
            # Should continue silently with defaults
            video = VideoProcessor(test_video)
            assert video.rotation == 0
            video.close()

    finally:
        Path(test_video).unlink()


def test_ffprobe_empty_streams():
    """Test that ffprobe with no streams is handled silently."""
    from unittest.mock import MagicMock

    test_video = create_test_video(640, 480)

    try:
        # Mock subprocess.run to return empty streams
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"streams": []}'

        with patch("subprocess.run", return_value=mock_result):
            # Should continue silently with defaults
            video = VideoProcessor(test_video)
            assert video.rotation == 0
            video.close()

    finally:
        Path(test_video).unlink()


def test_video_rotation_90_degrees():
    """Test video rotation handling for 90 degree rotation."""
    from unittest.mock import MagicMock

    test_video = create_test_video(640, 480)

    try:
        # Mock ffprobe to return 90 degree rotation
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """{
            "streams": [{
                "sample_aspect_ratio": "1:1",
                "side_data_list": [{
                    "side_data_type": "Display Matrix",
                    "rotation": 90
                }]
            }]
        }"""

        with patch("subprocess.run", return_value=mock_result):
            video = VideoProcessor(test_video)
            assert video.rotation == 90

            # Read frame and verify rotation is applied
            frame = video.read_frame()
            assert frame is not None
            # After 90° rotation: width and height should be swapped
            assert frame.shape[1] == 480  # Original height becomes width
            assert frame.shape[0] == 640  # Original width becomes height

            video.close()

    finally:
        Path(test_video).unlink()


def test_video_rotation_negative_90_degrees():
    """Test video rotation handling for -90 degree rotation."""
    from unittest.mock import MagicMock

    test_video = create_test_video(640, 480)

    try:
        # Mock ffprobe to return -90 degree rotation
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """{
            "streams": [{
                "sample_aspect_ratio": "1:1",
                "side_data_list": [{
                    "side_data_type": "Display Matrix",
                    "rotation": -90
                }]
            }]
        }"""

        with patch("subprocess.run", return_value=mock_result):
            video = VideoProcessor(test_video)
            assert video.rotation == -90

            # Read frame and verify rotation is applied
            frame = video.read_frame()
            assert frame is not None
            # After -90° rotation: dimensions swapped
            assert frame.shape[1] == 480
            assert frame.shape[0] == 640

            video.close()

    finally:
        Path(test_video).unlink()


def test_video_rotation_180_degrees():
    """Test video rotation handling for 180 degree rotation."""
    from unittest.mock import MagicMock

    test_video = create_test_video(640, 480)

    try:
        # Mock ffprobe to return 180 degree rotation
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """{
            "streams": [{
                "sample_aspect_ratio": "1:1",
                "side_data_list": [{
                    "side_data_type": "Display Matrix",
                    "rotation": 180
                }]
            }]
        }"""

        with patch("subprocess.run", return_value=mock_result):
            video = VideoProcessor(test_video)
            assert video.rotation == 180

            # Read frame and verify rotation is applied
            frame = video.read_frame()
            assert frame is not None
            # After 180° rotation: dimensions stay the same
            assert frame.shape[1] == 640
            assert frame.shape[0] == 480

            video.close()

    finally:
        Path(test_video).unlink()
