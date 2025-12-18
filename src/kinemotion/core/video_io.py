"""Generic video I/O functionality for all jump analysis types."""

import json
import subprocess
import warnings

import cv2
import numpy as np

from .timing import NULL_TIMER, Timer


class VideoProcessor:
    """
    Handles video reading and processing.

    IMPORTANT: This class preserves the exact aspect ratio of the source video.
    No dimensions are hardcoded - all dimensions are extracted from actual frame data.
    """

    def __init__(self, video_path: str, timer: Timer | None = None) -> None:
        """
        Initialize video processor.

        Args:
            video_path: Path to input video file
            timer: Optional Timer for measuring operations
        """
        self.video_path = video_path
        self.timer = timer or NULL_TIMER
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

        # Extract rotation metadata from video (iPhones store rotation in
        # side_data_list). OpenCV ignores rotation metadata, so we need to
        # extract and apply it manually
        self.rotation = 0  # Will be set by _extract_video_metadata()

        # Extract codec information from video metadata
        self.codec: str | None = None  # Will be set by _extract_video_metadata()

        # Calculate display dimensions considering SAR (Sample Aspect Ratio)
        # Mobile videos often have non-square pixels encoded in SAR metadata
        # OpenCV doesn't directly expose SAR, but we need to handle display correctly
        self.display_width = self.width
        self.display_height = self.height
        self._extract_video_metadata()

        # Apply rotation to dimensions if needed
        if self.rotation in [90, -90, 270]:
            # Swap dimensions for 90/-90 degree rotations
            self.width, self.height = self.height, self.width
            self.display_width, self.display_height = (
                self.display_height,
                self.display_width,
            )

    def _parse_sample_aspect_ratio(self, sar_str: str) -> None:
        """
        Parse SAR string and update display dimensions.

        Args:
            sar_str: SAR string in format "width:height" (e.g., "270:473")
        """
        if not sar_str or ":" not in sar_str:
            return

        sar_parts = sar_str.split(":")
        sar_width = int(sar_parts[0])
        sar_height = int(sar_parts[1])

        # Calculate display dimensions if pixels are non-square
        # DAR = (width * SAR_width) / (height * SAR_height)
        if sar_width != sar_height:
            self.display_width = int(self.width * sar_width / sar_height)
            self.display_height = self.height

    def _extract_rotation_from_stream(self, stream: dict) -> int:  # type: ignore[type-arg]
        """
        Extract rotation metadata from video stream.

        Args:
            stream: ffprobe stream dictionary

        Returns:
            Rotation angle in degrees (0, 90, -90, 180)
        """
        side_data_list = stream.get("side_data_list", [])
        for side_data in side_data_list:
            if side_data.get("side_data_type") == "Display Matrix":
                rotation = side_data.get("rotation", 0)
                return int(rotation)
        return 0

    def _extract_video_metadata(self) -> None:
        """
        Extract video metadata including SAR and rotation using ffprobe.

        Many mobile videos (especially from iPhones) have:
        - Non-square pixels (SAR != 1:1) affecting display dimensions
        - Rotation metadata in side_data_list that OpenCV ignores

        We extract both to ensure proper display and pose detection.
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

            if result.returncode != 0:
                return

            data = json.loads(result.stdout)
            if "streams" not in data or len(data["streams"]) == 0:
                return

            stream = data["streams"][0]

            # Extract codec name (e.g., "h264", "hevc", "vp9")
            self.codec = stream.get("codec_name")

            # Extract and parse SAR (Sample Aspect Ratio)
            sar_str = stream.get("sample_aspect_ratio", "1:1")
            self._parse_sample_aspect_ratio(sar_str)

            # Extract rotation from side_data_list (common for iPhone videos)
            self.rotation = self._extract_rotation_from_stream(stream)

        except FileNotFoundError:
            # ffprobe not found - warn user about reduced functionality
            warnings.warn(
                "ffprobe not found. Video rotation and aspect ratio metadata will be "
                "ignored. This may cause issues with mobile/rotated videos. "
                "Install FFmpeg for full video support: https://ffmpeg.org/download.html",
                UserWarning,
                stacklevel=2,
            )
        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            # If ffprobe fails for other reasons, silently continue with defaults
            pass

    def read_frame(self) -> np.ndarray | None:
        """
        Read next frame from video and apply rotation if needed.

        OpenCV ignores rotation metadata, so we manually apply rotation
        based on the display matrix metadata extracted from the video.
        """
        with self.timer.measure("frame_read"):
            ret, frame = self.cap.read()

        if not ret:
            return None

        # Apply rotation if video has rotation metadata
        with self.timer.measure("frame_rotation"):
            if self.rotation == -90 or self.rotation == 270:
                # -90 degrees = rotate 90 degrees clockwise
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            elif self.rotation == 90 or self.rotation == -270:
                # 90 degrees = rotate 90 degrees counter-clockwise
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            elif self.rotation == 180 or self.rotation == -180:
                # 180 degrees rotation
                frame = cv2.rotate(frame, cv2.ROTATE_180)

        return frame

    def close(self) -> None:
        """Release video capture."""
        self.cap.release()

    def __iter__(self) -> "VideoProcessor":
        """Make the processor iterable."""
        return self

    def __next__(self) -> np.ndarray:
        """Get the next frame during iteration."""
        frame = self.read_frame()
        if frame is None:
            raise StopIteration
        return frame

    def __enter__(self) -> "VideoProcessor":
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb) -> None:  # type: ignore[no-untyped-def]
        self.close()
