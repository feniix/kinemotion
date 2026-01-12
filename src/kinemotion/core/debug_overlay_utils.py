"""Shared debug overlay utilities for video rendering."""

# pyright: reportCallIssue=false
import os
import shutil
import subprocess
import time
from pathlib import Path

import cv2
import numpy as np
from typing_extensions import Self

from .overlay_constants import (
    ANKLE_COLOR,
    BLACK,
    CODECS_TO_TRY,
    CYAN,
    FFMPEG_CRF,
    FFMPEG_PIX_FMT,
    FFMPEG_PRESET,
    HIP_COLOR,
    JOINT_CIRCLE_RADIUS,
    JOINT_OUTLINE_RADIUS,
    KNEE_COLOR,
    MAX_VIDEO_DIMENSION,
    NOSE_CIRCLE_RADIUS,
    NOSE_OUTLINE_RADIUS,
    TRUNK_COLOR,
    VISIBILITY_THRESHOLD,
    WHITE,
    CodecAttemptLog,
    Color,
    Landmark,
    LandmarkDict,
)
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
    # See overlay_constants.py for codec list and critical VP9 exclusion notes
    codec_attempt_log: CodecAttemptLog = []

    for codec in CODECS_TO_TRY:
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
    attempt_log: CodecAttemptLog,
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
        if max(display_width, display_height) > MAX_VIDEO_DIMENSION:
            scale = MAX_VIDEO_DIMENSION / max(display_width, display_height)
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

    def _normalize_to_pixels(self, x: float, y: float) -> tuple[int, int]:
        """Convert normalized coordinates (0-1) to pixel coordinates.

        Args:
            x: Normalized x coordinate (0-1)
            y: Normalized y coordinate (0-1)

        Returns:
            Tuple of (pixel_x, pixel_y)
        """
        return int(x * self.width), int(y * self.height)

    def _landmark_to_pixel(self, landmark: Landmark) -> tuple[int, int]:
        """Convert normalized landmark coordinates to pixel coordinates."""
        return self._normalize_to_pixels(landmark[0], landmark[1])

    def _is_visible(self, landmark: Landmark, threshold: float = VISIBILITY_THRESHOLD) -> bool:
        """Check if a landmark has sufficient visibility."""
        return landmark[2] > threshold

    def _get_skeleton_segments(self, side_prefix: str) -> list[tuple[str, str, Color, int]]:
        """Get skeleton segments for one side of the body.

        Returns list of (start_key, end_key, color, thickness) tuples.
        """
        p = side_prefix  # Shorter alias for readability
        return [
            (f"{p}heel", f"{p}ankle", ANKLE_COLOR, 3),  # Foot
            (f"{p}heel", f"{p}foot_index", ANKLE_COLOR, 2),  # Alt foot
            (f"{p}ankle", f"{p}knee", KNEE_COLOR, 4),  # Shin
            (f"{p}knee", f"{p}hip", HIP_COLOR, 4),  # Femur
            (f"{p}hip", f"{p}shoulder", TRUNK_COLOR, 4),  # Trunk
            (f"{p}shoulder", "nose", (150, 150, 255), 2),  # Neck
        ]

    def _draw_segment(
        self,
        frame: np.ndarray,
        landmarks: LandmarkDict,
        start_key: str,
        end_key: str,
        color: Color,
        thickness: int,
    ) -> None:
        """Draw a single skeleton segment if both endpoints are visible."""
        if start_key not in landmarks or end_key not in landmarks:
            return

        start_landmark = landmarks[start_key]
        end_landmark = landmarks[end_key]

        if not (self._is_visible(start_landmark) and self._is_visible(end_landmark)):
            return

        start_pt = self._landmark_to_pixel(start_landmark)
        end_pt = self._landmark_to_pixel(end_landmark)
        cv2.line(frame, start_pt, end_pt, color, thickness)

    def _draw_joints(
        self,
        frame: np.ndarray,
        landmarks: LandmarkDict,
        side_prefix: str,
    ) -> None:
        """Draw joint circles for one side of the body."""
        p = side_prefix
        joint_keys = [
            f"{p}heel",
            f"{p}foot_index",
            f"{p}ankle",
            f"{p}knee",
            f"{p}hip",
            f"{p}shoulder",
        ]

        for key in joint_keys:
            if key not in landmarks:
                continue
            landmark = landmarks[key]
            if not self._is_visible(landmark):
                continue

            point = self._landmark_to_pixel(landmark)
            cv2.circle(frame, point, JOINT_CIRCLE_RADIUS, WHITE, -1)
            cv2.circle(frame, point, JOINT_OUTLINE_RADIUS, BLACK, 2)

    def _draw_skeleton(self, frame: np.ndarray, landmarks: LandmarkDict) -> None:
        """Draw skeleton segments showing body landmarks.

        Draws whatever landmarks are visible. In side-view videos, ankle/knee
        may have low visibility, so we draw available segments.

        Args:
            frame: Frame to draw on (modified in place)
            landmarks: Pose landmarks
        """
        # Draw segments and joints for both sides
        for side_prefix in ["right_", "left_"]:
            for start_key, end_key, color, thickness in self._get_skeleton_segments(side_prefix):
                self._draw_segment(frame, landmarks, start_key, end_key, color, thickness)
            self._draw_joints(frame, landmarks, side_prefix)

        # Draw nose (head position) if visible
        if "nose" in landmarks and self._is_visible(landmarks["nose"]):
            point = self._landmark_to_pixel(landmarks["nose"])
            cv2.circle(frame, point, NOSE_CIRCLE_RADIUS, CYAN, -1)
            cv2.circle(frame, point, NOSE_OUTLINE_RADIUS, BLACK, 2)

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
            FFMPEG_PIX_FMT,
            "-preset",
            FFMPEG_PRESET,
            "-crf",
            FFMPEG_CRF,
            "-an",
            temp_path,
        ]

        _log(
            "info",
            "debug_video_ffmpeg_reencoding_start",
            input_file=self.output_path,
            output_file=temp_path,
            output_codec="libx264",
            pixel_format=FFMPEG_PIX_FMT,
            reason="iOS_compatibility",
        )

        try:
            reencode_start = time.perf_counter()
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            self.reencode_duration_s = time.perf_counter() - reencode_start

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
                pixel_format=FFMPEG_PIX_FMT,
            )
        except Exception as e:
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
