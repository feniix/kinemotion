"""Shared debug overlay utilities for video rendering."""

# pyright: reportCallIssue=false
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from typing_extensions import Self

from .timing import NULL_TIMER, Timer

# Setup logging with structlog support for backend, fallback to standard logging for CLI
try:
    import structlog

    logger = structlog.get_logger(__name__)
    _using_structlog = True
except ImportError:
    import logging

    logger = logging.getLogger(__name__)
    _using_structlog = False


def _log(level: str, message: str, **kwargs: object) -> None:
    """Log message with kwargs support for both structlog and standard logging."""
    if _using_structlog:
        getattr(logger, level)(message, **kwargs)
    else:
        # For standard logging, format kwargs as part of the message
        if kwargs:
            kwargs_str = " ".join(f"{k}={v}" for k, v in kwargs.items())
            getattr(logger, level)(f"{message} {kwargs_str}")
        else:
            getattr(logger, level)(message)


def create_video_writer(
    output_path: str,
    width: int,
    height: int,
    display_width: int,
    display_height: int,
    fps: float,
) -> tuple[cv2.VideoWriter, bool, str]:
    """
    Create a video writer with fallback codec support.

    ⚠️  CRITICAL: DO NOT add "vp09" (VP9) to the codec list!
    VP9 is not supported on iOS browsers (iPhone/iPad) and causes playback failures.
    Regression test: tests/core/test_debug_overlay_utils.py::test_vp09_codec_never_in_codec_list

    Args:
        output_path: Path for output video
        width: Encoded frame width (from source video)
        height: Encoded frame height (from source video)
        display_width: Display width (considering SAR)
        display_height: Display height (considering SAR)
        fps: Frames per second

    Returns:
        Tuple of (video_writer, needs_resize, used_codec)
    """
    needs_resize = (display_width != width) or (display_height != height)

    # Try browser-compatible codecs first
    # avc1: H.264 (Most compatible, including iOS)
    # mp4v: MPEG-4 (Poor browser support, will trigger ffmpeg re-encoding for H.264)
    # ⚠️  CRITICAL: VP9 (vp09) is EXCLUDED - not supported on iOS/iPhone/iPad browsers!
    #     Adding VP9 will break debug video playback on all iOS devices.
    codecs_to_try = ["avc1", "mp4v"]
    codec_attempt_log: list[dict[str, Any]] = []

    for codec in codecs_to_try:
        writer = _try_open_video_writer(
            output_path, codec, fps, display_width, display_height, codec_attempt_log
        )
        if writer:
            return writer, needs_resize, codec

    _log(
        "error",
        "debug_video_writer_creation_failed",
        output_path=output_path,
        dimensions=f"{display_width}x{display_height}",
        fps=fps,
        codec_attempts=codec_attempt_log,
    )
    raise ValueError(
        f"Failed to create video writer for {output_path} with dimensions "
        f"{display_width}x{display_height}"
    )


def _try_open_video_writer(
    output_path: str,
    codec: str,
    fps: float,
    width: int,
    height: int,
    attempt_log: list[dict[str, Any]],
) -> cv2.VideoWriter | None:
    """Attempt to open a video writer with a specific codec."""
    try:
        fourcc = cv2.VideoWriter_fourcc(*codec)  # type: ignore[attr-defined]
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        if writer.isOpened():
            attempt_log.append({"codec": codec, "status": "success"})
            _log(
                "info",
                "debug_video_codec_selected",
                codec=codec,
                width=width,
                height=height,
                fps=fps,
            )
            if codec == "mp4v":
                msg = (
                    "Using fallback MPEG-4 codec; will re-encode with ffmpeg for "
                    "browser compatibility"
                )
                _log("warning", "debug_video_fallback_codec", codec="mp4v", warning=msg)
            return writer

        attempt_log.append(
            {"codec": codec, "status": "failed", "error": "isOpened() returned False"}
        )
    except Exception as e:
        attempt_log.append({"codec": codec, "status": "failed", "error": str(e)})
        _log("info", "debug_video_codec_attempt_failed", codec=codec, error=str(e))

    return None


def write_overlay_frame(
    writer: cv2.VideoWriter, frame: np.ndarray, width: int, height: int
) -> None:
    """
    Write a frame to the video writer with dimension validation.

    Args:
        writer: Video writer instance
        frame: Frame to write
        width: Expected frame width
        height: Expected frame height

    Raises:
        ValueError: If frame dimensions don't match expected dimensions
    """
    # Validate dimensions before writing
    if frame.shape[0] != height or frame.shape[1] != width:
        raise ValueError(
            f"Frame dimensions {frame.shape[1]}x{frame.shape[0]} do not match "
            f"expected dimensions {width}x{height}"
        )
    writer.write(frame)


