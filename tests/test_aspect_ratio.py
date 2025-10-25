"""Test that aspect ratio is preserved from source video."""

import tempfile
from pathlib import Path

import cv2
import numpy as np

from kinemotion.core.video_io import VideoProcessor
from kinemotion.dropjump.debug_overlay import DebugOverlayRenderer


def create_test_video(width: int, height: int, fps: float = 30.0, num_frames: int = 10) -> str:
    """Create a test video with specified dimensions."""
    temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    temp_path = temp_file.name
    temp_file.close()

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))

    for _ in range(num_frames):
        # Create a random frame
        frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
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
    import pytest

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
