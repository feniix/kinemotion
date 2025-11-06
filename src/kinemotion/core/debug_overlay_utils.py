"""Shared debug overlay utilities for video rendering."""

import cv2
import numpy as np


def create_video_writer(
    output_path: str,
    width: int,
    height: int,
    display_width: int,
    display_height: int,
    fps: float,
) -> tuple[cv2.VideoWriter, bool]:
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
        Tuple of (video_writer, needs_resize)
    """
    needs_resize = (display_width != width) or (display_height != height)

    # Try H.264 codec first (better quality/compatibility), fallback to mp4v
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (display_width, display_height))

    # Check if writer opened successfully, fallback to mp4v if not
    if not writer.isOpened():
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(
            output_path, fourcc, fps, (display_width, display_height)
        )

    if not writer.isOpened():
        raise ValueError(
            f"Failed to create video writer for {output_path} with dimensions "
            f"{display_width}x{display_height}"
        )

    return writer, needs_resize


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
        self.width = width
        self.height = height
        self.display_width = display_width
        self.display_height = display_height
        self.writer, self.needs_resize = create_video_writer(
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
        """Release video writer."""
        self.writer.release()

    def __enter__(self) -> "BaseDebugOverlayRenderer":
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb) -> None:  # type: ignore[no-untyped-def]
        self.close()
