"""Generic video I/O functionality for all jump analysis types."""

import json
import subprocess

import cv2
import numpy as np


class VideoProcessor:
    """
    Handles video reading and processing.

    IMPORTANT: This class preserves the exact aspect ratio of the source video.
    No dimensions are hardcoded - all dimensions are extracted from actual frame data.
    """

    def __init__(self, video_path: str):
        """
        Initialize video processor.

        Args:
            video_path: Path to input video file
        """
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Read first frame to get actual dimensions
        # This is critical for preserving aspect ratio, especially with mobile videos
        # that have rotation metadata. OpenCV properties (CAP_PROP_FRAME_WIDTH/HEIGHT)
        # may return incorrect dimensions, so we read the actual frame data.
        ret, first_frame = self.cap.read()
        if ret:
            # frame.shape is (height, width, channels) - extract actual dimensions
            self.height, self.width = first_frame.shape[:2]
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
        else:
            # Fallback to video properties if can't read frame
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Calculate display dimensions considering SAR (Sample Aspect Ratio)
        # Mobile videos often have non-square pixels encoded in SAR metadata
        # OpenCV doesn't directly expose SAR, but we need to handle display correctly
        self.display_width = self.width
        self.display_height = self.height
        self._calculate_display_dimensions()

    def _calculate_display_dimensions(self) -> None:
        """
        Calculate display dimensions by reading SAR metadata from video file.

        Many mobile videos use non-square pixels (SAR != 1:1), which means
        the encoded dimensions differ from how the video should be displayed.
        We use ffprobe to extract this metadata.
        """
        try:
            # Use ffprobe to get SAR metadata
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "quiet",
                    "-print_format",
                    "json",
                    "-show_streams",
                    "-select_streams",
                    "v:0",
                    self.video_path,
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                if "streams" in data and len(data["streams"]) > 0:
                    stream = data["streams"][0]
                    sar_str = stream.get("sample_aspect_ratio", "1:1")

                    # Parse SAR (e.g., "270:473")
                    if sar_str and ":" in sar_str:
                        sar_parts = sar_str.split(":")
                        sar_width = int(sar_parts[0])
                        sar_height = int(sar_parts[1])

                        # Calculate display dimensions
                        # DAR = (width * SAR_width) / (height * SAR_height)
                        if sar_width != sar_height:
                            self.display_width = int(
                                self.width * sar_width / sar_height
                            )
                            self.display_height = self.height
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            # If ffprobe fails, keep original dimensions (square pixels)
            pass

    def read_frame(self) -> np.ndarray | None:
        """Read next frame from video."""
        ret, frame = self.cap.read()
        return frame if ret else None

    def reset(self) -> None:
        """Reset video to beginning."""
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def close(self) -> None:
        """Release video capture."""
        self.cap.release()

    def __enter__(self) -> "VideoProcessor":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        self.close()
