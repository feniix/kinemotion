"""Shared debug overlay utilities for video rendering."""

import os
import shutil
import subprocess
import time
from pathlib import Path

import cv2
import numpy as np


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
    # avc1/h264: H.264 (Most compatible)
    # vp09: VP9 (Good compatibility)
    # mp4v: MPEG-4 (Poor browser support, last resort)
    codecs_to_try = ["avc1", "h264", "vp09", "mp4v"]

    writer = None
    used_codec = "mp4v"  # Default fallback

    for codec in codecs_to_try:
        try:
            fourcc = cv2.VideoWriter_fourcc(*codec)
            writer = cv2.VideoWriter(
                output_path, fourcc, fps, (display_width, display_height)
            )
            if writer.isOpened():
                used_codec = codec
                if codec == "mp4v":
                    print(
                        f"Warning: Fallback to {codec} codec. "
                        "Video may not play in browsers."
                    )
                break
        except Exception:
            continue

    if writer is None or not writer.isOpened():
        raise ValueError(
            f"Failed to create video writer for {output_path} with dimensions "
            f"{display_width}x{display_height}"
        )

    return writer, needs_resize, used_codec


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
        """
        self.output_path = output_path
        self.width = width
        self.height = height
        self.display_width = display_width
        self.display_height = display_height
        self.writer, self.needs_resize, self.used_codec = create_video_writer(
            output_path, width, height, display_width, display_height, fps
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
            frame = cv2.resize(
                frame,
                (self.display_width, self.display_height),
                interpolation=cv2.INTER_LANCZOS4,
            )

        write_overlay_frame(self.writer, frame, self.display_width, self.display_height)

    def close(self) -> None:
        """Release video writer and re-encode if possible."""
        self.writer.release()

        # Post-process with ffmpeg ONLY if we fell back to the incompatible mp4v codec
        if self.used_codec == "mp4v" and shutil.which("ffmpeg"):
            temp_path = None
            try:
                temp_path = str(
                    Path(self.output_path).with_suffix(
                        ".temp" + Path(self.output_path).suffix
                    )
                )

                # Convert to H.264 with yuv420p pixel format for browser compatibility
                # -y: Overwrite output file
                # -vcodec libx264: Use H.264 codec
                # -pix_fmt yuv420p: Required for wide browser support (Chrome,
                #                   Safari, Firefox)
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

                # Suppress output unless error
                reencode_start = time.time()
                subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                )
                reencode_duration = time.time() - reencode_start
                print(f"Debug video re-encoded in {reencode_duration:.2f}s")

                # Overwrite original file
                os.replace(temp_path, self.output_path)

            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to re-encode debug video with ffmpeg: {e}")
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception as e:
                print(f"Warning: Error during video post-processing: {e}")
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)

    def __enter__(self) -> "BaseDebugOverlayRenderer":
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb) -> None:  # type: ignore[no-untyped-def]
        self.close()