class BaseDebugOverlayRenderer:
    """Base class for debug overlay renderers with common functionality."""

    def __init__(
        self,
        output_path: str,
        width: int,
        height: int,
        display_width: int,
        display_height: int,
        fps: float,
        timer: Timer | None = None,
    ):
        """
        Initialize overlay renderer.

        Args:
            output_path: Path for output video
            width: Encoded frame width (from source video)
            height: Encoded frame height (from source video)
            display_width: Display width (considering SAR)
            display_height: Display height (considering SAR)
            fps: Frames per second
            timer: Optional Timer for measuring operations
        """
        self.output_path = output_path
        self.width = width
        self.height = height
        self.timer = timer or NULL_TIMER

        # Optimize debug video resolution: Cap max dimension to 720p
        # Reduces software encoding time on single-core Cloud Run instances.
        # while keeping sufficient quality for visual debugging.
        max_dimension = 720
        if max(display_width, display_height) > max_dimension:
            scale = max_dimension / max(display_width, display_height)
            # Ensure dimensions are even for codec compatibility
            self.display_width = int(display_width * scale) // 2 * 2
            self.display_height = int(display_height * scale) // 2 * 2
            _log(
                "info",
                "debug_video_resolution_optimized",
                original_width=display_width,
                original_height=display_height,
                optimized_width=self.display_width,
                optimized_height=self.display_height,
                scale_factor=round(scale, 2),
            )
        else:
            self.display_width = display_width
            self.display_height = display_height
            _log(
                "info",
                "debug_video_resolution_native",
                width=self.display_width,
                height=self.display_height,
            )

        _log(
            "info",
            "debug_overlay_renderer_initialized",
            output_path=output_path,
            source_width=width,
            source_height=height,
            output_width=self.display_width,
            output_height=self.display_height,
            fps=fps,
        )

        # Duration of ffmpeg re-encoding (0.0 if not needed)
        self.reencode_duration_s = 0.0
        self.writer, self.needs_resize, self.used_codec = create_video_writer(
            output_path, width, height, self.display_width, self.display_height, fps
        )

    def write_frame(self, frame: np.ndarray) -> None:
        """
        Write frame to output video.

        Args:
            frame: Video frame with shape (height, width, 3)

        Raises:
            ValueError: If frame dimensions don't match expected encoded dimensions
        """
        # Validate frame dimensions match expected encoded dimensions
        frame_height, frame_width = frame.shape[:2]
        if frame_height != self.height or frame_width != self.width:
            raise ValueError(
                f"Frame dimensions ({frame_width}x{frame_height}) don't match "
                f"source dimensions ({self.width}x{self.height}). "
                f"Aspect ratio must be preserved from source video."
            )

        # Resize to display dimensions if needed (to handle SAR)
        if self.needs_resize:
            with self.timer.measure("debug_video_resize"):
                frame = cv2.resize(
                    frame,
                    (self.display_width, self.display_height),
                    interpolation=cv2.INTER_LINEAR,
                )

        with self.timer.measure("debug_video_write"):
            write_overlay_frame(self.writer, frame, self.display_width, self.display_height)

    def close(self) -> None:
        """Release video writer and re-encode if possible."""
        self.writer.release()
        _log(
            "info",
            "debug_video_writer_released",
            output_path=self.output_path,
            codec=self.used_codec,
        )

        if self.used_codec != "mp4v":
            _log(
                "info",
                "debug_video_ready_for_playback",
                codec=self.used_codec,
                path=self.output_path,
            )
            return

        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            _log(
                "warning",
                "debug_video_ffmpeg_not_available",
                codec=self.used_codec,
                output_path=self.output_path,
                warning="Video may not play in all browsers",
            )
            return

        self._reencode_to_h264()

    def _reencode_to_h264(self) -> None:
        """Re-encode video to H.264 for browser compatibility using ffmpeg."""
        temp_path = str(
            Path(self.output_path).with_suffix(".temp" + Path(self.output_path).suffix)
        )

        # Convert to H.264 with yuv420p pixel format for browser compatibility
        # -y: Overwrite output file
        # -vcodec libx264: Use H.264 codec
        # -pix_fmt yuv420p: Required for wide browser support (Chrome, Safari, Firefox, iOS)
        # -preset fast: Reasonable speed/compression tradeoff
        # -crf 23: Standard quality
        # -an: Remove audio (debug video has no audio)
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            self.output_path,
            "-vcodec",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "fast",
            "-crf",
            "23",
            "-an",
            temp_path,
        ]

        _log(
            "info",
            "debug_video_ffmpeg_reencoding_start",
            input_file=self.output_path,
            output_file=temp_path,
            output_codec="libx264",
            pixel_format="yuv420p",
            reason="iOS_compatibility",
        )

        try:
            reencode_start = time.time()
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            self.reencode_duration_s = time.time() - reencode_start

            _log(
                "info",
                "debug_video_ffmpeg_reencoding_complete",
                duration_ms=round(self.reencode_duration_s * 1000, 1),
            )

            os.replace(temp_path, self.output_path)
            _log(
                "info",
                "debug_video_reencoded_file_replaced",
                output_path=self.output_path,
                final_codec="libx264",
                pixel_format="yuv420p",
            )
        except (subprocess.CalledProcessError, Exception) as e:
            self._handle_reencode_error(e, temp_path)

    def _handle_reencode_error(self, e: Exception, temp_path: str) -> None:
        """Handle errors during ffmpeg re-encoding."""
        if isinstance(e, subprocess.CalledProcessError):
            stderr_msg = e.stderr.decode("utf-8", errors="ignore") if e.stderr else "N/A"
            _log(
                "warning",
                "debug_video_ffmpeg_reencoding_failed",
                error=str(e),
                stderr=stderr_msg,
            )
        else:
            _log("warning", "debug_video_post_processing_error", error=str(e))

        if os.path.exists(temp_path):
            os.remove(temp_path)
            _log("info", "debug_video_temp_file_cleaned_up", temp_file=temp_path)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb) -> None:  # type: ignore[no-untyped-def]
        self.close()
