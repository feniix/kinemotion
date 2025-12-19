"""Tests for debug overlay video generation and codec selection.

REGRESSION TEST: Ensures VP9 codec is never re-added (breaks iOS compatibility).
These tests focus on the core functionality rather than implementation details.
"""

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from kinemotion.core.debug_overlay_utils import (
    BaseDebugOverlayRenderer,
    create_video_writer,
)


@pytest.fixture
def temp_output_path(tmp_path: Path) -> str:
    """Create a temporary output path for test videos."""
    return str(tmp_path / "test_output.mp4")


class TestCodecSelection:
    """Tests for codec selection logic (iOS compatibility fix).

    CRITICAL: VP9 (vp09) must never be in the codec list - it breaks iOS playback.
    """

    def test_vp09_codec_never_in_codec_list(self) -> None:
        """REGRESSION TEST: Ensure VP9 is never added back to codec list.

        This test prevents the iPhone 16 Pro playback bug from returning.
        VP9 is not supported by iOS browsers (they all use WebKit).
        """
        # Read the actual source code to check codec list
        import inspect
        import re

        from kinemotion.core import debug_overlay_utils

        source = inspect.getsource(debug_overlay_utils.create_video_writer)

        # Extract the actual codec list (not comments)
        # Look for: codecs_to_try = ["...", "...", ...]
        codec_list_match = re.search(r"codecs_to_try\s*=\s*\[(.*?)\]", source, re.DOTALL)
        assert codec_list_match, "Could not find codecs_to_try list in source"

        codec_list_str = codec_list_match.group(1).lower()

        # Check that vp09 is NOT in the actual codec list
        assert "vp09" not in codec_list_str and "vp9" not in codec_list_str, (
            "VP9 codec detected in codec list! This breaks iOS compatibility. "
            "VP9 is not supported on iPhone/iPad browsers. "
            "Only use: avc1, h264, mp4v (with FFmpeg re-encoding)"
        )

        # Also verify with actual function call
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "test.mp4")

            with patch("cv2.VideoWriter") as mock_writer_class:
                mock_writer = MagicMock()
                mock_writer.isOpened.return_value = True
                mock_writer_class.return_value = mock_writer

                writer, _, codec = create_video_writer(
                    output_path=output_path,
                    width=640,
                    height=480,
                    display_width=640,
                    display_height=480,
                    fps=30.0,
                )

                assert codec != "vp09", "VP9 codec used! This breaks iOS."
                assert codec in ["avc1", "mp4v"], f"Unexpected codec: {codec}"


class TestVideoWriterCreation:
    """Tests for video writer creation logic."""

    def test_writer_creation_success(self, temp_output_path: str) -> None:
        """Test successful video writer creation."""
        with patch("cv2.VideoWriter") as mock_writer_class:
            mock_writer = MagicMock()
            mock_writer.isOpened.return_value = True
            mock_writer_class.return_value = mock_writer

            writer, needs_resize, _ = create_video_writer(
                output_path=temp_output_path,
                width=640,
                height=480,
                display_width=640,
                display_height=480,
                fps=30.0,
            )

            assert writer is not None
            assert needs_resize is False  # Same dimensions

    def test_writer_creation_with_resize(self, temp_output_path: str) -> None:
        """Test that resize flag is set when dimensions differ."""
        with patch("cv2.VideoWriter") as mock_writer_class:
            mock_writer = MagicMock()
            mock_writer.isOpened.return_value = True
            mock_writer_class.return_value = mock_writer

            writer, needs_resize, _ = create_video_writer(
                output_path=temp_output_path,
                width=1920,
                height=1080,
                display_width=640,
                display_height=360,
                fps=30.0,
            )

            assert writer is not None
            assert needs_resize is True  # Different dimensions


class TestDebugOverlayRenderer:
    """Tests for BaseDebugOverlayRenderer class."""

    def test_resolution_unchanged_for_smaller_videos(self, temp_output_path: str) -> None:
        """Test that videos under 720p are not resized."""
        with patch("cv2.VideoWriter") as mock_writer_class:
            mock_writer = MagicMock()
            mock_writer.isOpened.return_value = True
            mock_writer_class.return_value = mock_writer

            # Use 640x480 which is definitely under the 1280 cap
            renderer = BaseDebugOverlayRenderer(
                output_path=temp_output_path,
                width=640,
                height=480,
                display_width=640,
                display_height=480,
                fps=30.0,
            )

            # Should remain unchanged
            assert renderer.display_width == 640
            assert renderer.display_height == 480

    def test_no_crash_when_ffmpeg_unavailable(self, temp_output_path: str) -> None:
        """Test that missing FFmpeg doesn't crash the renderer."""
        with patch("cv2.VideoWriter") as mock_writer_class:
            mock_writer = MagicMock()
            mock_writer.isOpened.return_value = True
            mock_writer_class.return_value = mock_writer

            with patch("shutil.which", return_value=None):  # FFmpeg not available
                renderer = BaseDebugOverlayRenderer(
                    output_path=temp_output_path,
                    width=640,
                    height=480,
                    display_width=640,
                    display_height=480,
                    fps=30.0,
                )

                # Should complete without error even if FFmpeg is missing
                renderer.close()  # Should not raise


class TestRegressionIOS:
    """Regression tests for iPhone 16 Pro video playback issue.

    CRITICAL: These tests prevent the iOS VP9 playback bug from returning.
    """

    def test_ios_compatible_codec_used(self) -> None:
        """Test that iOS-compatible codecs are prioritized (not VP9)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "test.mp4")

            with patch("cv2.VideoWriter") as mock_writer_class:
                # Simulate a scenario where first codec succeeds
                call_count = [0]

                def mock_writer_factory(*args: Any, **kwargs: Any) -> MagicMock:
                    writer = MagicMock()
                    # First codec (avc1 or h264) should succeed
                    call_count[0] += 1
                    writer.isOpened.return_value = call_count[0] == 1
                    return writer

                mock_writer_class.side_effect = mock_writer_factory

                _, _, codec = create_video_writer(
                    output_path=output_path,
                    width=640,
                    height=480,
                    display_width=640,
                    display_height=480,
                    fps=30.0,
                )

                # Should use H.264 (avc1) not VP9
                assert codec == "avc1", f"Expected avc1, got {codec}"
                assert codec != "vp09", "VP9 breaks iPhone playback!"
