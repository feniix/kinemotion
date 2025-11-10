"""Test that aspect ratio is preserved from source video."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
import pytest

from kinemotion.core.video_io import VideoProcessor
from kinemotion.dropjump.debug_overlay import DebugOverlayRenderer


def create_test_video(
    width: int, height: int, fps: float = 30.0, num_frames: int = 10
) -> str:
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
        assert frame.shape[0] == 1080  # height
        assert frame.shape[1] == 1920  # width
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

    finally:
        Path(test_video).unlink()


def test_frame_dimension_validation():
    """Test that mismatched frame dimensions raise an error."""
    output_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

    try:
        renderer = DebugOverlayRenderer(output_path, 1920, 1080, 1920, 1080, 30.0)

        # Try to write frame with wrong dimensions
        wrong_frame = np.zeros(
            (1080, 1080, 3), dtype=np.uint8
        )  # Square instead of 16:9

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
        with patch(
            "subprocess.run", side_effect=FileNotFoundError("ffprobe not found")
        ):
            with pytest.warns(
                UserWarning, match="ffprobe not found.*rotation and aspect ratio"
            ):
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
