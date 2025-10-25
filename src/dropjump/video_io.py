"""Video I/O and debug overlay rendering."""


import json
import subprocess

import cv2
import numpy as np

from .contact_detection import ContactState, compute_average_foot_position
from .kinematics import DropJumpMetrics
from .pose_tracker import compute_center_of_mass


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


class DebugOverlayRenderer:
    """Renders debug information on video frames."""

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
        self.needs_resize = (display_width != width) or (display_height != height)

        # Try H.264 codec first (better quality/compatibility), fallback to mp4v
        fourcc = cv2.VideoWriter_fourcc(*"avc1")  # type: ignore[attr-defined]
        # IMPORTANT: cv2.VideoWriter expects (width, height) tuple - NOT (height, width)
        # Write at display dimensions so video displays correctly without SAR metadata
        self.writer = cv2.VideoWriter(
            output_path, fourcc, fps, (display_width, display_height)
        )

        # Check if writer opened successfully, fallback to mp4v if not
        if not self.writer.isOpened():
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # type: ignore[attr-defined]
            self.writer = cv2.VideoWriter(
                output_path, fourcc, fps, (display_width, display_height)
            )

        if not self.writer.isOpened():
            raise ValueError(
                f"Failed to create video writer for {output_path} with dimensions "
                f"{display_width}x{display_height}"
            )

    def render_frame(
        self,
        frame: np.ndarray,
        landmarks: dict[str, tuple[float, float, float]] | None,
        contact_state: ContactState,
        frame_idx: int,
        metrics: DropJumpMetrics | None = None,
        use_com: bool = False,
    ) -> np.ndarray:
        """
        Render debug overlay on frame.

        Args:
            frame: Original video frame
            landmarks: Pose landmarks for this frame
            contact_state: Ground contact state
            frame_idx: Current frame index
            metrics: Drop-jump metrics (optional)
            use_com: Whether to visualize CoM instead of feet (optional)

        Returns:
            Frame with debug overlay
        """
        annotated = frame.copy()

        # Draw landmarks if available
        if landmarks:
            if use_com:
                # Draw center of mass position
                com_x, com_y, com_vis = compute_center_of_mass(landmarks)
                px = int(com_x * self.width)
                py = int(com_y * self.height)

                # Draw CoM with larger circle
                color = (
                    (0, 255, 0) if contact_state == ContactState.ON_GROUND else (0, 0, 255)
                )
                cv2.circle(annotated, (px, py), 15, color, -1)
                cv2.circle(annotated, (px, py), 17, (255, 255, 255), 2)  # White border

                # Draw body segments for reference
                # Draw hip midpoint
                if "left_hip" in landmarks and "right_hip" in landmarks:
                    lh_x, lh_y, _ = landmarks["left_hip"]
                    rh_x, rh_y, _ = landmarks["right_hip"]
                    hip_x = int((lh_x + rh_x) / 2 * self.width)
                    hip_y = int((lh_y + rh_y) / 2 * self.height)
                    cv2.circle(annotated, (hip_x, hip_y), 8, (255, 165, 0), -1)  # Orange
                    # Draw line from hip to CoM
                    cv2.line(annotated, (hip_x, hip_y), (px, py), (255, 165, 0), 2)
            else:
                # Draw foot position (original method)
                foot_x, foot_y = compute_average_foot_position(landmarks)
                px = int(foot_x * self.width)
                py = int(foot_y * self.height)

                # Draw foot position circle
                color = (
                    (0, 255, 0) if contact_state == ContactState.ON_GROUND else (0, 0, 255)
                )
                cv2.circle(annotated, (px, py), 10, color, -1)

                # Draw individual foot landmarks
                foot_keys = ["left_ankle", "right_ankle", "left_heel", "right_heel"]
                for key in foot_keys:
                    if key in landmarks:
                        x, y, vis = landmarks[key]
                        if vis > 0.5:
                            lx = int(x * self.width)
                            ly = int(y * self.height)
                            cv2.circle(annotated, (lx, ly), 5, (255, 255, 0), -1)

        # Draw contact state
        state_text = f"State: {contact_state.value}"
        state_color = (
            (0, 255, 0) if contact_state == ContactState.ON_GROUND else (0, 0, 255)
        )
        cv2.putText(
            annotated,
            state_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            state_color,
            2,
        )

        # Draw frame number
        cv2.putText(
            annotated,
            f"Frame: {frame_idx}",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        # Draw metrics if in relevant phase
        if metrics:
            y_offset = 110
            if (
                metrics.contact_start_frame
                and metrics.contact_end_frame
                and metrics.contact_start_frame
                <= frame_idx
                <= metrics.contact_end_frame
            ):
                cv2.putText(
                    annotated,
                    "GROUND CONTACT",
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
                y_offset += 40

            if (
                metrics.flight_start_frame
                and metrics.flight_end_frame
                and metrics.flight_start_frame <= frame_idx <= metrics.flight_end_frame
            ):
                cv2.putText(
                    annotated,
                    "FLIGHT PHASE",
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )
                y_offset += 40

            if metrics.peak_height_frame == frame_idx:
                cv2.putText(
                    annotated,
                    "PEAK HEIGHT",
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 0, 255),
                    2,
                )

        return annotated

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

        self.writer.write(frame)

    def close(self) -> None:
        """Release video writer."""
        self.writer.release()

    def __enter__(self) -> "DebugOverlayRenderer":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        self.close()
